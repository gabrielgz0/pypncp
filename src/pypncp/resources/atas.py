"""Recurso de atas de registro de preço — API de Consulta do PNCP."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import date

from pypncp._internal.http import HttpClient
from pypncp.models import Ata, Page
from pypncp.resources.base import BaseResource


class AtasResource(BaseResource):
    """Recurso para consulta de atas de registro de preço.

    Endpoints:
        GET /v1/atas              — por período de vigência
        GET /v1/atas/atualizacao  — por data de atualização global

    Nota: A API de atas espera data no formato **yyyyMMdd** (ex: 20240101).
    """

    def __init__(self, http: HttpClient) -> None:
        super().__init__(http)

    @staticmethod
    def _fmt(d: str | date) -> str:
        """Converte para yyyyMMdd se for date, senão passa string limpa."""
        if isinstance(d, date):
            return d.strftime("%Y%m%d")
        return d.replace("-", "")  # aceita YYYY-MM-DD ou yyyyMMdd

    async def list(
        self,
        *,
        data_inicial: str | date,
        data_final: str | date,
        pagina: int = 1,
    ) -> Page[Ata]:
        """Consulta atas por período de vigência.

        Args:
            data_inicial: Data inicial (formato YYYY-MM-DD ou yyyyMMdd).
            data_final: Data final (formato YYYY-MM-DD ou yyyyMMdd).
            pagina: Número da página (começa em 1).
        """
        return await self._list_page(
            "/atas",
            Ata,
            pagina=pagina,
            dataInicial=self._fmt(data_inicial),
            dataFinal=self._fmt(data_final),
        )

    async def list_all(
        self,
        *,
        data_inicial: str | date,
        data_final: str | date,
    ) -> AsyncIterator[Ata]:
        """Itera todas as atas em um período (paginação automática)."""
        async for item in self._list_all(
            "/atas",
            Ata,
            dataInicial=self._fmt(data_inicial),
            dataFinal=self._fmt(data_final),
        ):
            yield item

    async def list_atualizacao(
        self,
        *,
        data_inicial: str | date,
        data_final: str | date,
        pagina: int = 1,
    ) -> Page[Ata]:
        """Consulta atas por data de atualização global."""
        return await self._list_page(
            "/atas/atualizacao",
            Ata,
            pagina=pagina,
            dataInicial=self._fmt(data_inicial),
            dataFinal=self._fmt(data_final),
        )

    async def list_all_atualizacao(
        self,
        *,
        data_inicial: str | date,
        data_final: str | date,
    ) -> AsyncIterator[Ata]:
        """Itera todas as atas por atualização (paginação automática)."""
        async for item in self._list_all(
            "/atas/atualizacao",
            Ata,
            dataInicial=self._fmt(data_inicial),
            dataFinal=self._fmt(data_final),
        ):
            yield item
