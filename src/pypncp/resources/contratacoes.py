"""Recurso de contratações/compras — API de Consulta do PNCP."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import date

from pypncp._internal.http import HttpClient
from pypncp.models import Contratacao, Page
from pypncp.resources.base import BaseResource


class ContratacoesResource(BaseResource):
    """Recurso para consulta de contratações (compras/licitações)."""

    def __init__(self, http: HttpClient) -> None:
        super().__init__(http)

    async def list_publicacao(
        self,
        *,
        data_inicial: str | date,
        data_final: str | date,
        codigo_modalidade: int,
        pagina: int = 1,
    ) -> Page[Contratacao]:
        """Consulta contratações por data de publicação.

        Args:
            data_inicial: Data inicial.
            data_final: Data final.
            codigo_modalidade: Código da modalidade (obrigatório).
            pagina: Número da página (começa em 1).
        """
        return await self._list_page(
            "/contratacoes/publicacao",
            Contratacao,
            pagina=pagina,
            dataInicial=self._fmt_data(data_inicial),
            dataFinal=self._fmt_data(data_final),
            codigoModalidadeContratacao=codigo_modalidade,
        )

    async def list_all_publicacao(
        self,
        *,
        data_inicial: str | date,
        data_final: str | date,
        codigo_modalidade: int,
        prefetch: int = 1,
    ) -> AsyncIterator[Contratacao]:
        """Itera todas as contratações por publicação (paginação automática).

        Args:
            data_inicial: Data inicial.
            data_final: Data final.
            codigo_modalidade: Código da modalidade (obrigatório).
            prefetch: Quantas páginas antecipar em background (0 = sequencial).
        """
        async for item in self._list_all(
            "/contratacoes/publicacao",
            Contratacao,
            prefetch=prefetch,
            dataInicial=self._fmt_data(data_inicial),
            dataFinal=self._fmt_data(data_final),
            codigoModalidadeContratacao=codigo_modalidade,
        ):
            yield item

    async def list_com_proposta(
        self,
        *,
        data_final: str | date,
        codigo_modalidade: int | None = None,
        pagina: int = 1,
    ) -> Page[Contratacao]:
        """Consulta contratações com recebimento de propostas aberto.

        Args:
            data_final: Data final. Sem data inicial.
            codigo_modalidade: Código da modalidade (opcional).
            pagina: Número da página.
        """
        return await self._list_page(
            "/contratacoes/proposta",
            Contratacao,
            pagina=pagina,
            dataFinal=self._fmt_data(data_final),
            codigoModalidadeContratacao=codigo_modalidade,
        )

    async def list_all_com_proposta(
        self,
        *,
        data_final: str | date,
        codigo_modalidade: int | None = None,
        prefetch: int = 1,
    ) -> AsyncIterator[Contratacao]:
        """Itera todas as contratações com proposta aberta (paginação automática).

        Args:
            data_final: Data final.
            codigo_modalidade: Código da modalidade (opcional).
            prefetch: Quantas páginas antecipar em background (0 = sequencial).
        """
        async for item in self._list_all(
            "/contratacoes/proposta",
            Contratacao,
            prefetch=prefetch,
            dataFinal=self._fmt_data(data_final),
            codigoModalidadeContratacao=codigo_modalidade,
        ):
            yield item

    async def list_atualizacao(
        self,
        *,
        data_inicial: str | date,
        data_final: str | date,
        codigo_modalidade: int,
        pagina: int = 1,
    ) -> Page[Contratacao]:
        """Consulta contratações por data de atualização global."""
        return await self._list_page(
            "/contratacoes/atualizacao",
            Contratacao,
            pagina=pagina,
            dataInicial=self._fmt_data(data_inicial),
            dataFinal=self._fmt_data(data_final),
            codigoModalidadeContratacao=codigo_modalidade,
        )

    async def list_all_atualizacao(
        self,
        *,
        data_inicial: str | date,
        data_final: str | date,
        codigo_modalidade: int,
        prefetch: int = 1,
    ) -> AsyncIterator[Contratacao]:
        """Itera todas as contratações por atualização (paginação automática).

        Args:
            data_inicial: Data inicial.
            data_final: Data final.
            codigo_modalidade: Código da modalidade (obrigatório).
            prefetch: Quantas páginas antecipar em background (0 = sequencial).
        """
        async for item in self._list_all(
            "/contratacoes/atualizacao",
            Contratacao,
            prefetch=prefetch,
            dataInicial=self._fmt_data(data_inicial),
            dataFinal=self._fmt_data(data_final),
            codigoModalidadeContratacao=codigo_modalidade,
        ):
            yield item

    async def get(
        self,
        orgao_cnpj: str,
        ano: int,
        sequencial: int,
    ) -> Contratacao:
        """Consulta uma contratação específica."""
        data = await self._http.get(
            f"/orgaos/{orgao_cnpj}/compras/{ano}/{sequencial}",
        )
        return Contratacao(**data)
