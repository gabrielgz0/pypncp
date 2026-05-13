"""Recurso de atas de registro de preço — API de Consulta do PNCP."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import date

from pypncp._internal.http import HttpClient
from pypncp.models import Ata, Page
from pypncp.resources.base import BaseResource


class AtasResource(BaseResource):
    """Recurso para consulta de atas de registro de preço."""

    def __init__(self, http: HttpClient) -> None:
        super().__init__(http)

    async def list(
        self,
        *,
        data_inicial: str | date,
        data_final: str | date,
        pagina: int = 1,
    ) -> Page[Ata]:
        """Consulta atas por período de vigência."""
        return await self._list_page(
            "/atas",
            Ata,
            pagina=pagina,
            dataInicial=self._fmt_data(data_inicial),
            dataFinal=self._fmt_data(data_final),
        )

    async def list_all(
        self,
        *,
        data_inicial: str | date,
        data_final: str | date,
        prefetch: int = 1,
    ) -> AsyncIterator[Ata]:
        """Itera todas as atas em um período (paginação automática).

        Args:
            data_inicial: Data inicial.
            data_final: Data final.
            prefetch: Nível de concorrência: 0=seq, 1=prefetch, N=N workers
        """
        async for item in self._list_all(
            "/atas",
            Ata,
            prefetch=prefetch,
            dataInicial=self._fmt_data(data_inicial),
            dataFinal=self._fmt_data(data_final),
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
            dataInicial=self._fmt_data(data_inicial),
            dataFinal=self._fmt_data(data_final),
        )

    async def list_all_atualizacao(
        self,
        *,
        data_inicial: str | date,
        data_final: str | date,
        prefetch: int = 1,
    ) -> AsyncIterator[Ata]:
        """Itera todas as atas por atualização (paginação automática).

        Args:
            data_inicial: Data inicial.
            data_final: Data final.
            prefetch: Nível de concorrência: 0=seq, 1=prefetch, N=N workers
        """
        async for item in self._list_all(
            "/atas/atualizacao",
            Ata,
            prefetch=prefetch,
            dataInicial=self._fmt_data(data_inicial),
            dataFinal=self._fmt_data(data_final),
        ):
            yield item
