const express = require('express');
const path = require('path');
const crypto = require('crypto');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

/**
 * Plug-and-play sector matrices for the Sovereign Sector Gateway.
 * Each industry owns domain headers, research nodes, actionable speak,
 * sentinel profiles, and speech-keyword fallbacks.
 */
const SECTORS = {
  university_sports: {
    id: 'university_sports',
    label: 'University Sports',
    target_domain: 'Kinetic Biomechanics · Performance Vault',
    tenant_identity: 'AAT Phoenix · Elite Movement Unit',
    initial_credits: 100,
    actionableSpeakTitle: 'Actionable Coach Speak',
    metricsTitle: 'Biomechanical Metrics',
    metricsSubtitle: 'Medical staff layer',
    speechPlaceholder: 'Or tap microphone to speak…',
    speechFallbackKeyword: 'hamstring',
    indexTitle: 'TOTAL TEAM RESILIENCE INDEX',
    indexDescription:
      'PASSIVE ANOMALY SENTINEL: HIDDEN STRUCTURAL FATIGUE — ADJACENT ASSETS ABSORBING OVERCOMPENSATION STRAIN (-15%).',
    voicePhrases: [
      'Check his hamstring tension on that final deceleration cut.',
      'Verify load orientation across the primary joint plane.',
      'Audit torque asymmetry during high-impact braking loops.',
    ],
    research_nodes: [
      { id: 'hamstring_load', label: 'Hamstring Load Vector', credit_cost: 12 },
      { id: 'joint_plane', label: 'Primary Joint Plane Audit', credit_cost: 15 },
      { id: 'torque_asymmetry', label: 'Torque Asymmetry Loop', credit_cost: 18 },
      { id: 'deceleration_cut', label: 'Deceleration Cut Telemetry', credit_cost: 20 },
    ],
    actionableSpeak: {
      hamstring_load:
        'Jackson is slamming on the brakes too hard on his heels because his legs are tired. His left hamstring is actively tightening up to protect itself. Reduce his high-speed cutting repetitions for the next 24 hours.',
      joint_plane:
        'His knee is drifting inward on plant. Cue him to stack hip–knee–ankle and finish cuts tall. Pull him from max-intensity change-of-direction until that line holds.',
      torque_asymmetry:
        'He’s dumping most of the twist onto his strong side. Even out the braking work — force more plant-side reps on the quieter leg this session.',
      deceleration_cut:
        'The last cut looked clean and controlled. Keep him in the plan, but watch the plant foot if speed ramps back up.',
    },
    keywordSpeak:
      'Jackson is slamming on the brakes too hard on his heels because his legs are tired. His left hamstring is actively tightening up to protect itself. Reduce his high-speed cutting repetitions for the next 24 hours.',
    verdicts: {
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
    },
    sentinelAnomalies: {
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
    },
    sentinelTriggers: [
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
    ],
  },

  clinical_dental: {
    id: 'clinical_dental',
    label: 'Clinical Dental Vault',
    target_domain: 'CLINICAL ORAL SURGERY & LONGEVITY',
    tenant_identity: 'AAT Phoenix · Clinical Dental Vault',
    initial_credits: 100,
    actionableSpeakTitle: 'Actionable Surgeon Speak',
    metricsTitle: 'Clinical Metrics',
    metricsSubtitle: 'Surgical staff layer',
    speechPlaceholder: 'Describe implant seating, torque, or tissue load…',
    speechFallbackKeyword: 'implant',
    indexTitle: 'SURGICAL NETWORK STABILITY INDEX',
    indexDescription:
      'BIOMECHANICAL ERROR CAPTURED: LOCALIZED STRUCTURAL DEFICIT DETECTED — IMPLANT CLEARANCE COMPROMISED (-15%).',
    voicePhrases: [
      'Check implant seating against bone density on the posterior maxilla.',
      'Map screw torque against cortical thickness before final seating.',
      'Audit periodontal asymmetry and soft-tissue load under occlusion.',
    ],
    research_nodes: [
      {
        id: 'bone_density_screw_torque',
        label: 'Node 1.1: Bone Density Screw Torque Mapping',
        credit_cost: 6,
      },
      {
        id: 'periodontal_asymmetry',
        label: 'Node 1.2: Periodontal Asymmetry & Tissue Load',
        credit_cost: 10,
      },
    ],
    actionableSpeak: {
      bone_density_screw_torque:
        'Implant seating showing a 3mm bone density deficit. Structural failure risk active. Auto-routing to inventory procurement for alternative anchoring specs.',
      periodontal_asymmetry:
        'Tissue load is uneven on the mesial margin. Ease occlusal contacts and reassess soft-tissue perfusion before final torque.',
    },
    keywordSpeak:
      'Implant seating showing a 3mm bone density deficit. Structural failure risk active. Auto-routing to inventory procurement for alternative anchoring specs.',
    verdicts: {
      bone_density_screw_torque: [
        'Cortical engagement under seating torque shows localized density attenuation ~3mm apical to the intended platform. Insertion pathway remains viable with alternate anchor geometry.',
        'Screw torque curve plateaus early against trabecular resistance. Primary stability index is marginal for immediate load protocols.',
        'Bone-implant interface mapping isolates a density deficit coincident with seating depth. Structural reserve is below longevity thresholds for standard abutment specs.',
      ],
      periodontal_asymmetry: [
        'Periodontal tissue load is asymmetric under simulated occlusion. Soft-tissue perfusion on the mesial aspect trails the distal baseline.',
        'Gingival margin strain concentrates at the contact point. Tissue response remains reversible with load redistribution.',
        'Asymmetry in periodontal fiber tension exceeds quiet baseline. Recommend staged seating and tissue rest before final torque.',
      ],
    },
    sentinelAnomalies: {
      bone_density_screw_torque: {
        location: 'Posterior maxilla · implant platform',
        description:
          'Sub-clinical bone density deficit under seating torque. Sentinel flags structural failure risk and recommends alternate anchoring procurement.',
        timeline:
          'T+0h: halt final seating · T+4h: inventory alternate specs · T+24h: re-map density before retry',
      },
      periodontal_asymmetry: {
        location: 'Mesial soft-tissue margin',
        description:
          'Periodontal load asymmetry breached sentinel envelope. Soft-tissue ischemia risk if occlusion proceeds unchanged.',
        timeline:
          'T+0h: reduce occlusal load · T+12h: tissue re-check · T+36h: clearance or escalate',
      },
    },
    sentinelTriggers: [
      'implant',
      'torque',
      'density',
      'bone',
      'periodontal',
      'tissue',
      'failure',
      'risk',
      'screw',
      'asymmetry',
    ],
  },

  asset_infrastructure: {
    id: 'asset_infrastructure',
    label: 'Asset Infrastructure',
    target_domain: 'ENTERPRISE PIPELINE & MECHANICAL OPERATIONS',
    tenant_identity: 'AAT Phoenix · Asset Infrastructure Grid',
    initial_credits: 100,
    actionableSpeakTitle: 'Actionable Engineer Speak',
    metricsTitle: 'Mechanical Metrics',
    metricsSubtitle: 'Operations engineering layer',
    speechPlaceholder: 'Describe pump, thermal, or vibration signatures…',
    speechFallbackKeyword: 'pump',
    indexTitle: 'SYSTEMIC OPERATIONAL INTEGRITY INDEX',
    indexDescription:
      'CRITICAL COMPONENT ALERT: MECHANICAL CAVITATION TRACE DETECTED — HYDRAULIC ANOMALY OVERLOAD ACTIVE (-15%).',
    voicePhrases: [
      'Inspect pump A bearing output for micro-cavitation signatures.',
      'Run thermal stress vector analysis across the primary manifold.',
      'Check vibration asymmetry on the secondary flow loop.',
    ],
    research_nodes: [
      {
        id: 'thermal_stress_vector',
        label: 'Node 1.1: Thermal Stress Vector Analysis',
        credit_cost: 15,
      },
      {
        id: 'vibration_asymmetry_cavitation',
        label: 'Node 1.2: Vibration Asymmetry Cavitation',
        credit_cost: 22,
      },
    ],
    actionableSpeak: {
      thermal_stress_vector:
        'Thermal gradient on the primary manifold is climbing past design envelope. Shed load and inspect insulation before the next duty cycle.',
      vibration_asymmetry_cavitation:
        'Pump A bearing output exhibits micro-cavitation. Structural seal failure within 48 operational hours. Rerouting backup flow loops immediately.',
    },
    keywordSpeak:
      'Pump A bearing output exhibits micro-cavitation. Structural seal failure within 48 operational hours. Rerouting backup flow loops immediately.',
    verdicts: {
      thermal_stress_vector: [
        'Thermal stress vectors concentrate at the flange transition. Expansion differential exceeds quiet-running tolerance under current duty.',
        'Heat flux along the primary manifold is asymmetric. Cooling margin remains positive but trending toward alert band.',
        'Vector analysis isolates elevated thermal strain coincident with peak flow. Structural envelope is intact with monitored cooldown required.',
      ],
      vibration_asymmetry_cavitation: [
        'Vibration asymmetry on Pump A indicates micro-cavitation at the bearing interface. Seal integrity timeline compresses under continued load.',
        'Cavitation harmonics breach sentinel threshold on the secondary loop. Backup flow path should be primed for immediate cutover.',
        'Bearing output spectrum shows progressive cavitation signature. Predictive model places structural seal risk inside a 48-hour operational window.',
      ],
    },
    sentinelAnomalies: {
      thermal_stress_vector: {
        location: 'Primary manifold · flange transition',
        description:
          'Thermal stress vector exceeded design envelope. Sentinel recommends load shed and insulation inspection before next duty cycle.',
        timeline:
          'T+0h: reduce duty · T+6h: thermal re-map · T+24h: clearance or maintenance lock',
      },
      vibration_asymmetry_cavitation: {
        location: 'Pump A · bearing / seal interface',
        description:
          'Micro-cavitation detected on Pump A bearing output. Sentinel projects structural seal failure within 48 operational hours.',
        timeline:
          'T+0h: arm backup loops · T+12h: vibration re-sample · T+48h: forced cutover if unresolved',
      },
    },
    sentinelTriggers: [
      'pump',
      'cavitation',
      'vibration',
      'thermal',
      'bearing',
      'seal',
      'failure',
      'stress',
      'asymmetry',
      'risk',
    ],
  },
};

