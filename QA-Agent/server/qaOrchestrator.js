// QA Agent orchestrator: classify -> retrieve (workspace knowledge base) -> reason (LLM) -> validate.
// Retrieval runs in memory over the workspace JSON files with BM25, so a trial works without
// MongoDB. Generation uses Groq when GROQ_API_KEY is set; otherwise the agent returns a
// retrieval-grounded draft so the workflow can still be demonstrated end to end.
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import Groq from 'groq-sdk';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA = path.join(__dirname, '..', 'src', 'data');

export const WORKSPACES = {
  servynx: {
    id: 'servynx',
    name: 'Servynx Marketplace',
    url: 'https://www.servynx.com',
    description: 'Service marketplace: seekers post requirements, providers buy leads with credits.',
    stories: path.join(DATA, 'servynx', 'stories.json'),
    testcases: path.join(DATA, 'servynx', 'testcases.json'),
  },
  healthcare: {
    id: 'healthcare',
    name: 'Health Care (sample)',
    description: 'Original hospital management sample data.',
    stories: path.join(DATA, 'stories.json'),
    testcases: path.join(DATA, 'testcases.json'),
  },
};

const LABELS = {
  requirements: 'Requirement analysis',
  'test-cases': 'Test case generation',
  'test-data': 'Test data generation',
  'api-bdd': 'API and BDD mapping',
  defects: 'Defect analysis',
  'test-plan': 'Test plan creation',
};

const INSTRUCTIONS = {
  requirements: 'Analyse the requirement: list scope, ambiguities/gaps, missing acceptance criteria, risks and questions for the product owner.',
  'test-cases': 'Write new test cases (positive, negative, boundary, security). Do not duplicate the existing test cases provided; reference them where they already cover something.',
  'test-data': 'Produce test data sets (valid, invalid, boundary). Use obviously fake values only; never real personal data.',
  'api-bdd': 'Write Gherkin scenarios (Feature/Scenario/Given/When/Then) and list the API calls each scenario likely exercises.',
  defects: 'Analyse the described defect: likely root causes, affected stories/modules, regression tests to run, and severity.',
  'test-plan': 'Create a concise test plan: scope, out of scope, approach by test type, environments, entry/exit criteria, risks and the regression set to run.',
};

// ---------- knowledge base + BM25 ----------
const cache = new Map();
const STOP = new Set('a an the and or of to in on for with is are be as at by from that this it i we you my our so when then given should can will not no'.split(' '));
const tokenize = (t) => String(t || '').toLowerCase().replace(/[^a-z0-9\s]/g, ' ').split(/\s+/).filter((w) => w.length > 1 && !STOP.has(w));

function storyText(s) { return [s.key, s.summary, s.description, s.epic, (s.components || []).join(' '), s.acceptanceCriteria].join(' '); }
function testText(t) { return [t.id, t.module, t.title, t.description, t.steps, t.expectedResults, t.linkedStories, t.type].join(' '); }

function buildIndex(docs) {
  const toks = docs.map((d) => tokenize(d.text));
  const df = new Map();
  toks.forEach((ts) => new Set(ts).forEach((w) => df.set(w, (df.get(w) || 0) + 1)));
  const avg = toks.reduce((a, t) => a + t.length, 0) / Math.max(toks.length, 1);
  return { docs, toks, df, avg, N: docs.length };
}

function bm25(index, query, k = 6) {
  const q = tokenize(query); const { toks, df, avg, N } = index; const k1 = 1.4, b = 0.75;
  return toks.map((ts, i) => {
    const tf = new Map(); ts.forEach((w) => tf.set(w, (tf.get(w) || 0) + 1));
    let score = 0;
    q.forEach((w) => {
      const f = tf.get(w); if (!f) return;
      const idf = Math.log(1 + (N - df.get(w) + 0.5) / (df.get(w) + 0.5));
      score += idf * (f * (k1 + 1)) / (f + k1 * (1 - b + b * ts.length / avg));
    });
    return { i, score };
  }).filter((r) => r.score > 0).sort((a, b2) => b2.score - a.score).slice(0, k).map((r) => ({ ...index.docs[r.i], score: +r.score.toFixed(2) }));
}

