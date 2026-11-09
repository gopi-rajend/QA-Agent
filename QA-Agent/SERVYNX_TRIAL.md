# QA Agent: Servynx Trial

This branch points QA Agent at **Servynx** (https://www.servynx.com), the TrustyBytes marketplace app, for an active trial.

## What changed

| Area | Change |
|---|---|
| Knowledge base | New `src/data/servynx/` with 24 user stories (`SVX-001`…`SVX-024`) and 55 test cases (`SVX_TC_001`…), in the same JSON/XLSX shapes as the healthcare sample. Story text files are in `releases/servynx-trial/stories/`. |
| Generator | `src/scripts/data-conversion/build-servynx-dataset.py` rebuilds all of the above. Edit the stories there and re-run it. |
| Orchestrator | `POST /api/qa/orchestrate` was a stub that always returned the same canned text. It now retrieves from the selected workspace (BM25, no MongoDB needed), runs the chosen capability through Groq, and applies guardrails (PII redaction on input, traceability check on story IDs, sensitive-data scan on output). If there's no Groq key, or Groq fails, it returns a draft built from retrieval only. |
| Workspaces | New `GET /api/workspaces` returns Servynx (default) and Health Care (sample). |
| Portal | Application selector, application-area suggestions, live evidence counts, artifacts/assumptions/grounding display, and a working **Export** (Markdown). Added `"proxy"` to `client/package.json`; without it the portal never reached the API in dev and always showed the canned preview. |
| Bug fix | `groqClient.js` crashed the server at startup when `GROQ_API_KEY` was unset. The client is now created lazily. |

## Run the trial

```powershell
cd QA-Agent
Copy-Item .env.example .env      # set GROQ_API_KEY for full generation
npm install
npm run dev                      # portal http://localhost:3000, API http://localhost:3001
```

1. Under Application, choose **Servynx Marketplace**.
2. Pick a capability and an application area (e.g. *Credits*, *Post Requirement*), then describe the objective.
3. Select **Run QA workflow**, review the output, and select **Export**.

Optional: to use the existing MongoDB vector/hybrid search screens with Servynx data, upload `src/data/servynx/testcases.xlsx` and `userstories.xlsx` through the existing Convert / Embeddings screens.

### Suggested trial prompts

| Capability | Area | Objective |
|---|---|---|
| Test case generation | Credits | Regression suite for buying credits and unlocking provider contacts, including payment failures and double-click charges |
| Requirement analysis | Post Requirement | Find gaps and open questions in the requirement posting flow (category, postal code, attachments, privacy) |
| Test data generation | Post Requirement | Valid and invalid postal codes for Canada, US, India, UK, EU and Middle East |
| API & BDD mapping | Role Switch | Gherkin scenarios for seeker/provider switching and provider lead purchase |
| Defect analysis | Settings | Settings > Contact Details shows "No email on file" while the header shows the signed-in email |
| Test plan creation | Servynx Marketplace | Release test plan for the seeker journey from sign-in to chatting with a provider |

## How the knowledge base was built

On 2026-11-08 we walked through the Servynx seeker view in read-only mode: Dashboard, Post Requirement (Fill Form / Just Say / Voice), My Requirements, Find Providers, Invitations Sent, My Connects, Chat, Credits and Settings. Nothing was posted, purchased or changed.

- **Observed** stories (21) come straight from the UI.
- **Inferred** stories (3: SVX-018, SVX-022, SVX-023) cover the provider side and credit unlocking. They're based on on-screen text and need confirming by TrustyBytes.

## Early observations to share with TrustyBytes

1. **Settings > Contact Details** shows "No email on file" while the header shows the signed-in email (see SVX_TC test for SVX-019).
2. **Dashboard tiles** briefly show "—" before data loads. The tests check that they always end on a number.
3. **Find Providers** returns 0 providers for all categories and regions, so discovery, invitations and chat can't be tested end to end without seeded provider data.
4. **My Connects** shows "Loading…" with no visible empty state for a new account.

## Feedback we're asking for

- Are the 24 stories accurate? Please correct the inferred provider-side stories.
- Would TrustyBytes provide a staging environment and test provider accounts so the provider journey can be covered?
- Which output formats help most (Markdown, Excel, qTest/JIRA import)?
