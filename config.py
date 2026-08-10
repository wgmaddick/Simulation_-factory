"""AATPHOENIX sector books - executive dashboard configuration."""

from __future__ import annotations

from typing import Any, TypedDict


class MetricCard(TypedDict, total=False):
    label: str
    big_value: str
    ground_truth_basis: str
    sequence_tag: str
    value_class: str
    border_accent: str
    card_id: str


class Layer2SiteMetric(TypedDict):
    site: str
    queue: str
    backlog: str
    delay_days: str
    burn: str
    ground_truth_basis: str


class Layer2Operations(TypedDict):
    title: str
    caption: str
    inspect_label: str
    site_queue_metrics: list[Layer2SiteMetric]
    layer3_action_label: str
    layer3_clearance_receipt: str


class SectorHeader(TypedDict):
    title: str
    statutory_meta: str
    subtitle: str


class OperationalBridge(TypedDict):
    section_caption: str
    banner_badge: str
    banner_title: str
    banner_headline: str
    banner_footer: str
    channel_receipts: list[dict[str, str]]


class SectorBook(TypedDict):
    code: str
    display_name: str
    header: SectorHeader
    operational_bridge: OperationalBridge
    bridge_metrics: list[MetricCard]
    # Structural Mirror Standard: exactly 3 KPI cards
    structural_mirror: list[MetricCard]
    layer2_operations: Layer2Operations
    sidebar_caption: str
    critical_subjects: int


# Structural Mirror card IDs (order is fixed across all sector books)
MIRROR_CARD_MACRO = "macro_valuation"
MIRROR_CARD_VELOCITY = "velocity_friction"
MIRROR_CARD_ACTIONABLE = "actionable_controllable_loss"
STRUCTURAL_MIRROR_CARD_IDS: tuple[str, str, str] = (
    MIRROR_CARD_MACRO,
    MIRROR_CARD_VELOCITY,
    MIRROR_CARD_ACTIONABLE,
)


# Executive dark theme - CursorRules standard
EXECUTIVE_THEME: dict[str, str] = {
    "bg": "#0b0f17",
    "card": "#131d2a",
    "border": "#1e293b",
    "accent": "#2f81f7",
    "accent_soft": "rgba(47, 129, 247, 0.15)",
    "text": "#f8fafc",
    "muted": "#8b949e",
}

# Private Chrome Removal — hide Streamlit host chrome on iPad Board presentations
PRIVATE_CHROME: dict[str, Any] = {
    "enabled": True,
    "hide_header": True,
    "hide_share": True,
    "hide_hamburger": True,
    "hide_github_link": True,
    "hide_footer": True,
    "presentation_mode": "ipad_board_chair",
}

# Shared CSS: hide Streamlit Community Cloud toolbar / GitHub public watermark.
# Scoped to host chrome (header/toolbar/footer/viewer badge) — not in-app content links.
PRIVATE_CHROME_CSS: str = """
<style>
/* ============================================================
   PRIVATE CHROME REMOVAL
   Hide Streamlit host UI: header, Share/Star/Edit, GitHub repo
   watermark, hamburger/menu, Deploy, footer, viewer badge.
   ============================================================ */
#MainMenu,
#MainMenu > button,
#GithubIcon,
header,
header[data-testid="stHeader"],
header.stAppHeader,
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stAppDeployButton"],
[data-testid="stDeployButton"],
[data-testid="baseButton-header"],
[data-testid="baseButton-headerNoPadding"],
[data-testid="stBaseButton-header"],
[data-testid="stBaseButton-headerNoPadding"],
[data-testid="stHeaderActionElements"],
[data-testid="stToolbarActions"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"],
[data-testid="stExpandSidebarButton"],
[data-testid="manage-app-button"],
.stDeployButton,
.stAppDeployButton,
.stAppToolbar,
.stDecoration,
footer,
footer[data-testid="stFooter"],
.stApp > footer,
/* Community Cloud GitHub public watermark + viewer badge variants */
[class*="viewerBadge"],
[class*="ViewerBadge"],
[class*="styles_viewerBadge"],
a[data-testid="viewerBadge"],
/* Repo / Streamlit host links only inside chrome surfaces */
header a[href*="github.com"],
[data-testid="stHeader"] a[href*="github.com"],
[data-testid="stToolbar"] a[href*="github.com"],
[data-testid="stToolbarActions"] a[href*="github.com"],
a[href*="github.com/streamlit"],
a[href*="share.streamlit.io"],
a[href^="https://streamlit.io"],
a[href^="https://www.streamlit.io"],
div[data-testid="stToolbar"] button,
section[data-testid="stSidebar"] [data-testid="stLogoSpacer"] {
  display: none !important;
  visibility: hidden !important;
  height: 0 !important;
  min-height: 0 !important;
  max-height: 0 !important;
  width: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  opacity: 0 !important;
  pointer-events: none !important;
  overflow: hidden !important;
  position: absolute !important;
  clip: rect(0 0 0 0) !important;
}

/* Reclaim the top chrome strip for a full-bleed executive canvas */
.stApp,
[data-testid="stAppViewContainer"],
.main .block-container {
  padding-top: max(12px, env(safe-area-inset-top, 0px)) !important;
}
</style>
"""


