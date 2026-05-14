"""testes do searchresource — api de busca do pncp."""

from pypncp.models import Page, ResultadoItem, SearchResult
from pypncp.resources.search import SearchResource


class TestSearchResource:
    search_json = {
        "id": "abc123",
        "title": "edital nº 001/2024",
        "description": "aquisicao de dipirona",
        "document_type": "edital",
        "item_url": "/compras/00394502000144/2024/1",
        "ano": "2024",
        "numero_sequencial": "1",
        "numeroControlePNCP": "123456-1-000001/2024",
        "orgaoCnpj": "00394502000144",
        "orgaoNome": "ministerio da gestao",
        "unidadeNome": "unidade central",
        "esferaNome": "federal",
        "poderNome": "executivo",
        "uf": "df",
        "municipioNome": "brasilia",
        "modalidadeLicitacaoNome": "pregao",
        "situacaoNome": "divulgada no pncp",
        "dataPublicacaoPncp": "2024-01-15T10:00:00",
        "valorGlobal": 50000.0,
        "cancelado": False,
        "temResultado": True,
        "tipoNome": "edital",
    }

    async def test_query_returns_page(self, httpx_mock):
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/search/?q=dipirona&tipos_documento=edital&pagina=1&tam_pagina=10",
            json={"items": [self.search_json], "total": 1},
        )
        resource = SearchResource()
        page = await resource.query(q="dipirona", tipos_documento="edital")

        assert isinstance(page, Page)
        assert len(page.data) == 1
        assert isinstance(page.data[0], SearchResult)
        assert page.data[0].title == "edital nº 001/2024"
        assert page.data[0]._http is not None
        await resource._http.aclose()

    async def test_query_all_iterates(self, httpx_mock):
        """query_all itera todas as paginas."""
        items_p1 = [
            dict(self.search_json, id="1", title=f"item {i}") for i in range(1, 3)
        ]
        items_p2 = [
            dict(self.search_json, id="2", title=f"item {i}") for i in range(3, 5)
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
        async for item in resource.query_all(
            q="dipirona", tipos_documento="edital", tam_pagina=2
        ):
            results.append(item)

        assert len(results) == 4
        assert all(isinstance(r, SearchResult) for r in results)
        await resource._http.aclose()

    async def test_query_all_prefetch_single_page(self, httpx_mock):
        """query_all com prefetch nao faz requisicao extra se so tem 1 pagina."""
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/search/?q=dipirona&tipos_documento=edital&pagina=1&tam_pagina=50",
            json={"items": [self.search_json], "total": 1},
        )
        resource = SearchResource()
        results = []
        async for item in resource.query_all(
            q="dipirona", tipos_documento="edital", prefetch=1
        ):
            results.append(item)
        assert len(results) == 1
        await resource._http.aclose()

    async def test_query_with_filters(self, httpx_mock):
        """query com filtros opcionais."""
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/search/?q=dipirona&tipos_documento=edital&pagina=1&tam_pagina=10&ordenacao=-data&status=encerradas&uf=sp",
            json={"items": [self.search_json], "total": 1},
        )
        resource = SearchResource()
        page = await resource.query(
            q="dipirona",
            tipos_documento="edital",
            ordenacao="-data",
            status="encerradas",
            uf="sp",
        )
        assert len(page.data) == 1
        await resource._http.aclose()

    async def test_query_empty(self, httpx_mock):
        """query sem resultados retorna pagina vazia."""
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/search/?q=zzzzz&tipos_documento=edital&pagina=1&tam_pagina=10",
            json={"items": [], "total": 0},
        )
        resource = SearchResource()
        page = await resource.query(q="zzzzz", tipos_documento="edital")
        assert page.data == []
        assert page.total_registros == 0
        assert page.total_paginas == 0
        await resource._http.aclose()

    async def test_resultado_lazy_fetch(self, httpx_mock):
        """get_resultados faz fetch lazy dos precos homologados."""
        # mock da search
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/search/?q=dipirona&tipos_documento=edital&pagina=1&tam_pagina=10",
            json={"items": [self.search_json], "total": 1},
        )
        # mock dos itens da compra
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/pncp/v1/orgaos/00394502000144/compras/2024/1/itens?pagina=1&tamanhoPagina=50",
            json=[
                {
                    "numeroItem": 1,
                    "descricao": "dipirona",
                    "temResultado": True,
                }
            ],
        )
        # mock dos resultados
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/pncp/v1/orgaos/00394502000144/compras/2024/1/itens/1/resultados",
            json=[
                {
                    "nomeRazaoSocialFornecedor": "medilar s/a",
                    "niFornecedor": "07752236000123",
                    "valorUnitarioHomologado": 0.75,
                }
            ],
        )

        resource = SearchResource()
        page = await resource.query(q="dipirona", tipos_documento="edital")
        item = page.data[0]
        assert item._http is not None

        resultados = await item.get_resultados()
        assert len(resultados) == 1
        assert isinstance(resultados[0], ResultadoItem)
        assert resultados[0].fornecedor_nome == "medilar s/a"
        assert resultados[0].valor_unitario_homologado == 0.75
        await resource._http.aclose()

    async def test_resultado_sem_resultado(self, httpx_mock):
        """get_resultados retorna vazio se tem_resultado=false."""
        item = self.search_json.copy()
        item["temResultado"] = False

        httpx_mock.add_response(
            url="https://pncp.gov.br/api/search/?q=dipirona&tipos_documento=edital&pagina=1&tam_pagina=10",
            json={"items": [item], "total": 1},
        )
        resource = SearchResource()
        page = await resource.query(q="dipirona", tipos_documento="edital")
        resultados = await page.data[0].get_resultados()
        assert resultados == []
        await resource._http.aclose()

    async def test_resultado_item_url_invalido(self):
        """get_resultados retorna vazio se item_url nao puder ser parseado."""
        from pypncp._internal.http import HttpClient

        item = SearchResult(**self.search_json)
        item._http = HttpClient(base_url="https://pncp.gov.br/api/search")
        item.item_url = "/invalido"
        resultados = await item.get_resultados()
        assert resultados == []
        await item._http.aclose()

    async def test_search_result_repr(self):
        r = SearchResult(**self.search_json)
        assert "edital nº 001/2024" in repr(r)
