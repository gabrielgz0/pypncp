"""Testes do SearchResource — API de busca do PNCP."""

from pypncp.models import Page, SearchResult
from pypncp.resources.search import SearchResource


class TestSearchResource:
    SEARCH_JSON = {
        "id": "abc123",
        "title": "Edital nº 001/2024",
        "description": "Aquisição de dipirona",
        "document_type": "edital",
        "item_url": "/compras/123/2024/1",
        "ano": "2024",
        "numero_sequencial": "1",
        "numeroControlePNCP": "123456-1-000001/2024",
        "orgaoCnpj": "00394502000144",
        "orgaoNome": "Ministerio da Gestao",
        "unidadeNome": "Unidade Central",
        "esferaNome": "Federal",
        "poderNome": "Executivo",
        "uf": "DF",
        "municipioNome": "Brasilia",
        "modalidadeLicitacaoNome": "Pregao",
        "situacaoNome": "Divulgada no PNCP",
        "dataPublicacaoPncp": "2024-01-15T10:00:00",
        "valorGlobal": 50000.0,
        "cancelado": False,
        "temResultado": True,
        "tipoNome": "Edital",
    }

    async def test_search_returns_page(self, httpx_mock):
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/search/?q=dipirona&tipos_documento=edital&pagina=1&tam_pagina=10",
            json={
                "items": [self.SEARCH_JSON],
                "total": 1,
            },
        )

        resource = SearchResource()
        page = await resource.search(q="dipirona", tipos_documento="edital")

        assert isinstance(page, Page)
        assert len(page.data) == 1
        assert isinstance(page.data[0], SearchResult)
        assert page.data[0].title == "Edital nº 001/2024"
        assert page.data[0].orgao_nome == "Ministerio da Gestao"
        assert page.data[0].valor_global == 50000.0
        await resource._http.aclose()

    async def test_search_all_iterates(self, httpx_mock):
        """search_all itera todas as paginas."""
        items_p1 = [
            dict(self.SEARCH_JSON, id="1", title=f"Item {i}") for i in range(1, 3)
        ]
        items_p2 = [
            dict(self.SEARCH_JSON, id="2", title=f"Item {i}") for i in range(3, 5)
        ]

        httpx_mock.add_response(
            url="https://pncp.gov.br/api/search/?q=dipirona&tipos_documento=edital&pagina=1&tam_pagina=2",
            json={"items": items_p1, "total": 4},
        )
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/search/?q=dipirona&tipos_documento=edital&pagina=2&tam_pagina=2",
            json={"items": items_p2, "total": 4},
        )

        resource = SearchResource()
        results = []
        async for item in resource.search_all(
            q="dipirona", tipos_documento="edital", tam_pagina=2
        ):
            results.append(item)

        assert len(results) == 4
        assert all(isinstance(r, SearchResult) for r in results)
        await resource._http.aclose()

    async def test_search_with_filters(self, httpx_mock):
        """search com filtros opcionais."""
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/search/?q=dipirona&tipos_documento=edital&pagina=1&tam_pagina=10&ordenacao=-data&status=encerradas&uf=SP",
            json={"items": [self.SEARCH_JSON], "total": 1},
        )

        resource = SearchResource()
        page = await resource.search(
            q="dipirona",
            tipos_documento="edital",
            ordenacao="-data",
            status="encerradas",
            uf="SP",
        )

        assert len(page.data) == 1
        await resource._http.aclose()

    async def test_search_empty(self, httpx_mock):
        """search sem resultados retorna pagina vazia."""
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/search/?q=zzzzz&tipos_documento=edital&pagina=1&tam_pagina=10",
            json={"items": [], "total": 0},
        )

        resource = SearchResource()
        page = await resource.search(q="zzzzz", tipos_documento="edital")

        assert page.data == []
        assert page.total_registros == 0
        assert page.total_paginas == 0
        await resource._http.aclose()
