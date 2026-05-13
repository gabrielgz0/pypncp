"""Modelos Pydantic baseados na OpenAPI real do PNCP Consulta.

Esquemas extraídos de https://pncp.gov.br/api/consulta/v3/api-docs
"""

from datetime import date, datetime
from typing import TypeVar

from pydantic import BaseModel, Field, model_validator

T = TypeVar("T")


# --------------------------------------------------------------------------- #
#  Paginação — usada por TODOS os endpoints de lista
# --------------------------------------------------------------------------- #


class Page[T](BaseModel):
    """Resposta paginada da API de Consulta.

    A API usa ``data`` para a lista de itens, ``numeroPagina`` para o
    número da página atual, ``totalPaginas``/``totalRegistros`` para
    metadados e ``paginasRestantes`` para controle de paginação.
    """

    data: list[T] = []
    numero_pagina: int = Field(default=1, alias="numeroPagina")
    total_paginas: int = Field(default=0, alias="totalPaginas")
    total_registros: int = Field(default=0, alias="totalRegistros")
    paginas_restantes: int = Field(default=0, alias="paginasRestantes")
    empty: bool = True

    model_config = {"populate_by_name": True}

    @property
    def has_more(self) -> bool:
        return self.paginas_restantes > 0

    @property
    def items(self) -> list[T]:
        """Alias conveniente para ``data``."""
        return self.data


# --------------------------------------------------------------------------- #
#  Órgão / Entidade (aninhado em outros DTOs)
# --------------------------------------------------------------------------- #


class OrgaoEntidade(BaseModel):
    """Órgão/entidade pública."""

    cnpj: str = ""
    razao_social: str = Field(default="", alias="razaoSocial")
    poder_id: str | None = Field(default=None, alias="poderId")
    esfera_id: str | None = Field(default=None, alias="esferaId")

    model_config = {"populate_by_name": True}

    @property
    def nome(self) -> str:
        return self.razao_social


class UnidadeOrgao(BaseModel):
    """Unidade administrativa de um órgão."""

    codigo_unidade: str = Field(default="", alias="codigoUnidade")
    nome_unidade: str = Field(default="", alias="nomeUnidade")
    uf_sigla: str | None = Field(default=None, alias="ufSigla")
    uf_nome: str | None = Field(default=None, alias="ufNome")
    municipio_nome: str | None = Field(default=None, alias="municipioNome")
    codigo_ibge: str | None = Field(default=None, alias="codigoIbge")

    model_config = {"populate_by_name": True}


# --------------------------------------------------------------------------- #
#  Contrato/Empenho — RecuperarContratoDTO
# --------------------------------------------------------------------------- #


class Contrato(BaseModel):
    """Contrato/Empenho (RecuperarContratoDTO).

    Os campos ``orgao_*`` e ``unidade_nome`` são achatados a partir
    dos objetos aninhados ``orgaoEntidade`` e ``unidadeOrgao`` que a
    API devolve.
    """

    numero_controle_pncp_compra: str | None = Field(
        default=None, alias="numeroControlePncpCompra"
    )
    numero_controle_pncp_ata: str | None = Field(
        default=None, alias="numeroControlePncpAta"
    )
    ano_contrato: int = Field(default=0, alias="anoContrato")
    sequencial_contrato: int = Field(default=0, alias="sequencialContrato")
    numero_contrato_empenho: str = Field(default="", alias="numeroContratoEmpenho")
    processo: str | None = None
    objeto_contrato: str = Field(default="", alias="objetoContrato")
    informacao_complementar: str | None = Field(
        default=None, alias="informacaoComplementar"
    )

    # Fornecedor
    ni_fornecedor: str | None = Field(default=None, alias="niFornecedor")
    fornecedor_nome: str | None = Field(default=None, alias="nomeRazaoSocialFornecedor")

    # Valores
    valor_inicial: float | None = Field(default=None, alias="valorInicial")
    valor_global: float | None = Field(default=None, alias="valorGlobal")
    valor_acumulado: float | None = Field(default=None, alias="valorAcumulado")

    # Datas
    data_assinatura: date | None = Field(default=None, alias="dataAssinatura")
    data_vigencia_inicio: date | None = Field(default=None, alias="dataVigenciaInicio")
    data_vigencia_fim: date | None = Field(default=None, alias="dataVigenciaFim")
    data_publicacao_pncp: datetime | None = Field(
        default=None, alias="dataPublicacaoPncp"
    )
    data_atualizacao_global: datetime | None = Field(
        default=None, alias="dataAtualizacaoGlobal"
    )

    # Relacionamentos (extraídos de orgaoEntidade / unidadeOrgao via validator)
    orgao_cnpj: str | None = None
    orgao_nome: str | None = None
    orgao_uf: str | None = None
    unidade_nome: str | None = None

    # Número de controle PNCP
    numero_controle_pncp: str | None = Field(default=None, alias="numeroControlePNCP")

    model_config = {"populate_by_name": True, "extra": "ignore"}

    @model_validator(mode="before")
    @classmethod
    def _flatten_orgao(cls, data: dict) -> dict:
        """Extrai campos de ``orgaoEntidade`` e ``unidadeOrgao`` para o nível
        superior, já que a API devolve esses dados aninhados."""
        if not isinstance(data, dict):
            return data

        if (orgao := data.get("orgaoEntidade")) and isinstance(orgao, dict):
            data.setdefault("orgao_cnpj", orgao.get("cnpj"))
            data.setdefault("orgao_nome", orgao.get("razaoSocial"))

        if (unidade := data.get("unidadeOrgao")) and isinstance(unidade, dict):
            data.setdefault("orgao_uf", unidade.get("ufSigla"))
            data.setdefault("unidade_nome", unidade.get("nomeUnidade"))

        return data

    def __repr__(self) -> str:
        return (
            f"Contrato(numero={self.numero_contrato_empenho}, "
            f"orgao={self.orgao_nome}, "
            f"valor={self.valor_global})"
        )


