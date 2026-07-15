const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const CONFIG_PATH = path.join(__dirname, 'config.json');

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

let systemState = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));

function reloadBaseCredits() {
  const fresh = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
  return fresh.initial_credits;
}

// Route 1: Serve configuration to frontend
app.get('/api/config', (req, res) => {
  res.json(systemState);
});

// Optional: reset credits to config baseline (dev / demo)
app.post('/api/reset-credits', (req, res) => {
  systemState.initial_credits = reloadBaseCredits();
  res.json({ creditsRemaining: systemState.initial_credits });
});

// Route 2: Process the "Video + Talk + Send" execution loop
app.post('/api/analyze', (req, res) => {
  const { nodeId, userSpeech } = req.body;
  const selectedNode = systemState.research_nodes.find((n) => n.id === nodeId);

  if (!selectedNode) {
    return res.status(400).json({ error: 'Invalid Node' });
  }
  if (systemState.initial_credits < selectedNode.credit_cost) {
    return res.status(402).json({ error: 'Insufficient Credit Allocation' });
  }

  // Deduct compute credits instantly
  systemState.initial_credits -= selectedNode.credit_cost;

  const speech = typeof userSpeech === 'string' && userSpeech.trim()
    ? userSpeech.trim()
    : '(no vocal input)';

  // Simulate Twin-Track Output Engine
  const dynamicResponse = {
    creditsRemaining: systemState.initial_credits,
    nodeId: selectedNode.id,
    nodeLabel: selectedNode.label,
    expertVerdict: `[Verified Outcome for ${selectedNode.label}]: Spatial tracking isolates minor vector variation matching vocal parameter: '${speech}'. System tracking optimized.`,
    laymanSummary: 'The engine processed your vocal query successfully. Metrics stabilized within dynamic margins.',
    sentinelOverride: false,
    anomalyData: null,
  };

  // Passive Anomaly Sentinel Trigger: 70% chance to mock intercept a blind spot
  if (Math.random() > 0.3) {
    dynamicResponse.sentinelOverride = true;
    dynamicResponse.anomalyData = {
      title: 'CRITICAL ADVISORY: UNPROMPTED PATHWAY DRIFT',
      location: 'Right Lateral Ankle Stabilizer',
      description: 'Sub-clinical 4.8-degree eversion drift isolated outside query scope.',
      timeline: '84% Probability of non-contact structural joint failure within 15 active cycles.',
    };
  }

  res.json(dynamicResponse);
});

app.listen(PORT, () => console.log(`Engine live at http://localhost:${PORT}`));
