"""Recurso de contratos/empenhos — API de Consulta do PNCP."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import date

from pypncp._internal.http import HttpClient
from pypncp.models import Contrato, Page
from pypncp.resources.base import BaseResource


class ContratosResource(BaseResource):
    """Recurso para consulta de contratos e empenhos.

    Endpoints:
        GET /v1/contratos                   — por data de publicação
        GET /v1/contratos/atualizacao       — por data de atualização global
        GET /v1/orgaos/{cnpj}/compras/{ano}/{sequencial}  — contrato específico

    Datas sempre normalizadas para yyyyMMdd via ``_fmt_data()``.
    """

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
        """Consulta contratos por período de publicação do PNCP.

        Args:
            data_inicial: Data inicial (date ou YYYY-MM-DD ou YYYYMMDD).
            data_final: Data final.
            cnpj_orgao: CNPJ do órgão (opcional, apenas dígitos).
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
    ) -> AsyncIterator[Contrato]:
        """Itera todos os contratos em um período (paginação automática)."""
        async for item in self._list_all(
            "/contratos",
            Contrato,
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
    ) -> AsyncIterator[Contrato]:
        """Itera todos os contratos por atualização (paginação automática)."""
        async for item in self._list_all(
            "/contratos/atualizacao",
            Contrato,
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
        """Consulta um contrato específico por CNPJ do órgão, ano e sequencial."""
        data = await self._http.get(
            f"/orgaos/{orgao_cnpj}/compras/{ano}/{sequencial}",
        )
        return Contrato(**data)
