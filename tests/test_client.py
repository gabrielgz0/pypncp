"""Testes do PNCPClient — facade, builder, context manager."""

import pytest

from pypncp import PNCPClient


class TestPNCPClientBuilder:
    def test_builder_defaults(self):
        client = PNCPClient.builder().build()
        assert client._http.base_url == "https://pncp.gov.br/api/consulta/v1"
        assert client._http._max_retries == 3
        assert client._http._token is None

    def test_builder_custom(self):
        client = (
            PNCPClient.builder()
            .base_url("https://custom.url/api")
            .timeout(60)
            .retries(5)
            .build()
        )
        assert client._http.base_url == "https://custom.url/api"
        assert client._http._max_retries == 5

    def test_builder_fluent_returns_self(self):
        builder = PNCPClient.builder()
        assert builder.timeout(10) is builder
        assert builder.retries(2) is builder
        assert builder.base_url("x") is builder


class TestPNCPClientResources:
    def test_resources_are_attached(self):
        client = PNCPClient()
        assert client.contratos is not None
        assert client.contratacoes is not None
        assert client.atas is not None

    def test_http_injected_in_resources(self):
        client = PNCPClient()
        assert client.contratos._http is client._http
        assert client.contratacoes._http is client._http
        assert client.atas._http is client._http


class TestPNCPClientDependencyInjection:
    def test_context_manager(self):
        async def run():
            async with PNCPClient() as client:
                assert isinstance(client, PNCPClient)

        pytest.mark.asyncio(run)
