from database_config import DatabaseConfig
import mysql.connector

class ProfileManager:
    @staticmethod
    def delete_profile():
        conn = DatabaseConfig.connect_db()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)

        try:
            print("\n--- Delete Profile ---")
            profile_type = input("Select profile type to delete (1: User, 2: Repair Shop): ").strip()
            if profile_type not in ['1', '2']:
                print("Invalid profile type.")
                return

            table = 'users' if profile_type == '1' else 'repair_shops'
            role = 'user' if profile_type == '1' else 'repair shop'

            cursor.execute(f"SELECT id, username FROM {table}")
            profiles = cursor.fetchall()
            if not profiles:
                print(f"No {role}s available to delete.")
                return

            print(f"\nAvailable {role}s:")
            for profile in profiles:
                print(f"ID: {profile['id']}, Username: {profile['username']}")

            profile_id = input(f"Enter {role} ID to delete (or press Enter to cancel): ").strip()
            if not profile_id:
                print("Deletion cancelled.")
                return

            cursor.execute(f"SELECT username FROM {table} WHERE id = %s", (profile_id,))
            profile = cursor.fetchone()
            if not profile:
                print(f"Invalid {role} ID.")
                return

            confirm = input(f"Are you sure you want to delete {role} '{profile['username']}'? This will delete all associated data (y/n): ").strip().lower()
            if confirm != 'y':
                print("Deletion cancelled.")
                return

            if profile_type == '1':
                cursor.execute("DELETE FROM feedback WHERE user_id = %s", (profile_id,))
                cursor.execute("DELETE FROM shop_ratings WHERE user_id = %s", (profile_id,))
                cursor.execute("DELETE FROM appointment_requests WHERE user_id = %s", (profile_id,))
                cursor.execute("DELETE FROM appointments WHERE user_id = %s", (profile_id,))
            else:
                cursor.execute("DELETE FROM shop_ratings WHERE shop_id = %s", (profile_id,))
                cursor.execute("DELETE FROM shop_availability WHERE shop_id = %s", (profile_id,))
                cursor.execute("DELETE FROM appointment_requests WHERE shop_id = %s", (profile_id,))
                cursor.execute("DELETE FROM appointments WHERE shop_id = %s", (profile_id,))
                cursor.execute("""
                UPDATE repair_shops rs
                SET user_rating = (
                    SELECT AVG(rating)
                    FROM shop_ratings
                    WHERE shop_id = rs.id
                )
                WHERE id = %s
                """, (profile_id,))

            # Corrected line
            cursor.execute(f"DELETE FROM {table} WHERE id = %s", (profile_id,))
            if cursor.rowcount > 0:
                conn.commit()
                print(f"{role.title()} '{profile['username']}' deleted successfully!")
            else:
                print(f"Failed to delete {role}.")
        except Exception as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()