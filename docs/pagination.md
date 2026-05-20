# Paginação

## Manual

O método `list()` devolve um `Page[T]` com metadados:

```python
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

## Automática

`list_all*()` itera **todas as páginas** com prefetch em background:

```python
async for contrato in client.contratos.list_all(
    data_inicial="20250101",
    data_final="20251231",
):
    ...
```

## Prefetch

Por padrão, `list_all*()` baixa a próxima página em background enquanto o
consumidor processa a página atual. O overlap entre I/O e processamento reduz
o tempo total sem mudar a API:

```
Sem prefetch (prefetch=0):
  fetch p1 ---> processa p1 ---> fetch p2 ---> processa p2 ---> ...

Com prefetch (prefetch=1, padrão):
  fetch p1 ---> processa p1 ---> processa p2 ---> ...
                  ^                  ^
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

## Workers concorrentes (`prefetch >= 2`)

Para acelerar ainda mais, vários workers baixam páginas em paralelo enquanto
o consumidor já está recebendo os dados. Cada worker faz um stride:
com `prefetch=4`, o worker 0 baixa as páginas 1, 5, 9… o worker 1 baixa
2, 6, 10… etc. Resultados fora de ordem são bufferizados e entregues na
sequência correta.

```
prefetch=4, 12 páginas:
worker 0: p1 ---+--- p5 ---+--- p9
worker 1: p2 ---+--- p6 ---+--- p10
worker 2: p3 ---+--- p7 ---+--- p11
worker 3: p4 ---+--- p8 ---+--- p12

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

> **Nota:** `prefetch` maior que o número de páginas total não acelera além
> do necessário. O ideal é `prefetch` igual ao número de páginas que cabem
> numa "rodada" de paralelismo.
