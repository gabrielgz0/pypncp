"""Testes do PrecosResource — precos homologados no PNCP."""

from pypncp.models import ItemCompra, ResultadoItem
from pypncp.resources.precos import PrecosResource


class TestPrecosResource:
    ITEM_JSON = {
        "numeroItem": 1,
        "descricao": "Dipirona 500mg/ml injetavel",
        "quantidade": 1000.0,
        "unidadeMedida": "Unitário",
        "valorUnitarioEstimado": 0.78,
        "valorTotal": 780.0,
        "situacaoCompraItemNome": "Homologado",
        "temResultado": True,
    }
    RESULTADO_JSON = {
        "nomeRazaoSocialFornecedor": "MEDILAR S/A",
        "niFornecedor": "07752236000123",
        "valorUnitarioHomologado": 0.75,
        "valorTotalHomologado": 750.0,
        "quantidadeHomologada": 1000.0,
        "dataResultado": "2024-04-19",
        "sequencialResultado": 1,
        "situacaoCompraItemResultadoNome": "Informado",
    }

    async def test_get_items(self, httpx_mock):
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/pncp/v1/orgaos/78680337000770/compras/2024/128/itens?pagina=1&tamanhoPagina=50",
            json=[self.ITEM_JSON],
        )

        resource = PrecosResource()
        itens = await resource.get_items(orgao="78680337000770", ano=2024, compra=128)

        assert len(itens) == 1
        assert isinstance(itens[0], ItemCompra)
        assert itens[0].numero_item == 1
        assert itens[0].descricao == "Dipirona 500mg/ml injetavel"
        assert itens[0].valor_unitario_estimado == 0.78
        await resource._http.aclose()

    async def test_get_resultados(self, httpx_mock):
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/pncp/v1/orgaos/78680337000770/compras/2024/128/itens/1/resultados",
            json=[self.RESULTADO_JSON],
        )

        resource = PrecosResource()
        resultados = await resource.get_resultados(
            orgao="78680337000770", ano=2024, compra=128, item=1
        )

        assert len(resultados) == 1
        assert isinstance(resultados[0], ResultadoItem)
        assert resultados[0].fornecedor_nome == "MEDILAR S/A"
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

    async def test_resultado_repr(self):
        r = ResultadoItem(
            nomeRazaoSocialFornecedor="Fornecedor A",
            niFornecedor="123",
            valorUnitarioHomologado=10.0,
        )
        assert "Fornecedor A" in repr(r)
        assert "10.0" in repr(r)

    async def test_item_repr(self):
        i = ItemCompra(numeroItem=1, descricao="Item de teste")
        assert "Item de teste" in repr(i)
