"""pypncp — Cliente Python assíncrono para a API de Consulta do PNCP.

API pública — apenas o que está em __all__ é suportado por semver.

Uso básico:
    from pypncp import PNCPClient

    async with PNCPClient() as client:
        async for contrato in client.contratos.list_all(
            data_inicial="2024-01-01",
            data_final="2024-12-31",
        ):
            print(contrato.objeto_contrato)
"""

from .client import PNCPClient
from .exceptions import (
    AuthError,
    NotFoundError,
    PNCPError,
    RateLimitError,
    ServerError,
    ValidationError,
)

__all__ = [
    "PNCPClient",
    "PNCPError",
    "NotFoundError",
    "AuthError",
    "RateLimitError",
    "ServerError",
    "ValidationError",
]
