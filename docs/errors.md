# Tratamento de erros

## Hierarquia de exceções

```
PNCPError (base)
├── AuthError              (401, 403)
├── NotFoundError          (404)
├── RateLimitError         (429)
├── ServerError            (500+)
└── ValidationError        (outros)
```

## Exemplo

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

## Retry automático

O `HttpClient` aplica **exponential backoff** com tenacity nas seguintes
exceções:

- `httpx.TimeoutException`
- `httpx.ConnectError`
- `httpx.RemoteProtocolError`
- `RateLimitError` (429)

Ou seja, se a API retornar 429 (Too Many Requests), o cliente espera 1s,
depois 2s, depois 4s (até 10s) e tenta novamente, até 3 tentativas.

Esse comportamento é combinado com o parâmetro `delay` do
[`buscar_precos()`](resources/precos.md), que insere uma pausa entre
compras para evitar que o rate limit seja atingido.
