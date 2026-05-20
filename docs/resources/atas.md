# Atas

Recurso para consulta de atas de registro de preço do PNCP.

## Endpoints

| Método | Descrição |
|--------|-----------|
| `atas.list(data_inicial, data_final, pagina, tam_pagina)` | Lista atas por período |
| `atas.list_all(data_inicial, data_final, ...)` | Itera todas as páginas |
| `atas.list_por_atualizacao(data_inicial, data_final, pagina)` | Atas atualizadas |
| `atas.list_all_por_atualizacao(data_inicial, data_final, ...)` | Itera todas as atualizações |

## Exemplos

```python
from datetime import date
from pypncp import PNCPClient

async with PNCPClient() as client:
    async for ata in client.atas.list_all(
        data_inicial=date(2025, 1, 1),
        data_final=date(2025, 12, 31),
    ):
        print(ata.objeto_contratacao, ata.orgao_nome)
```

## Parâmetros

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `data_inicial` | `str \| date` | sim | Início do período |
| `data_final` | `str \| date` | sim | Fim do período |
| `pagina` | `int` | não | Padrão 1 |
| `tam_pagina` | `int` | não | Padrão 50 |
| `prefetch` | `int` | não | Workers de prefetch (apenas `list_all`) |
