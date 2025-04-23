import unittest
from unittest.mock import MagicMock, patch
from io import StringIO
import sys
from database_config import DatabaseConfig
from repair_shop_manager import RepairShopManager

class TestRepairShopManager(unittest.TestCase):
   
    def setUp(self):
        self.held_output = StringIO()  
        sys.stdout = self.held_output   

      
        self.mock_shops = [
            {
                "username": "Shop1", "location": "Sofia", "user_rating": 4.5,
                "specialization": "Toyota,Honda",
                "oil_change_price": 50, "water_pump_price": 200, "belt_change_price": 150,
                "pulleys_price": 100, "filter_change_price": 80,
                "oil_change_time": 30, "water_pump_time": 120, "belt_change_time": 90,
                "pulleys_time": 60, "filter_change_time": 45
            },
            {
                "username": "Shop2", "location": "Sofia", "user_rating": 4.0,
                "specialization": "Toyota",
                "oil_change_price": 45, "water_pump_price": 190, "belt_change_price": 140,
                "pulleys_price": 95, "filter_change_price": 75,
                "oil_change_time": 25, "water_pump_time": 110, "belt_change_time": 85,
                "pulleys_time": 55, "filter_change_time": 40
            }
        ]

        
        self.user = {"car_brand": "Toyota"}

    def tearDown(self):
        sys.stdout = sys.__stdout__  

    def test_valid_location_and_sort_by_price(self):
     
        mock_connection = MagicMock()
        mock_cursor = MagicMock()

       
        mock_cursor.fetchall.return_value = [
            {'username': 'Best Repair', 'location': 'Sofia', 'user_rating': 4.5, 'specialization': 'oil_change',
             'oil_change_price': 50, 'water_pump_price': 100, 'belt_change_price': 30, 'pulleys_price': 40,
             'filter_change_price': 25, 'oil_change_time': 30, 'water_pump_time': 45, 'belt_change_time': 25, 'pulleys_time': 20, 'filter_change_time': 15}
        ]

        mock_connection.cursor.return_value = mock_cursor
        DatabaseConfig.connect_db = MagicMock(return_value=mock_connection)

        # Simulate user input
        input_values = ["Sofia", "1", "1"]  

      
        def mock_input(prompt):
            return input_values.pop(0)

        with patch('builtins.input', mock_input):
            RepairShopManager.list_repair_shops(self.user)
            result = self.held_output.getvalue()

       
        self.assertIn("Shop: Best Repair, Location: Sofia", result)
        self.assertIn("Prices: Oil: 50", result)
        print(".", end="")  

    def test_invalid_sorting_option(self):
      
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_connection.cursor.return_value = mock_cursor
        DatabaseConfig.connect_db = MagicMock(return_value=mock_connection)

        
        input_values = ["", "4"] 

        def mock_input(prompt):
            return input_values.pop(0)

        with patch('builtins.input', mock_input):
            RepairShopManager.list_repair_shops(self.user)
            result = self.held_output.getvalue()

          
        self.assertIn("No repair shops registered.", result)
        print("E", end="")  

    def test_no_matching_shops(self):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_connection.cursor.return_value = mock_cursor
        DatabaseConfig.connect_db = MagicMock(return_value=mock_connection)

       
        input_values = ["", "2"]  

        def mock_input(prompt):
            return input_values.pop(0)

        with patch('builtins.input', mock_input):
            RepairShopManager.list_repair_shops(self.user)
            result = self.held_output.getvalue()

      
        self.assertIn("No repair shops registered.", result)
        print("F", end="") 

    @patch('database_config.DatabaseConfig.connect_db')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_list_repair_shops_valid_location(self, mock_print, mock_input, mock_connect_db): 
        
        mock_input.side_effect = ["Sofia", "2"]  

        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

       
        mock_cursor.fetchall.side_effect = [
            [{"location": "Sofia"}, {"location": "Plovdiv"}], 
            self.mock_shops  
        ]

      
        RepairShopManager.list_repair_shops(self.user)

       
        expected_query = """
            SELECT * FROM repair_shops
            WHERE FIND_IN_SET(%s, specialization)
             AND location = %s ORDER BY user_rating DESC"""
        mock_cursor.execute.assert_called_with(expected_query, ["Toyota", "Sofia"])

      
        self.assertEqual(mock_cursor.fetchall.call_count, 2)

        self.assertTrue(mock_print.called)
        expected_calls = [
            unittest.mock.call("\nAvailable locations:", "Sofia, Plovdiv"),
            unittest.mock.call("\nShop: Shop1, Location: Sofia, Rating: 4.5"),
            unittest.mock.call("Specialization: Toyota,Honda"),
            unittest.mock.call("Prices: Oil: 50, Water Pump: 200, Belt: 150, Pulleys: 100, Filter: 80"),
            unittest.mock.call("Times (minutes): Oil: 30, Water Pump: 120, Belt: 90, Pulleys: 60, Filter: 45"),
            unittest.mock.call("\nShop: Shop2, Location: Sofia, Rating: 4.0"),
            unittest.mock.call("Specialization: Toyota"),
            unittest.mock.call("Prices: Oil: 45, Water Pump: 190, Belt: 140, Pulleys: 95, Filter: 75"),
            unittest.mock.call("Times (minutes): Oil: 25, Water Pump: 110, Belt: 85, Pulleys: 55, Filter: 40")
        ]
        for call in expected_calls:
            self.assertIn(call, mock_print.call_args_list)

      
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
