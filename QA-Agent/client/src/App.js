import React, { useState } from 'react';
import {
  Box, Button, Chip, CssBaseline, Divider, Drawer, IconButton,
  LinearProgress, List, ListItemButton, ListItemIcon, ListItemText, Paper,
  Stack, ThemeProvider, Tooltip, Typography, createTheme,
} from '@mui/material';
import {
  AssessmentOutlined, BugReportOutlined, ChecklistOutlined, ChevronLeft,
  ContentPasteSearchOutlined, DescriptionOutlined, DownloadOutlined, HubOutlined,
  IntegrationInstructionsOutlined, Menu, PsychologyOutlined, ScienceOutlined,
  SettingsOutlined, ShieldOutlined, StorageOutlined, TableChartOutlined,
  UploadFileOutlined,
} from '@mui/icons-material';
import { SnackbarProvider, useSnackbar } from 'notistack';
import './App.css';

const capabilities = [
  { id: 'requirements', label: 'Requirement analysis', short: 'Scope, gaps & risk', icon: <ContentPasteSearchOutlined /> },
  { id: 'test-cases', label: 'Test case generation', short: 'Positive to edge cases', icon: <ChecklistOutlined /> },
  { id: 'test-data', label: 'Test data generation', short: 'Valid, masked & boundary', icon: <TableChartOutlined /> },
  { id: 'api-bdd', label: 'API & BDD mapping', short: 'Contracts & Gherkin', icon: <IntegrationInstructionsOutlined /> },
  { id: 'defects', label: 'Defect analysis', short: 'Root cause & impact', icon: <BugReportOutlined /> },
  { id: 'test-plan', label: 'Test plan creation', short: 'Strategy & execution', icon: <AssessmentOutlined /> },
];
const evidence = [
  { title: 'User stories', detail: '48 indexed records', tone: 'teal' },
  { title: 'Test repository', detail: '1,240 test cases', tone: 'blue' },
  { title: 'API specifications', detail: '12 OpenAPI contracts', tone: 'orange' },
  { title: 'Defect history', detail: '326 resolved issues', tone: 'red' },
];
const theme = createTheme({
  palette: { mode: 'light', primary: { main: '#0f5b61', dark: '#093c41', light: '#d9f0ec' }, secondary: { main: '#e8793e' }, background: { default: '#f4f7f5', paper: '#ffffff' }, text: { primary: '#153437', secondary: '#607476' } },
  typography: { fontFamily: '"DM Sans", "Trebuchet MS", sans-serif', h1: { fontFamily: '"Fraunces", Georgia, serif' }, h2: { fontFamily: '"Fraunces", Georgia, serif' } }, shape: { borderRadius: 8 },
});

