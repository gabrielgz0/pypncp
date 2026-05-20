# Contratos

Recurso para consulta de contratos do PNCP.

Datas aceitas como `str "YYYYMMDD"`, `str "YYYY-MM-DD"` ou `date`.

## Endpoints

| Método | Descrição |
|--------|-----------|
| `contratos.list(data_inicial, data_final, pagina, tam_pagina)` | Lista contratos por período |
| `contratos.list_all(data_inicial, data_final, ...)` | Itera todas as páginas (automático) |
| `contratos.get(orgao_cnpj, ano, sequencial)` | Contrato específico |
| `contratos.list_por_atualizacao(data_inicial, data_final, pagina)` | Contratos atualizados no período |
| `contratos.list_all_por_atualizacao(data_inicial, data_final, ...)` | Itera todas as páginas de atualizações |

## Exemplos

```python
from datetime import date
from pypncp import PNCPClient

async with PNCPClient() as client:
    # Listagem manual
    page = await client.contratos.list(
        data_inicial="20250101",
        data_final="20250331",
        pagina=1,
    )
    for contrato in page.data:
        print(contrato.numero_contrato_empenho, contrato.valor_global)

    # Paginação automática
    async for c in client.contratos.list_all(
        data_inicial=date(2025, 1, 1),
        data_final=date(2025, 3, 31),
    ):
        print(c.objeto_contrato, c.orgao_nome)

    # Contrato específico
    contrato = await client.contratos.get(
        orgao_cnpj="00394502000123",
        ano=2024,
        sequencial=1,
    )
    print(contrato.objeto_contrato)
```

## Parâmetros

### `list()` e `list_all()`

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `data_inicial` | `str \| date` | sim | Início do período |
| `data_final` | `str \| date` | sim | Fim do período |
| `pagina` | `int` | não | Padrão 1 (apenas `list`) |
| `tam_pagina` | `int` | não | Padrão 50 |
| `prefetch` | `int` | não | Workers de prefetch (apenas `list_all`) |

### `get()`

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `orgao_cnpj` | `str` | sim | CNPJ do órgão |
| `ano` | `int` | sim | Ano do contrato |
| `sequencial` | `int` | sim | Sequencial do contrato |