ACC_BASELINE: SectorBook = {
    "code": "ACC_BASELINE",
    "display_name": "ACC Baseline - NZ Scheme Book",
    "header": {
        "title": "NZ AAT SOVEREIGN ORCHESTRATION ENGINE",
        "statutory_meta": (
            "Statutory Governance: Answerable to Cabinet Minister "
            "(Executive Authority) | Crown Entity Act Compliance Mode"
        ),
        "subtitle": (
            "AAT Scheme Performance - Predictive Operational Risk and "
            "Long-Tail Claims Governance (NZD) - All-of-Government Integration"
        ),
    },
    "operational_bridge": {
        "section_caption": (
            "What / Where / When - Crown Agency Sync Surface - "
            "Health NZ / MSD / IRD / Ministerial"
        ),
        "banner_badge": "[MINISTERIAL WATCHLIST ACTIVE]",
        "banner_title": "Critical Pathway Drift - Statutory Escalation Surface",
        "banner_headline": (
            "{critical_subjects} Subjects breaching long-tail liability thresholds"
        ),
        "banner_footer": (
            "Crown Entity Act - Answerable to Minister for ACC - "
            "BIM / Statutory Escalation channel"
        ),
        "channel_receipts": [
            {
                "agency": "Health NZ",
                "status": "PROXIED / OPERATIONAL",
                "receipt": "Last harvest 10:15 AM - HNZ-MED-4402",
            },
            {
                "agency": "MSD",
                "status": "LIVE INTEGRATION",
                "receipt": "Last harvest 11:40 AM - MSD-AX-7710",
            },
            {
                "agency": "IRD",
                "status": "SECURE LIVE SYNC",
                "receipt": "Last harvest 11:42 AM - IRD-2026-99X4",
            },
            {
                "agency": "Ministerial",
                "status": "BLUE / ACTIVE",
                "receipt": "Last harvest 11:45 AM - CAB-BIM-2026-ACC",
            },
        ],
    },
    "bridge_metrics": [
        {
            "sequence_tag": "What",
            "label": "Health NZ Clinical Grid",
            "big_value": "Operational",
            "ground_truth_basis": "Orthopaedic records linked - HNZ-MED-4402",
            "value_class": "metric-value-green",
        },
        {
            "sequence_tag": "Where",
            "label": "MSD Workforce Pipeline",
            "big_value": "14 Matches",
            "ground_truth_basis": "Modified light-duty - MSD-AX-7710",
            "value_class": "metric-value-silver",
        },
        {
            "sequence_tag": "When",
            "label": "IRD Income Exchange",
            "big_value": "Live Sync",
            "ground_truth_basis": "12-month wage ledger - IRD-2026-99X4 - 11:42",
            "value_class": "metric-value-green",
        },
        {
            "sequence_tag": "Crown",
            "label": "Ministerial Cabinet Pipeline",
            "big_value": "Blue / Active",
            "ground_truth_basis": "BIM escalation - CAB-BIM-2026-ACC",
            "value_class": "metric-value-silver",
        },
    ],
    "structural_mirror": [
        {
            "card_id": "macro_valuation",
            "label": "Macro Valuation",
            "big_value": "NZD $4.82B",
            "ground_truth_basis": "Total capital baseline at risk - scheme reserve book",
            "value_class": "metric-value-silver",
        },
        {
            "card_id": "velocity_friction",
            "label": "Velocity Friction",
            "big_value": "NZD $186M / yr",
            "ground_truth_basis": "Annual financial cost of timeline drift",
            "value_class": "metric-value-crimson",
        },
        {
            "card_id": "actionable_controllable_loss",
            "label": "Actionable Controllable Loss",
            "big_value": "NZD $41.6M",
            "ground_truth_basis": (
                "Cumulative burn from administrative / site delays"
            ),
            "value_class": "metric-value-crimson",
        },
    ],
    "layer2_operations": {
        "title": "Layer 2 Operations View",
        "caption": (
            "Site / queue breakdown of actionable controllable loss "
            "(administrative and site delay burn)"
        ),
        "inspect_label": "Inspect Layer 2 Operational Drift",
        "site_queue_metrics": [
            {
                "site": "Auckland Clinical Hub",
                "queue": "MRI / Imaging Gate",
                "backlog": "64 claims",
                "delay_days": "18.4 d",
                "burn": "NZD $12.1M",
                "ground_truth_basis": "HNZ-MED-4402 harvest · imaging SLA breach",
            },
            {
                "site": "Wellington Casework Pod",
                "queue": "MSD Light-Duty Match",
                "backlog": "29 claims",
                "delay_days": "11.2 d",
                "burn": "NZD $8.7M",
                "ground_truth_basis": "MSD-AX-7710 · placement latency",
            },
            {
                "site": "Christchurch Ortho Corridor",
                "queue": "Surgical Scheduling",
                "backlog": "41 claims",
                "delay_days": "22.0 d",
                "burn": "NZD $14.4M",
                "ground_truth_basis": "Theatre slot friction · long-tail reserve",
            },
            {
                "site": "National Income Desk",
                "queue": "IRD Wage Ledger Sync",
                "backlog": "17 claims",
                "delay_days": "6.5 d",
                "burn": "NZD $6.4M",
                "ground_truth_basis": "IRD-2026-99X4 · compensation lag",
            },
        ],
        "layer3_action_label": "Trigger Layer 3 Actionable Clearance",
        "layer3_clearance_receipt": (
            "Layer 3 Actionable Clearance staged - site delay packets sealed "
            "for Cabinet / Scheme Director execution deck."
        ),
    },
    "sidebar_caption": (
        "Localized NZ ACC / IRD / MSD / Health NZ / Cabinet Minister AoG grids"
    ),
    "critical_subjects": 18,
}


