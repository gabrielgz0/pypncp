"""testes do precosresource — precos homologados no pncp."""

from pypncp.models import ItemCompra, ResultadoItem
from pypncp.resources.precos import PrecosResource


class TestPrecosResource:
    item_json = {
        "numeroItem": 1,
        "descricao": "dipirona 500mg/ml injetavel",
        "quantidade": 1000.0,
        "unidadeMedida": "unitario",
        "valorUnitarioEstimado": 0.78,
        "valorTotal": 780.0,
        "situacaoCompraItemNome": "homologado",
        "temResultado": True,
    }
    resultado_json = {
        "nomeRazaoSocialFornecedor": "medilar s/a",
        "niFornecedor": "07752236000123",
        "valorUnitarioHomologado": 0.75,
        "valorTotalHomologado": 750.0,
        "quantidadeHomologada": 1000.0,
        "dataResultado": "2024-04-19",
        "sequencialResultado": 1,
        "situacaoCompraItemResultadoNome": "informado",
    }

    async def test_get_items(self, httpx_mock):
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/pncp/v1/orgaos/78680337000770/compras/2024/128/itens?pagina=1&tamanhoPagina=50",
            json=[self.item_json],
        )
        resource = PrecosResource()
        itens = await resource.get_items(orgao="78680337000770", ano=2024, compra=128)

        assert len(itens) == 1
        assert isinstance(itens[0], ItemCompra)
        assert itens[0].numero_item == 1
        assert itens[0].descricao == "dipirona 500mg/ml injetavel"
        assert itens[0].valor_unitario_estimado == 0.78
        await resource._http.aclose()

    async def test_get_resultados(self, httpx_mock):
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/pncp/v1/orgaos/78680337000770/compras/2024/128/itens/1/resultados",
            json=[self.resultado_json],
        )
        resource = PrecosResource()
        resultados = await resource.get_resultados(
            orgao="78680337000770", ano=2024, compra=128, item=1
        )

        assert len(resultados) == 1
        assert isinstance(resultados[0], ResultadoItem)
        assert resultados[0].fornecedor_nome == "medilar s/a"
        assert resultados[0].cnpj == "07752236000123"
        assert resultados[0].valor_unitario_homologado == 0.75
        assert resultados[0].data_resultado == "2024-04-19"
        await resource._http.aclose()

    async def test_get_items_lista_vazia(self, httpx_mock):
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/pncp/v1/orgaos/123/compras/2024/1/itens?pagina=1&tamanhoPagina=50",
            json=[],
        )
        resource = PrecosResource()
        itens = await resource.get_items(orgao="123", ano=2024, compra=1)
        assert itens == []
        await resource._http.aclose()

    async def test_buscar_precos_pipeline(self, httpx_mock):
        """buscar_precos faz o pipeline completo: search → items → resultados."""
        # mock da search
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/search/?q=dipirona&tipos_documento=edital&pagina=1&tam_pagina=50&ordenacao=-data&status=encerradas",
            json={
                "items": [
                    {
                        "id": "1",
                        "title": "edital dipirona",
                        "description": "dipirona",
                        "document_type": "edital",
                        "item_url": "/compras/00394502000144/2025/1",
                        "ano": "2025",
                        "orgaoCnpj": "00394502000144",
                        "orgaoNome": "ministerio",
                        "temResultado": True,
                    }
                ],
                "total": 1,
            },
        )
        # mock dos itens
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/pncp/v1/orgaos/00394502000144/compras/2025/1/itens?pagina=1&tamanhoPagina=50",
            json=[self.item_json],
        )
        # mock dos resultados
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/pncp/v1/orgaos/00394502000144/compras/2025/1/itens/1/resultados",
            json=[self.resultado_json],
        )

        resource = PrecosResource()
        results = []
        async for r in resource.buscar_precos(q="dipirona", tipos_documento="edital"):
            results.append(r)

        assert len(results) == 1
        assert results[0]["fornecedor"] == "medilar s/a"
        assert results[0]["cnpj"] == "07752236000123"
        assert results[0]["valor_unitario"] == 0.75
        assert "00394502000144" in results[0]["link"]
        await resource._http.aclose()

    async def test_resultado_repr(self):
        r = ResultadoItem(
            nomeRazaoSocialFornecedor="fornecedor a",
            niFornecedor="123",
            valorUnitarioHomologado=10.0,
        )
        assert "fornecedor a" in repr(r)

    async def test_item_repr(self):
        i = ItemCompra(numeroItem=1, descricao="item de teste")
        assert "item de teste" in repr(i)
