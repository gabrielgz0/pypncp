"""Testes dos modelos Pydantic baseados na OpenAPI real do PNCP."""

from datetime import date

from pypncp.models import (
    Ata,
    Contratacao,
    Contrato,
    OrgaoEntidade,
    Page,
    UnidadeOrgao,
)


class TestOrgaoEntidade:
    def test_minimal(self):
        o = OrgaoEntidade(cnpj="00394502000144", razaoSocial="MGI")
        assert o.cnpj == "00394502000144"
        assert o.nome == "MGI"

    def test_populate_by_name(self):
        o = OrgaoEntidade(cnpj="1", razao_social="Teste")
        assert o.razao_social == "Teste"


class TestUnidadeOrgao:
    def test_minimal(self):
        u = UnidadeOrgao(codigoUnidade="1", nomeUnidade="Setor de Compras")
        assert u.codigo_unidade == "1"
        assert u.nome_unidade == "Setor de Compras"


class TestContrato:
    def test_minimal(self):
        c = Contrato(
            anoContrato=2024,
            sequencialContrato=1,
            numeroContratoEmpenho="001/2024",
            objetoContrato="Objeto do contrato",
        )
        assert c.ano_contrato == 2024
        assert c.objeto_contrato == "Objeto do contrato"
        assert c.numero_contrato_empenho == "001/2024"

    def test_ignores_extra_fields(self):
        """Model com extra='ignore' não quebra com campos inesperados."""
        c = Contrato(
            anoContrato=2024,
            sequencialContrato=1,
            numeroContratoEmpenho="001/2024",
            objetoContrato="X",
            campoInexistente="deve ser ignorado",
        )
        assert c.ano_contrato == 2024

    def test_dates(self):
        c = Contrato(
            anoContrato=2024,
            sequencialContrato=1,
            numeroContratoEmpenho="001/2024",
            objetoContrato="X",
            dataAssinatura="2024-01-15",
        )
        assert c.data_assinatura == date(2024, 1, 15)

    def test_nested_orgao(self):
        """Caso o DTO contenha orgaoEntidade aninhado, os campos
        flattened do model podem ser populados manualmente."""
        c = Contrato(
            anoContrato=2024,
            sequencialContrato=1,
            numeroContratoEmpenho="001/2024",
            objetoContrato="X",
            orgao_cnpj="00394502000144",
            orgao_nome="MGI",
        )
        assert c.orgao_cnpj == "00394502000144"
        assert c.orgao_nome == "MGI"


class TestContratacao:
    def test_minimal(self):
        c = Contratacao(
            anoCompra=2024,
            sequencialCompra=1,
            numeroCompra="001/2024",
            objetoCompra="Compra de exemplo",
        )
        assert c.ano_compra == 2024
        assert c.objeto_compra == "Compra de exemplo"

    def test_srp_default(self):
        c = Contratacao(
            anoCompra=2024,
            sequencialCompra=1,
            numeroCompra="001/2024",
            objetoCompra="X",
        )
        assert c.srp is None


class TestAta:
    def test_minimal(self):
        a = Ata(
            numeroAtaRegistroPreco="001/2024",
            anoAta=2024,
            objetoContratacao="Objeto da ata",
        )
        assert a.numero_ata_registro_preco == "001/2024"
        assert a.objeto_contratacao == "Objeto da ata"

    def test_cancelado_default(self):
        a = Ata(
            numeroAtaRegistroPreco="001/2024",
            anoAta=2024,
            objetoContratacao="X",
        )
        assert a.cancelado is None


class TestPage:
    def test_empty_page(self):
        p = Page(
            data=[],
            numeroPagina=1,
            totalPaginas=0,
            totalRegistros=0,
            paginasRestantes=0,
            empty=True,
        )
        assert p.items == []
        assert not p.has_more

    def test_has_more(self):
        p = Page(
            data=[1, 2],
            numeroPagina=1,
            totalPaginas=3,
            totalRegistros=30,
            paginasRestantes=2,
            empty=False,
        )
        assert p.has_more

    def test_no_more(self):
        p = Page(
            data=[],
            numeroPagina=3,
            totalPaginas=3,
            totalRegistros=30,
            paginasRestantes=0,
            empty=True,
        )
        assert not p.has_more

    def test_items_alias(self):
        """items é alias para data."""
        p = Page[int](
            data=[1, 2, 3],
            numeroPagina=1,
            totalPaginas=1,
            totalRegistros=3,
            paginasRestantes=0,
            empty=False,
        )
        assert p.items == [1, 2, 3]

    def test_populate_by_name(self):
        p = Page(
            data=[1, 2],
            numero_pagina=1,
            total_paginas=2,
            total_registros=20,
            paginas_restantes=1,
            empty=False,
        )
        assert p.numero_pagina == 1
        assert p.total_paginas == 2