const SECTOR_LIST = Object.values(SECTORS).map((s) => ({
  id: s.id,
  label: s.label,
  target_domain: s.target_domain,
}));

let activeSectorId = 'university_sports';

function activeSector() {
  return SECTORS[activeSectorId];
}

function nodeMap(sector = activeSector()) {
  return Object.fromEntries(sector.research_nodes.map((n) => [n.id, n]));
}

function publicSectorConfig(sector = activeSector()) {
  return {
    sectorId: sector.id,
    sectorLabel: sector.label,
    target_domain: sector.target_domain,
    tenant_identity: sector.tenant_identity,
    initial_credits: credits,
    research_nodes: sector.research_nodes,
    actionableSpeakTitle: sector.actionableSpeakTitle,
    metricsTitle: sector.metricsTitle,
    metricsSubtitle: sector.metricsSubtitle,
    speechPlaceholder: sector.speechPlaceholder,
    speechFallbackKeyword: sector.speechFallbackKeyword,
    voicePhrases: sector.voicePhrases,
    indexTitle: sector.indexTitle,
    indexDescription: sector.indexDescription,
    sectors: SECTOR_LIST,
  };
}

/** In-memory credit ledger for the demo session. */
let credits = SECTORS.university_sports.initial_credits;

/** Total Team Resilience Index — systemic network fatigue (0–100%). */
const TEAM_RESILIENCE_INITIAL = 88;
let teamResilience = TEAM_RESILIENCE_INITIAL;

