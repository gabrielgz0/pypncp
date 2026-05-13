"""Testes do AtasResource."""

from pypncp._internal.http import HttpClient
from pypncp.models import Ata, Page
from pypncp.resources.atas import AtasResource


class TestAtasResource:
    ATA_JSON = {
        "numeroAtaRegistroPreco": "001/2024",
        "anoAta": 2024,
        "objetoContratacao": "Ata de exemplo",
    }

    async def test_list_returns_page(self, httpx_mock):
        httpx_mock.add_response(
            url="https://pncp.gov.br/api/consulta/v1/atas?pagina=1&dataInicial=20240101&dataFinal=20241231",
            json={
                "data": [self.ATA_JSON],
                "numeroPagina": 1,
                "totalPaginas": 1,
                "totalRegistros": 1,
                "paginasRestantes": 0,
                "empty": False,
            },
        )

        http = HttpClient()
        resource = AtasResource(http)
        page = await resource.list(data_inicial="2024-01-01", data_final="2024-12-31")

        assert isinstance(page, Page)
        assert len(page.data) == 1
        assert isinstance(page.data[0], Ata)
        assert page.data[0].numero_ata_registro_preco == "001/2024"
        await http.aclose()

    async def test_list_with_date_objects(self, httpx_mock):
        from datetime import date

        httpx_mock.add_response(
            url="https://pncp.gov.br/api/consulta/v1/atas?pagina=1&dataInicial=20240101&dataFinal=20241231",
            json={
                "data": [self.ATA_JSON],
                "numeroPagina": 1,
                "totalPaginas": 1,
                "totalRegistros": 1,
                "paginasRestantes": 0,
                "empty": False,
            },
        )

        http = HttpClient()
        resource = AtasResource(http)
        page = await resource.list(
            data_inicial=date(2024, 1, 1),
            data_final=date(2024, 12, 31),
        )

        assert len(page.data) == 1
        await http.aclose()
