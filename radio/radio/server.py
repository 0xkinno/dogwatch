"""Radio Officer host API. The sandbox reaches only these four routes through the gateway."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from dogwatch.outbox.digest import digest as compute_digest
from dogwatch.vault.placeholders import Registry
from dogwatch.watch.state import State


class IdentifierIn(BaseModel):
    kind: str
    value: str


def create_app(state: State, registry: Registry, persist=lambda: None) -> FastAPI:
    app = FastAPI(title="Dogwatch Radio Officer")
    inbox: list[dict] = []
    questions: list[dict] = []

    def leaks(obj) -> bool:
        flat = str(obj)
        return any(v and v in flat for _, v in registry.values())

    @app.post("/vault/identifiers")
    def put_identifier(body: IdentifierIn):
        """The sandbox sends a detected value and receives only its placeholder back."""
        ph = registry.assign(body.kind, body.value)
        persist()
        return {"placeholder": ph}

    @app.post("/drafts")
    def post_draft(draft: dict):
        if leaks(draft):
            raise HTTPException(422, "draft contains a vault value; only placeholders may leave the sandbox")
        pk = draft.get("packet_envelope", draft)
        d = compute_digest(pk["packet"], pk["recipients"], pk["attachments"])
        if d != pk.get("digest"):
            raise HTTPException(422, "digest does not match packet")
        created = state.add_draft(f"d-{d[:8]}", d, pk, d)
        return {"id": f"d-{d[:8]}", "digest": d, "created": created}

    @app.post("/questions")
    def post_question(q: dict):
        if leaks(q):
            raise HTTPException(422, "question contains a vault value")
        questions.append(q)
        return {"queued": len(questions)}

    @app.get("/inbox")
    def get_inbox():
        out = list(inbox)
        inbox.clear()
        return {"messages": out}

    app.state.inbox = inbox
    app.state.questions = questions
    return app
