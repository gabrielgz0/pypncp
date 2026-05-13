# pypncp

[![CI](https://github.com/gabrielgz0/pypncp/actions/workflows/ci.yml/badge.svg)](https://github.com/gabrielgz0/pypncp/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/pypncp)](https://pypi.org/project/pypncp/)
[![Python Version](https://img.shields.io/pypi/pyversions/pypncp)](https://pypi.org/project/pypncp/)
[![License](https://img.shields.io/pypi/l/pypncp)](https://pypi.org/project/pypncp/)
[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/gabrielgz0/.../raw/coverage.json)](https://github.com/gabrielgz0/pypncp/actions)

**Cliente Python assíncrono para a API de Consulta do PNCP** — Portal Nacional de Contratações Públicas.

---

## Como usar

### Adicionar ao projeto

```bash
uv add pypncp          # com uv (recomendado)
pip install pypncp     # ou com pip
```

Ou direto no `pyproject.toml`:

```toml
[project]
dependencies = ["pypncp>=0.1"]
```

### Criar o cliente

```python
from pypncp import PNCPClient

async def buscar():
    async with PNCPClient() as client:
        ...  # client pronto
```

### Exemplos por recurso

**Contratos** — datas aceitas como `str "YYYYMMDD"`, `str "YYYY-MM-DD"` ou `date`:

```python
from datetime import date

async with PNCPClient() as client:
    page = await client.contratos.list(
        data_inicial="20250101",       # ou date(2025, 1, 1)
        data_final="20250331",
    )
    for contrato in page.data:
        print(contrato.numero_contrato_empenho, contrato.valor_global)

    # Paginação automática
    async for c in client.contratos.list_all(
        data_inicial=date(2025, 1, 1),
        data_final=date(2025, 3, 31),
    ):
        print(c.objeto_contrato, c.orgao_nome)
```

**Contratações (licitações)** — `codigo_modalidade` é obrigatório em `list_publicacao` e `list_atualizacao`, opcional em `list_com_proposta`:

```python
from datetime import date

async with PNCPClient() as client:
    # Publicações — modalidade obrigatória (1 = Pregão)
    async for compra in client.contratacoes.list_all_publicacao(
        data_inicial=date(2025, 1, 1),
        data_final=date(2025, 3, 31),
        codigo_modalidade=1,
    ):
        print(compra.objeto_compra, compra.orgao_nome)

    # Propostas abertas — modalidade opcional, data_final >= hoje
    async for compra in client.contratacoes.list_all_com_proposta(
        data_final=date.today(),
    ):
        print(compra.objeto_compra, compra.data_abertura_proposta)

    # Atualizações — modalidade obrigatória
    async for compra in client.contratacoes.list_all_atualizacao(
        data_inicial=date(2025, 1, 1),
        data_final=date(2025, 3, 31),
        codigo_modalidade=5,
    ):
        ...
```

**Atas de registro de preço:**

```python
from datetime import date

async with PNCPClient() as client:
    async for ata in client.atas.list_all(
        data_inicial=date(2025, 1, 1),
        data_final=date(2025, 12, 31),
    ):
        print(ata.objeto_contratacao, ata.orgao_nome)
```

### Paginação

```python
# Automática — list_all*() itera todas as páginas com prefetch
async for contrato in client.contratos.list_all(
    data_inicial="20250101",
    data_final="20251231",
):
    ...

# Manual — list() devolve Page[T] com metadados
page = await client.contratos.list(
    data_inicial="20250101",
    data_final="20251231",
    pagina=1,
)
print(f"Página {page.numero_pagina} de {page.total_paginas}")
print(f"Itens nesta página: {len(page.data)}")
print(f"Há mais páginas: {page.has_more}")

# page pode ser usado como iterador assíncrono
async for item in page:
    print(item)
```

**Prefetch:** por padrão, `list_all*()` baixa a próxima página em background
enquanto o consumidor processa a página atual. O overlap entre I/O e
processamento reduz o tempo total sem mudar a API:

```
Sem prefetch (prefetch=0):
  fetch p1 —> processa p1 —> fetch p2 —> processa p2 —> ...

Com prefetch (prefetch=1, padrão):
  fetch p1 ──> processa p1 ──> processa p2 ──> ...
                 ↑                  ↑
           fetch p2 (bg)      fetch p3 (bg)
```

Para desligar o prefetch (comportamento estritamente sequencial):

```python
async for item in client.contratos.list_all(
    data_inicial="20250101",
    data_final="20251231",
    prefetch=0,
):
    ...
```

**N workers concorrentes (`prefetch >= 2`):** para acelerar ainda mais,
vários workers baixam páginas em paralelo enquanto o consumidor já está
recebendo os dados. Cada worker faz um stride: com `prefetch=4`, o worker
0 baixa as páginas 1, 5, 9… o worker 1 baixa 2, 6, 10… etc. Resultados
fora de ordem são bufferizados e entregues na sequência correta.

```
prefetch=4, 12 páginas:
worker 0: p1 ──┬─ p5 ──┬─ p9
worker 1: p2 ──┤─ p6 ──┤─ p10
worker 2: p3 ──┤─ p7 ──┤─ p11
worker 3: p4 ──┴─ p8 ──┴─ p12

Tempo: 3 rodadas × 300ms = 0.9s (vs 12 × 300ms = 3.6s sequencial)
```

```python
# 4 workers concorrentes — útil para coletores/scrappers
async for item in client.contratos.list_all(
    data_inicial="20250101",
    data_final="20251231",
    prefetch=4,
):
    ...
```

> **Nota:** `prefetch` maior que o número de páginas total não acelera
> além do necessário. O ideal é `prefetch` igual ao número de páginas
> que cabem numa "rodada" de paralelismo.

### Tratamento de erros

```python
from pypncp import PNCPError, NotFoundError, RateLimitError

try:
    page = await client.contratos.list(
        data_inicial="20250101",
        data_final="20251231",
    )
except NotFoundError:
    print("Recurso não encontrado (HTTP 404)")
except RateLimitError:
    print("Muitas requisições (HTTP 429)")
except PNCPError as e:
    print(f"Erro na API: {e}")
```

### Exemplo completo com FastAPI

```python
from datetime import date

from fastapi import FastAPI, HTTPException
from pypncp import PNCPClient, NotFoundError

app = FastAPI()


@app.get("/contratos")
async def listar_contratos(data_inicial: str, data_final: str, pagina: int = 1):
    async with PNCPClient() as client:
        page = await client.contratos.list(
            data_inicial=data_inicial,
            data_final=data_final,
            pagina=pagina,
        )
        return {
            "contratos": [c.model_dump() for c in page.data],
            "pagina": page.numero_pagina,
            "total_paginas": page.total_paginas,
            "total_registros": page.total_registros,
        }


@app.get("/contratos/{orgao_cnpj}/{ano}/{sequencial}")
async def get_contrato(orgao_cnpj: str, ano: int, sequencial: int):
    async with PNCPClient() as client:
        try:
            contrato = await client.contratos.get(
                orgao_cnpj=orgao_cnpj, ano=ano, sequencial=sequencial,
            )
            return contrato.model_dump()
        except NotFoundError:
            raise HTTPException(status_code=404, detail="Contrato não encontrado")
```

---

## Modelos

### Contrato

| Campo | Tipo | Origem na API |
|-------|------|---------------|
| `numero_contrato_empenho` | `str` | `numeroContratoEmpenho` |
| `ano_contrato` | `int` | `anoContrato` |
| `sequencial_contrato` | `int` | `sequencialContrato` |
| `objeto_contrato` | `str` | `objetoContrato` |
| `processo` | `str \| None` | `processo` |
| `orgao_cnpj` | `str \| None` | `orgaoEntidade.cnpj` |
| `orgao_nome` | `str \| None` | `orgaoEntidade.razaoSocial` |
| `orgao_uf` | `str \| None` | `unidadeOrgao.ufSigla` |
| `fornecedor_nome` | `str \| None` | `nomeRazaoSocialFornecedor` |
| `ni_fornecedor` | `str \| None` | `niFornecedor` |
| `valor_inicial` | `float \| None` | `valorInicial` |
| `valor_global` | `float \| None` | `valorGlobal` |
| `data_assinatura` | `date \| None` | `dataAssinatura` |
| `data_vigencia_inicio` | `date \| None` | `dataVigenciaInicio` |
| `data_vigencia_fim` | `date \| None` | `dataVigenciaFim` |
| `data_publicacao_pncp` | `datetime \| None` | `dataPublicacaoPncp` |

### Contratacao

| Campo | Tipo | Origem na API |
|-------|------|---------------|
| `numero_compra` | `str` | `numeroCompra` |
| `ano_compra` | `int` | `anoCompra` |
| `sequencial_compra` | `int` | `sequencialCompra` |
| `objeto_compra` | `str` | `objetoCompra` |
| `orgao_cnpj` | `str \| None` | `orgaoEntidade.cnpj` |
| `orgao_nome` | `str \| None` | `orgaoEntidade.razaoSocial` |
| `orgao_uf` | `str \| None` | `unidadeOrgao.ufSigla` |
| `modalidade_nome` | `str \| None` | `modalidadeNome` |
| `data_publicacao_pncp` | `datetime \| None` | `dataPublicacaoPncp` |
| `data_abertura_proposta` | `datetime \| None` | `dataAberturaProposta` |
| `valor_total_estimado` | `float \| None` | `valorTotalEstimado` |
| `valor_total_homologado` | `float \| None` | `valorTotalHomologado` |
| `srp` | `bool \| None` | `srp` |

### Ata

| Campo | Tipo | Origem na API |
|-------|------|---------------|
| `numero_ata_registro_preco` | `str` | `numeroAtaRegistroPreco` |
| `ano_ata` | `int` | `anoAta` |
| `objeto_contratacao` | `str` | `objetoContratacao` |
| `orgao_cnpj` | `str \| None` | `cnpjOrgao` |
| `orgao_nome` | `str \| None` | `nomeOrgao` |
| `vigencia_inicio` | `datetime \| None` | `vigenciaInicio` |
| `vigencia_fim` | `datetime \| None` | `vigenciaFim` |
| `data_publicacao_pncp` | `datetime \| None` | `dataPublicacaoPncp` |
| `cancelado` | `bool \| None` | `cancelado` |
| `possibilidade_adesao` | `bool \| None` | `possibilidadeAdesao` |

---

## Códigos de Modalidade

| Código | Modalidade |
|--------|-----------|
| 1 | Pregão |
| 2 | Concorrência |
| 3 | Concurso |
| 4 | Leilão |
| 5 | Diálogo Competitivo |
| 6 | Consulta Pública |
| 7 | Credenciamento |
| 8 | Pré-qualificação |
| 9 | Manifestação de Interesse |
| 10 | Procedimento Auxiliar |
| 99 | Inexigibilidade |
| 100 | Dispensa |

---

## Referência da API

| Recurso | Endpoints |
|---------|-----------|
| `client.contratos` | `GET /v1/contratos`, `GET /v1/contratos/atualizacao`, `GET /orgaos/{cnpj}/compras/{ano}/{sequencial}` |
| `client.contratacoes` | `GET /v1/contratacoes/publicacao`, `GET /v1/contratacoes/proposta`, `GET /v1/contratacoes/atualizacao`, `GET /orgaos/{cnpj}/compras/{ano}/{sequencial}` |
| `client.atas` | `GET /v1/atas`, `GET /v1/atas/atualizacao` |

### Parâmetros obrigatórios por endpoint

| Método | Parâmetros obrigatórios |
|--------|------------------------|
| `contratos.list()` | `data_inicial`, `data_final` |
| `contratos.list_por_atualizacao()` | `data_inicial`, `data_final` |
| `contratacoes.list_publicacao()` | `data_inicial`, `data_final`, **`codigo_modalidade`** |
| `contratacoes.list_atualizacao()` | `data_inicial`, `data_final`, **`codigo_modalidade`** |
| `contratacoes.list_com_proposta()` | `data_final` |
| `atas.list()` | `data_inicial`, `data_final` |

Documentação oficial: [Swagger da API de Consulta](https://pncp.gov.br/api/consulta/swagger-ui/index.html)

---

## Para contribuir

### Requisitos

- Python **3.12+**
- [uv](https://docs.astral.sh/uv/)

```bash
uv sync
```

### Rodar verificações

```bash
git clone https://github.com/gabrielgz0/pypncp
cd pypncp
uv sync
uv run pytest -v
uv run ruff check src/ tests/
uv run mypy src/
```

### Licença

MIT
