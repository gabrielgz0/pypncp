# Busca no catálogo

```
GET https://pncp.gov.br/api/search/?q=<termo>&tipos_documento=<tipo>
```

> **Atenção:** esta API **não é documentada oficialmente** pelo PNCP — foi
> mapeada por engenharia reversa do portal. Use com ciência de que pode mudar
> sem aviso.

Ela faz busca **full-text** em todo o catálogo do PNCP (editais, contratos,
atas, avisos, etc.) e é especialmente útil para:

- **Coletas de preço** — encontre itens comprados por órgãos públicos
- **Pesquisa de mercado** — veja o que está sendo licitado em cada região
- **Monitoramento de concorrentes** — acompanhe atas e contratos por
  termo, UF, modalidade ou situação

## Endpoints

| Método | Descrição |
|--------|-----------|
| `search.query(q, tipos_documento, ...)` | Busca paginada |
| `search.query_all(q, tipos_documento, ...)` | Itera todos os resultados |
| `SearchResult.get_resultados()` | (lazy) Preços homologados do item |

## Exemplos

```python
from pypncp import PNCPClient

async with PNCPClient() as client:
    # Busca simples — resultados paginados
    page = await client.search.query(
        q="dipirona",
        tipos_documento="edital",
    )
    for item in page.data:
        print(item.title, item.orgao_nome, item.valor_global)

        # Fetch lazy: cada item pode buscar seus precos homologados
        resultados = await item.get_resultados()
        for r in resultados:
            print(r.fornecedor_nome, r.cnpj, r.valor_unitario_homologado)

    # Com filtros
    page = await client.search.query(
        q="notebook",
        tipos_documento="ata",
        status="encerradas",
        uf="SP",
        ordenacao="-data",
        pagina=1,
    )

    # Paginação automática — itera todos os resultados
    async for item in client.search.query_all(
        q="cadeira",
        tipos_documento="edital,contrato",
        uf="RJ",
    ):
        print(item.description, item.orgao_nome)
```

## Parâmetros

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `q` | `str` | sim | Termo de busca (produto, serviço, etc.) |
| `tipos_documento` | `str` | sim | `edital`, `contrato`, `ata` (ou separado por vírgula) |
| `pagina` | `int` | não | Padrão 1 |
| `tam_pagina` | `int` | não | Padrão 10 |
| `ordenacao` | `str` | não | `-data` (decrescente) ou `data` (crescente) |
| `status` | `str` | não | `encerradas`, `recebendo_proposta` |
| `uf` | `str` | não | Sigla da UF (`SP`, `RJ`, `MG`, etc.) |
| `municipio` | `str` | não | Código IBGE do município |
