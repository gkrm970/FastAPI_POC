"""Request ID, timing, and access-logging middleware."""

import logging
import time
import uuid

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger("app.request")


class RequestContextMiddleware:
    """Attach a request ID and processing time to every HTTP response."""

    request_id_header = "X-Request-ID"
    process_time_header = "X-Process-Time"

    def __init__(self, app: ASGIApp) -> None:
        """Wrap the downstream ASGI application."""
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Process an ASGI request."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = self._get_request_id(scope)
        scope.setdefault("state", {})["request_id"] = request_id
        start = time.perf_counter()
        status_code = 500

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                headers = MutableHeaders(scope=message)
                headers[self.request_id_header] = request_id
                headers[self.process_time_header] = f"{self._elapsed_ms(start):.2f}ms"
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            logger.info(
                "%s %s %s %.2fms request_id=%s",
                scope["method"],
                scope["path"],
                status_code,
                self._elapsed_ms(start),
                request_id,
            )

    def _get_request_id(self, scope: Scope) -> str:
        """Reuse the client's request ID or generate a new one."""
        header_name = self.request_id_header.lower().encode()
        for name, value in scope.get("headers", []):
            if name == header_name and value:
                return value.decode("latin-1")
        return str(uuid.uuid4())

    @staticmethod
    def _elapsed_ms(start: float) -> float:
        """Return milliseconds elapsed since start."""
        return (time.perf_counter() - start) * 1000
