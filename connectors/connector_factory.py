from connectors.dummyjson_connector import DummyJsonConnector
from connectors.mock_connector import MockConnector


class ConnectorFactory:

    @staticmethod
    def create(
        connector_type: str,
        **kwargs,
    ):

        if connector_type == "dummyjson":
            return DummyJsonConnector(**kwargs)

        if connector_type == "mock":
            return MockConnector()

        raise ValueError(
            f"Unsupported connector type: {connector_type}"
        )