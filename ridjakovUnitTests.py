import unittest
import mysql.connector
from unittest.mock import patch
from io import StringIO
from repair_shop_manager import RepairShopManager
from admin_manager import AdminManager
from database_config import DatabaseConfig

class TestCarRepairApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = DatabaseConfig.connect_db()
        cls.cursor = cls.conn.cursor()
        cls.cursor.execute("DELETE FROM shop_ratings")
        cls.cursor.execute("DELETE FROM repair_shops")
        cls.cursor.execute("DELETE FROM users")
        cls.cursor.execute("""
        INSERT INTO users (id, username, email, password, car_brand, car_model, car_year)
        VALUES (1, 'test_user', 'test@example.com', 'hashed_password', 'Toyota', 'Corolla', 2020)
        """)
        cls.cursor.execute("""
        INSERT INTO repair_shops (id, username, email, password, location, specialization, 
                                oil_change_price, water_pump_price, belt_change_price, 
                                pulleys_price, filter_change_price,
                                oil_change_time, water_pump_time, belt_change_time,
                                pulleys_time, filter_change_time, user_rating)
        VALUES (1, 'shop1', 'shop1@example.com', 'hashed_password', 'Sofia', 'Toyota,Honda',
                50.00, 150.00, 100.00, 200.00, 30.00,
                30, 90, 60, 120, 20, 4.5),
               (2, 'shop2', 'shop2@example.com', 'hashed_password', 'Sofia', 'Toyota,BMW',
                40.00, 140.00, 90.00, 180.00, 25.00,
                25, 80, 50, 100, 15, 4.0)
        """)
        cls.conn.commit()

    @classmethod
    def tearDownClass(cls):
        cls.cursor.execute("DELETE FROM shop_ratings")
        cls.cursor.execute("DELETE FROM repair_shops")
        cls.cursor.execute("DELETE FROM users")
        cls.conn.commit()
        cls.cursor.close()
        cls.conn.close()

    def test_sort_repair_shops_by_price(self):
        user = {'id': 1, 'username': 'test_user', 'car_brand': 'Toyota'}
        with patch('builtins.input', side_effect=['Sofia', '1', '1']), patch('sys.stdout', new=StringIO()) as fake_out:
            RepairShopManager.list_repair_shops(user)
            output = fake_out.getvalue()
            shop1_index = output.find('shop1')
            shop2_index = output.find('shop2')
            self.assertTrue(shop2_index < shop1_index)

    def test_sort_repair_shops_by_time(self):
        user = {'id': 1, 'username': 'test_user', 'car_brand': 'Toyota'}
        with patch('builtins.input', side_effect=['Sofia', '3', '1']), patch('sys.stdout', new=StringIO()) as fake_out:
            RepairShopManager.list_repair_shops(user)
            output = fake_out.getvalue()
            shop1_index = output.find('shop1')
            shop2_index = output.find('shop2')
            self.assertTrue(shop2_index < shop1_index)

    def test_admin_query_users_by_car_brand(self):
        with patch('builtins.input', side_effect=['1', 'Toyota', '14']), patch('sys.stdout', new=StringIO()) as fake_out:
            AdminManager.admin_queries()
            output = fake_out.getvalue()
            self.assertIn("Users with Toyota: 1", output)

    def test_admin_query_repair_shops_by_location(self):
        with patch('builtins.input', side_effect=['2', 'Sofia', '14']), patch('sys.stdout', new=StringIO()) as fake_out:
            AdminManager.admin_queries()
            output = fake_out.getvalue()
            self.assertIn("Repair shops in Sofia: 2", output)

    def test_admin_query_average_service_prices(self):
        with patch('builtins.input', side_effect=['3', '14']), patch('sys.stdout', new=StringIO()) as fake_out:
            AdminManager.admin_queries()
            output = fake_out.getvalue()
            self.assertIn("Average prices: {'oil': Decimal('45.00'), 'water_pump': Decimal('145.00'), 'belt': Decimal('95.00'), 'pulleys': Decimal('190.00'), 'filter': Decimal('27.50')}", output)

    def test_admin_query_highest_service_prices(self):
        with patch('builtins.input', side_effect=['4', '14']), patch('sys.stdout', new=StringIO()) as fake_out:
            AdminManager.admin_queries()
            output = fake_out.getvalue()
            self.assertIn("Highest prices: {'oil': Decimal('50.00'), 'water_pump': Decimal('150.00'), 'belt': Decimal('100.00'), 'pulleys': Decimal('200.00'), 'filter': Decimal('30.00')}", output)

    def test_admin_query_lowest_service_prices(self):
        with patch('builtins.input', side_effect=['5', '14']), patch('sys.stdout', new=StringIO()) as fake_out:
            AdminManager.admin_queries()
            output = fake_out.getvalue()
            self.assertIn("Lowest prices: {'oil': Decimal('40.00'), 'water_pump': Decimal('140.00'), 'belt': Decimal('90.00'), 'pulleys': Decimal('180.00'), 'filter': Decimal('25.00')}", output)

    def test_admin_query_most_popular_car_brand(self):
        with patch('builtins.input', side_effect=['6', '14']), patch('sys.stdout', new=StringIO()) as fake_out:
            AdminManager.admin_queries()
            output = fake_out.getvalue()
            self.assertIn("Most popular car brand: Toyota (1 users)", output)

    def test_admin_query_highest_rated_shop(self):
        with patch('builtins.input', side_effect=['7', '14']), patch('sys.stdout', new=StringIO()) as fake_out:
            AdminManager.admin_queries()
            output = fake_out.getvalue()
            self.assertIn("Highest rated shop: shop1 (4.5 stars)", output)

    def test_admin_query_lowest_rated_shop(self):
        with patch('builtins.input', side_effect=['8', '14']), patch('sys.stdout', new=StringIO()) as fake_out:
            AdminManager.admin_queries()
            output = fake_out.getvalue()
            self.assertIn("Lowest rated shop: shop2 (4.0 stars)", output)

    def test_admin_query_average_rating_by_location(self):
        with patch('builtins.input', side_effect=['9', 'Sofia', '14']), patch('sys.stdout', new=StringIO()) as fake_out:
            AdminManager.admin_queries()
            output = fake_out.getvalue()
            self.assertIn("Average rating in Sofia: 4.2 stars", output)

    def test_admin_query_average_service_times(self):
        with patch('builtins.input', side_effect=['10', '14']), patch('sys.stdout', new=StringIO()) as fake_out:
            AdminManager.admin_queries()
            output = fake_out.getvalue()
            self.assertIn("Average times (minutes): {'oil': Decimal('27.5'), 'water_pump': Decimal('85.0'), 'belt': Decimal('55.0'), 'pulleys': Decimal('110.0'), 'filter': Decimal('17.5')}", output)

if __name__ == '__main__':
    unittest.main()