GRID_PJM: SectorBook = {
    "code": "GRID_PJM",
    "display_name": "Grid PJM - Interconnection Book",
    "header": {
        "title": "PJM GRID ORCHESTRATION ENGINE",
        "statutory_meta": (
            "Regional Transmission Organization - FERC Compliance Mode | "
            "Independent Market Monitor Oversight"
        ),
        "subtitle": (
            "PJM Interconnection Performance - Congestion Risk and Long-Tail "
            "Capacity Governance (USD) - RTO Integration"
        ),
    },
    "operational_bridge": {
        "section_caption": (
            "What / Where / When - RTO Sync Surface - "
            "Generation / Transmission / Load / Market Ops"
        ),
        "banner_badge": "[CONGESTION WATCHLIST ACTIVE]",
        "banner_title": "Critical Congestion Drift - Market Escalation Surface",
        "banner_headline": (
            "{critical_subjects} Nodes breaching long-tail congestion thresholds"
        ),
        "banner_footer": (
            "FERC Order 2222 - Answerable to PJM Board - "
            "IMM / Market Escalation channel"
        ),
        "channel_receipts": [
            {
                "agency": "Generation",
                "status": "DISPATCHED / OPERATIONAL",
                "receipt": "Last LMP harvest 10:15 AM - GEN-PJM-4402",
            },
            {
                "agency": "Transmission",
                "status": "LIVE INTEGRATION",
                "receipt": "Last flow harvest 11:40 AM - TX-PJM-7710",
            },
            {
                "agency": "Load",
                "status": "SECURE LIVE SYNC",
                "receipt": "Last demand harvest 11:42 AM - LD-PJM-99X4",
            },
            {
                "agency": "Market Ops",
                "status": "BLUE / ACTIVE",
                "receipt": "Last auction harvest 11:45 AM - MKT-PJM-2026",
            },
        ],
    },
    "bridge_metrics": [
        {
            "sequence_tag": "What",
            "label": "Generation Dispatch Grid",
            "big_value": "Operational",
            "ground_truth_basis": "Unit commitments linked - GEN-PJM-4402",
            "value_class": "metric-value-green",
        },
        {
            "sequence_tag": "Where",
            "label": "Transmission Flow Pipeline",
            "big_value": "14 Constraints",
            "ground_truth_basis": "Binding limits - TX-PJM-7710",
            "value_class": "metric-value-silver",
        },
        {
            "sequence_tag": "When",
            "label": "Load Forecast Exchange",
            "big_value": "Live Sync",
            "ground_truth_basis": "Hourly demand curve - LD-PJM-99X4 - 11:42",
            "value_class": "metric-value-green",
        },
        {
            "sequence_tag": "Market",
            "label": "Market Operations Pipeline",
            "big_value": "Blue / Active",
            "ground_truth_basis": "LMP escalation - MKT-PJM-2026",
            "value_class": "metric-value-silver",
        },
    ],
    "structural_mirror": [
        {
            "card_id": "macro_valuation",
            "label": "Macro Valuation",
            "big_value": "USD $9.4B",
            "ground_truth_basis": "Total capital baseline at risk - interconnection book",
            "value_class": "metric-value-silver",
        },
        {
            "card_id": "velocity_friction",
            "label": "Velocity Friction",
            "big_value": "USD $312M / yr",
            "ground_truth_basis": "Annual financial cost of congestion timeline drift",
            "value_class": "metric-value-crimson",
        },
        {
            "card_id": "actionable_controllable_loss",
            "label": "Actionable Controllable Loss",
            "big_value": "USD $67.8M",
            "ground_truth_basis": (
                "Cumulative burn from queue / study administrative delays"
            ),
            "value_class": "metric-value-crimson",
        },
    ],
    "layer2_operations": {
        "title": "Layer 2 Operations View",
        "caption": (
            "Site / queue breakdown of actionable controllable loss "
            "(study and interconnection administrative delays)"
        ),
        "inspect_label": "Inspect Layer 2 Operational Drift",
        "site_queue_metrics": [
            {
                "site": "MAAC Study Cluster",
                "queue": "System Impact Study",
                "backlog": "88 projects",
                "delay_days": "142 d",
                "burn": "USD $24.6M",
                "ground_truth_basis": "GEN-PJM-4402 · SIS cycle overrun",
            },
            {
                "site": "DOM Zone Transmission",
                "queue": "Network Upgrade Cost Allocation",
                "backlog": "36 projects",
                "delay_days": "97 d",
                "burn": "USD $18.2M",
                "ground_truth_basis": "TX-PJM-7710 · CIA friction",
            },
            {
                "site": "Western Load Pocket",
                "queue": "Facility Study Gate",
                "backlog": "52 projects",
                "delay_days": "118 d",
                "burn": "USD $15.9M",
                "ground_truth_basis": "LD-PJM-99X4 · facility study backlog",
            },
            {
                "site": "Market Ops Desk",
                "queue": "Capacity Auction Settlement",
                "backlog": "21 filings",
                "delay_days": "34 d",
                "burn": "USD $9.1M",
                "ground_truth_basis": "MKT-PJM-2026 · settlement lag",
            },
        ],
        "layer3_action_label": "Trigger Layer 3 Actionable Clearance",
        "layer3_clearance_receipt": (
            "Layer 3 Actionable Clearance staged - queue delay packets sealed "
            "for PJM Board / IMM escalation deck."
        ),
    },
    "sidebar_caption": (
        "Localized PJM / Generation / Transmission / Load / Market Ops RTO grids"
    ),
    "critical_subjects": 24,
}


