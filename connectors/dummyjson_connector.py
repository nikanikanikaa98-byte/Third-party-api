import logging
from time import sleep
from typing import Any

import requests

from connectors.base_connector import BaseConnector


class DummyJsonConnector(BaseConnector):

    def __init__(
        self,
        api_url: str,
        timeout: float,
        retries: int,
        limit: int | None = None,
        skip: int | None = None,
    ) -> None:
        self.api_url = api_url
        self.timeout = timeout
        self.retries = retries
        self.limit = limit
        self.skip = skip

    def fetch_products(self) -> list[dict[str, Any]]:
        params = {}

        if self.limit is not None:
            params["limit"] = self.limit

        if self.skip is not None:
            params["skip"] = self.skip

        last_error = None

        for attempt in range(1, self.retries + 2):

            try:
                logging.info(
                    f"Fetching products from API. Attempt {attempt}."
                )

                response = requests.get(
                    self.api_url,
                    params=params,
                    timeout=self.timeout,
                )

                response.raise_for_status()

                data = response.json()

                if "products" not in data:
                    raise RuntimeError(
                        "Missing 'products' field in API response."
                    )

                products = data["products"]

                if not isinstance(products, list):
                    raise RuntimeError(
                        "'products' field is not a list."
                    )

                if not products:
                    raise RuntimeError(
                        "The API returned an empty product list."
                    )

                return products

            except requests.Timeout:
                last_error = (
                    f"Request timed out after {self.timeout} seconds."
                )

            except requests.HTTPError as error:
                last_error = (
                    f"API request failed with status code "
                    f"{response.status_code}: {error}"
                )

            except requests.RequestException as error:
                last_error = f"Request failed: {error}"

            except ValueError:
                last_error = "Invalid JSON response received from API."

            logging.warning(last_error)

            if attempt <= self.retries:
                logging.info("Retrying request in 1 second...")
                sleep(1)

        raise RuntimeError(last_error)