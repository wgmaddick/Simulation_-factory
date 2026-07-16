const express = require('express');
const path = require('path');
const crypto = require('crypto');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const RESEARCH_NODES = [
  { id: 'hamstring_load', label: 'Hamstring Load Vector', credit_cost: 12 },
  { id: 'joint_plane', label: 'Primary Joint Plane Audit', credit_cost: 15 },
  { id: 'torque_asymmetry', label: 'Torque Asymmetry Loop', credit_cost: 18 },
  { id: 'deceleration_cut', label: 'Deceleration Cut Telemetry', credit_cost: 20 },
];

const NODE_BY_ID = Object.fromEntries(RESEARCH_NODES.map((n) => [n.id, n]));

const VAULT_CONFIG = {
  target_domain: 'Kinetic Biomechanics · Performance Vault',
  tenant_identity: 'AAT Phoenix · Elite Movement Unit',
  initial_credits: 100,
  research_nodes: RESEARCH_NODES,
};

const VERDICTS = {
  hamstring_load: [
    'Posterior chain tension peaks late in the swing phase; eccentric capacity is within band but residual tightness concentrates at the distal musculotendinous junction.',
    'Hamstring load vector shows controlled stretch-shortening. Peak force aligns with push-off timing; no acute overload signature in the sampled cut.',
    'Bilateral hamstring tension is elevated on the plant leg during final deceleration. Soft-tissue readiness is acceptable with monitored recovery windows.',
  ],
  joint_plane: [
    'Primary joint plane remains stacked through contact. Load orientation tracks the intended path with minor medial drift under fatigue.',
    'Hip-knee-ankle alignment holds through the braking frame. Frontal-plane excursion is inside operational tolerance for the selected research node.',
    'Load orientation across the primary joint plane is coherent. Slight external rotation at toe-off is compensatory, not structural.',
  ],
  torque_asymmetry: [
    'Torque asymmetry exceeds quiet-standing baseline during high-impact braking loops. Dominant-side contribution absorbs ~12% more rotational demand.',
    'Rotational torque distribution is uneven across the kinetic chain. Left-side lag appears during the final deceleration window.',
    'Asymmetry index remains actionable but not critical. Redistribute braking intent across both limbs on the next intake cycle.',
  ],
  deceleration_cut: [
    'Final deceleration cut shows clean force attenuation. Ground contact time is efficient; residual energy dissipates through the posterior chain.',
    'Cut angle and braking impulse are synchronized. Athlete communicates intent clearly through the plant phase with stable trunk control.',
    'Deceleration telemetry confirms controlled shedding of horizontal velocity. No abrupt shear spike at the change-of-direction hinge.',
  ],
};

const SENTINEL_ANOMALIES = {
  hamstring_load: {
    location: 'Distal biceps femoris · plant leg',
    description:
      'Eccentric tension spike detected on the final deceleration cut. Sentinel recommends immediate load moderation before next high-speed exposure.',
    timeline:
      'T+0h: flag · T+24h: soft-tissue screen · T+48h: clearance or escalate to medical review',
  },
  joint_plane: {
    location: 'Knee joint plane · frontal axis',
    description:
      'Load orientation drifts outside the primary plane under braking. Sentinel override locks further high-intensity cuts until plane integrity is revalidated.',
    timeline:
      'T+0h: lock high-intensity cuts · T+12h: plane re-audit · T+36h: conditional release',
  },
  torque_asymmetry: {
    location: 'Lumbo-pelvic torque couple',
    description:
      'Rotational torque asymmetry breached sentinel threshold during high-impact braking loops. Risk of compensatory cascade into the contralateral chain.',
    timeline:
      'T+0h: alert coaches · T+6h: asymmetry re-measure · T+24h: escalate if delta > 15%',
  },
  deceleration_cut: {
    location: 'Plant-foot shear · change-of-direction hinge',
    description:
      'Abrupt horizontal shear on the final cut exceeds sentinel envelope. Deep analysis recommends pause on reactive COD drills.',
    timeline:
      'T+0h: suspend COD block · T+18h: controlled decelerations only · T+48h: full release if clean',
  },
};

const SENTINEL_TRIGGERS = [
  'hamstring',
  'tension',
  'asymmetry',
  'torque',
  'pain',
  'spike',
  'override',
  'risk',
  'shear',
  'overload',
  'ankle',
];

/** In-memory credit ledger for the demo session. */
let credits = VAULT_CONFIG.initial_credits;

function pickVerdict(nodeId, speech) {
  const options = VERDICTS[nodeId] || VERDICTS.joint_plane;
  const digest = crypto.createHash('sha256').update(`${nodeId}:${speech.toLowerCase()}`).digest('hex');
  const index = parseInt(digest.slice(0, 8), 16) % options.length;
  const base = options[index];
  if (speech) {
    return `${base} Query context noted: “${speech.slice(0, 120)}”.`;
  }
  return base;
}

function shouldTriggerSentinel(nodeId, speech) {
  const lowered = speech.toLowerCase();
  const triggerHits = SENTINEL_TRIGGERS.filter((word) => lowered.includes(word)).length;
  const seed = parseInt(
    crypto.createHash('sha256').update(`sentinel:${nodeId}:${lowered}`).digest('hex').slice(0, 8),
    16
  );
  // Mulberry32-style PRNG from seed for stable demo behavior
  let t = (seed + 0x6d2b79f5) >>> 0;
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  const rnd = ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  const baseChance = 0.35 + Math.min(triggerHits, 3) * 0.18;
  return rnd < baseChance;
}

function slugify(name) {
  return String(name)
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '') || 'athlete';
}

