from abc import ABC, abstractmethod
from typing import Any


class BaseConnector(ABC):

    @abstractmethod
    def fetch_products(self) -> list[dict[str, Any]]:
        pass