"""HttpClient — camada de transporte com retry, autenticação e mapeamento de erros."""

from __future__ import annotations

import contextlib
from typing import Any

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from pypncp.exceptions import (
    AuthError,
    NotFoundError,
    PNCPError,
    RateLimitError,
    ServerError,
    ValidationError,
)

__all__ = ["HttpClient"]

_RETRYABLE = (
    httpx.TimeoutException,
    httpx.ConnectError,
    httpx.RemoteProtocolError,
)


class HttpClient:
    """Cliente HTTP assíncrono com suporte a:

    * Injeção de dependência (recebe ou cria httpx.AsyncClient)
    * Retry com exponential backoff via tenacity
    * Autenticação Bearer automática (opcional — API de Consulta é pública)
    * Mapeamento de erros HTTP para a hierarquia PNCPError
    * Métodos convenientes get/post/put/delete
    """

    def __init__(
        self,
        *,
        base_url: str = "https://pncp.gov.br/api/consulta/v1",
        timeout: int = 30,
        max_retries: int = 3,
        token: str | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._token = token
        self._max_retries = max_retries
        self._client = client or httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
        )

    # ------------------------------------------------------------------ #
    #  Métodos públicos conveniente
    # ------------------------------------------------------------------ #

    async def get(self, path: str, **kwargs: Any) -> Any:
        response = await self.request("GET", path, **kwargs)
        return response.json()

    async def post(self, path: str, **kwargs: Any) -> Any:
        response = await self.request("POST", path, **kwargs)
        return response.json()

    async def put(self, path: str, **kwargs: Any) -> Any:
        response = await self.request("PUT", path, **kwargs)
        return response.json()

    async def delete(self, path: str, **kwargs: Any) -> None:
        await self.request("DELETE", path)

    # ------------------------------------------------------------------ #
    #  Método central com retry
    # ------------------------------------------------------------------ #

    async def request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Executa uma requisição HTTP com retry e tratamento de erros."""
        url = self.base_url + path
        headers = kwargs.pop("headers", {})

        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        # Garante que params vazios/none sejam ignorados
        params = kwargs.pop("params", None)
        if params:
            params = {k: v for k, v in params.items() if v is not None}
            kwargs["params"] = params

        kwargs.setdefault("headers", headers)

        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(self._max_retries),
                wait=wait_exponential(min=1, max=10),
                retry=retry_if_exception_type(_RETRYABLE),
                reraise=True,
            ):
                with attempt:
                    response = await self._client.request(method, url, **kwargs)
                    self._raise_on_error(response)
        except _RETRYABLE as exc:
            raise PNCPError(
                f"Requisição falhou após {self._max_retries} tentativas: {exc}"
            ) from exc

        return response

    # ------------------------------------------------------------------ #
    #  Mapeamento de erros
    # ------------------------------------------------------------------ #

    @staticmethod
    def _raise_on_error(response: httpx.Response) -> None:
        """Mapeia status code HTTP para a hierarquia PNCPError."""
        if response.status_code < 400:
            return

        body: dict[str, Any] = {}
        with contextlib.suppress(Exception):
            body = response.json()

        message = (
            body.get("message") or body.get("titulo") or response.reason_phrase or ""
        )

        if response.status_code in (401, 403):
            raise AuthError(message)
        if response.status_code == 404:
            raise NotFoundError(message)
        if response.status_code == 429:
            raise RateLimitError(message or "Rate limit exceeded")
        if response.status_code >= 500:
            raise ServerError(
                f"Erro interno do servidor ({response.status_code}): {message}"
            )

        raise ValidationError(f"Erro inesperado {response.status_code}: {message}")

    # ------------------------------------------------------------------ #
    #  Lifecycle
    # ------------------------------------------------------------------ #

    async def aclose(self) -> None:
        await self._client.aclose()
