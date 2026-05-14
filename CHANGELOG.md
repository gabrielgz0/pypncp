# Changelog

## v1.0.0 (2026-05-13)

- API estável — Facade + Resource pattern completo
- Novos recursos: busca no catálogo (`client.search.query`) e preços homologados (`client.precos`)
- `SearchResult.get_resultados()` — fetch lazy de preços com fornecedor e CNPJ
- `buscar_precos()` — pipeline completo: busca → itens → preços homologados
- Prefetch com N workers concorrentes em todas as `list_all*`
- Modelos: `SearchResult`, `ItemCompra`, `ResultadoItem`
- 69 testes, 91% cobertura, mypy strict (13 fontes)

## v0.1.3 (2026-05-13)

- Corrige badge Python Version no PyPI (classifiers)
- Adiciona `[build-system]` ao pyproject.toml

## v0.1.2 (2026-05-13)

- Normalização de datas para yyyyMMdd em todos os resources
- `orgao_nome` extraído de `orgaoEntidade` aninhado
- `Page.__aiter__` — `async for item in page:`

## v0.1.1 (2025-05-13)

- Adicionados classifiers Python 3.12/3.13 ao pyproject.toml
- Adicionado `[build-system]` ao pyproject.toml

## v0.1.0 (2025-05-13)

- Primeira release
- Recursos: contratos, contratações, atas
- Paginação automática (list_all)
- Retry com exponential backoff via tenacity
- Modelos Pydantic tipados
- Context manager, Builder, DI
- Hierarquia de exceções própria
- 44 testes, 91% cobertura
