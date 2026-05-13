"""BaseResource — classe base para todos os resources."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from datetime import date
from typing import Any, TypeVar

from pypncp._internal.http import HttpClient
from pypncp.models import Page

T = TypeVar("T")


class BaseResource:
    """Classe base que todos os resources devem estender.

    Recebe o HttpClient por injeção de dependência — nunca cria o próprio.
    """

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    # ------------------------------------------------------------------ #
    #  Utilitários
    # ------------------------------------------------------------------ #

    @staticmethod
    def _fmt_data(d: str | date) -> str:
        """Normaliza data para o formato yyyyMMdd exigido pela API.

        Aceita:
        - objeto ``date``      → ``date(2025, 1, 1)``
        - string ``YYYY-MM-DD`` → ``"20250101"``
        - string ``yyyyMMdd``   → ``"20250101"`` (inalterado)
        """
        if isinstance(d, date):
            return d.strftime("%Y%m%d")
        return d.replace("-", "")

    # ------------------------------------------------------------------ #
    #  Paginação
    # ------------------------------------------------------------------ #

    async def _list_page(
        self,
        path: str,
        model_class: type[T],
        pagina: int = 1,
        **params: Any,
    ) -> Page[T]:
        """Faz GET paginado e retorna Page[model_class].

        A API de Consulta do PNCP retorna paginação no formato:
        { "data": [...], "numeroPagina": 1, "totalPaginas": 10,
          "totalRegistros": 100, "paginasRestantes": 9, "empty": false }
        """
        data = await self._http.get(path, params={"pagina": pagina, **params})
        items = [model_class(**item) for item in data.get("data", [])]
        return Page(
            data=items,
            numeroPagina=data.get("numeroPagina", pagina),
            totalPaginas=data.get("totalPaginas", 0),
            totalRegistros=data.get("totalRegistros", 0),
            paginasRestantes=data.get("paginasRestantes", 0),
            empty=data.get("empty", len(items) == 0),
        )

    async def _list_all(
        self,
        path: str,
        model_class: type[T],
        prefetch: int = 1,
        **params: Any,
    ) -> AsyncIterator[T]:
        """Itera todas as páginas de um endpoint paginado com prefetch.

        Quando ``prefetch > 0`` (padrão), a próxima página começa a ser
        baixada em background enquanto o consumidor processa os itens da
        página atual. O overlap entre I/O e processamento reduz o tempo
        total da iteração.

        Com ``prefetch=0`` o comportamento é totalmente sequencial: cada
        página é baixada e processada por vez, sem overlap.

        Exemplo com prefetch=1 (time em ms):
            fetch p1(500) → yield itens p1(300) → fetch p2(500) → ...
                     ↓ sobreposto  ↑                   ↓ sobreposto
                fetch p2 começa ───┘              fetch p3 começa ───┘

            Resultado: 500 + 300 + 500 + 300 = 1300ms (vs 1600ms sequencial)
        """
        pagina = 1
        preload: asyncio.Task[Page[T]] | None = None

        while True:
            # Se havia prefetch do loop anterior, aguarda
            if preload is not None:
                page = await preload
                preload = None
            else:
                page = await self._list_page(path, model_class, pagina=pagina, **params)

            # Dispara prefetch da próxima página em background
            if page.has_more and prefetch > 0:
                preload = asyncio.ensure_future(
                    self._list_page(path, model_class, pagina=pagina + 1, **params)
                )

            # Yield dos itens — enquanto isso a próxima página baixa
            for item in page.data:
                yield item

            if not page.has_more:
                break
            pagina += 1
