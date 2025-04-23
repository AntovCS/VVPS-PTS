import mysql.connector
from database_config import DatabaseConfig
from feedback_manager import FeedbackManager
from profile_manager import ProfileManager

class AdminManager:
    @staticmethod
    def admin_queries():
        conn = DatabaseConfig.connect_db()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)

        try:
            while True:
                print("\n--- Admin Queries ---")
                print("1. Users by car brand")
                print("2. Repair shops by location")
                print("3. Average service prices")
                print("4. Highest service prices")
                print("5. Lowest service prices")
                print("6. Most popular car brand")
                print("7. Highest rated repair shop")
                print("8. Lowest rated repair shop")
                print("9. Average rating by location")
                print("10. Average service times")
                print("11. Manage feedback")
                print("12. Appointment requests by status")
                print("13. Delete profile")
                print("14. Exit")
                choice = input("Select option: ").strip()

                if choice == '1':
                    car_brand = input("Enter car brand: ").strip()
                    cursor.execute("SELECT COUNT(*) as count FROM users WHERE car_brand = %s", (car_brand,))
                    print(f"Users with {car_brand}: {cursor.fetchone()['count']}")
                elif choice == '2':
                    location = input("Enter location: ").strip()
                    cursor.execute("SELECT COUNT(*) as count FROM repair_shops WHERE location = %s", (location,))
                    print(f"Repair shops in {location}: {cursor.fetchone()['count']}")
                elif choice == '3':
                    cursor.execute("""
                    SELECT AVG(oil_change_price) as oil, AVG(water_pump_price) as water_pump,
                           AVG(belt_change_price) as belt, AVG(pulleys_price) as pulleys,
                           AVG(filter_change_price) as filter
                    FROM repair_shops
                    """)
                    prices = cursor.fetchone()
                    print("Average prices:", {k: round(v, 2) if v else 'N/A' for k, v in prices.items()})
                elif choice == '4':
                    cursor.execute("""
                    SELECT MAX(oil_change_price) as oil, MAX(water_pump_price) as water_pump,
                           MAX(belt_change_price) as belt, MAX(pulleys_price) as pulleys,
                           MAX(filter_change_price) as filter
                    FROM repair_shops
                    """)
                    prices = cursor.fetchone()
                    print("Highest prices:", {k: v if v else 'N/A' for k, v in prices.items()})
                elif choice == '5':
                    cursor.execute("""
                    SELECT MIN(oil_change_price) as oil, MIN(water_pump_price) as water_pump,
                           MIN(belt_change_price) as belt, MIN(pulleys_price) as pulleys,
                           MIN(filter_change_price) as filter
                    FROM repair_shops
                    """)
                    prices = cursor.fetchone()
                    print("Lowest prices:", {k: v if v else 'N/A' for k, v in prices.items()})
                elif choice == '6':
                    cursor.execute("""
                    SELECT car_brand, COUNT(*) as count
                    FROM users
                    GROUP BY car_brand
                    ORDER BY count DESC
                    LIMIT 1
                    """)
                    result = cursor.fetchone()
                    if result:
                        print(f"Most popular car brand: {result['car_brand']} ({result['count']} users)")
                    else:
                        print("No users registered.")
                elif choice == '7':
                    cursor.execute("SELECT username, user_rating FROM repair_shops ORDER BY user_rating DESC LIMIT 1")
                    result = cursor.fetchone()
                    if result:
                        print(f"Highest rated shop: {result['username']} ({result['user_rating']} stars)")
                    else:
                        print("No repair shops registered.")
                elif choice == '8':
                    cursor.execute("SELECT username, user_rating FROM repair_shops WHERE user_rating > 0 ORDER BY user_rating ASC LIMIT 1")
                    result = cursor.fetchone()
                    if result:
                        print(f"Lowest rated shop: {result['username']} ({result['user_rating']} stars)")
                    else:
                        print("No rated repair shops.")
                elif choice == '9':
                    location = input("Enter location: ").strip()
                    cursor.execute("SELECT AVG(user_rating) as avg_rating FROM repair_shops WHERE location = %s", (location,))
                    result = cursor.fetchone()
                    print(f"Average rating in {location}: {round(result['avg_rating'], 1) if result['avg_rating'] else 'N/A'} stars")
                elif choice == '10':
                    cursor.execute("""
                    SELECT AVG(oil_change_time) as oil, AVG(water_pump_time) as water_pump,
                           AVG(belt_change_time) as belt, AVG(pulleys_time) as pulleys,
                           AVG(filter_change_time) as filter
                    FROM repair_shops
                    """)
                    times = cursor.fetchone()
                    print("Average times (minutes):", {k: round(v, 1) if v else 'N/A' for k, v in times.items()})
                elif choice == '11':
                    FeedbackManager.manage_feedback()
                elif choice == '12':
                    status = input("Enter status (pending/approved/denied): ").strip()
                    if status not in ['pending', 'approved', 'denied']:
                        print("Invalid status.")
                        continue
                    cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM appointment_requests
                    WHERE status = %s
                    """, (status,))
                    result = cursor.fetchone()
                    print(f"{status.title()} appointment requests: {result['count']}")
                elif choice == '13':
                    ProfileManager.delete_profile()
                elif choice == '14':
                    break
                else:
                    print("Invalid option.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()