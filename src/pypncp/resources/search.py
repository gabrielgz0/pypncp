"""Recurso de busca — API de Pesquisa do PNCP.

Endpoint nao documentado oficialmente (interno do portal):
    GET https://pncp.gov.br/api/search/?q=<termo>&tipos_documento=<tipo>

A API de busca faz full-text search no catalogo do PNCP e retorna
resultados de editais, contratos, atas e outros documentos.
"""

from __future__ import annotations

import asyncio
import math
from collections.abc import AsyncIterator
from typing import Any

from pypncp._internal.http import HttpClient
from pypncp.models import Page, SearchResult


class SearchResource:
    """Recurso para busca full-text no catalogo do PNCP.

    Uso:
        async with PNCPClient() as client:
            page = await client.search.search(
                q="dipirona",
                tipos_documento="edital",
                pagina=1,
            )
            for item in page.data:
                print(item.title, item.orgao_nome)

            async for item in client.search.search_all(
                q="notebook",
                tipos_documento="edital",
                status="encerradas",
            ):
                print(item.description, item.valor_global)
    """

    BASE_URL = "https://pncp.gov.br/api/search"

    def __init__(self) -> None:
        self._http = HttpClient(base_url=self.BASE_URL)

    # ------------------------------------------------------------------ #
    #  Busca paginada
    # ------------------------------------------------------------------ #

    async def search(
        self,
        *,
        q: str,
        tipos_documento: str,
        pagina: int = 1,
        tam_pagina: int = 10,
        ordenacao: str | None = None,
        status: str | None = None,
        uf: str | None = None,
        municipio: str | None = None,
        modalidade_licitacao: int | None = None,
    ) -> Page[SearchResult]:
        """Busca itens no catalogo do PNCP.

        Args:
            q: Termo de busca (obrigatorio).
            tipos_documento: Filtro de tipo (edital, contrato, ata, ...).
            pagina: Numero da pagina (comeca em 1).
            tam_pagina: Itens por pagina (max 50?).
            ordenacao: Ordenacao ("-data" para decrescente, "data" para crescente).
            status: Filtro de status ("encerradas", "recebendo_proposta", ...).
            uf: Sigla da UF (SP, RJ, MG, ...).
            municipio: Codigo do municipio IBGE.
            modalidade_licitacao: Codigo da modalidade (1=Pregao, ...).
        """
        params: dict[str, Any] = {
            "q": q,
            "tipos_documento": tipos_documento,
            "pagina": pagina,
            "tam_pagina": tam_pagina,
        }
        if ordenacao is not None:
            params["ordenacao"] = ordenacao
        if status is not None:
            params["status"] = status
        if uf is not None:
            params["uf"] = uf
        if municipio is not None:
            params["municipio"] = municipio
        if modalidade_licitacao is not None:
            params["modalidade_licitacao"] = modalidade_licitacao

        data = await self._http.get("/", params=params)
        raw_items = data.get("items", [])
        total = data.get("total", 0)
        total_paginas = max(1, math.ceil(total / tam_pagina)) if total > 0 else 0

        items = [SearchResult(**item) for item in raw_items]
        return Page(
            data=items,
            numeroPagina=pagina,
            totalPaginas=total_paginas,
            totalRegistros=total,
            paginasRestantes=total_paginas - pagina,
            empty=len(items) == 0,
        )

    # ------------------------------------------------------------------ #
    #  Busca com paginacao automatica
    # ------------------------------------------------------------------ #

    async def search_all(
        self,
        *,
        q: str,
        tipos_documento: str,
        tam_pagina: int = 50,
        prefetch: int = 1,
        ordenacao: str | None = None,
        status: str | None = None,
        uf: str | None = None,
        municipio: str | None = None,
        modalidade_licitacao: int | None = None,
    ) -> AsyncIterator[SearchResult]:
        """Itera todos os resultados de busca (paginação automática).

        Quando ``prefetch > 0`` (padrão), a próxima página é baixada em
        background enquanto o consumidor processa a página atual.

        Args:
            q: Termo de busca.
            tipos_documento: Filtro de tipo.
            tam_pagina: Itens por pagina.
            prefetch: Nivel de concorrencia (0=seq, 1=prefetch, N=workers).
            ordenacao: Ordenacao.
            status: Filtro de status.
            uf: Sigla da UF.
            municipio: Codigo do municipio.
            modalidade_licitacao: Codigo da modalidade.
        """
        pagina = 1
        preload: asyncio.Task[Page[SearchResult]] | None = None

        while True:
            if preload is not None:
                page = await preload
                preload = None
            else:
                page = await self.search(
                    q=q,
                    tipos_documento=tipos_documento,
                    pagina=pagina,
                    tam_pagina=tam_pagina,
                    ordenacao=ordenacao,
                    status=status,
                    uf=uf,
                    municipio=municipio,
                    modalidade_licitacao=modalidade_licitacao,
                )

            if page.has_more and prefetch > 0:
                preload = asyncio.ensure_future(
                    self.search(
                        q=q,
                        tipos_documento=tipos_documento,
                        pagina=pagina + 1,
                        tam_pagina=tam_pagina,
                        ordenacao=ordenacao,
                        status=status,
                        uf=uf,
                        municipio=municipio,
                        modalidade_licitacao=modalidade_licitacao,
                    )
                )

            for item in page.data:
                yield item

            if not page.has_more:
                break
            pagina += 1
