from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import httpx


class HarvestError(Exception):
    """A non-success response from the Harvest API."""

    def __init__(self, status: int, message: str) -> None:
        super().__init__(f"{status}: {message}")
        self.status = status
        self.message = message


class BadRequestError(HarvestError):
    pass


class UnauthorizedError(HarvestError):
    pass


class ForbiddenError(HarvestError):
    pass


class NotFoundError(HarvestError):
    pass


class UnprocessableError(HarvestError):
    pass


class RateLimitedError(HarvestError):
    def __init__(
        self, status: int, message: str, *, retry_after: float | None = None
    ) -> None:
        super().__init__(status, message)
        self.retry_after = retry_after
        """Seconds Harvest asked the client to wait, from ``Retry-After``."""


class ServerError(HarvestError):
    pass


_BY_STATUS: dict[int, type[HarvestError]] = {
    400: BadRequestError,
    401: UnauthorizedError,
    403: ForbiddenError,
    404: NotFoundError,
    422: UnprocessableError,
    429: RateLimitedError,
}


def _message(response: httpx.Response) -> str:
    # Measured: 400/403/422 carry "message", 401 "error_description"
    # (OAuth style), 404 only "error".
    try:
        body = response.json()
    except ValueError:
        return response.text or response.reason_phrase
    if isinstance(body, dict):
        for key in ("message", "error_description", "error"):
            value = body.get(key)
            if isinstance(value, str):
                return value
    return response.text


def error_for(response: httpx.Response) -> HarvestError:
    status = response.status_code
    if status == 429:
        return RateLimitedError(
            status, _message(response), retry_after=retry_after(response)
        )
    cls = _BY_STATUS.get(status, ServerError if status >= 500 else HarvestError)
    return cls(status, _message(response))


def retry_after(response: httpx.Response) -> float | None:
    try:
        return float(response.headers["Retry-After"])
    except (KeyError, ValueError):
        return None
