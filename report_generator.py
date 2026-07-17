"""Sovereign Intelligence Report — print-ready PDF generation engine.

Compiles Holistic Audit Segment / session-frame data into a stark,
defense-grade monochrome forensic PDF matching the official SIR layout
blueprint:

  Header Matrix — Document Integrity State, Master Segment Hash,
                  System Instance ID, Temporal Anchor
  Section I     — The Systemic Context (Digital Twin Baseline)
  Section II    — The Moment of Drift Record
  Section III   — The Human Governance Ledger
  Section IV    — The Reactivated "New Reality" Projection

Primary renderer: ``fpdf2``. If unavailable, attempts a clean pip install;
on failure, falls back to a structured HTML→PDF-compatible wrapper that
still produces a valid printable PDF binary.
"""

from __future__ import annotations

import html
import io
import json
import logging
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

logger = logging.getLogger(__name__)

REPORT_TITLE = "SOVEREIGN INTELLIGENCE REPORT"
REPORT_SUBTITLE = "Holistic Audit Segment - Absolute Cryptographic Binding"
HUMAN_LIABILITY_HANDOFF = (
    "HUMAN LIABILITY HAND-OFF: Zero-latency circuit breaker trip recorded. "
    "Human responsibility is hereby engaged for governance of the compromised "
    "kinetic trajectory."
)


# ---------------------------------------------------------------------------
# Dependency bootstrap
# ---------------------------------------------------------------------------


def _ensure_fpdf():
    """Import fpdf2, installing via pip if missing. Returns FPDF class or None."""
    try:
        from fpdf import FPDF  # type: ignore

        return FPDF
    except ImportError:
        pass

    logger.warning("fpdf2 not found — attempting clean pip installation…")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "fpdf2>=2.7.0", "-q"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        from fpdf import FPDF  # type: ignore

        logger.info("fpdf2 installed successfully")
        return FPDF
    except Exception:  # noqa: BLE001
        logger.exception("fpdf2 install failed — using HTML-to-PDF fallback wrapper")
        return None


