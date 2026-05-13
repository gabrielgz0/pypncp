"""Testes do ContratosResource com a estrutura real da API."""

from pypncp._internal.http import HttpClient
from pypncp.models import Contrato, Page
from pypncp.resources.contratos import ContratosResource


class TestContratosResource:
    CONTRATO_JSON = {
        "anoContrato": 2024,
        "sequencialContrato": 1,
        "numeroContratoEmpenho": "001/2024",
        "objetoContrato": "Contrato de exemplo",
    }

    async def test_list_returns_page(self, httpx_mock):
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/consulta/v1/contratos?pagina=1&dataInicial=20240101&dataFinal=20241231",
            json={
                "data": [self.CONTRATO_JSON],
                "numeroPagina": 1,
                "totalPaginas": 1,
                "totalRegistros": 1,
                "paginasRestantes": 0,
                "empty": False,
            },
        )

        http = HttpClient()
        resource = ContratosResource(http)
        page = await resource.list(data_inicial="2024-01-01", data_final="2024-12-31")

        assert isinstance(page, Page)
        assert len(page.data) == 1
        assert isinstance(page.data[0], Contrato)
        assert page.data[0].numero_contrato_empenho == "001/2024"
        await http.aclose()

    async def test_list_all_iterates_all_pages(self, httpx_mock):
        """Verifica que list_all percorre múltiplas páginas."""
        items_p1 = [
            {
                "anoContrato": 2024,
                "sequencialContrato": i,
                "numeroContratoEmpenho": f"{i}/2024",
                "objetoContrato": f"Obj {i}",
            }
            for i in range(1, 4)
        ]
        items_p2 = [
            {
                "anoContrato": 2024,
                "sequencialContrato": i,
                "numeroContratoEmpenho": f"{i}/2024",
                "objetoContrato": f"Obj {i}",
            }
            for i in range(4, 6)
        ]

        httpx_mock.add_response(
            url="https://pncp.gov.br/api/consulta/v1/contratos?pagina=1&dataInicial=20240101&dataFinal=20241231",
            json={
                "data": items_p1,
                "numeroPagina": 1,
                "totalPaginas": 2,
                "totalRegistros": 5,
                "paginasRestantes": 1,
                "empty": False,
            },
        )
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/consulta/v1/contratos?pagina=2&dataInicial=20240101&dataFinal=20241231",
            json={
                "data": items_p2,
                "numeroPagina": 2,
                "totalPaginas": 2,
                "totalRegistros": 5,
                "paginasRestantes": 0,
                "empty": False,
            },
        )

        http = HttpClient()
        resource = ContratosResource(http)

        results = []
        async for contrato in resource.list_all(
            data_inicial="2024-01-01", data_final="2024-12-31"
        ):
            results.append(contrato)

        assert len(results) == 5
        assert all(isinstance(c, Contrato) for c in results)
        await http.aclose()

    async def test_list_all_single_page(self, httpx_mock):
        """list_all com apenas 1 página não deve fazer requisição extra."""
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/consulta/v1/contratos?pagina=1&dataInicial=20240101&dataFinal=20241231",
            json={
                "data": [self.CONTRATO_JSON],
                "numeroPagina": 1,
                "totalPaginas": 1,
                "totalRegistros": 1,
                "paginasRestantes": 0,
                "empty": False,
            },
        )

        http = HttpClient()
        resource = ContratosResource(http)

        results = []
        async for contrato in resource.list_all(
            data_inicial="2024-01-01", data_final="2024-12-31"
        ):
            results.append(contrato)

        assert len(results) == 1
        await http.aclose()