BIOPHARMA_CLARITY: SectorBook = {
    "code": "BIOPHARMA_CLARITY",
    "display_name": "Biopharma Clarity - GMP Book",
    "header": {
        "title": "BIOPHARMA CLARITY ORCHESTRATION ENGINE",
        "statutory_meta": (
            "FDA / EMA GMP Compliance Mode | Quality Assurance Board Oversight"
        ),
        "subtitle": (
            "Biologics Manufacturing Performance - Batch Deviation Risk and "
            "Long-Tail Release Governance (USD) - CMC Integration"
        ),
    },
    "operational_bridge": {
        "section_caption": (
            "What / Where / When - CMC Sync Surface - "
            "Manufacturing / QC / Supply Chain / Regulatory"
        ),
        "banner_badge": "[DEVIATION WATCHLIST ACTIVE]",
        "banner_title": "Critical Batch Drift - Regulatory Escalation Surface",
        "banner_headline": (
            "{critical_subjects} Lots breaching long-tail release thresholds"
        ),
        "banner_footer": (
            "21 CFR Part 211 - Answerable to QA Board - "
            "CAPA / Regulatory Escalation channel"
        ),
        "channel_receipts": [
            {
                "agency": "Manufacturing",
                "status": "VALIDATED / OPERATIONAL",
                "receipt": "Last batch harvest 10:15 AM - MFG-BIO-4402",
            },
            {
                "agency": "QC Lab",
                "status": "LIVE INTEGRATION",
                "receipt": "Last assay harvest 11:40 AM - QC-BIO-7710",
            },
            {
                "agency": "Supply Chain",
                "status": "SECURE LIVE SYNC",
                "receipt": "Last cold-chain harvest 11:42 AM - SC-BIO-99X4",
            },
            {
                "agency": "Regulatory",
                "status": "BLUE / ACTIVE",
                "receipt": "Last submission harvest 11:45 AM - REG-BIO-2026",
            },
        ],
    },
    "bridge_metrics": [
        {
            "sequence_tag": "What",
            "label": "Manufacturing Execution Grid",
            "big_value": "Operational",
            "ground_truth_basis": "Batch records linked - MFG-BIO-4402",
            "value_class": "metric-value-green",
        },
        {
            "sequence_tag": "Where",
            "label": "QC Release Pipeline",
            "big_value": "9 Pending",
            "ground_truth_basis": "Assay queue - QC-BIO-7710",
            "value_class": "metric-value-silver",
        },
        {
            "sequence_tag": "When",
            "label": "Cold-Chain Exchange",
            "big_value": "Live Sync",
            "ground_truth_basis": "Temperature ledger - SC-BIO-99X4 - 11:42",
            "value_class": "metric-value-green",
        },
        {
            "sequence_tag": "Regulatory",
            "label": "Regulatory Submission Pipeline",
            "big_value": "Blue / Active",
            "ground_truth_basis": "CAPA escalation - REG-BIO-2026",
            "value_class": "metric-value-silver",
        },
    ],
    "structural_mirror": [
        {
            "card_id": "macro_valuation",
            "label": "Macro Valuation",
            "big_value": "USD $2.15B",
            "ground_truth_basis": "Total capital baseline at risk - GMP release book",
            "value_class": "metric-value-silver",
        },
        {
            "card_id": "velocity_friction",
            "label": "Velocity Friction",
            "big_value": "USD $94M / yr",
            "ground_truth_basis": "Annual financial cost of batch timeline drift",
            "value_class": "metric-value-crimson",
        },
        {
            "card_id": "actionable_controllable_loss",
            "label": "Actionable Controllable Loss",
            "big_value": "USD $28.3M",
            "ground_truth_basis": (
                "Cumulative burn from QC / site administrative delays"
            ),
            "value_class": "metric-value-crimson",
        },
    ],
    "layer2_operations": {
        "title": "Layer 2 Operations View",
        "caption": (
            "Site / queue breakdown of actionable controllable loss "
            "(QC release and site administrative delays)"
        ),
        "inspect_label": "Inspect Layer 2 Operational Drift",
        "site_queue_metrics": [
            {
                "site": "Suite B Fill / Finish",
                "queue": "Batch Record Review",
                "backlog": "14 lots",
                "delay_days": "9.6 d",
                "burn": "USD $8.4M",
                "ground_truth_basis": "MFG-BIO-4402 · BRR cycle time",
            },
            {
                "site": "QC Central Lab",
                "queue": "Assay Release Gate",
                "backlog": "22 lots",
                "delay_days": "12.1 d",
                "burn": "USD $9.7M",
                "ground_truth_basis": "QC-BIO-7710 · assay queue friction",
            },
            {
                "site": "Cold-Chain Node West",
                "queue": "Excursion Disposition",
                "backlog": "7 lots",
                "delay_days": "5.4 d",
                "burn": "USD $4.2M",
                "ground_truth_basis": "SC-BIO-99X4 · temperature excursion hold",
            },
            {
                "site": "Regulatory Ops",
                "queue": "CAPA / Variation Packet",
                "backlog": "11 filings",
                "delay_days": "16.8 d",
                "burn": "USD $6.0M",
                "ground_truth_basis": "REG-BIO-2026 · submission latency",
            },
        ],
        "layer3_action_label": "Trigger Layer 3 Actionable Clearance",
        "layer3_clearance_receipt": (
            "Layer 3 Actionable Clearance staged - site delay packets sealed "
            "for QA Board / CAPA execution deck."
        ),
    },
    "sidebar_caption": (
        "Localized Biopharma / Manufacturing / QC / Supply Chain / Regulatory grids"
    ),
    "critical_subjects": 11,
}