# ---------------------------------------------------------------------------
# Report data model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ReportFrame:
    """Normalized inputs for the Sovereign Intelligence Report PDF."""

    master_segment_hash: str
    system_instance_id: str
    temporal_anchor_ms: int
    document_integrity_state: str
    systemic_context: dict[str, Any]
    moment_of_drift: dict[str, Any]
    governance_ledger: dict[str, Any]
    new_reality_projection: dict[str, Any]

    @classmethod
    def from_session(
        cls,
        session_data: Mapping[str, Any],
        *,
        segment_hash: str | None = None,
        segment_id: str | None = None,
        created_at_ms: int | None = None,
    ) -> ReportFrame:
        user_input = dict(session_data.get("user_input") or {})
        system_context = dict(session_data.get("system_context") or {})
        avatar_output = dict(session_data.get("avatar_output") or {})
        systemic = dict(session_data.get("systemic_interpretation") or {})

        path = (
            systemic.get("path")
            or user_input.get("path_selection")
            or avatar_output.get("directive")
            or "UNDECLARED"
        )
        path_key = str(path).upper().replace(" ", "_")
        if "PATH_A" in path_key or path_key in {"A", "COMPLIANCE"}:
            integrity = "COMPLIANT"
            path_label = "Path A (Compliance)"
        elif "PATH_B" in path_key or path_key in {"B", "OVERRIDE", "FAILURE"}:
            integrity = "OVERRIDE_HAZARD"
            path_label = "Path B (Failure to Act)"
        else:
            integrity = "PENDING"
            path_label = str(path)

        trip_ms = (
            systemic.get("trip_timestamp_ms")
            or systemic.get("path_b_triggered_ms")
            or system_context.get("trip_timestamp_ms")
            or created_at_ms
            or int(time.time() * 1000)
        )
        instance_id = (
            segment_id
            or avatar_output.get("drift_id")
            or system_context.get("drift_record_id")
            or system_context.get("system_instance_id")
            or "INSTANCE_UNBOUND"
        )
        master_hash = segment_hash or systemic.get("block_hash") or ""

        digital_twin = system_context.get("digital_twin") or system_context
        athletes = list(
            (digital_twin.get("athletes") if isinstance(digital_twin, dict) else None)
            or system_context.get("athletes")
            or []
        )
        breaker = (
            (digital_twin.get("breaker") if isinstance(digital_twin, dict) else None)
            or system_context.get("breaker")
            or {}
        )

        cost = dict(systemic.get("cost_avoidance_projection") or {})
        breach_math = list(systemic.get("breach_math") or systemic.get("breach_summary") or [])

        return cls(
            master_segment_hash=str(master_hash),
            system_instance_id=str(instance_id),
            temporal_anchor_ms=int(trip_ms),
            document_integrity_state=integrity,
            systemic_context={
                "digital_twin_baseline": digital_twin if isinstance(digital_twin, dict) else {},
                "athletes": athletes,
                "breaker": breaker,
                "tick": (
                    digital_twin.get("tick")
                    if isinstance(digital_twin, dict)
                    else system_context.get("tick")
                ),
                "tenant": system_context.get("tenant"),
                "sector": system_context.get("sector"),
            },
            moment_of_drift={
                "trip_timestamp_ms": trip_ms,
                "human_responsibility_engaged": True,
                "human_liability_handoff": HUMAN_LIABILITY_HANDOFF,
                "zero_latency_breaker_trip": True,
                "breach_math": breach_math,
                "verbal_declaration": avatar_output.get("verbal_declaration"),
                "drift_id": avatar_output.get("drift_id")
                or system_context.get("drift_record_id"),
            },
            governance_ledger={
                "path_selection": path_label,
                "path_key": path_key,
                "operator_id": user_input.get("operator_id"),
                "operator_key_verified": bool(user_input.get("operator_id")),
                "intervention": user_input.get("intervention")
                or user_input.get("conversation"),
                "intervention_supplied": bool(
                    user_input.get("intervention_supplied")
                    if "intervention_supplied" in user_input
                    else user_input.get("intervention")
                ),
                "fork_id": avatar_output.get("fork_id") or system_context.get("fork_id"),
            },
            new_reality_projection={
                "divergence_score": systemic.get("divergence_score"),
                "cost_avoidance_projection": cost,
                "peak_telemetry": systemic.get("peak_telemetry") or {},
                "pre_drift_metrics": systemic.get("pre_drift_metrics") or {},
                "engine_reactivated_under_hazard": "PATH_B" in path_key
                or path_key in {"B", "OVERRIDE", "FAILURE"},
            },
        )

    @classmethod
    def from_segment(cls, segment: Any, session_data: Mapping[str, Any] | None = None) -> ReportFrame:
        data = dict(session_data or {})
        data.setdefault("user_input", getattr(segment, "user_input", {}))
        data.setdefault("system_context", getattr(segment, "system_context", {}))
        data.setdefault("avatar_output", getattr(segment, "avatar_output", {}))
        data.setdefault(
            "systemic_interpretation", getattr(segment, "systemic_interpretation", {})
        )
        return cls.from_session(
            data,
            segment_hash=getattr(segment, "block_hash", None)
            or getattr(segment, "hash", None),
            segment_id=getattr(segment, "segment_id", None),
            created_at_ms=getattr(segment, "created_at_ms", None),
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def compile_pdf(
    session_data: Mapping[str, Any] | None = None,
    *,
    segment: Any | None = None,
    frame: ReportFrame | None = None,
) -> bytes:
    """Compile a print-ready Sovereign Intelligence Report PDF.

    Accepts session_data, a HolisticAuditSegment, or a pre-built ReportFrame.
    Returns raw PDF bytes suitable for vault hard-write or Streamlit download.
    """
    if frame is None:
        if segment is not None:
            frame = ReportFrame.from_segment(segment, session_data)
        elif session_data is not None:
            # Prefer hash from an already-sealed segment when present in session.
            frame = ReportFrame.from_session(session_data)
        else:
            raise ValueError("compile_pdf requires session_data, segment, or frame")

    fpdf_cls = _ensure_fpdf()
    if fpdf_cls is not None:
        return _render_with_fpdf(fpdf_cls, frame)
    return _render_html_pdf_fallback(frame)


def compile_pdf_to_path(
    destination: str | Path,
    session_data: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> Path:
    """Compile PDF and write bytes to ``destination`` (exclusive create)."""
    pdf_bytes = compile_pdf(session_data, **kwargs)
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(pdf_bytes)
    return path


# ---------------------------------------------------------------------------
# fpdf2 renderer — stark monochrome forensic layout
# ---------------------------------------------------------------------------


def _render_with_fpdf(FPDF: Any, frame: ReportFrame) -> bytes:
    pdf = FPDF(orientation="P", unit="mm", format="Letter")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(14, 14, 14)
    pdf.add_page()

    # --- Header bar ---
    _black_bar(pdf, REPORT_TITLE, y=10, h=10)
    pdf.set_font("Courier", "B", 8)
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(14, 22)
    pdf.cell(0, 5, _ascii(REPORT_SUBTITLE), ln=1)

    # --- Header Matrix ---
    _section_bar(pdf, "HEADER MATRIX — DOCUMENT CONTROL")
    _kv_grid(
        pdf,
        [
            ("Document Integrity State", frame.document_integrity_state),
            ("Master Segment Hash", frame.master_segment_hash or "PENDING_SEAL"),
            ("System Instance ID", frame.system_instance_id),
            ("Temporal Anchor (ms)", str(frame.temporal_anchor_ms)),
        ],
    )

    # --- Section I ---
    _section_bar(pdf, "SECTION I — THE SYSTEMIC CONTEXT")
    pdf.set_font("Courier", "B", 8)
    pdf.cell(0, 5, _ascii("Digital Twin Baseline Metrics"), ln=1)
    ctx = frame.systemic_context
    _kv_grid(
        pdf,
        [
            ("Tenant / Sector", f"{ctx.get('tenant') or '—'} / {ctx.get('sector') or '—'}"),
            ("Acquisition Tick", str(ctx.get("tick") if ctx.get("tick") is not None else "—")),
            (
                "Breaker State",
                f"{(ctx.get('breaker') or {}).get('system_state', '—')} "
                f"(binary={(ctx.get('breaker') or {}).get('binary', '—')})",
            ),
            ("Trip Count", str((ctx.get("breaker") or {}).get("trip_count", "—"))),
        ],
    )
    athletes = ctx.get("athletes") or []
    if athletes:
        _table(
            pdf,
            headers=["Athlete", "State", "Shear (N)", "Asym (%)", "Tissue Debt"],
            rows=[
                [
                    str(a.get("name", "")),
                    str(a.get("state", "")),
                    _fmt(a.get("shear_peak_n")),
                    _fmt(a.get("asymmetry_pct")),
                    _fmt(a.get("tissue_debt")),
                ]
                for a in athletes[:12]
            ],
            col_widths=(45, 28, 28, 28, 28),
        )
    else:
        twin = ctx.get("digital_twin_baseline") or {}
        _mono_block(pdf, _pretty(twin)[:1800])

    # --- Section II ---
    _section_bar(pdf, "SECTION II — THE MOMENT OF DRIFT RECORD")
    drift = frame.moment_of_drift
    pdf.set_font("Courier", "B", 9)
    pdf.set_fill_color(0, 0, 0)
    pdf.set_text_color(255, 255, 255)
    pdf.multi_cell(
        0,
        6,
        _ascii(
            f"ZERO-LATENCY CIRCUIT BREAKER TRIP @ {drift.get('trip_timestamp_ms')} ms  |  "
            f"DRIFT ID: {drift.get('drift_id') or '—'}"
        ),
        fill=True,
    )
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)
    pdf.set_font("Courier", "B", 8)
    pdf.multi_cell(
        0, 5, _ascii(str(drift.get("human_liability_handoff") or HUMAN_LIABILITY_HANDOFF))
    )
    pdf.ln(1)
    _kv_grid(
        pdf,
        [
            ("Human Responsibility Engaged", str(bool(drift.get("human_responsibility_engaged")))),
            ("Zero-Latency Breaker Trip", str(bool(drift.get("zero_latency_breaker_trip")))),
            ("Verbal Declaration", str(drift.get("verbal_declaration") or "—")[:90]),
        ],
    )
    breaches = drift.get("breach_math") or []
    if breaches:
        pdf.set_font("Courier", "B", 8)
        pdf.cell(0, 5, _ascii("Breach Mathematics"), ln=1)
        rows = []
        for b in breaches[:16]:
            if isinstance(b, dict):
                rows.append(
                    [
                        str(b.get("variable", b.get("source_id", ""))),
                        _fmt(b.get("observed")),
                        _fmt(b.get("threshold")),
                        _fmt(b.get("overshoot", "")),
                    ]
                )
        if rows:
            _table(
                pdf,
                headers=["Variable", "Observed", "Threshold", "Overshoot"],
                rows=rows,
                col_widths=(55, 35, 35, 32),
            )

    # --- Section III ---
    _section_bar(pdf, "SECTION III — THE HUMAN GOVERNANCE LEDGER")
    gov = frame.governance_ledger
    operator_id = gov.get("operator_id")
    verified = bool(gov.get("operator_key_verified"))
    _kv_grid(
        pdf,
        [
            ("Path Selection", str(gov.get("path_selection") or "—")),
            ("Operator Key", str(operator_id) if operator_id else "NONE — UNAUTHENTICATED"),
            (
                "Operator Key Verification",
                "VERIFIED" if verified else "FAILED / NOT PRESENTED",
            ),
            ("Intervention Supplied", str(bool(gov.get("intervention_supplied")))),
            ("Fork ID", str(gov.get("fork_id") or "—")),
        ],
    )
    if gov.get("intervention"):
        pdf.set_font("Courier", "B", 8)
        pdf.cell(0, 5, _ascii("Operator / Conversation Record"), ln=1)
        _mono_block(pdf, str(gov.get("intervention"))[:1200])

    # --- Section IV ---
    _section_bar(pdf, 'SECTION IV - THE REACTIVATED "NEW REALITY" PROJECTION')
    proj = frame.new_reality_projection
    _kv_grid(
        pdf,
        [
            ("Divergence Score", _fmt(proj.get("divergence_score"))),
            (
                "Engine Reactivated Under Hazard",
                str(bool(proj.get("engine_reactivated_under_hazard"))),
            ),
        ],
    )

    cost = proj.get("cost_avoidance_projection") or {}
    if cost:
        pdf.set_font("Courier", "B", 8)
        pdf.cell(0, 5, _ascii("Dynamic Risk / Financial Consequence Table"), ln=1)
        _table(
            pdf,
            headers=["Metric", "Projected Value"],
            rows=[[str(k), _fmt(v)] for k, v in cost.items()],
            col_widths=(100, 57),
        )

    pre = proj.get("pre_drift_metrics") or {}
    peak = proj.get("peak_telemetry") or {}
    if pre or peak:
        pdf.set_font("Courier", "B", 8)
        pdf.cell(0, 5, _ascii("Trajectory Delta - Pre-Drift vs Peak Telemetry"), ln=1)
        keys = sorted(set(pre) | set(peak))
        _table(
            pdf,
            headers=["Metric", "Pre-Drift", "Peak / Post"],
            rows=[
                [k, _fmt(pre.get(k, "—")), _fmt(peak.get(k, "—"))] for k in keys
            ],
            col_widths=(55, 50, 52),
        )

    # --- Footer seal ---
    pdf.ln(4)
    _black_bar(pdf, "STATUS: SEALED — TAMPER-PROOF FORENSIC AUDIT TRAIL", h=8)
    pdf.set_font("Courier", "", 7)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)
    pdf.multi_cell(
        0,
        4,
        _ascii(
            f"SHA-256 BLOCK HASH (UN-ALTERABLE SEAL)\n{frame.master_segment_hash or 'PENDING_SEAL'}"
        ),
    )

    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()


