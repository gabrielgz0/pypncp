"""Testes do HttpClient — retry, error mapping, auth."""

import asyncio

import httpx
import pytest

from pypncp._internal.http import HttpClient
from pypncp.exceptions import (
    AuthError,
    NotFoundError,
    PNCPError,
    ServerError,
)


class TestHttpClientBase:
    def test_rejects_non_positive_max_concurrent(self):
        with pytest.raises(ValueError, match="max_concurrent must be at least 1"):
            HttpClient(max_concurrent=0)

    async def test_get_success(self, httpx_mock):
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/consulta/v1/teste",
            json={"ok": True},
        )
        client = HttpClient()
        result = await client.get("/teste")
        assert result == {"ok": True}
        await client.aclose()

    async def test_limits_concurrent_requests(self, httpx_mock):
        active_requests = 0
        peak_requests = 0
        first_two_started = asyncio.Event()
        release_requests = asyncio.Event()

        async def handler(_request):
            nonlocal active_requests, peak_requests
            active_requests += 1
            peak_requests = max(peak_requests, active_requests)

            if active_requests == 2:
                first_two_started.set()

            await release_requests.wait()
            active_requests -= 1
            return httpx.Response(200, json={"ok": True})

        httpx_mock.add_callback(
            callback=handler,
            url="https://pncp.gov.br/api/consulta/v1/teste",
            is_reusable=True,
        )

        client = HttpClient(max_concurrent=2)
        requests = [asyncio.create_task(client.get("/teste")) for _ in range(3)]

        await asyncio.wait_for(first_two_started.wait(), timeout=1)
        await asyncio.sleep(0)
        assert peak_requests == 2

        release_requests.set()
        assert await asyncio.gather(*requests) == [{"ok": True}] * 3
        await client.aclose()

    async def test_clean_params(self, httpx_mock):
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/consulta/v1/teste",
            match_params={"pagina": "1"},
            json={"items": []},
        )
        client = HttpClient()
        result = await client.get("/teste", params={"pagina": 1, "none_val": None})
        assert result == {"items": []}
        await client.aclose()


class TestHttpClientAuth:
    async def test_no_token_by_default(self, httpx_mock):
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/consulta/v1/teste",
            json={"ok": True},
        )
        client = HttpClient()
        await client.get("/teste")
        request = httpx_mock.get_request()
        assert "Authorization" not in request.headers
        await client.aclose()

    async def test_bearer_token(self, httpx_mock):
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/consulta/v1/teste",
            json={"ok": True},
        )
        client = HttpClient(token="my-token")
        await client.get("/teste")
        request = httpx_mock.get_request()
        assert request.headers["Authorization"] == "Bearer my-token"
        await client.aclose()


class TestHttpClientErrorMapping:
    async def test_404_raises_not_found(self, httpx_mock):
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/consulta/v1/teste",
            status_code=404,
            json={"message": "Recurso nao encontrado"},
        )
        client = HttpClient()
        with pytest.raises(NotFoundError, match="Recurso nao encontrado"):
            await client.get("/teste")
        await client.aclose()

    async def test_401_raises_auth_error(self, httpx_mock):
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/consulta/v1/teste",
            status_code=401,
            json={"message": "Unauthorized"},
        )
        client = HttpClient()
        with pytest.raises(AuthError, match="Unauthorized"):
            await client.get("/teste")
        await client.aclose()

    async def test_403_raises_auth_error(self, httpx_mock):
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/consulta/v1/teste",
            status_code=403,
            json={"message": "Forbidden"},
        )
        client = HttpClient()
        with pytest.raises(AuthError, match="Forbidden"):
            await client.get("/teste")
        await client.aclose()

    async def test_429_is_retried_then_raises(self, httpx_mock):
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/consulta/v1/teste",
            status_code=429,
        )
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/consulta/v1/teste",
            status_code=429,
        )
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/consulta/v1/teste",
            status_code=429,
        )
        client = HttpClient(max_retries=3)
        with pytest.raises(PNCPError, match="Requisição falhou após 3 tentativas"):
            await client.get("/teste")
        await client.aclose()

    async def test_500_raises_server_error(self, httpx_mock):
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/consulta/v1/teste",
            status_code=500,
        )
        client = HttpClient()
        with pytest.raises(ServerError):
            await client.get("/teste")
        await client.aclose()


class TestHttpClientRetry:
    async def test_retry_on_timeout_eventually_succeeds(self, httpx_mock):
        """Simula 2 timeouts seguidos de 1 sucesso."""
        call_count = 0

        async def handler(req):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise httpx.TimeoutException("Simulated timeout", request=req)
            return httpx.Response(200, json={"ok": True})

        # is_reusable=True porque o tenacity faz múltiplas tentativas na mesma URL
        httpx_mock.add_callback(
            callback=handler,
            url="https://pncp.gov.br/api/consulta/v1/teste",
            is_reusable=True,
        )

        client = HttpClient(max_retries=3)
        result = await client.get("/teste")
        assert result == {"ok": True}
        assert call_count == 3
        await client.aclose()

    async def test_all_retries_fail(self, httpx_mock):
        """Simula timeouts em todas as tentativas — deve propagar exceção."""

        async def handler(req):
            raise httpx.TimeoutException("Simulated timeout", request=req)

        # is_reusable=True porque o tenacity fará 3 tentativas na mesma URL
        httpx_mock.add_callback(
            callback=handler,
            url="https://pncp.gov.br/api/consulta/v1/teste",
            is_reusable=True,
        )

        client = HttpClient(max_retries=3)
        with pytest.raises(PNCPError):
            await client.get("/teste")
        await client.aclose()

    async def test_no_retry_on_4xx(self, httpx_mock):
        """404 não deve ser retentado — apenas 1 chamada."""
        call_count = 0

        def handler(req):
            nonlocal call_count
            call_count += 1
            return httpx.Response(404, json={"message": "not found"})

        httpx_mock.add_callback(
            callback=handler,
            url="https://pncp.gov.br/api/consulta/v1/teste",
        )

        client = HttpClient(max_retries=3)
        with pytest.raises(NotFoundError):
            await client.get("/teste")
        assert call_count == 1
        await client.aclose()
