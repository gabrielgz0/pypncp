# Contratações (licitações)

Recurso para consulta de contratações/licitações do PNCP.

`codigo_modalidade` é obrigatório em `list_publicacao` e `list_atualizacao`,
opcional em `list_com_proposta`.

## Endpoints

| Método | Descrição |
|--------|-----------|
| `contratacoes.list_publicacao(...)` | Publicações de contratações |
| `contratacoes.list_all_publicacao(...)` | Itera todas as publicações |
| `contratacoes.list_com_proposta(...)` | Contratações com proposta aberta |
| `contratacoes.list_all_com_proposta(...)` | Itera todas com proposta aberta |
| `contratacoes.list_atualizacao(...)` | Contratações atualizadas |
| `contratacoes.list_all_atualizacao(...)` | Itera todas as atualizações |
| `contratacoes.get(orgao_cnpj, ano, sequencial)` | Contratação específica |

## Exemplos

```python
from datetime import date
from pypncp import PNCPClient

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
        codigo_modalidade=5,  # Diálogo Competitivo
    ):
        ...
```

## Parâmetros

### `list_publicacao()` / `list_all_publicacao()`

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `data_inicial` | `str \| date` | sim | Início do período |
| `data_final` | `str \| date` | sim | Fim do período |
| `codigo_modalidade` | `int` | **sim** | Código da modalidade |
| `pagina` | `int` | não | Padrão 1 |
| `tam_pagina` | `int` | não | Padrão 50 |

### `list_com_proposta()` / `list_all_com_proposta()`

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `data_final` | `str \| date` | sim | Data limite (>= hoje) |
| `codigo_modalidade` | `int \| None` | não | Filtrar por modalidade |
| `pagina` | `int` | não | Padrão 1 |
| `tam_pagina` | `int` | não | Padrão 50 |

### `list_atualizacao()` / `list_all_atualizacao()`

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `data_inicial` | `str \| date` | sim | Início do período |
| `data_final` | `str \| date` | sim | Fim do período |
| `codigo_modalidade` | `int` | **sim** | Código da modalidade |
| `pagina` | `int` | não | Padrão 1 |
| `tam_pagina` | `int` | não | Padrão 50 |

## Códigos de modalidade

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
