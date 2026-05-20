# pypncp

[![CI](https://github.com/gabrielgz0/pypncp/actions/workflows/ci.yml/badge.svg)](https://github.com/gabrielgz0/pypncp/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/pypncp)](https://pypi.org/project/pypncp/)
[![Python Version](https://img.shields.io/pypi/pyversions/pypncp)](https://pypi.org/project/pypncp/)
[![License](https://img.shields.io/pypi/l/pypncp)](https://pypi.org/project/pypncp/)
[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/gabrielgz0/.../raw/coverage.json)](https://github.com/gabrielgz0/pypncp/actions)

**Cliente Python assíncrono para a API de Consulta do PNCP** — Portal Nacional de Contratações Públicas.

```python
from pypncp import PNCPClient

async with PNCPClient() as client:
    async for p in client.precos.buscar_precos(
        q="dipirona",
        tipos_documento="edital",
        uf="SP",
    ):
        print(f"{p['descricao']} | {p['fornecedor']} | R$ {p['valor_unitario']}")
```

```bash
uv add pypncp
```

---

Documentação completa em [`docs/`](docs/quickstart.md):

| Seção | Descrição |
|-------|-----------|
| [Quickstart](docs/quickstart.md) | Instalação, exemplos básicos, FastAPI |
| [Paginação](docs/pagination.md) | `list_all*`, prefetch, workers concorrentes |
| **Recursos** | |
| [Contratos](docs/resources/contratos.md) | Consulta de contratos |
| [Contratações](docs/resources/contratacoes.md) | Licitações, publicações, propostas |
| [Atas](docs/resources/atas.md) | Atas de registro de preço |
| [Busca no catálogo](docs/resources/search.md) | Busca full-text em todo o PNCP |
| [Preços homologados](docs/resources/precos.md) | Pipeline busca → itens → preços |
| [Modelos](docs/models.md) | Todos os campos e tipos |
| [Erros](docs/errors.md) | Hierarquia de exceções, retry automático |
| [Contribuindo](docs/contributing.md) | Setup, testes, lint |

Documentação oficial: [Swagger da API PNCP](https://pncp.gov.br/api/pncp/swagger-ui/index.html)

Licença: MIT