SECTOR_BOOKS: dict[str, SectorBook] = {
    "ACC_BASELINE": ACC_BASELINE,
    "GRID_PJM": GRID_PJM,
    "BIOPHARMA_CLARITY": BIOPHARMA_CLARITY,
}

DEFAULT_SECTOR_KEY = "ACC_BASELINE"


def get_sector_book(key: str) -> SectorBook:
    """Return sector book by key, falling back to ACC baseline."""
    if key in SECTOR_BOOKS:
        return SECTOR_BOOKS[key]
    return SECTOR_BOOKS[DEFAULT_SECTOR_KEY]


def sector_book_options() -> list[str]:
    """Ordered sector book keys for sidebar selectbox."""
    return list(SECTOR_BOOKS.keys())


def structural_mirror_cards(sector: SectorBook | dict[str, Any]) -> list[MetricCard]:
    """Return the three Structural Mirror KPI cards in canonical order."""
    cards = list(sector.get("structural_mirror", []))
    by_id = {str(card.get("card_id", "")): card for card in cards}
    ordered: list[MetricCard] = []
    for card_id in STRUCTURAL_MIRROR_CARD_IDS:
        if card_id in by_id:
            ordered.append(by_id[card_id])
    # Fall back to first three if IDs are missing (defensive).
    if len(ordered) < 3:
        ordered = cards[:3]
    return ordered


