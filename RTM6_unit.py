import unittest
from unittest.mock import patch, MagicMock
from repair_shop_manager import RepairShopManager

class TestRepairShopRequests(unittest.TestCase):

    @patch('repair_shop_manager.DatabaseConfig.connect_db')
    def test_TC_R1_pending_requests_listed(self, mock_connect):
        # R1: Показване на чакащи заявки
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [{
            'id': 1,
            'username': 'client1',
            'car_brand': 'Toyota',
            'car_model': 'Yaris',
            'car_year': 2015,
            'service_type': 'oil_change',
            'requested_time': '2025-05-01 12:00:00',
            'status': 'pending'
        }]
        with patch('builtins.input', side_effect=['']):
            RepairShopManager.view_appointment_requests({'id': 10})
        mock_cursor.execute.assert_any_call("""
            SELECT ar.id, u.username, u.car_brand, u.car_model, u.car_year,
                   ar.service_type, ar.requested_time, ar.status
            FROM appointment_requests ar
            JOIN users u ON ar.user_id = u.id
            WHERE ar.shop_id = %s AND ar.status = 'pending'
            """, (10,))

    @patch('repair_shop_manager.DatabaseConfig.connect_db')
    def test_TC_R3_approve_request(self, mock_connect):
        # R3 + R4: Одобряване на заявка
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [{
            'id': 1,
            'username': 'client1',
            'car_brand': 'Toyota',
            'car_model': 'Yaris',
            'car_year': 2015,
            'service_type': 'oil_change',
            'requested_time': '2025-05-01 12:00:00',
            'status': 'pending'
        }]
        mock_cursor.rowcount = 1

        with patch('builtins.input', side_effect=['1', '1']):
            RepairShopManager.view_appointment_requests({'id': 99})

        mock_cursor.execute.assert_any_call("""
                UPDATE appointment_requests
                SET status = %s
                WHERE id = %s AND shop_id = %s
                """, ('approved', '1', 99))

    @patch('repair_shop_manager.DatabaseConfig.connect_db')
    def test_TC_R3_deny_request(self, mock_connect):
        # R3 + R4: Отказ на заявка
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [{
            'id': 2,
            'username': 'client2',
            'car_brand': 'VW',
            'car_model': 'Golf',
            'car_year': 2018,
            'service_type': 'belt_change',
            'requested_time': '2025-05-01 13:00:00',
            'status': 'pending'
        }]
        mock_cursor.rowcount = 1

        with patch('builtins.input', side_effect=['2', '2']):
            RepairShopManager.view_appointment_requests({'id': 77})

        mock_cursor.execute.assert_any_call("""
                UPDATE appointment_requests
                SET status = %s
                WHERE id = %s AND shop_id = %s
                """, ('denied', '2', 77))

    @patch('repair_shop_manager.DatabaseConfig.connect_db')
    def test_TC_R6_reject_foreign_request(self, mock_connect):
        # R6: Защита от обработка на чужда заявка
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [{
            'id': 3,
            'username': 'clientX',
            'car_brand': 'Ford',
            'car_model': 'Focus',
            'car_year': 2019,
            'service_type': 'filter_change',
            'requested_time': '2025-05-01 14:00:00',
            'status': 'pending'
        }]
        mock_cursor.rowcount = 0  # simulate invalid request ID or wrong shop

        with patch('builtins.input', side_effect=['3', '1']):
            RepairShopManager.view_appointment_requests({'id': 200})

        mock_cursor.execute.assert_any_call("""
                UPDATE appointment_requests
                SET status = %s
                WHERE id = %s AND shop_id = %s
                """, ('approved', '3', 200))

        # няма commit ако няма rowcount > 0
        mock_conn.commit.assert_not_called()

if __name__ == '__main__':
    unittest.main()
