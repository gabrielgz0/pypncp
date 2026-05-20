# Preços homologados

A API de integração do PNCP expõe os **preços efetivamente pagos** pela
administração pública, com fornecedor, CNPJ e data de homologação — dados
essenciais para pesquisa de preços em licitações.

> **Atenção:** esta API **não é documentada oficialmente** — foi mapeada
> por engenharia reversa do portal. Use com ciência de que pode mudar.

## Endpoints

| Método | Descrição |
|--------|-----------|
| `precos.get_items(orgao, ano, compra)` | Itens de uma compra |
| `precos.get_resultados(orgao, ano, compra, item)` | Preços homologados de um item |
| `precos.buscar_precos(q, ...)` | Pipeline completo: busca → itens → preços |

## Exemplos

```python
from pypncp import PNCPClient

async with PNCPClient() as client:
    # Itens de uma compra específica
    itens = await client.precos.get_items(
        orgao="78680337000770", ano=2024, compra=128
    )
    for item in itens:
        print(item.descricao, item.valor_unitario_estimado)

    # Preços homologados de um item
    resultados = await client.precos.get_resultados(
        orgao="78680337000770", ano=2024, compra=128, item=1
    )
    for r in resultados:
        print(r.fornecedor_nome, r.cnpj, r.valor_unitario_homologado)
```

## Pipeline completo (buscar_precos)

Combina busca no catálogo, itens e preços homologados em um iterador só:

```python
async for preco in client.precos.buscar_precos(
    q="dipirona",
    tipos_documento="edital",
    uf="SP",
):
    print(
        f"{preco['descricao']} | "
        f"{preco['fornecedor']} ({preco['cnpj']}) | "
        f"R$ {preco['valor_unitario']}"
    )
```

### Controle de rate limit

O parâmetro `delay` (padrão `1.0`) insere uma pausa entre compras para
evitar sobrecarregar a API:

```python
async for preco in client.precos.buscar_precos(
    q="dipirona",
    tipos_documento="edital",
    uf="SP",
    delay=2.0,         # pausa de 2s entre cada compra
    max_compras=5,     # limita o total de compras processadas
):
    ...
```

> O `buscar_precos` utiliza `delay` entre compras combinado com **retry
> automático com exponential backoff** no HTTP client para 429 (Too Many
> Requests) — veja [Tratamento de erros](../errors.md).

## Parâmetros do `buscar_precos`

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `q` | `str` | — | Termo de busca |
| `tipos_documento` | `str` | `"edital"` | Tipo de documento |
| `ano` | `int \| None` | `None` | Filtrar por ano |
| `ordenacao` | `str \| None` | `"-data"` | Ordenação |
| `status` | `str \| None` | `"encerradas"` | Status das compras |
| `uf` | `str \| None` | `None` | Filtrar por UF |
| `tam_pagina_search` | `int` | `50` | Itens por página na busca |
| `max_compras` | `int` | `20` | Máximo de compras a processar |
| `paginas_itens` | `int` | `3` | Páginas de itens por compra |
| `delay` | `float` | `1.0` | Pausa (s) entre compras |
| `prefetch` | `int` | `1` | Workers de prefetch na busca |
