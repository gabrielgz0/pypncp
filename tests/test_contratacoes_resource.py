"""Testes do ContratacoesResource."""

from pypncp._internal.http import HttpClient
from pypncp.models import Contratacao, Page
from pypncp.resources.contratacoes import ContratacoesResource


class TestContratacoesResource:
    PUBLICACAO_JSON = {
        "anoCompra": 2024,
        "sequencialCompra": 1,
        "numeroCompra": "001/2024",
        "objetoCompra": "Compra de exemplo",
    }

    async def test_list_publicacao_returns_page(self, httpx_mock):
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao?pagina=1&dataInicial=2024-01-01&dataFinal=2024-12-31&codigoModalidadeContratacao=1",
            json={
                "data": [self.PUBLICACAO_JSON],
                "numeroPagina": 1,
                "totalPaginas": 1,
                "totalRegistros": 1,
                "paginasRestantes": 0,
                "empty": False,
            },
        )

        http = HttpClient()
        resource = ContratacoesResource(http)
        page = await resource.list_publicacao(
            data_inicial="2024-01-01",
            data_final="2024-12-31",
            codigo_modalidade=1,
        )

        assert isinstance(page, Page)
        assert len(page.data) == 1
        assert isinstance(page.data[0], Contratacao)
        assert page.data[0].numero_compra == "001/2024"
        await http.aclose()

    async def test_list_com_proposta(self, httpx_mock):
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/consulta/v1/contratacoes/proposta?pagina=1&dataFinal=2024-12-31",
            json={
                "data": [self.PUBLICACAO_JSON],
                "numeroPagina": 1,
                "totalPaginas": 1,
                "totalRegistros": 1,
                "paginasRestantes": 0,
                "empty": False,
            },
        )

        http = HttpClient()
        resource = ContratacoesResource(http)
        page = await resource.list_com_proposta(data_final="2024-12-31")

        assert len(page.data) == 1
        assert isinstance(page.data[0], Contratacao)
        await http.aclose()
