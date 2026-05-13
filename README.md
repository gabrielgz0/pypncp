# pypncp

![PyPI](https://img.shields.io/pypi/v/pypncp) ![Python Version](https://img.shields.io/pypi/pyversions/pypncp) ![License](https://img.shields.io/pypi/l/pypncp)

**Cliente Python assíncrono para a API de Consulta do PNCP** — Portal Nacional de Contratações Públicas.

---

## Como usar

### Adicionar ao projeto

Com `uv` (recomendado):

```bash
uv add pypncp
```

Com `pip`:

```bash
pip install pypncp
```

Ou direto no `pyproject.toml`:

```toml
[project]
dependencies = [
    "pypncp>=0.1",
]
```

### Criar o cliente

O cliente é a entrada única para a API. Use `async with` pra gerenciar o ciclo de vida:

```python
from pypncp import PNCPClient


async def buscar_dados():
    async with PNCPClient() as client:
        # client está pronto — usa os resources abaixo
        ...

# Fora de async def, use asyncio.run():
# asyncio.run(buscar_dados())
```

### Exemplos por recurso

**Contratos** — busque contratos por período de publicação:

```python
async with PNCPClient() as client:
    # Uma página
    page = await client.contratos.list(
        data_inicial="2025-01-01",
        data_final="2025-03-31",
    )
    for contrato in page.data:
        print(contrato.numero_contrato_empenho, contrato.valor_global)

    # Todas as páginas (paginação automática)
    async for contrato in client.contratos.list_all(
        data_inicial="2025-01-01",
        data_final="2025-03-31",
    ):
        print(contrato.objeto_contrato)
```

**Contratações (licitações)** — filtre por modalidade (código 1 = pregão):

```python
async with PNCPClient() as client:
    async for compra in client.contratacoes.list_all_publicacao(
        data_inicial="2025-01-01",
        data_final="2025-03-31",
        codigo_modalidade=1,  # 1 = Pregão
    ):
        print(compra.objeto_compra, compra.orgao_nome)

    # Com propostas abertas (apenas data_final)
    async for compra in client.contratacoes.list_all_com_proposta(
        data_final="2025-12-31",
    ):
        print(compra.objeto_compra, compra.data_abertura_proposta)
```

**Atas de registro de preço:**

```python
async with PNCPClient() as client:
    async for ata in client.atas.list_all(
        data_inicial="2025-01-01",
        data_final="2025-12-31",
    ):
        print(ata.objeto_contratacao, ata.orgao_nome)
```

### Paginação

```python
# Automática — use list_all*() (async generator)
async for contrato in client.contratos.list_all(
    data_inicial="2025-01-01",
    data_final="2025-12-31",
):
    ...


# Manual — use list() e controle a página
page = await client.contratos.list(
    data_inicial="2025-01-01",
    data_final="2025-12-31",
    pagina=1,
)
print(f"Página {page.numero_pagina} de {page.total_paginas}")
print(f"Itens nesta página: {len(page.data)}")

# Propriedades úteis de Page[T]:
#   page.data        → list[T]
#   page.numero_pagina
#   page.total_paginas
#   page.has_more    → True se há mais páginas
```

### Tratamento de erros

Todas as exceções herdam de `PNCPError` — nunca vazam exceções de transporte:

```python
from pypncp import PNCPError, NotFoundError, RateLimitError

try:
    page = await client.contratos.list(
        data_inicial="2025-01-01",
        data_final="2025-12-31",
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
from fastapi import FastAPI, HTTPException
from pypncp import PNCPClient, NotFoundError

app = FastAPI()


@app.get("/contratos")
async def listar_contratos(
    data_inicial: str,
    data_final: str,
    pagina: int = 1,
):
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
                orgao_cnpj=orgao_cnpj,
                ano=ano,
                sequencial=sequencial,
            )
            return contrato.model_dump()
        except NotFoundError:
            raise HTTPException(status_code=404, detail="Contrato não encontrado")
```

---

## Para contribuir

### Requisitos

- Python **3.12+**
- [uv](https://docs.astral.sh/uv/) — gerenciador de projetos e pacotes

```bash
uv sync
```

### Rodar verificações

```bash
git clone https://github.com/gabrielgz0/pypncp
cd pypncp
uv sync           # instala tudo — dev deps inclusas
uv run pytest -v  # tests
uv run ruff check src/ tests/
uv run mypy src/
```

### Licença

MIT
