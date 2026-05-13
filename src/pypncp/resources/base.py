"""BaseResource — classe base para todos os resources."""

from __future__ import annotations

from collections.abc import AsyncIterator
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
        **params: Any,
    ) -> AsyncIterator[T]:
        """Itera todas as páginas de um endpoint paginado."""
        pagina = 1
        while True:
            page = await self._list_page(path, model_class, pagina=pagina, **params)
            for item in page.data:
                yield item
            if not page.has_more:
                break
            pagina += 1
