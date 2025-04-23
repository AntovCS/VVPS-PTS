import unittest
from unittest.mock import patch, MagicMock
from repair_shop_manager import RepairShopManager

class TestRepairShopManager(unittest.TestCase):
    @patch('repair_shop_manager.DatabaseConfig.connect_db')
    def test_approve_appointment_request(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Fake pending request
        mock_cursor.fetchall.return_value = [{
            'id': 1,
            'username': 'john_doe',
            'car_brand': 'Toyota',
            'car_model': 'Corolla',
            'car_year': 2015,
            'service_type': 'oil_change',
            'requested_time': '2025-05-01 10:00:00',
            'status': 'pending'
        }]
        mock_cursor.rowcount = 1

        inputs = ['1', '1']  # request ID, then approve
        with patch('builtins.input', side_effect=inputs):
            RepairShopManager.view_appointment_requests({'id': 123})

        mock_cursor.execute.assert_any_call("""
                UPDATE appointment_requests
                SET status = %s
                WHERE id = %s AND shop_id = %s
                """, ('approved', '1', 123))

    @patch('repair_shop_manager.DatabaseConfig.connect_db')
    def test_deny_appointment_request(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [{
            'id': 2,
            'username': 'jane_doe',
            'car_brand': 'Honda',
            'car_model': 'Civic',
            'car_year': 2018,
            'service_type': 'belt_change',
            'requested_time': '2025-05-01 12:00:00',
            'status': 'pending'
        }]
        mock_cursor.rowcount = 1

        inputs = ['2', '2']  # request ID, then deny
        with patch('builtins.input', side_effect=inputs):
            RepairShopManager.view_appointment_requests({'id': 321})

        mock_cursor.execute.assert_any_call("""
                UPDATE appointment_requests
                SET status = %s
                WHERE id = %s AND shop_id = %s
                """, ('denied', '2', 321))

if __name__ == '__main__':
    unittest.main()
