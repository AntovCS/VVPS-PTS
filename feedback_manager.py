import mysql.connector
from datetime import datetime
from database_config import DatabaseConfig

class FeedbackManager:
    @staticmethod
    def submit_feedback(user):
        conn = DatabaseConfig.connect_db()
        if not conn:
            return
        cursor = conn.cursor()

        try:
            comment = input("Enter your feedback about the program (max 500 characters): ").strip()
            if not comment:
                print("Feedback cannot be empty.")
                return
            if len(comment) > 500:
                print("Feedback is too long. Maximum 500 characters allowed.")
                return

            query = """
            INSERT INTO feedback (user_id, username, comment, created_at)
            VALUES (%s, %s, %s, %s)
            """
            values = (user['id'], user['username'], comment, datetime.now())
            cursor.execute(query, values)
            conn.commit()
            print("Feedback submitted successfully!")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def manage_feedback():
        conn = DatabaseConfig.connect_db()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT id, username, comment, created_at FROM feedback ORDER BY created_at DESC")
            feedback_list = cursor.fetchall()
            
            if not feedback_list:
                print("No feedback available.")
                return

            print("\n--- Feedback List ---")
            for feedback in feedback_list:
                print(f"ID: {feedback['id']}, Username: {feedback['username']}")
                print(f"Comment: {feedback['comment']}")
                print(f"Date: {feedback['created_at']}")
                print("---")

            action = input("Enter feedback ID to delete (or press Enter to exit): ").strip()
            if action:
                cursor.execute("DELETE FROM feedback WHERE id = %s", (action,))
                if cursor.rowcount > 0:
                    conn.commit()
                    print("Feedback deleted successfully!")
                else:
                    print("Invalid feedback ID.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()