export function loadWorkspace(id) {
  const ws = WORKSPACES[id] || WORKSPACES.servynx;
  if (cache.has(ws.id)) return cache.get(ws.id);
  const read = (f) => (fs.existsSync(f) ? JSON.parse(fs.readFileSync(f, 'utf8')) : []);
  const stories = read(ws.stories); const testcases = read(ws.testcases);
  const kb = {
    ws, stories, testcases,
    storyIndex: buildIndex(stories.map((s) => ({ kind: 'story', id: s.key, title: s.summary, module: (s.components || [])[0] || s.epic, raw: s, text: storyText(s) }))),
    testIndex: buildIndex(testcases.map((t) => ({ kind: 'testcase', id: t.id, title: t.title, module: t.module, raw: t, text: testText(t) }))),
  };
  cache.set(ws.id, kb);
  return kb;
}

export function workspaceSummaries() {
  return Object.keys(WORKSPACES).map((id) => {
    const kb = loadWorkspace(id);
    const modules = [...new Set(kb.stories.map((s) => (s.components || [])[0] || s.epic).filter(Boolean))];
    return { id, name: kb.ws.name, description: kb.ws.description, url: kb.ws.url || null, stories: kb.stories.length, testcases: kb.testcases.length, modules };
  });
}

// ---------- guardrails ----------
const PII = [/\b[\w.+-]+@[\w-]+\.[\w.]+\b/, /\b(?:\d[ -]?){13,16}\b/, /\b\d{3}[- ]?\d{2}[- ]?\d{4}\b/, /password\s*[:=]/i, /(api[_-]?key|secret|token)\s*[:=]/i];
const hasSensitive = (text) => PII.some((r) => r.test(text));
function redact(text) {
  return String(text)
    .replace(/\b[\w.+-]+@[\w-]+\.[\w.]+\b/g, '[email]')
    .replace(/\b(?:\d[ -]?){13,16}\b/g, '[card]')
    .replace(/(password|api[_-]?key|secret|token)(\s*[:=]\s*)\S+/gi, '$1$2[redacted]');
}

// ---------- LLM ----------
let groq = null;
function llm() {
  if (!process.env.GROQ_API_KEY || process.env.GROQ_API_KEY.startsWith('your_')) return null;
  if (!groq) groq = new Groq({ apiKey: process.env.GROQ_API_KEY });
  return groq;
}

function contextBlock(stories, tests) {
  const s = stories.map((d) => `STORY ${d.id} [${d.module}] ${d.title}\n${d.raw.description}\nAcceptance criteria:\n${d.raw.acceptanceCriteria}`).join('\n\n');
  const t = tests.map((d) => `TEST ${d.id} [${d.module}] ${d.title} (links ${d.raw.linkedStories}, ${d.raw.type})\nExpected: ${d.raw.expectedResults}`).join('\n');
  return `${s}\n\nEXISTING TEST CASES:\n${t}`;
}

async function generate(client, { capability, label, prompt, area, kb, stories, tests }) {
  const system = `You are QA Agent, a senior QA engineer for the application "${kb.ws.name}" (${kb.ws.description}).
Ground every statement in the retrieved context. If something is not in the context, list it under "assumptions".
${INSTRUCTIONS[capability] || INSTRUCTIONS['test-cases']}
Return ONLY JSON: {"title": string, "summary": string, "items": [string], "artifacts": [{"id": string, "title": string, "details": string, "linkedStories": [string], "priority": "P1"|"P2"|"P3"}], "assumptions": [string]}`;
  const user = `Application area: ${area}\nQA objective: ${prompt}\n\nRETRIEVED CONTEXT:\n${contextBlock(stories, tests)}`;
  const res = await client.chat.completions.create({
    model: process.env.GROQ_SUMMARIZATION_MODEL || 'llama-3.3-70b-versatile',
    messages: [{ role: 'system', content: system }, { role: 'user', content: user }],
    temperature: 0.2, top_p: 0.9, max_tokens: 4000, response_format: { type: 'json_object' },
  });
  const out = JSON.parse(res.choices[0].message.content);
  return { title: out.title || `${label} result`, summary: out.summary || '', items: out.items || [], artifacts: out.artifacts || [], assumptions: out.assumptions || [] };
}