const REPLACEMENT_PROFILES = {
  Davis: { match: 94, fatigueRisk: 12, riskBand: 'Low' },
  Miller: { match: 78, fatigueRisk: 38, riskBand: 'Medium' },
  Henderson: { match: 62, fatigueRisk: 5, riskBand: 'Low' },
};

function clampResilience(value) {
  return Math.max(0, Math.min(100, Math.round(value)));
}

function resiliencePayload(delta = 0, reason = null, sector = activeSector()) {
  return {
    teamResilience,
    teamResiliencePercent: teamResilience,
    resilienceDelta: delta,
    resilienceReason: reason,
    resilienceStatus: teamResilience >= 75 ? 'stable' : 'vulnerable',
    indexTitle: sector.indexTitle,
    indexDescription: sector.indexDescription,
  };
}

function pickVerdict(nodeId, speech, sector = activeSector()) {
  const options =
    (sector.verdicts && sector.verdicts[nodeId]) ||
    Object.values(sector.verdicts || {})[0] ||
    ['Structural intake processed within operational margins.'];
  const digest = crypto
    .createHash('sha256')
    .update(`${sector.id}:${nodeId}:${speech.toLowerCase()}`)
    .digest('hex');
  const index = parseInt(digest.slice(0, 8), 16) % options.length;
  const base = options[index];
  if (speech) {
    return `${base} Query context noted: “${speech.slice(0, 120)}”.`;
  }
  return base;
}

function pickActionableSpeak(nodeId, speech, sector = activeSector()) {
  const lowered = (speech || '').toLowerCase();
  const keyword = (sector.speechFallbackKeyword || '').toLowerCase();
  if (keyword && lowered.includes(keyword) && sector.keywordSpeak) {
    return sector.keywordSpeak;
  }
  if (sector.actionableSpeak && sector.actionableSpeak[nodeId]) {
    return sector.actionableSpeak[nodeId];
  }
  return (
    sector.keywordSpeak ||
    Object.values(sector.actionableSpeak || {})[0] ||
    'Operational advisory ready.'
  );
}

