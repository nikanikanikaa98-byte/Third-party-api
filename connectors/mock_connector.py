from connectors.base_connector import BaseConnector


class MockConnector(BaseConnector):

    def fetch_products(self):

        return [
            {
                "id": 1001,
                "title": "Mock Product",
                "category": "test",
                "brand": "Mock",
                "price": 100,
                "discountPercentage": 0,
                "rating": 5,
                "stock": 10,
            }
        ]