# --------------------------------------------------------------------------- #
#  Contratação (Compra) — RecuperarCompraPublicacaoDTO / RecuperarCompraDTO
# --------------------------------------------------------------------------- #


class Contratacao(BaseModel):
    """Contratação pública (RecuperarCompraPublicacaoDTO).

    Os campos ``orgao_*`` e ``unidade_nome`` são achatados a partir
    dos objetos aninhados ``orgaoEntidade`` e ``unidadeOrgao`` que a
    API devolve.
    """

    ano_compra: int = Field(default=0, alias="anoCompra")
    sequencial_compra: int = Field(default=0, alias="sequencialCompra")
    numero_compra: str = Field(default="", alias="numeroCompra")
    processo: str | None = None
    objeto_compra: str = Field(default="", alias="objetoCompra")
    informacao_complementar: str | None = Field(
        default=None, alias="informacaoComplementar"
    )
    numero_controle_pncp: str | None = Field(default=None, alias="numeroControlePNCP")

    # Órgão (extraídos de orgaoEntidade / unidadeOrgao via validator)
    orgao_cnpj: str | None = None
    orgao_nome: str | None = None
    orgao_uf: str | None = None
    unidade_nome: str | None = None

    # Modalidade
    modalidade_id: int | None = Field(default=None, alias="modalidadeId")
    modalidade_nome: str | None = Field(default=None, alias="modalidadeNome")

    # Datas
    data_publicacao_pncp: datetime | None = Field(
        default=None, alias="dataPublicacaoPncp"
    )
    data_abertura_proposta: datetime | None = Field(
        default=None, alias="dataAberturaProposta"
    )
    data_atualizacao_global: datetime | None = Field(
        default=None, alias="dataAtualizacaoGlobal"
    )

    # Valores
    valor_total_estimado: float | None = Field(default=None, alias="valorTotalEstimado")
    valor_total_homologado: float | None = Field(
        default=None, alias="valorTotalHomologado"
    )

    # SRP
    srp: bool | None = None

    model_config = {"populate_by_name": True, "extra": "ignore"}

    @model_validator(mode="before")
    @classmethod
    def _flatten_orgao(cls, data: dict) -> dict:
        """Extrai campos de ``orgaoEntidade`` e ``unidadeOrgao`` para o nível
        superior."""
        if not isinstance(data, dict):
            return data

        if (orgao := data.get("orgaoEntidade")) and isinstance(orgao, dict):
            data.setdefault("orgao_cnpj", orgao.get("cnpj"))
            data.setdefault("orgao_nome", orgao.get("razaoSocial"))

        if (unidade := data.get("unidadeOrgao")) and isinstance(unidade, dict):
            data.setdefault("orgao_uf", unidade.get("ufSigla"))
            data.setdefault("unidade_nome", unidade.get("nomeUnidade"))

        return data

    def __repr__(self) -> str:
        return (
            f"Contratacao(numero={self.numero_compra}, "
            f"orgao={self.orgao_nome}, "
            f"modalidade={self.modalidade_nome})"
        )


# --------------------------------------------------------------------------- #
#  Ata de Registro de Preço — AtaRegistroPrecoPeriodoDTO
# --------------------------------------------------------------------------- #


class Ata(BaseModel):
    """Ata de Registro de Preço (AtaRegistroPrecoPeriodoDTO)."""

    numero_ata_registro_preco: str = Field(default="", alias="numeroAtaRegistroPreco")
    ano_ata: int = Field(default=0, alias="anoAta")
    numero_controle_pncp_ata: str | None = Field(
        default=None, alias="numeroControlePNCPAta"
    )
    numero_controle_pncp_compra: str | None = Field(
        default=None, alias="numeroControlePNCPCompra"
    )
    objeto_contratacao: str = Field(default="", alias="objetoContratacao")
    situacao: str | None = None
    cancelado: bool | None = None
    possibilidade_adesao: bool | None = Field(default=None, alias="possibilidadeAdesao")

    # Órgão (já vem em campo plano no JSON: cnpjOrgao, nomeOrgao)
    orgao_cnpj: str | None = Field(default=None, alias="cnpjOrgao")
    orgao_nome: str | None = Field(default=None, alias="nomeOrgao")
    orgao_uf: str | None = None
    unidade_nome: str | None = None

    # Datas
    data_assinatura: datetime | None = Field(default=None, alias="dataAssinatura")
    vigencia_inicio: datetime | None = Field(default=None, alias="vigenciaInicio")
    vigencia_fim: datetime | None = Field(default=None, alias="vigenciaFim")
    data_publicacao_pncp: datetime | None = Field(
        default=None, alias="dataPublicacaoPncp"
    )
    data_atualizacao_global: datetime | None = Field(
        default=None, alias="dataAtualizacaoGlobal"
    )

    model_config = {"populate_by_name": True, "extra": "ignore"}

    def __repr__(self) -> str:
        return f"Ata(numero={self.numero_ata_registro_preco}, orgao={self.orgao_nome})"