function shouldTriggerSentinel(nodeId, speech, sector = activeSector()) {
  const lowered = speech.toLowerCase();
  const triggers = sector.sentinelTriggers || [];
  const triggerHits = triggers.filter((word) => lowered.includes(word)).length;
  const seed = parseInt(
    crypto
      .createHash('sha256')
      .update(`sentinel:${sector.id}:${nodeId}:${lowered}`)
      .digest('hex')
      .slice(0, 8),
    16
  );
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
  return {
    day: 'Saturday',
    surfaceTempF: 54,
    precipProbability: 0.22,
    windMph: 12,
    fieldCondition: 'firm-damp',
    recommendedSpike: 'soft-ground · 6mm molded',
  };
}

app.get('/api/sectors', (req, res) => {
  res.json({
    activeSectorId,
    sectors: SECTOR_LIST,
  });
});

app.get('/api/config', (req, res) => {
  res.json({
    ...publicSectorConfig(),
    ...resiliencePayload(0, 'baseline'),
  });
});

/**
 * Switch the active industry matrix and return the full plug-and-play config
 * so the UI can re-render with zero full-page refresh.
 */
app.post('/api/sector', (req, res) => {
  const requested =
    (req.body && (req.body.sectorId || req.body.sector || req.body.id)) || '';
  const id = String(requested).trim();

  if (!SECTORS[id]) {
    return res.status(400).json({
      error: 'Unknown sector',
      sectors: SECTOR_LIST,
    });
  }

  activeSectorId = id;
  const sector = activeSector();
  // Reset allocation to the sector baseline so each industry demo starts clean.
  credits = sector.initial_credits;

  res.json({
    success: true,
    switched: true,
    ...publicSectorConfig(sector),
    ...resiliencePayload(0, sector.indexDescription, sector),
  });
});

app.post('/api/reset-credits', (req, res) => {
  credits = activeSector().initial_credits;
  teamResilience = TEAM_RESILIENCE_INITIAL;
  res.json({
    creditsRemaining: credits,
    ...resiliencePayload(0, 'reset'),
  });
});

app.post('/api/analyze', (req, res) => {
  const sector = activeSector();
  const nodes = nodeMap(sector);
  const { nodeId, userSpeech } = req.body || {};
  const selectedNode = nodes[nodeId];

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

  const sentinelOverride = shouldTriggerSentinel(selectedNode.id, speech, sector);
  const actionable = pickActionableSpeak(selectedNode.id, speech, sector);
  const metrics = pickVerdict(selectedNode.id, speech, sector);

  let resilienceDelta = 0;
  let resilienceReason = null;
  if (sentinelOverride) {
    resilienceDelta = -15;
    teamResilience = clampResilience(teamResilience + resilienceDelta);
    resilienceReason = sector.indexDescription;
  }

  const anomaly =
    sentinelOverride && sector.sentinelAnomalies
      ? sector.sentinelAnomalies[selectedNode.id] ||
        Object.values(sector.sentinelAnomalies)[0]
      : null;

  res.json({
    creditsRemaining: credits,
    sectorId: sector.id,
    sectorLabel: sector.label,
    nodeId: selectedNode.id,
    nodeLabel: selectedNode.label,
    creditCost: selectedNode.credit_cost,
    expertVerdict: metrics,
    biomechanicalMetrics: metrics,
    coachSpeak: actionable,
    actionableSpeak: actionable,
    actionableSpeakTitle: sector.actionableSpeakTitle,
    metricsTitle: sector.metricsTitle,
    laymanSummary: actionable,
    sentinelOverride,
    anomalyData: anomaly ? { ...anomaly } : null,
    ...resiliencePayload(resilienceDelta, resilienceReason),
  });
});

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
  const profile = REPLACEMENT_PROFILES[name] || {
    match: 50,
    fatigueRisk: 50,
    riskBand: 'Unknown',
  };

  let resilienceDelta = 0;
  let resilienceReason = null;
  if (profile.fatigueRisk <= 15 || profile.riskBand === 'Low') {
    resilienceDelta = 20;
    teamResilience = clampResilience(teamResilience + resilienceDelta);
    resilienceReason = `Self-heal cascade: ${name} activated (fatigue risk ${profile.fatigueRisk}%) — organizational network stabilized (+20%).`;
  } else {
    resilienceReason = `Rotation of ${name} dispatched; fatigue risk ${profile.fatigueRisk}% is above low-risk band — resilience held steady.`;
  }

  const loadPathId = buildLoadPathSignature(name);
  const weather = saturdayWeatherGrid();
  const dispatchedAt = new Date().toISOString();
  const passportId = `NIL-${slugify(name).toUpperCase()}-${crypto
    .randomBytes(3)
    .toString('hex')
    .toUpperCase()}`;

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
    candidateProfile: profile,
    sectorId: activeSectorId,
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
    ...resiliencePayload(resilienceDelta, resilienceReason),
  });
});

app.listen(PORT, () => {
  console.log(`Decision engine live at http://localhost:${PORT}`);
});
