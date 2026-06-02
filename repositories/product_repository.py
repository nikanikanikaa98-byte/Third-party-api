import sqlite3


class ProductRepository:

    def __init__(self, database_path: str) -> None:
        self.database_path = database_path

    def create_table(self) -> None:

        connection = sqlite3.connect(self.database_path)

        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                category TEXT,
                brand TEXT,
                price REAL NOT NULL,
                discount_percentage REAL,
                rating REAL,
                stock INTEGER
            )
            """
        )
    
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_products_stock
            ON products(stock)
            """
        )
        connection.commit()
        connection.close()

    def save_products(
        self,
        products: list[dict],
    ) -> None:

        connection = sqlite3.connect(self.database_path)

        cursor = connection.cursor()

        for product in products:
            cursor.execute(
                """
                INSERT OR REPLACE INTO products (
                    id,
                    title,
                    category,
                    brand,
                    price,
                    discount_percentage,
                    rating,
                    stock
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    product["id"],
                    product["title"],
                    product["category"],
                    product["brand"],
                    product["price"],
                    product["discountPercentage"],
                    product["rating"],
                    product["stock"],
                ),
            )

        connection.commit()
        connection.close()

    def get_all_products(self) -> list[tuple]:

        connection = sqlite3.connect(self.database_path)

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM products
            """
        )

        products = cursor.fetchall()

        connection.close()

        return products

    def get_low_stock_products(
    
        self,
        threshold: int,
        ) -> list[tuple]:

        connection = sqlite3.connect(self.database_path)

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM products
            WHERE stock <= ?
            """,
            (threshold,),
        )

        products = cursor.fetchall()

        connection.close()

        return products