function draftFromContext({ label, area, stories, tests }) {
  // No LLM configured: derive a grounded draft directly from the retrieved knowledge.
  const items = [];
  stories.slice(0, 4).forEach((s) => s.raw.acceptanceCriteria.split('\n').forEach((ac) => items.push(`${s.id}: cover "${ac}"`)));
  const covered = new Set(tests.map((t) => t.raw.linkedStories));
  const gaps = stories.filter((s) => !covered.has(s.id)).map((s) => `${s.id} ${s.title} has no retrieved test coverage`);
  return {
    title: `${label} draft (retrieval only)`,
    summary: `Grounded in ${stories.length} stories and ${tests.length} existing test cases for ${area}. Set GROQ_API_KEY to have the reasoning agent write the full artifact.`,
    items: items.slice(0, 12),
    artifacts: tests.map((t) => ({ id: t.id, title: t.title, details: t.raw.expectedResults, linkedStories: [t.raw.linkedStories], priority: t.raw.priority })),
    assumptions: gaps,
  };
}

export async function orchestrate({ capability = 'test-cases', prompt, source, workspace = 'servynx' }) {
  const kb = loadWorkspace(workspace);
  const label = LABELS[capability] || 'QA artifact generation';
  const area = source || kb.ws.name;
  const cleanPrompt = redact(prompt.trim());
  const query = `${cleanPrompt} ${area}`;
  const stories = bm25(kb.storyIndex, query, 6);
  const linked = new Set(stories.map((s) => s.id));
  const testsByQuery = bm25(kb.testIndex, query, 10);
  const testsByLink = kb.testIndex.docs.filter((d) => linked.has(d.raw.linkedStories));
  const tests = [...new Map([...testsByQuery, ...testsByLink].map((t) => [t.id, t])).values()].slice(0, 15);

  const client = llm();
  let output; let mode; let llmError = null;
  if (client && stories.length) {
    try { output = await generate(client, { capability, label, prompt: cleanPrompt, area, kb, stories, tests }); mode = 'orchestrated'; }
    catch (e) { llmError = e.message; }
  }
  if (!output) { output = draftFromContext({ label, area, stories, tests }); mode = 'retrieval-only'; }

  const knownIds = new Set([...kb.stories.map((s) => s.key), ...kb.testcases.map((t) => t.id)]);
  const cited = (output.artifacts || []).flatMap((a) => a.linkedStories || []);
  const unknown = cited.filter((id) => id && !knownIds.has(id));
  const outText = JSON.stringify(output);

  return {
    mode,
    workspace: { id: kb.ws.id, name: kb.ws.name },
    plan: ['Classify request', `Retrieve ${kb.ws.name} context`, `Run ${label} agent`, 'Apply validation guardrails'],
    retrieval: {
      query: cleanPrompt, strategy: 'BM25 over workspace knowledge base + linked test expansion',
      sources: [...new Set([...stories.map((s) => s.module), ...tests.map((t) => t.module)])].slice(0, 8),
      matches: stories.length + tests.length,
      stories: stories.map(({ id, title, module, score }) => ({ id, title, module, score })),
      testcases: tests.map(({ id, title, module, raw }) => ({ id, title, module, linkedStories: raw.linkedStories })),
    },
    validation: [
      { label: 'Prompt completeness', status: cleanPrompt.length >= 15 ? 'Passed' : 'Warning: objective is very short' },
      { label: 'Context relevance', status: stories.length ? `Passed (${stories.length} stories)` : 'Failed: no matching stories' },
      { label: 'Traceability', status: unknown.length ? `Warning: unknown IDs ${[...new Set(unknown)].join(', ')}` : 'Passed' },
      { label: 'Sensitive data scan', status: hasSensitive(prompt) ? 'Redacted input' : hasSensitive(outText) ? 'Warning: review output' : 'Passed' },
      ...(llmError ? [{ label: 'Reasoning agent', status: `Fallback: ${llmError}` }] : []),
    ],
    output,
  };
}
