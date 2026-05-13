"""BaseResource — classe base para todos os resources."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from datetime import date
from typing import Any, TypeVar

from pypncp._internal.http import HttpClient
from pypncp.models import Page

T = TypeVar("T")

_STOP = object()  # sentinela para sinalizar fim de worker


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

    def _list_all(
        self,
        path: str,
        model_class: type[T],
        prefetch: int = 1,
        **params: Any,
    ) -> AsyncIterator[T]:
        """Itera todas as páginas de um endpoint paginado.

        O parâmetro ``prefetch`` controla o nível de concorrência:

        * ``0`` — sequencial puro: uma página por vez, sem overlap.
        * ``1`` — **prefetch simples** (padrão): a página N+1 é baixada
          em background enquanto o consumidor processa a página N.
        * ``≥2`` — **N workers concorrentes**: ``prefetch`` workers baixam
          páginas em paralelo com stride. Resultados fora de ordem são
          bufferizados e entregues na ordem correta ao consumidor.

        Exemplo com ``prefetch=2`` (2 workers, stride=2):
            worker A: p1 ──┬─ buffer ──┬─> yield p1 itens ──┬─> yield p3 ...
            worker B: p2 ──┘           │                     └── [p2 pronto]
                                       └──> yield p2 itens ───┘
        """
        if prefetch <= 0:
            return self._list_all_sequential(path, model_class, **params)
        if prefetch == 1:
            return self._list_all_prefetch(path, model_class, **params)
        return self._list_all_workers(path, model_class, prefetch, **params)

    # ------------------------------------------------------------------ #
    #  Estratégia: sequencial (prefetch=0)
    # ------------------------------------------------------------------ #

    async def _list_all_sequential(
        self,
        path: str,
        model_class: type[T],
        **params: Any,
    ) -> AsyncIterator[T]:
        """Itera todas as páginas sem nenhum overlap."""
        pagina = 1
        while True:
            page = await self._list_page(path, model_class, pagina=pagina, **params)
            for item in page.data:
                yield item
            if not page.has_more:
                break
            pagina += 1

    # ------------------------------------------------------------------ #
    #  Estratégia: prefetch simples (prefetch=1)
    # ------------------------------------------------------------------ #

    async def _list_all_prefetch(
        self,
        path: str,
        model_class: type[T],
        **params: Any,
    ) -> AsyncIterator[T]:
        """Itera com uma página de antecipação em background.

        Enquanto o consumidor processa os itens da página N, a página
        N+1 já está sendo baixada em background (``asyncio.ensure_future``).
        """
        pagina = 1
        preload: asyncio.Task[Page[T]] | None = None

        while True:
            if preload is not None:
                page = await preload
                preload = None
            else:
                page = await self._list_page(path, model_class, pagina=pagina, **params)

            if page.has_more:
                preload = asyncio.ensure_future(
                    self._list_page(path, model_class, pagina=pagina + 1, **params)
                )

            for item in page.data:
                yield item

            if not page.has_more:
                break
            pagina += 1

    # ------------------------------------------------------------------ #
    #  Estratégia: N workers concorrentes (prefetch >= 2)
    # ------------------------------------------------------------------ #

    async def _list_all_workers(
        self,
        path: str,
        model_class: type[T],
        num_workers: int,
        **params: Any,
    ) -> AsyncIterator[T]:
        """Itera com ``num_workers`` workers baixando páginas em paralelo.

        Cada worker faz um stride de ``num_workers``:
            worker 0 → páginas 1, 1+N, 1+2N, ...
            worker 1 → páginas 2, 2+N, 2+2N, ...
            ...

        Os resultados são postos em uma ``asyncio.Queue``. O consumidor
        retira da fila e entrega os itens na ordem correta de página,
        bufferizando resultados que chegam adiantados.
        """
        queue: asyncio.Queue[Any] = asyncio.Queue()
        stops = 0

        async def _worker(worker_id: int) -> None:
            """Worker individual: baixa páginas no stride e publica na fila."""
            p = worker_id + 1
            try:
                while True:
                    page = await self._list_page(
                        path, model_class, pagina=p, **params
                    )
                    await queue.put((p, page))
                    if not page.has_more:
                        break
                    if p >= page.total_paginas:
                        break
                    p += num_workers
                    if p > page.total_paginas:
                        break
            except BaseException as exc:
                await queue.put(exc)
            finally:
                await queue.put(_STOP)

        # Dispara todos os workers
        for i in range(num_workers):
            asyncio.ensure_future(_worker(i))

        # Consumidor com buffer ordenado
        next_page = 1
        buffer: dict[int, Page[T]] = {}

        while stops < num_workers:
            result = await queue.get()

            if result is _STOP:
                stops += 1
                continue

            if isinstance(result, BaseException):
                raise result

            page_num, page = result

            if page_num == next_page:
                for item in page.data:
                    yield item
                next_page += 1
                # Descarta página do buffer se pulamos alguma
                while next_page in buffer:
                    buf = buffer.pop(next_page)
                    for item in buf.data:
                        yield item
                    next_page += 1
            else:
                buffer[page_num] = page
