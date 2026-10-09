from app.middleware.request_context import RequestContextMiddleware


class TestRequestContextMiddleware:
    """Test request ID and timing headers added by the middleware."""

    @staticmethod
    async def _endpoint(scope, receive, send) -> None:
        """Minimal ASGI app returning an empty 200 response."""
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    async def _call(self, headers: list[tuple[bytes, bytes]]) -> dict[bytes, bytes]:
        """Run the middleware and return the response headers."""
        messages: list[dict] = []

        async def receive() -> dict:
            return {"type": "http.request", "body": b""}

        async def send(message: dict) -> None:
            messages.append(message)

        scope = {"type": "http", "method": "GET", "path": "/", "headers": headers}
        await RequestContextMiddleware(self._endpoint)(scope, receive, send)
        return dict(messages[0]["headers"])

    async def test_generates_request_id_and_process_time(self) -> None:
        """Generate a request ID when the client does not send one."""
        headers = await self._call([])

        assert headers[b"x-request-id"]
        assert headers[b"x-process-time"].endswith(b"ms")

    async def test_reuses_incoming_request_id(self) -> None:
        """Propagate the client's request ID."""
        headers = await self._call([(b"x-request-id", b"abc-123")])

        assert headers[b"x-request-id"] == b"abc-123"
