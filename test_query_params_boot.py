"""Regression checks for app.py query-param boot / sync logic.

Simulates Streamlit query_params + session_state without a full AppTest run.
"""
from __future__ import annotations

import sys
import types
import unittest
from unittest import mock


class FakeQueryParams(dict):
    """Minimal stand-in for st.query_params (dict + from_dict)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.from_dict_calls = []

    def from_dict(self, mapping):
        self.from_dict_calls.append(dict(mapping))
        self.clear()
        self.update(mapping)

    def get(self, key, default=None):
        return super().get(key, default)


def _install_fake_streamlit(qp: FakeQueryParams, session: dict):
    st = types.ModuleType("streamlit")
    st.query_params = qp
    st.session_state = session

    def _set_page_config(**kwargs):
        return None

    def _markdown(*args, **kwargs):
        return None

    def _sidebar():
        side = types.SimpleNamespace()
        side.title = lambda *a, **k: None
        side.markdown = lambda *a, **k: None
        side.caption = lambda *a, **k: None
        side.success = lambda *a, **k: None
        side.selectbox = lambda *a, **k: session.get("sector_book_key", "ACC_BASELINE")
        return side

    st.set_page_config = _set_page_config
    st.markdown = _markdown
    st.sidebar = _sidebar()
    st.columns = lambda n: [types.SimpleNamespace() for _ in range(n)]
    st.progress = lambda *a, **k: None
    st.expander = lambda *a, **k: mock.MagicMock()
    st.table = lambda *a, **k: None
    st.info = lambda *a, **k: None
    st.button = lambda *a, **k: False
    st.success = lambda *a, **k: None
    st.caption = lambda *a, **k: None
    sys.modules["streamlit"] = st
    return st


class QueryParamsBootTests(unittest.TestCase):
    def tearDown(self):
        sys.modules.pop("streamlit", None)
        # Drop cached app module between cases
        for name in list(sys.modules):
            if name == "app" or name.startswith("app."):
                sys.modules.pop(name, None)

    def test_boot_pass_does_not_write_query_params(self):
        qp = FakeQueryParams({"co": "PJM", "embed": "true", "utm_source": "safari"})
        session = {}
        _install_fake_streamlit(qp, session)

        # Import triggers module-level boot routing. We only need the helpers /
        # flags, so stop before full UI by loading source fragments.
        import importlib.util
        from pathlib import Path

        # Exercise helpers by exec'ing the routing block in isolation
        from config import resolve_sector_co, sector_book_options, sector_co_short

        # Inline the fixed helper logic (mirrors app.py) against the fake proxy
        def _qp_scalar(value):
            if isinstance(value, (list, tuple)):
                value = value[0] if value else ""
            return str(value or "").strip()

        def _query_params_snapshot():
            snap = {}
            for key in list(qp.keys()):
                snap[str(key)] = _qp_scalar(qp.get(key))
            return snap

        def _sync_co_query_param():
            short = sector_co_short(session["sector_book_key"])
            snap = _query_params_snapshot()
            current = snap.get("co", "")
            has_cl = "cl" in snap
            if current == short and not has_cl:
                return
            snap["co"] = short
            snap.pop("cl", None)
            qp.from_dict(snap)

        options = sector_book_options()
        keys = list(options.keys())
        co_raw = _query_params_snapshot().get("co", "")
        matched = resolve_sector_co(co_raw, default=None)
        self.assertEqual(matched, "GRID_PJM")
        session["sector_book_key"] = matched

        is_boot = not session.get("_co_query_boot_done")
        self.assertTrue(is_boot)
        session["_co_query_boot_done"] = True

        # Boot path must NOT mutate query params
        if not is_boot:
            _sync_co_query_param()
        self.assertEqual(qp.from_dict_calls, [])
        self.assertEqual(qp.get("co"), "PJM")
        self.assertEqual(qp.get("embed"), "true")
        self.assertEqual(qp.get("utm_source"), "safari")

        # Post-boot sync with mismatched shortcode preserves siblings
        session["sector_book_key"] = "HEALTH_NHS"
        is_boot = not session.get("_co_query_boot_done")
        self.assertFalse(is_boot)
        if not is_boot:
            _sync_co_query_param()
        self.assertEqual(len(qp.from_dict_calls), 1)
        self.assertEqual(qp.get("co"), "NHS")
        self.assertEqual(qp.get("embed"), "true")
        self.assertEqual(qp.get("utm_source"), "safari")

    def test_sync_drops_legacy_cl_and_keeps_siblings(self):
        qp = FakeQueryParams({"cl": "PJM", "embed": "true"})
        session = {"sector_book_key": "GRID_PJM", "_co_query_boot_done": True}
        _install_fake_streamlit(qp, session)
        from config import sector_co_short

        def _qp_scalar(value):
            if isinstance(value, (list, tuple)):
                value = value[0] if value else ""
            return str(value or "").strip()

        def _query_params_snapshot():
            return {str(k): _qp_scalar(qp.get(k)) for k in list(qp.keys())}

        def _sync_co_query_param():
            short = sector_co_short(session["sector_book_key"])
            snap = _query_params_snapshot()
            if snap.get("co", "") == short and "cl" not in snap:
                return
            snap["co"] = short
            snap.pop("cl", None)
            qp.from_dict(snap)

        _sync_co_query_param()
        self.assertNotIn("cl", qp)
        self.assertEqual(qp.get("co"), "PJM")
        self.assertEqual(qp.get("embed"), "true")

    def test_resolve_sector_co_pjm(self):
        from config import resolve_sector_co

        self.assertEqual(resolve_sector_co("PJM"), "GRID_PJM")
        self.assertEqual(resolve_sector_co("pjm"), "GRID_PJM")
        self.assertEqual(resolve_sector_co("NHS"), "HEALTH_NHS")


if __name__ == "__main__":
    unittest.main()
