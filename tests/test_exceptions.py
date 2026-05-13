"""Testes da hierarquia de exceções."""

import pytest

from pypncp import (
    AuthError,
    NotFoundError,
    PNCPError,
    RateLimitError,
    ServerError,
    ValidationError,
)


class TestExceptionHierarchy:
    def test_pncp_error_is_base(self):
        assert issubclass(NotFoundError, PNCPError)
        assert issubclass(AuthError, PNCPError)
        assert issubclass(RateLimitError, PNCPError)
        assert issubclass(ServerError, PNCPError)
        assert issubclass(ValidationError, PNCPError)

    def test_catch_base_catches_all(self):
        exceptions = [
            NotFoundError("404"),
            AuthError("401"),
            RateLimitError("429"),
            ServerError("500"),
            ValidationError("bad request"),
        ]
        for exc in exceptions:
            with pytest.raises(PNCPError):
                raise exc

    def test_message_is_preserved(self):
        msg = "custom message"
        exc = NotFoundError(msg)
        assert str(exc) == msg
