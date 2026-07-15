"""Kinetic Asset Management Vault — analysis engine and session state."""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, field
from typing import Any


RESEARCH_NODES: list[dict[str, Any]] = [
    {
        "id": "hamstring_load",
        "label": "Hamstring Load Vector",
        "credit_cost": 12,
    },
    {
        "id": "joint_plane",
        "label": "Primary Joint Plane Audit",
        "credit_cost": 15,
    },
    {
        "id": "torque_asymmetry",
        "label": "Torque Asymmetry Loop",
        "credit_cost": 18,
    },
    {
        "id": "deceleration_cut",
        "label": "Deceleration Cut Telemetry",
        "credit_cost": 20,
    },
]

NODE_BY_ID = {node["id"]: node for node in RESEARCH_NODES}

VAULT_CONFIG: dict[str, Any] = {
    "target_domain": "Kinetic Biomechanics · Performance Vault",
    "tenant_identity": "AAT Phoenix · Elite Movement Unit",
    "initial_credits": 100,
    "research_nodes": RESEARCH_NODES,
}

VERDICTS: dict[str, list[str]] = {
    "hamstring_load": [
        "Posterior chain tension peaks late in the swing phase; eccentric capacity is within band but residual tightness concentrates at the distal musculotendinous junction.",
        "Hamstring load vector shows controlled stretch-shortening. Peak force aligns with push-off timing; no acute overload signature in the sampled cut.",
        "Bilateral hamstring tension is elevated on the plant leg during final deceleration. Soft-tissue readiness is acceptable with monitored recovery windows.",
    ],
    "joint_plane": [
        "Primary joint plane remains stacked through contact. Load orientation tracks the intended path with minor medial drift under fatigue.",
        "Hip-knee-ankle alignment holds through the braking frame. Frontal-plane excursion is inside operational tolerance for the selected research node.",
        "Load orientation across the primary joint plane is coherent. Slight external rotation at toe-off is compensatory, not structural.",
    ],
    "torque_asymmetry": [
        "Torque asymmetry exceeds quiet-standing baseline during high-impact braking loops. Dominant-side contribution absorbs ~12% more rotational demand.",
        "Rotational torque distribution is uneven across the kinetic chain. Left-side lag appears during the final deceleration window.",
        "Asymmetry index remains actionable but not critical. Redistribute braking intent across both limbs on the next intake cycle.",
    ],
    "deceleration_cut": [
        "Final deceleration cut shows clean force attenuation. Ground contact time is efficient; residual energy dissipates through the posterior chain.",
        "Cut angle and braking impulse are synchronized. Athlete communicates intent clearly through the plant phase with stable trunk control.",
        "Deceleration telemetry confirms controlled shedding of horizontal velocity. No abrupt shear spike at the change-of-direction hinge.",
    ],
}

SENTINEL_ANOMALIES: dict[str, dict[str, str]] = {
    "hamstring_load": {
        "location": "Distal biceps femoris · plant leg",
        "description": "Eccentric tension spike detected on the final deceleration cut. Sentinel recommends immediate load moderation before next high-speed exposure.",
        "timeline": "T+0h: flag · T+24h: soft-tissue screen · T+48h: clearance or escalate to medical review",
    },
    "joint_plane": {
        "location": "Knee joint plane · frontal axis",
        "description": "Load orientation drifts outside the primary plane under braking. Sentinel override locks further high-intensity cuts until plane integrity is revalidated.",
        "timeline": "T+0h: lock high-intensity cuts · T+12h: plane re-audit · T+36h: conditional release",
    },
    "torque_asymmetry": {
        "location": "Lumbo-pelvic torque couple",
        "description": "Rotational torque asymmetry breached sentinel threshold during high-impact braking loops. Risk of compensatory cascade into the contralateral chain.",
        "timeline": "T+0h: alert coaches · T+6h: asymmetry re-measure · T+24h: escalate if delta > 15%",
    },
    "deceleration_cut": {
        "location": "Plant-foot shear · change-of-direction hinge",
        "description": "Abrupt horizontal shear on the final cut exceeds sentinel envelope. Deep analysis recommends pause on reactive COD drills.",
        "timeline": "T+0h: suspend COD block · T+18h: controlled decelerations only · T+48h: full release if clean",
    },
}

# Keywords in speech that raise sentinel probability.
SENTINEL_TRIGGERS = (
    "hamstring",
    "tension",
    "asymmetry",
    "torque",
    "pain",
    "spike",
    "override",
    "risk",
    "shear",
    "overload",
)


@dataclass
class VaultSession:
    """In-memory credit ledger for the vault session."""

    credits: int = VAULT_CONFIG["initial_credits"]
    history: list[dict[str, Any]] = field(default_factory=list)

    def analyze(self, node_id: str, user_speech: str) -> dict[str, Any]:
        node = NODE_BY_ID.get(node_id)
        if node is None:
            raise KeyError(f"Unknown research node: {node_id}")

        cost = int(node["credit_cost"])
        if self.credits < cost:
            raise ValueError(
                f"Insufficient credits. Need {cost}, have {self.credits}."
            )

        self.credits -= cost
        speech = (user_speech or "").strip()
        verdict = _pick_verdict(node_id, speech)
        sentinel = _should_trigger_sentinel(node_id, speech)

        result: dict[str, Any] = {
            "creditsRemaining": self.credits,
            "expertVerdict": verdict,
            "sentinelOverride": sentinel,
            "nodeId": node_id,
            "creditCost": cost,
        }
        if sentinel:
            result["anomalyData"] = dict(SENTINEL_ANOMALIES[node_id])
        else:
            result["anomalyData"] = None

        self.history.append(
            {
                "nodeId": node_id,
                "userSpeech": speech,
                "sentinelOverride": sentinel,
                "creditsRemaining": self.credits,
            }
        )
        return result


def _pick_verdict(node_id: str, speech: str) -> str:
    options = VERDICTS.get(node_id, VERDICTS["joint_plane"])
    digest = hashlib.sha256(f"{node_id}:{speech.lower()}".encode()).hexdigest()
    index = int(digest[:8], 16) % len(options)
    base = options[index]
    if speech:
        return f"{base} Query context noted: “{speech[:120]}”."
    return base


def _should_trigger_sentinel(node_id: str, speech: str) -> bool:
    """Deterministic-ish sentinel gate from speech + node, with slight randomness."""
    lowered = speech.lower()
    trigger_hits = sum(1 for word in SENTINEL_TRIGGERS if word in lowered)
    # Seed from content so the same query tends to behave consistently.
    seed = int(
        hashlib.sha256(f"sentinel:{node_id}:{lowered}".encode()).hexdigest()[:8],
        16,
    )
    rng = random.Random(seed)
    base_chance = 0.35 + min(trigger_hits, 3) * 0.18
    return rng.random() < base_chance


def get_config() -> dict[str, Any]:
    return {
        "target_domain": VAULT_CONFIG["target_domain"],
        "tenant_identity": VAULT_CONFIG["tenant_identity"],
        "initial_credits": VAULT_CONFIG["initial_credits"],
        "research_nodes": list(RESEARCH_NODES),
    }