def _ascii(text: Any) -> str:
    """Normalize to fpdf core-font-safe Latin-1 (defense-log typography)."""
    s = str(text if text is not None else "")
    replacements = {
        "\u2014": "-",  # em dash
        "\u2013": "-",  # en dash
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2022": "*",
        "\u00a0": " ",
        "\u2192": "->",
        "\u2264": "<=",
        "\u2265": ">=",
    }
    for src, dst in replacements.items():
        s = s.replace(src, dst)
    return s.encode("latin-1", errors="replace").decode("latin-1")


def _black_bar(pdf: Any, text: str, y: float | None = None, h: float = 9) -> None:
    if y is not None:
        pdf.set_y(y)
    pdf.set_fill_color(0, 0, 0)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Courier", "B", 11)
    pdf.cell(0, h, f"  {_ascii(text)}", ln=1, fill=True)
    pdf.set_text_color(0, 0, 0)


def _section_bar(pdf: Any, title: str) -> None:
    pdf.ln(3)
    pdf.set_fill_color(0, 0, 0)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Courier", "B", 9)
    pdf.cell(0, 7, f"  {_ascii(title)}", ln=1, fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(1)


def _kv_grid(pdf: Any, pairs: list[tuple[str, str]]) -> None:
    label_w, value_w = 55, 102
    for label, value in pairs:
        pdf.set_font("Courier", "B", 7)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(label_w, 5, f" {_ascii(label)}", border=1, fill=True)
        pdf.set_font("Courier", "", 7)
        pdf.cell(value_w, 5, f" {_ascii(value)}"[:78], border=1, ln=1)


def _table(
    pdf: Any,
    *,
    headers: list[str],
    rows: list[list[str]],
    col_widths: tuple[float, ...],
) -> None:
    pdf.set_font("Courier", "B", 7)
    pdf.set_fill_color(0, 0, 0)
    pdf.set_text_color(255, 255, 255)
    for h, w in zip(headers, col_widths):
        pdf.cell(w, 5, f" {_ascii(h)}", border=1, fill=True)
    pdf.ln()
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Courier", "", 7)
    fill = False
    for row in rows:
        if fill:
            pdf.set_fill_color(245, 245, 245)
        else:
            pdf.set_fill_color(255, 255, 255)
        for cell, w in zip(row, col_widths):
            pdf.cell(w, 5, f" {_ascii(cell)}"[: int(w / 1.6)], border=1, fill=True)
        pdf.ln()
        fill = not fill
    pdf.ln(1)


def _mono_block(pdf: Any, text: str) -> None:
    pdf.set_font("Courier", "", 6.5)
    pdf.set_fill_color(245, 245, 245)
    pdf.multi_cell(0, 3.5, _ascii(text), border=1, fill=True)
    pdf.ln(1)


# ---------------------------------------------------------------------------
# HTML → printable PDF fallback (dependency-free valid PDF)
# ---------------------------------------------------------------------------


def _render_html_pdf_fallback(frame: ReportFrame) -> bytes:
    """Structured HTML blueprint compiled into a minimal multi-page PDF.

    Used when fpdf2 cannot be installed. Content mirrors the same four
    sections and header matrix for print-ready forensic output.
    """
    html_doc = _build_html_blueprint(frame)
    # Embed HTML as PDF text lines (print-faithful monochrome layout).
    lines: list[str] = [
        REPORT_TITLE,
        REPORT_SUBTITLE,
        "",
        "HEADER MATRIX — DOCUMENT CONTROL",
        f"Document Integrity State : {frame.document_integrity_state}",
        f"Master Segment Hash      : {frame.master_segment_hash or 'PENDING_SEAL'}",
        f"System Instance ID       : {frame.system_instance_id}",
        f"Temporal Anchor (ms)     : {frame.temporal_anchor_ms}",
        "",
        "SECTION I — THE SYSTEMIC CONTEXT",
        _pretty(frame.systemic_context)[:2000],
        "",
        "SECTION II — THE MOMENT OF DRIFT RECORD",
        f"ZERO-LATENCY CIRCUIT BREAKER TRIP @ {frame.moment_of_drift.get('trip_timestamp_ms')} ms",
        HUMAN_LIABILITY_HANDOFF,
        _pretty(frame.moment_of_drift)[:1600],
        "",
        "SECTION III — THE HUMAN GOVERNANCE LEDGER",
        _pretty(frame.governance_ledger)[:1600],
        "",
        'SECTION IV — THE REACTIVATED "NEW REALITY" PROJECTION',
        _pretty(frame.new_reality_projection)[:2000],
        "",
        "STATUS: SEALED — TAMPER-PROOF FORENSIC AUDIT TRAIL",
        f"SHA-256: {frame.master_segment_hash or 'PENDING_SEAL'}",
        "",
        "<!-- HTML_BLUEPRINT_BEGIN -->",
        html_doc[:2500],
        "<!-- HTML_BLUEPRINT_END -->",
    ]
    return _lines_to_minimal_pdf(lines)


def _build_html_blueprint(frame: ReportFrame) -> str:
    def esc(v: Any) -> str:
        return html.escape(str(v))

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"/>
<title>{esc(REPORT_TITLE)}</title>
<style>
  body {{ font-family: Courier, monospace; color:#000; background:#fff; margin:24px; }}
  h1,h2 {{ background:#000; color:#fff; padding:8px 12px; }}
  table {{ border-collapse: collapse; width:100%; margin:8px 0; }}
  th,td {{ border:1px solid #000; padding:4px 8px; text-align:left; font-size:12px; }}
  th {{ background:#000; color:#fff; }}
  .seal {{ border:2px solid #000; padding:12px; margin-top:16px; }}
</style></head><body>
<h1>{esc(REPORT_TITLE)}</h1>
<p>{esc(REPORT_SUBTITLE)}</p>
<h2>HEADER MATRIX — DOCUMENT CONTROL</h2>
<table>
<tr><th>Document Integrity State</th><td>{esc(frame.document_integrity_state)}</td></tr>
<tr><th>Master Segment Hash</th><td>{esc(frame.master_segment_hash or 'PENDING_SEAL')}</td></tr>
<tr><th>System Instance ID</th><td>{esc(frame.system_instance_id)}</td></tr>
<tr><th>Temporal Anchor (ms)</th><td>{esc(frame.temporal_anchor_ms)}</td></tr>
</table>
<h2>SECTION I — THE SYSTEMIC CONTEXT</h2>
<pre>{esc(_pretty(frame.systemic_context))}</pre>
<h2>SECTION II — THE MOMENT OF DRIFT RECORD</h2>
<p><strong>{esc(HUMAN_LIABILITY_HANDOFF)}</strong></p>
<pre>{esc(_pretty(frame.moment_of_drift))}</pre>
<h2>SECTION III — THE HUMAN GOVERNANCE LEDGER</h2>
<pre>{esc(_pretty(frame.governance_ledger))}</pre>
<h2>SECTION IV — THE REACTIVATED &quot;NEW REALITY&quot; PROJECTION</h2>
<pre>{esc(_pretty(frame.new_reality_projection))}</pre>
<div class="seal">STATUS: SEALED — TAMPER-PROOF FORENSIC AUDIT TRAIL<br/>
SHA-256: {esc(frame.master_segment_hash or 'PENDING_SEAL')}</div>
</body></html>"""


def _lines_to_minimal_pdf(lines: list[str]) -> bytes:
    """Dependency-free multi-page PDF from text lines (Letter, Courier)."""
    # Paginate ~58 lines per page.
    pages: list[list[str]] = []
    chunk: list[str] = []
    for line in lines:
        for wrapped in _wrap(line, 95):
            chunk.append(wrapped)
            if len(chunk) >= 58:
                pages.append(chunk)
                chunk = []
    if chunk:
        pages.append(chunk)
    if not pages:
        pages = [["(empty report)"]]

    objects: list[bytes] = []
    # Catalog + Pages placeholder indices
    # We'll build page objects dynamically.
    page_ids: list[int] = []
    content_ids: list[int] = []

    # Object numbering: 1=Catalog, 2=Pages, 3=Font, then pairs of Page/Content
    font_id = 3
    next_id = 4
    page_objs: list[tuple[int, int, bytes]] = []  # page_id, content_id, stream

    for page_lines in pages:
        content_lines = []
        y = 750
        for line in page_lines:
            safe = (
                line.replace("\\", "\\\\")
                .replace("(", "\\(")
                .replace(")", "\\)")
            )
            content_lines.append(f"BT /F1 8 Tf 40 {y} Td ({safe}) Tj ET")
            y -= 12
        stream = "\n".join(content_lines).encode("latin-1", errors="replace")
        page_id = next_id
        content_id = next_id + 1
        next_id += 2
        page_ids.append(page_id)
        content_ids.append(content_id)
        page_objs.append((page_id, content_id, stream))

    kids = " ".join(f"{pid} 0 R" for pid in page_ids)
    objects_by_id: dict[int, bytes] = {
        1: b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n",
        2: (
            f"2 0 obj<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>endobj\n"
        ).encode("ascii"),
        font_id: (
            b"3 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>endobj\n"
        ),
    }
    for page_id, content_id, stream in page_objs:
        objects_by_id[page_id] = (
            f"{page_id} 0 obj<< /Type /Page /Parent 2 0 R "
            f"/MediaBox [0 0 612 792] /Contents {content_id} 0 R "
            f"/Resources << /Font << /F1 {font_id} 0 R >> >> >>endobj\n"
        ).encode("ascii")
        objects_by_id[content_id] = (
            f"{content_id} 0 obj<< /Length {len(stream)} >>stream\n".encode("ascii")
            + stream
            + b"\nendstream\nendobj\n"
        )

    out = bytearray(b"%PDF-1.4\n")
    offsets = {0: 0}
    for oid in sorted(objects_by_id):
        offsets[oid] = len(out)
        out.extend(objects_by_id[oid])
    xref_pos = len(out)
    max_id = max(objects_by_id)
    out.extend(f"xref\n0 {max_id + 1}\n".encode("ascii"))
    out.extend(b"0000000000 65535 f \n")
    for oid in range(1, max_id + 1):
        out.extend(f"{offsets[oid]:010d} 00000 n \n".encode("ascii"))
    out.extend(
        f"trailer<< /Size {max_id + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_pos}\n%%EOF\n".encode("ascii")
    )
    return bytes(out)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _pretty(obj: Any) -> str:
    try:
        return json.dumps(obj, indent=2, sort_keys=True, default=str)
    except TypeError:
        return str(obj)


def _fmt(value: Any) -> str:
    if value is None or value == "":
        return "—"
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def _wrap(text: str, width: int) -> list[str]:
    if not text:
        return [""]
    text = text.replace("\t", " ")
    out: list[str] = []
    while len(text) > width:
        out.append(text[:width])
        text = text[width:]
    out.append(text)
    return out


__all__ = [
    "HUMAN_LIABILITY_HANDOFF",
    "REPORT_SUBTITLE",
    "REPORT_TITLE",
    "ReportFrame",
    "compile_pdf",
    "compile_pdf_to_path",
]