function buildLoadPathSignature(candidateName) {
  const digest = crypto
    .createHash('sha256')
    .update(`loadpath:${candidateName}:${Date.now()}`)
    .digest('hex')
    .slice(0, 10)
    .toUpperCase();
  return `LP-${slugify(candidateName).slice(0, 8).toUpperCase()}-${digest}`;
}

function saturdayWeatherGrid() {
  // Simulated Saturday weather grid for equipment logistics
  return {
    day: 'Saturday',
    surfaceTempF: 54,
    precipProbability: 0.22,
    windMph: 12,
    fieldCondition: 'firm-damp',
    recommendedSpike: 'soft-ground · 6mm molded',
  };
}

// Route 1: Serve configuration to frontend
app.get('/api/config', (req, res) => {
  res.json({
    ...VAULT_CONFIG,
    initial_credits: credits,
  });
});

app.post('/api/reset-credits', (req, res) => {
  credits = VAULT_CONFIG.initial_credits;
  res.json({ creditsRemaining: credits });
});

// Route 2: Process the "Video + Talk + Send" execution loop
app.post('/api/analyze', (req, res) => {
  const { nodeId, userSpeech } = req.body || {};
  const selectedNode = NODE_BY_ID[nodeId];

  if (!selectedNode) {
    return res.status(400).json({ error: 'Invalid Node' });
  }
  if (credits < selectedNode.credit_cost) {
    return res.status(402).json({ error: 'Insufficient Credit Allocation' });
  }

  const speech =
    typeof userSpeech === 'string' && userSpeech.trim()
      ? userSpeech.trim()
      : '';

  if (!speech) {
    return res.status(400).json({ error: 'userSpeech is required' });
  }

  credits -= selectedNode.credit_cost;

  const sentinelOverride = shouldTriggerSentinel(selectedNode.id, speech);

  const dynamicResponse = {
    creditsRemaining: credits,
    nodeId: selectedNode.id,
    nodeLabel: selectedNode.label,
    creditCost: selectedNode.credit_cost,
    expertVerdict: pickVerdict(selectedNode.id, speech),
    laymanSummary:
      'The engine processed your vocal query successfully. Metrics stabilized within dynamic margins.',
    sentinelOverride,
    anomalyData: sentinelOverride ? { ...SENTINEL_ANOMALIES[selectedNode.id] } : null,
  };

  res.json(dynamicResponse);
});

/**
 * Cascading Downstream Loop — confirm roster rotation and dispatch
 * instant data packets to three personal organizations.
 */
app.post('/api/confirm-rotation', (req, res) => {
  const candidateName =
    (req.body && (req.body.candidateName || req.body.name || req.body.candidate)) || '';

  if (!String(candidateName).trim()) {
    return res.status(400).json({
      success: false,
      error: 'Candidate name is required',
    });
  }

  const name = String(candidateName).trim();
  const loadPathId = buildLoadPathSignature(name);
  const weather = saturdayWeatherGrid();
  const dispatchedAt = new Date().toISOString();
  const passportId = `NIL-${slugify(name).toUpperCase()}-${crypto
    .randomBytes(3)
    .toString('hex')
    .toUpperCase()}`;

  // Simulate instant data dispatch to three downstream personal organizations
  const downstream = {
    sportsMedicine: {
      organization: 'Sports Medicine',
      status: 'DISPATCHED',
      action: 'Auto-generated pre-game ankle tape profile',
      detail: `Tape profile unique to ${name}'s load path ${loadPathId}: lateral stabilizer bias, 3-wrap figure-8, proprioceptive cue set for plant-leg eversion control.`,
      profileId: `TAPE-${loadPathId}`,
      loadPathId,
    },
    equipmentLogistics: {
      organization: 'Equipment Logistics',
      status: 'DISPATCHED',
      action: "Auto-queried inventory to match shoe spikes to Saturday's weather grid",
      detail: `Inventory match locked for ${name}: ${weather.recommendedSpike} (surface ${weather.fieldCondition}, precip ${(weather.precipProbability * 100).toFixed(0)}%, wind ${weather.windMph} mph).`,
      weatherGrid: weather,
      sku: `SPIKE-SG-6MM-${slugify(name).slice(0, 4).toUpperCase()}`,
    },
    athletePortableVault: {
      organization: "Athlete's Portable Personal Vault",
      status: 'DISPATCHED',
      action: 'Updated core biological NIL passport',
      detail: `${name}'s biological NIL passport ${passportId} marked ACTIVE_ROTATION with sentinel-linked clearance and sub-org realignment stamp.`,
      passportId,
      clearance: 'ACTIVE_ROTATION',
    },
  };

  res.json({
    success: true,
    message: `Rotation confirmed for ${name}. Entire sub-organization automatically re-aligned and self-healed.`,
    candidateName: name,
    dispatchedAt,
    cascadeComplete: true,
    selfHealed: true,
    downstream,
    notifications: [
      {
        org: downstream.sportsMedicine.organization,
        status: 'ok',
        summary: downstream.sportsMedicine.action,
        detail: downstream.sportsMedicine.detail,
      },
      {
        org: downstream.equipmentLogistics.organization,
        status: 'ok',
        summary: downstream.equipmentLogistics.action,
        detail: downstream.equipmentLogistics.detail,
      },
      {
        org: downstream.athletePortableVault.organization,
        status: 'ok',
        summary: downstream.athletePortableVault.action,
        detail: downstream.athletePortableVault.detail,
      },
    ],
  });
});

app.listen(PORT, () => {
  console.log(`Decision engine live at http://localhost:${PORT}`);
});