function AppContent() {
  const { enqueueSnackbar } = useSnackbar();
  const [selected, setSelected] = useState('test-cases');
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [prompt, setPrompt] = useState('Create a thorough regression suite for the checkout flow, including payment failures and guest users.');
  const [source, setSource] = useState('Checkout / Payments');
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState(null);
  const capability = capabilities.find((item) => item.id === selected);
  const runWorkflow = async () => {
    if (!prompt.trim()) { enqueueSnackbar('Add a QA objective before running the workflow.', { variant: 'warning' }); return; }
    setIsRunning(true); setResult(null);
    try {
      const response = await fetch('/api/qa/orchestrate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ capability: selected, prompt, source }) });
      if (!response.ok) throw new Error('QA orchestration endpoint unavailable');
      setResult(await response.json());
    } catch (error) {
      setResult({ mode: 'preview', plan: ['Classify request', 'Retrieve application context', 'Generate QA artifact', 'Run guardrails'], retrieval: { query: prompt, sources: ['User stories', 'Historical test cases', 'QA standards'], matches: 12 }, validation: [{ label: 'Prompt completeness', status: 'Passed' }, { label: 'Context relevance', status: 'Passed' }, { label: 'Sensitive data scan', status: 'Passed' }], output: { title: `${capability.label} preview`, summary: `A grounded ${capability.label.toLowerCase()} workflow is ready for ${source}.`, items: ['Scope is identified from the request', 'Relevant application evidence is attached', 'Output is ready for review and export'] } });
      enqueueSnackbar('Preview generated. Connect the API to run live retrieval.', { variant: 'info' });
    } finally { setIsRunning(false); }
  };
  return <Box className="app-shell">
    <Drawer className="side-drawer" variant="permanent" open={drawerOpen} sx={{ '& .MuiDrawer-paper': { width: drawerOpen ? 248 : 72 } }}>
      <Box className="brand-lockup"><Box className="brand-mark"><HubOutlined /></Box>{drawerOpen && <Box><Typography className="brand-name">QA Agent</Typography><Typography className="brand-caption">Created by Gopi Rajendran</Typography></Box>}</Box><Divider />
      {drawerOpen && <Typography className="nav-label">CAPABILITIES</Typography>}
      <List className="capability-list">{capabilities.map((item) => <ListItemButton key={item.id} selected={selected === item.id} onClick={() => { setSelected(item.id); setResult(null); }}><ListItemIcon>{item.icon}</ListItemIcon>{drawerOpen && <ListItemText primary={item.label} secondary={item.short} />}</ListItemButton>)}</List>
      <Box className="drawer-bottom"><ListItemButton><ListItemIcon><StorageOutlined /></ListItemIcon>{drawerOpen && <ListItemText primary="Knowledge base" secondary="Connected" />}</ListItemButton><ListItemButton><ListItemIcon><SettingsOutlined /></ListItemIcon>{drawerOpen && <ListItemText primary="Workspace settings" />}</ListItemButton>{drawerOpen && <Box className="system-status"><span className="status-dot" />RAG services operational</Box>}</Box>
    </Drawer>
    <Box component="main" className="main-area">
      <header className="topbar"><Tooltip title={drawerOpen ? 'Collapse navigation' : 'Expand navigation'}><IconButton onClick={() => setDrawerOpen(!drawerOpen)}>{drawerOpen ? <ChevronLeft /> : <Menu />}</IconButton></Tooltip><Box className="breadcrumbs"><Typography>Workspace</Typography><span>/</span><Typography className="crumb-active">{capability.label}</Typography></Box><Box className="topbar-actions"><Chip icon={<ShieldOutlined />} label="Guardrails on" className="guardrail-chip" /><Box className="avatar">SK</Box></Box></header>
      <Box className="page-content"><Box className="eyebrow"><PsychologyOutlined /> AGENTIC QA WORKFLOW</Box><Box className="page-heading"><Box><Typography variant="h1">What are we testing today?</Typography><Typography className="lede">Turn application knowledge into review-ready QA artifacts, grounded in your team's evidence.</Typography></Box><Chip label="Workspace: Checkout" className="workspace-chip" /></Box>
        <Box className="workflow-strip">{['Request', 'Orchestrate', 'Retrieve', 'Reason', 'Validate', 'Export'].map((step, index) => <React.Fragment key={step}><Box className={`workflow-step ${index === 0 ? 'active' : ''}`}><span>{String(index + 1).padStart(2, '0')}</span>{step}</Box>{index < 5 && <span className="workflow-arrow">→</span>}</React.Fragment>)}</Box>
        <Box className="workspace-grid"><Paper className="request-panel"><Box className="panel-heading"><Box><Typography className="section-kicker">01 / DEFINE REQUEST</Typography><Typography variant="h2">{capability.label}</Typography></Box><ScienceOutlined className="heading-icon" /></Box><Typography className="field-label">QA objective</Typography><textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} className="objective-input" rows={5} placeholder="Describe what you need to test..." /><Typography className="field-label">Application area</Typography><Box className="source-selector"><DescriptionOutlined /><input value={source} onChange={(event) => setSource(event.target.value)} /><span>⌄</span></Box><Box className="attachment-row"><UploadFileOutlined /><Typography><strong>Attach context</strong> <span>requirements, logs, API specs</span></Typography><Chip label="Optional" size="small" /></Box><Button className="run-button" variant="contained" onClick={runWorkflow} disabled={isRunning} endIcon={<span>→</span>}>{isRunning ? 'Running agents...' : 'Run QA workflow'}</Button>{isRunning && <LinearProgress className="progress-line" />}</Paper>
          <Box className="right-column"><Paper className="evidence-panel"><Box className="panel-heading compact"><Box><Typography className="section-kicker">02 / RAG KNOWLEDGE LAYER</Typography><Typography variant="h2">Evidence available</Typography></Box><StorageOutlined className="heading-icon" /></Box><Typography className="panel-description">The orchestrator will ground this request in trusted application context.</Typography><Box className="evidence-grid">{evidence.map((item) => <Box key={item.title} className={`evidence-item ${item.tone}`}><Box className="evidence-icon"><DescriptionOutlined /></Box><Box><Typography className="evidence-title">{item.title}</Typography><Typography className="evidence-detail">{item.detail}</Typography></Box><span className="evidence-check">✓</span></Box>)}</Box></Paper><Paper className="orchestrator-panel"><Box className="panel-heading compact"><Box><Typography className="section-kicker">03 / ORCHESTRATOR</Typography><Typography variant="h2">Agent coordination</Typography></Box><HubOutlined className="heading-icon" /></Box><Box className="agent-flow"><Box className="agent-node user-node"><span>YOU</span><Typography>QA request</Typography></Box><span className="flow-line" /><Box className="agent-node orchestrator-node"><span>CORE</span><Typography>Orchestrator</Typography></Box><span className="flow-line" /><Box className="agent-agents">{['Retrieve', 'Reason', 'Guardrail'].map((agent) => <Chip key={agent} label={agent} size="small" />)}</Box></Box></Paper></Box></Box>
        {result && <Paper className="result-panel"><Box className="result-header"><Box><Typography className="section-kicker">04 / GENERATED QA OUTPUT</Typography><Typography variant="h2">{result.output.title}</Typography></Box><Box className="result-actions"><Chip label={result.mode === 'preview' ? 'Preview' : 'Validated'} className="validated-chip" /><Button startIcon={<DownloadOutlined />} variant="outlined" size="small">Export</Button></Box></Box><Box className="result-grid"><Box><Typography className="subheading">Agent plan</Typography>{result.plan.map((step, index) => <Box className="plan-row" key={step}><span>{index + 1}</span>{step}<strong>✓</strong></Box>)}</Box><Box><Typography className="subheading">Retrieved context <Chip label={`${result.retrieval.matches} matches`} size="small" /></Typography><Typography className="result-summary">{result.output.summary}</Typography><Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>{result.retrieval.sources.map((item) => <Chip key={item} label={item} size="small" variant="outlined" />)}</Stack></Box><Box><Typography className="subheading">Validation checks</Typography>{result.validation.map((check) => <Box className="validation-row" key={check.label}><ShieldOutlined />{check.label}<span>{check.status}</span></Box>)}</Box></Box><Divider /><Box className="output-items">{result.output.items.map((item) => <Box key={item}><span>+</span>{item}</Box>)}</Box></Paper>}
      </Box><footer><span>Created by Gopi Rajendran</span> Enterprise QA intelligence <span className="footer-right">Last indexed 8 min ago · RAG v1.4</span></footer>
    </Box>
  </Box>;
}
function App() { return <ThemeProvider theme={theme}><CssBaseline /><SnackbarProvider maxSnack={3}><AppContent /></SnackbarProvider></ThemeProvider>; }
export default App;
