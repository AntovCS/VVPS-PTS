import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import mysql.connector
from feedback_manager import FeedbackManager

class TestManageFeedback(unittest.TestCase):
    @patch('feedback_manager.DatabaseConfig.connect_db')
    def test_manage_feedback_no_feedback(self, mock_connect_db):
        # Симулиране на връзка с базата данни и курсор
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []  # Няма обратна връзка
        
        # Симулиране на изхода (print)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            FeedbackManager.manage_feedback()
            self.assertIn("No feedback available.", fake_out.getvalue())
        
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('feedback_manager.DatabaseConfig.connect_db')
    @patch('builtins.input', return_value="")  # Симулиране на натискане на Enter за изход
    def test_manage_feedback_display_feedback(self, mock_input, mock_connect_db):
        # Симулиране на връзка с базата данни и курсор
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            {'id': 1, 'username': 'user1', 'comment': 'Great app!', 'created_at': '2023-10-01 12:00:00'}
        ]
        
        # Симулиране на изхода (print)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            FeedbackManager.manage_feedback()
            output = fake_out.getvalue()
            self.assertIn("ID: 1, Username: user1", output)
            self.assertIn("Comment: Great app!", output)
            self.assertIn("Date: 2023-10-01 12:00:00", output)
        
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('feedback_manager.DatabaseConfig.connect_db')
    @patch('builtins.input', return_value="1")  # Симулиране на въвеждане на валиден ID за изтриване
    def test_manage_feedback_delete_success(self, mock_input, mock_connect_db):
        # Симулиране на връзка с базата данни и курсор
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            {'id': 1, 'username': 'user1', 'comment': 'Great app!', 'created_at': '2023-10-01 12:00:00'}
        ]
        mock_cursor.rowcount = 1  # Симулиране на успешно изтриване
        
        # Симулиране на изхода (print)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            FeedbackManager.manage_feedback()
            self.assertIn("Feedback deleted successfully!", fake_out.getvalue())
        
        mock_cursor.execute.assert_called_with("DELETE FROM feedback WHERE id = %s", ("1",))
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('feedback_manager.DatabaseConfig.connect_db')
    @patch('builtins.input', return_value="2")  # Симулиране на въвеждане на невалиден ID
    def test_manage_feedback_delete_invalid_id(self, mock_input, mock_connect_db):
        # Симулиране на връзка с базата данни и курсор
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            {'id': 1, 'username': 'user1', 'comment': 'Great app!', 'created_at': '2023-10-01 12:00:00'}
        ]
        mock_cursor.rowcount = 0  # Симулиране на неуспешно изтриване (невалиден ID)
        
        # Симулиране на изхода (print)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            FeedbackManager.manage_feedback()
            self.assertIn("Invalid feedback ID.", fake_out.getvalue())
        
        mock_cursor.execute.assert_called_with("DELETE FROM feedback WHERE id = %s", ("2",))
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()