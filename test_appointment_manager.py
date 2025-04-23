import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, date, time, timedelta
from appointment_manager import AppointmentManager

class TestAppointmentManager(unittest.TestCase):
    def setUp(self):
        self.user = {
            'id': 1,
            'car_brand': 'Toyota'
        }
        self.shop = {
            'id': 1,
            'username': 'Test Shop',
            'location': 'Sofia'
        }
        self.available_slot = {
            'id': 1,
            'start_time': time(9, 0),
            'end_time': time(12, 0)
        }
        self.booked_appointment = {
            'requested_time': datetime(2025, 4, 22, 10, 0),
            'service_type': 'oil_change',
            'oil_change_time': 30,
            'water_pump_time': None,
            'belt_change_time': None,
            'pulleys_time': None,
            'filter_change_time': None
        }

    @patch('appointment_manager.DatabaseConfig.connect_db')
    def test_no_compatible_shops(self, mock_connect_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        with patch('builtins.print') as mock_print:
            AppointmentManager.request_appointment(self.user)
            mock_print.assert_called_with("No compatible repair shops available.")
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('appointment_manager.DatabaseConfig.connect_db')
    def test_no_available_slots(self, mock_connect_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.side_effect = [[self.shop], []]

        with patch('builtins.print') as mock_print, patch('builtins.input', side_effect=['1', '2025-04-22']):
            AppointmentManager.request_appointment(self.user)
            mock_print.assert_any_call("No available slots for this date.")
        mock_cursor.execute.assert_called()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('appointment_manager.DatabaseConfig.connect_db')
    def test_display_available_slots(self, mock_connect_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.side_effect = [[self.shop], [self.available_slot], []]
        mock_cursor.fetchone.return_value = {'start_time': time(9, 0), 'end_time': time(12, 0)}

        # Добавяме всички необходими входове: shop_id, date, slot_id, service, time
        input_side_effects = ['1', '2025-04-22', '1', '1', '09:00']
        with patch('builtins.print') as mock_print, patch('builtins.input', side_effect=input_side_effects):
            mock_cursor.fetchone.side_effect = [
                {'start_time': time(9, 0), 'end_time': time(12, 0)},  # slot
                {'oil_change_time': 30}  # service duration
            ]
            AppointmentManager.request_appointment(self.user)
            mock_print.assert_any_call("\nAvailable time slots:")
            mock_print.assert_any_call("Slot ID: 1, 09:00 - 12:00")
            mock_print.assert_any_call("Appointment request submitted successfully!")
        mock_cursor.execute.assert_called()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('appointment_manager.DatabaseConfig.connect_db')
    def test_display_booked_appointments_in_slot(self, mock_connect_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.side_effect = [[self.shop], [self.available_slot], [self.booked_appointment]]
        mock_cursor.fetchone.return_value = {'start_time': time(9, 0), 'end_time': time(12, 0)}

        # Добавяме всички необходими входове: shop_id, date, slot_id, service, time
        input_side_effects = ['1', '2025-04-22', '1', '1', '09:00']
        with patch('builtins.print') as mock_print, patch('builtins.input', side_effect=input_side_effects):
            mock_cursor.fetchone.side_effect = [
                {'start_time': time(9, 0), 'end_time': time(12, 0)},  # slot
                {'oil_change_time': 30}  # service duration
            ]
            AppointmentManager.request_appointment(self.user)
            mock_print.assert_any_call("\nAvailable time slots:")
            mock_print.assert_any_call("Slot ID: 1, 09:00 - 12:00")
            mock_print.assert_any_call("  Booked:")
            mock_print.assert_any_call("    10:00 - 10:30 (Oil Change)")
            mock_print.assert_any_call("Appointment request submitted successfully!")
        mock_cursor.execute.assert_called()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('appointment_manager.DatabaseConfig.connect_db')
    def test_invalid_slot_id(self, mock_connect_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.side_effect = [[self.shop], [self.available_slot], []]
        mock_cursor.fetchone.return_value = None

        with patch('builtins.print') as mock_print, patch('builtins.input', side_effect=['1', '2025-04-22', '999']):
            AppointmentManager.request_appointment(self.user)
            mock_print.assert_any_call("Invalid slot ID.")
        mock_cursor.execute.assert_called()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()