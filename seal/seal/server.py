"""The Seal: an OpenShell supervisor middleware (research preview) that denies requests carrying a vault value.

Register it with on_error: fail_closed on every allowed endpoint, so if this process dies, traffic stops.
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
import uuid
from concurrent import futures
from pathlib import Path

import grpc

from . import gen  # noqa: F401  (adds the generated modules to sys.path)
import extension_pb2 as ext  # type: ignore  # noqa: E402
import supervisor_middleware_pb2 as pb  # type: ignore  # noqa: E402
import supervisor_middleware_pb2_grpc as pbg  # type: ignore  # noqa: E402

from . import normalize

MAX_MESSAGE = 4_718_592  # 4.5 MiB, as the middleware docs require
NAME = "dogwatch-seal"


class SealService(pbg.SupervisorMiddlewareServicer):
    def __init__(self, values: list[tuple[str, str]], log_path: Path | None = None):
        self.salt = os.urandom(16)
        self.needles = normalize.build_needles(values, self.salt)
        self.log_path = log_path
        self.decisions: list[dict] = []
        self._lock = threading.Lock()

    def load(self, values: list[tuple[str, str]]) -> None:
        with self._lock:
            self.needles = normalize.build_needles(values, self.salt)

    def _log(self, rec: dict) -> None:
        with self._lock:
            self.decisions.append(rec)
            if self.log_path:
                self.log_path.parent.mkdir(parents=True, exist_ok=True)
                with self.log_path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(rec) + "\n")

    def Describe(self, request, context):
        meta = ext.PeerMetadata(
            protocol_version=ext.ProtocolVersion(major=1, minor=0),
            implementation_name=NAME,
            implementation_version="0.1.0",
            supported_capabilities=["openshell.supervisor-middleware.contract"],
        )
        return pb.MiddlewareManifest(
            name=NAME, service_version="0.1.0",
            bindings=[pb.MiddlewareBinding(
                operation=pb.SUPERVISOR_MIDDLEWARE_OPERATION_HTTP_REQUEST,
                phase=pb.SUPERVISOR_MIDDLEWARE_PHASE_PRE_CREDENTIALS, max_payload_bytes=4 * 1024 * 1024)],
            extension=meta)

    def ValidateConfig(self, request, context):
        return pb.ValidateConfigResponse(valid=True, reason="")

    def EvaluateHttpRequest(self, request, context):
        t = request.target
        extra = [t.path, t.query] + [h.value for h in request.headers]
        d = normalize.check_body(bytes(request.body), extra, self.needles)
        rec = {"id": request.context.request_id or uuid.uuid4().hex[:12], "ts": time.time(),
               "endpoint": f"{t.host}:{t.port}", "method": t.method, "decision": "deny" if d.deny else "allow",
               "kind": d.kind, "path": list(d.path), "fp": d.fp}
        self._log(rec)
        if d.deny:
            return pb.HttpRequestResult(decision=pb.DECISION_DENY, reason=f"vault_value:{d.kind}",
                                        reason_code="vault_value",
                                        findings=[pb.Finding(type="vault_value", label=d.kind, count=1, severity="high")])
        return pb.HttpRequestResult(decision=pb.DECISION_ALLOW)


def serve(values: list[tuple[str, str]], address: str = "127.0.0.1:0", log_path: Path | None = None):
    svc = SealService(values, log_path)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8),
                         options=[("grpc.max_receive_message_length", MAX_MESSAGE),
                                  ("grpc.max_send_message_length", MAX_MESSAGE)])
    pbg.add_SupervisorMiddlewareServicer_to_server(svc, server)
    port = server.add_insecure_port(address)
    server.start()
    return server, svc, port


def main() -> None:
    """Values arrive once on stdin as JSON [[kind, value], ...] from the Radio Officer and stay in memory."""
    values = [tuple(x) for x in json.loads(sys.stdin.read() or "[]")]
    addr = os.environ.get("SEAL_ADDRESS", "127.0.0.1:50061")
    log = Path(os.environ.get("SEAL_LOG", "seal-decisions.jsonl"))
    server, svc, port = serve(values, addr, log)
    print(f"seal listening on {addr} with {len(svc.needles)} needles", flush=True)
    server.wait_for_termination()


if __name__ == "__main__":
    main()
