"""Hierarquia de exceções do PNCP Client.

Todas as exceções herdam de `PNCPError` — o usuário pode capturá-la
para tratar qualquer erro da lib sem vazar exceções de transporte (httpx, etc).
"""


class PNCPError(Exception):
    """Base exception para todos os erros do PNCP Client."""


class NotFoundError(PNCPError):
    """Recurso não encontrado (HTTP 404)."""


class AuthError(PNCPError):
    """Erro de autenticação/autorização (HTTP 401/403)."""


class RateLimitError(PNCPError):
    """Limite de requisições excedido (HTTP 429)."""


class ServerError(PNCPError):
    """Erro interno do servidor (HTTP 5xx)."""


class ValidationError(PNCPError):
    """Erro de validação de resposta ou de parâmetros."""
