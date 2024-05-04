from typing import Optional, List
from time import sleep
import requests

from app.config import HEALTHCHECK_TIMEOUT, HEALTHCHECK_SLEEP


class Readiness:
    """Class that handles /readiness endpoint."""

    urls: Optional[List[str]] = None

    def __init__(
        self,
        urls: List[str],
    ) -> None:
        """
        :param urls: list of service urls to check.
        :param task: list of futures or coroutines
        :param client: HTTPClient object.
        """

        Readiness.urls = urls or []
        Readiness.status = False

    @classmethod
    def _make_request(cls, url: str) -> None:
        """Check readiness of the specified service."""

        while True:
            try:
                response = requests.get(url=f"{url}", timeout=HEALTHCHECK_TIMEOUT)
                if response.status_code:
                    break

            except Exception as e:
                pass

            sleep(HEALTHCHECK_SLEEP)


    @classmethod
    def _check_readiness(cls) -> None:
        """Check readiness of all services."""

        print(
            f"Running readiness checks.",
        )
        [cls._make_request(url) for url in cls.urls or []]

        print(f"Successfully finished readiness checks.",)

    @classmethod
    def run(cls) -> None:
        cls._check_readiness()
