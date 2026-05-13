"""PNCPClient — Facade principal da biblioteca.

Coordena todos os resources e expõe uma interface limpa para o usuário.
"""

from __future__ import annotations

import httpx

from pypncp._internal.http import HttpClient
from pypncp.resources.atas import AtasResource
from pypncp.resources.contratacoes import ContratacoesResource
from pypncp.resources.contratos import ContratosResource
from pypncp.resources.search import SearchResource


class PNCPClient:
    """Cliente para a API de Consulta do PNCP (Portal Nacional de Contratações
    Públicas). A API de consulta é **pública** — não requer autenticação.

    Uso básico:
        async with PNCPClient() as client:
            async for contrato in client.contratos.list_all(
                data_inicial="2024-01-01",
                data_final="2024-12-31",
            ):
                print(contrato.objeto_contrato)

    Usando o Builder:
        client = (
            PNCPClient.builder()
            .timeout(60)
            .retries(5)
            .build()
        )
    """

    def __init__(
        self,
        *,
        base_url: str = "https://pncp.gov.br/api/consulta/v1",
        timeout: int = 30,
        max_retries: int = 3,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._http = HttpClient(
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            token=None,
            client=http_client,
        )

        # Resources — cada um recebe o HttpClient via DI
        self.contratos = ContratosResource(self._http)
        self.contratacoes = ContratacoesResource(self._http)
        self.atas = AtasResource(self._http)
        self.search = SearchResource()

    # ------------------------------------------------------------------ #
    #  Builder
    # ------------------------------------------------------------------ #

    @classmethod
    def builder(cls) -> _Builder:
        return _Builder()

    # ------------------------------------------------------------------ #
    #  Lifecycle
    # ------------------------------------------------------------------ #

    async def close(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> PNCPClient:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()


class _Builder:
    """Builder para configuração fluente do PNCPClient."""

    def __init__(self) -> None:
        self._base_url = "https://pncp.gov.br/api/consulta/v1"
        self._timeout = 30
        self._max_retries = 3

    def base_url(self, value: str) -> _Builder:
        self._base_url = value
        return self

    def timeout(self, value: int) -> _Builder:
        self._timeout = value
        return self

    def retries(self, value: int) -> _Builder:
        self._max_retries = value
        return self

    def build(self) -> PNCPClient:
        return PNCPClient(
            base_url=self._base_url,
            timeout=self._timeout,
            max_retries=self._max_retries,
        )
