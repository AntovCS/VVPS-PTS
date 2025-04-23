import unittest
from unittest.mock import patch, MagicMock
from repair_shop_manager import RepairShopManager

class TestRepairShopManager(unittest.TestCase):
    def setUp(self):
        self.user = {'car_brand': 'Toyota'}
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor
        self.sample_shop = {
            'username': 'Shop1',
            'location': 'Sofia',
            'specialization': 'Toyota',
            'user_rating': 4.5,
            'oil_change_price': 50,
            'water_pump_price': 150,
            'belt_change_price': 100,
            'pulleys_price': 120,
            'filter_change_price': 80,
            'oil_change_time': 30,
            'water_pump_time': 90,
            'belt_change_time': 60,
            'pulleys_time': 75,
            'filter_change_time': 45
        }

    @patch('database_config.DatabaseConfig.connect_db')
    def test_list_locations(self, mock_connect_db):
        mock_connect_db.return_value = self.mock_conn
        self.mock_cursor.fetchall.side_effect = [
            [{'location': 'Sofia'}, {'location': 'Plovdiv'}],
            [self.sample_shop]
    ]

        with patch('builtins.print') as mock_print, patch('builtins.input', side_effect=['', '2']):
            RepairShopManager.list_repair_shops(self.user)

           
            printed_lines = [' '.join(str(arg) for arg in call.args).strip()
                         for call in mock_print.call_args_list]

           
            print("PRINTED LINES:", printed_lines)

           
            found = any("Available locations:" in line and "Sofia" in line and "Plovdiv" in line
                    for line in printed_lines)
            self.assertTrue(found, "Did not find expected locations line in print output.")

    @patch('database_config.DatabaseConfig.connect_db')
    def test_no_locations(self, mock_connect_db):
        mock_connect_db.return_value = self.mock_conn
        self.mock_cursor.fetchall.return_value = []
        
        with patch('builtins.print') as mock_print:
            RepairShopManager.list_repair_shops(self.user)
            mock_print.assert_called_with('No repair shops registered.')

    @patch('database_config.DatabaseConfig.connect_db')
    def test_filter_by_location_and_car_brand(self, mock_connect_db):
        mock_connect_db.return_value = self.mock_conn
        self.mock_cursor.fetchall.side_effect = [[{'location': 'Sofia'}], [self.sample_shop]]
        
        with patch('builtins.print') as mock_print, patch('builtins.input', side_effect=['Sofia', '2']):
            RepairShopManager.list_repair_shops(self.user)
            self.mock_cursor.execute.assert_called_with(
                '\n            SELECT * FROM repair_shops\n            WHERE FIND_IN_SET(%s, specialization)\n             AND location = %s ORDER BY user_rating DESC',
                ['Toyota', 'Sofia']
            )
            calls = [args[0] for args, _ in mock_print.call_args_list]
            self.assertIn('Shop: Shop1, Location: Sofia, Rating: 4.5', [c.strip() for c in calls])

    @patch('database_config.DatabaseConfig.connect_db')
    def test_sort_by_price(self, mock_connect_db):
        mock_connect_db.return_value = self.mock_conn
        shop2 = self.sample_shop.copy()
        shop2['username'] = 'Shop2'
        shop2['oil_change_price'] = 40
        self.mock_cursor.fetchall.side_effect = [[{'location': 'Sofia'}], [shop2, self.sample_shop]]
        
        with patch('builtins.print') as mock_print, patch('builtins.input', side_effect=['', '1', '1']):
            RepairShopManager.list_repair_shops(self.user)
            self.mock_cursor.execute.assert_called_with(
                '\n            SELECT * FROM repair_shops\n            WHERE FIND_IN_SET(%s, specialization)\n             ORDER BY oil_change_price ASC',
                ['Toyota']
            )
            calls = [args[0] for args, _ in mock_print.call_args_list]
            shop_order = [c.strip() for c in calls if c.strip().startswith('Shop:')]
            self.assertTrue(shop_order[0].startswith('Shop: Shop2'))
            self.assertTrue(shop_order[1].startswith('Shop: Shop1'))

    @patch('database_config.DatabaseConfig.connect_db')
    def test_invalid_service(self, mock_connect_db):
        mock_connect_db.return_value = self.mock_conn
        self.mock_cursor.fetchall.return_value = [{'location': 'Sofia'}]
        
        with patch('builtins.print') as mock_print, patch('builtins.input', side_effect=['', '1', '6']):
            RepairShopManager.list_repair_shops(self.user)
            mock_print.assert_called_with('Invalid service.')

    @patch('database_config.DatabaseConfig.connect_db')
    def test_no_matching_shops(self, mock_connect_db):
        mock_connect_db.return_value = self.mock_conn
        self.mock_cursor.fetchall.side_effect = [[{'location': 'Sofia'}], []]
        
        with patch('builtins.print') as mock_print, patch('builtins.input', side_effect=['Sofia', '2']):
            RepairShopManager.list_repair_shops(self.user)
            mock_print.assert_called_with('No matching repair shops found.')

    @patch('database_config.DatabaseConfig.connect_db')
    def test_database_error(self, mock_connect_db):
        mock_connect_db.return_value = self.mock_conn
        self.mock_cursor.execute.side_effect = Exception('Database error')
        
        with patch('builtins.print') as mock_print:
            RepairShopManager.list_repair_shops(self.user)
            calls = [args[0] for args, _ in mock_print.call_args_list]
            self.assertIn('Error: Database error', [c.strip() for c in calls])

if __name__ == '__main__':
    unittest.main()