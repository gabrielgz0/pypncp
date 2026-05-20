# Quickstart

```bash
uv add pypncp          # com uv (recomendado)
pip install pypncp     # ou com pip
```

## Criar o cliente

```python
from pypncp import PNCPClient

async def main():
    async with PNCPClient() as client:
        ...  # client pronto
```

## Exemplos por recurso

### Contratos

```python
from datetime import date

async with PNCPClient() as client:
    # Listagem com paginação automática
    async for c in client.contratos.list_all(
        data_inicial=date(2025, 1, 1),
        data_final=date(2025, 3, 31),
    ):
        print(c.objeto_contrato, c.orgao_nome, c.valor_global)
```

### Contratações (licitações)

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

    # Propostas abertas — modalidade opcional
    async for compra in client.contratacoes.list_all_com_proposta(
        data_final=date.today(),
    ):
        print(compra.objeto_compra, compra.data_abertura_proposta)
```

### Atas

```python
from datetime import date

async with PNCPClient() as client:
    async for ata in client.atas.list_all(
        data_inicial=date(2025, 1, 1),
        data_final=date(2025, 12, 31),
    ):
        print(ata.objeto_contratacao, ata.orgao_nome)
```

### Busca no catálogo

```python
# Busca simples
page = await client.search.query(q="dipirona", tipos_documento="edital")
for item in page.data:
    print(item.title, item.orgao_nome, item.valor_global)

# Com filtros
page = await client.search.query(
    q="notebook",
    tipos_documento="ata",
    status="encerradas",
    uf="SP",
)

# Paginação automática
async for item in client.search.query_all(
    q="cadeira",
    tipos_documento="edital,contrato",
    uf="RJ",
):
    print(item.description, item.orgao_nome)
```

### Preços homologados

```python
# Itens de uma compra
itens = await client.precos.get_items(
    orgao="78680337000770", ano=2024, compra=128
)
for item in itens:
    print(item.descricao, item.valor_unitario_estimado)

# Pipeline completo: busca → preços homologados
async for preco in client.precos.buscar_precos(
    q="dipirona",
    tipos_documento="edital",
    uf="SP",
    max_compras=5,
):
    print(f"{preco['descricao']} | {preco['fornecedor']} | R$ {preco['valor_unitario']}")
```

## FastAPI

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
```

## Próximos passos

- [Paginação (`list_all*`, prefetch, workers)](pagination.md)
- [Contratos](resources/contratos.md)
- [Contratações](resources/contratacoes.md)
- [Atas](resources/atas.md)
- [Busca no catálogo](resources/search.md)
- [Preços homologados](resources/precos.md)
- [Modelos](models.md)
- [Tratamento de erros](errors.md)
- [Contribuindo](contributing.md)
