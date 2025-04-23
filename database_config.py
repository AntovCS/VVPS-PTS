import mysql.connector

class DatabaseConfig:
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '1298',
        'database': 'car_repair_app',
        'port': 3307
    }

    @staticmethod
    def connect_db():
        try:
            return mysql.connector.connect(**DatabaseConfig.db_config)
        except mysql.connector.Error as err:
            print(f"Database connection error: {err}")
            return None