def layer2_operations(sector: SectorBook | dict[str, Any]) -> Layer2Operations:
    """Return Layer 2 Operations View config for the active sector."""
    return sector["layer2_operations"]  # type: ignore[return-value]


# --- Kinetic Lab tenant config (University Operations Vault) ---


class ResearchNode(TypedDict):
    id: str
    label: str
    credit_cost: int
    short_name: str
    summary: str
    unlock_yield: str


class ThemeTokens(TypedDict):
    bg: str
    card: str
    border: str
    accent: str
    accent_soft: str
    text: str
    muted: str


TENANT_CONFIG: dict[str, Any] = {
    "target_domain": "UNIVERSITY INTERCOLLEGIATE ATHLETICS",
    "tenant_identity": "University Operations Vault",
    "active_sector_code": "SEC_01_KINETIC",
    "initial_credits": 450,
    "theme": {
        "bg_color": "bg-slate-950",
        "card_color": "bg-slate-900",
        "border_color": "border-slate-800",
        "accent_color": "emerald-500",
    },
    "research_nodes": [
        {
            "id": "node_1_1",
            "label": "Node 1.1: Dynamic Interface Shear Stress Mapping",
            "credit_cost": 5,
            "short_name": "Shear Stress Mapping",
            "summary": (
                "Map plantar and contact-surface shear vectors during cut, plant, "
                "and push-off so coaching staff can see where force leaks into the "
                "medial/lateral chain."
            ),
            "unlock_yield": (
                "Live shear heatmaps, peak medial shear (N), and cut-angle stress "
                "flags for practice and game-day readiness."
            ),
        },
        {
            "id": "node_1_2",
            "label": "Node 1.2: Pelvic Tilt and Deceleration Chain Asymmetry",
            "credit_cost": 8,
            "short_name": "Decel Chain Asymmetry",
            "summary": (
                "Quantify anterior/posterior pelvic tilt and left-right deceleration "
                "timing so soft-tissue load is attributed to the correct kinetic chain."
            ),
            "unlock_yield": (
                "Asymmetry index, pelvic tilt degrees, and braking-impulse imbalance "
                "for return-to-play and weekly load boards."
            ),
        },
        {
            "id": "node_1_3",
            "label": "Node 1.3: Cellular Longevity and Micro-Tear Chronology",
            "credit_cost": 12,
            "short_name": "Micro-Tear Chronology",
            "summary": (
                "Chronologize micro-tear accumulation against recovery windows so "
                "staff can separate productive overload from lingering tissue debt."
            ),
            "unlock_yield": (
                "Tissue debt score, projected clear-window (hrs), and cumulative "
                "micro-tear chronology across the training microcycle."
            ),
        },
    ],
}

THEME: ThemeTokens = {
    "bg": "#020617",
    "card": "#0f172a",
    "border": "#1e293b",
    "accent": "#10b981",
    "accent_soft": "rgba(16, 185, 129, 0.15)",
    "text": "#f8fafc",
    "muted": "#94a3b8",
}


def research_nodes() -> list[ResearchNode]:
    return list(TENANT_CONFIG["research_nodes"])


def node_by_id(node_id: str) -> ResearchNode | None:
    for node in research_nodes():
        if node["id"] == node_id:
            return node
    return None


def total_unlock_cost() -> int:
    return sum(int(n["credit_cost"]) for n in research_nodes())
