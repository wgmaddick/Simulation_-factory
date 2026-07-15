"""Kinetic Asset Management Vault — Flask application."""

from __future__ import annotations

from flask import Flask, jsonify, render_template, request, session

from engine import VaultSession, get_config

app = Flask(__name__)
app.secret_key = "kinetic-vault-dev-secret"


def _session_vault() -> VaultSession:
    """Restore or create the in-memory vault ledger tied to the Flask session."""
    if "vault" not in session:
        session["vault"] = {"credits": get_config()["initial_credits"], "history": []}

    state = session["vault"]
    vault = VaultSession(credits=int(state["credits"]), history=list(state.get("history", [])))
    return vault


def _persist_vault(vault: VaultSession) -> None:
    session["vault"] = {
        "credits": vault.credits,
        "history": vault.history,
    }
    session.modified = True


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/config")
def api_config():
    config = get_config()
    vault = _session_vault()
    # Reflect live credit balance for returning sessions.
    payload = dict(config)
    payload["initial_credits"] = vault.credits
    return jsonify(payload)


@app.post("/api/analyze")
def api_analyze():
    payload = request.get_json(silent=True) or {}
    node_id = payload.get("nodeId")
    user_speech = payload.get("userSpeech", "")

    if not node_id:
        return jsonify({"error": "nodeId is required"}), 400
    if not str(user_speech).strip():
        return jsonify({"error": "userSpeech is required"}), 400

    vault = _session_vault()
    try:
        result = vault.analyze(str(node_id), str(user_speech))
    except KeyError as exc:
        return jsonify({"error": exc.args[0] if exc.args else "Unknown research node"}), 400
    except ValueError as exc:
        return jsonify({"error": exc.args[0] if exc.args else "Analysis rejected"}), 402

    _persist_vault(vault)
    return jsonify(result)


@app.post("/api/reset")
def api_reset():
    session.pop("vault", None)
    return jsonify({"ok": True, "credits": get_config()["initial_credits"]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
