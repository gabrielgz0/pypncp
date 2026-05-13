"""Recurso de contratos/empenhos — API de Consulta do PNCP."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import date

from pypncp._internal.http import HttpClient
from pypncp.models import Contrato, Page
from pypncp.resources.base import BaseResource


class ContratosResource(BaseResource):
    """Recurso para consulta de contratos e empenhos."""

    def __init__(self, http: HttpClient) -> None:
        super().__init__(http)

    async def list(
        self,
        *,
        data_inicial: str | date,
        data_final: str | date,
        cnpj_orgao: str | None = None,
        pagina: int = 1,
    ) -> Page[Contrato]:
        """Consulta contratos por período de publicação.

        Args:
            data_inicial: Data inicial.
            data_final: Data final.
            cnpj_orgao: CNPJ do órgão (opcional).
            pagina: Número da página (começa em 1).
        """
        return await self._list_page(
            "/contratos",
            Contrato,
            pagina=pagina,
            dataInicial=self._fmt_data(data_inicial),
            dataFinal=self._fmt_data(data_final),
            cnpjOrgao=cnpj_orgao,
        )

    async def list_all(
        self,
        *,
        data_inicial: str | date,
        data_final: str | date,
        cnpj_orgao: str | None = None,
        prefetch: int = 1,
    ) -> AsyncIterator[Contrato]:
        """Itera todos os contratos em um período (paginação automática).

        Args:
            data_inicial: Data inicial.
            data_final: Data final.
            cnpj_orgao: CNPJ do órgão (opcional).
            prefetch: Quantas páginas antecipar em background (0 = sequencial).
        """
        async for item in self._list_all(
            "/contratos",
            Contrato,
            prefetch=prefetch,
            dataInicial=self._fmt_data(data_inicial),
            dataFinal=self._fmt_data(data_final),
            cnpjOrgao=cnpj_orgao,
        ):
            yield item

    async def list_por_atualizacao(
        self,
        *,
        data_inicial: str | date,
        data_final: str | date,
        cnpj_orgao: str | None = None,
        pagina: int = 1,
    ) -> Page[Contrato]:
        """Consulta contratos por data de atualização global."""
        return await self._list_page(
            "/contratos/atualizacao",
            Contrato,
            pagina=pagina,
            dataInicial=self._fmt_data(data_inicial),
            dataFinal=self._fmt_data(data_final),
            cnpjOrgao=cnpj_orgao,
        )

    async def list_all_por_atualizacao(
        self,
        *,
        data_inicial: str | date,
        data_final: str | date,
        cnpj_orgao: str | None = None,
        prefetch: int = 1,
    ) -> AsyncIterator[Contrato]:
        """Itera todos os contratos por atualização (paginação automática)."""
        async for item in self._list_all(
            "/contratos/atualizacao",
            Contrato,
            prefetch=prefetch,
            dataInicial=self._fmt_data(data_inicial),
            dataFinal=self._fmt_data(data_final),
            cnpjOrgao=cnpj_orgao,
        ):
            yield item

    async def get(
        self,
        orgao_cnpj: str,
        ano: int,
        sequencial: int,
    ) -> Contrato:
        """Consulta um contrato específico por CNPJ, ano e sequencial."""
        data = await self._http.get(
            f"/orgaos/{orgao_cnpj}/compras/{ano}/{sequencial}",
        )
        return Contrato(**data)
