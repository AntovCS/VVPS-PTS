import unittest
from unittest.mock import patch, MagicMock
from feedback_manager import FeedbackManager  # <-- името на твоя файл

class TestFeedbackManager(unittest.TestCase):

    @patch('feedback_manager.DatabaseConfig.connect_db')  # <-- тук също сменено
    def test_manage_feedback_display(self, mock_connect):
        # REQ-001: Проверка дали се показва списък с коректни данни

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        feedback_sample = [{
            'id': 1,
            'username': 'testuser',
            'comment': 'Great feature!',
            'created_at': '2025-04-22 10:00:00'
        }]
        mock_cursor.fetchall.return_value = feedback_sample

        with patch('builtins.input', return_value=''):
            FeedbackManager.manage_feedback()

        mock_cursor.execute.assert_called_with("SELECT id, username, comment, created_at FROM feedback ORDER BY created_at DESC")
        mock_cursor.fetchall.assert_called()
        mock_conn.close.assert_called()

    @patch('feedback_manager.DatabaseConfig.connect_db')  # <-- и тук
    def test_manage_feedback_delete(self, mock_connect):
        # REQ-002: Проверка дали обратна връзка се трие по ID

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [{
            'id': 2,
            'username': 'user2',
            'comment': 'Bad UI',
            'created_at': '2025-04-22 11:00:00'
        }]
        mock_cursor.rowcount = 1

        with patch('builtins.input', return_value='2'):
            FeedbackManager.manage_feedback()

        mock_cursor.execute.assert_any_call("DELETE FROM feedback WHERE id = %s", ('2',))
        mock_conn.commit.assert_called()
        mock_conn.close.assert_called()

if __name__ == '__main__':
    unittest.main()
