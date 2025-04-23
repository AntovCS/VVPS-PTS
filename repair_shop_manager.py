import mysql.connector
from database_config import DatabaseConfig
from datetime import date, datetime

class RepairShopManager:
    @staticmethod
    def list_repair_shops(user):
        conn = DatabaseConfig.connect_db()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT DISTINCT location FROM repair_shops")
            locations = [row['location'] for row in cursor.fetchall()]
            if not locations:
                print("No repair shops registered.")
                return

            print("\nAvailable locations:", ", ".join(locations))
            location = input("Enter location (or press Enter for all): ").strip()
            sort_by = input("Sort by (1: Price, 2: Rating, 3: Time): ").strip()

            query = """
            SELECT * FROM repair_shops
            WHERE FIND_IN_SET(%s, specialization)
            """
            params = [user['car_brand']]
            if location:
                query += " AND location = %s"
                params.append(location)

            if sort_by == '1':
                service = input("Sort by price of (1: Oil Change, 2: Water Pump, 3: Belt, 4: Pulleys, 5: Filter): ").strip()
                service_map = {
                    '1': 'oil_change_price', '2': 'water_pump_price', '3': 'belt_change_price',
                    '4': 'pulleys_price', '5': 'filter_change_price'
                }
                if service not in service_map:
                    print("Invalid service.")
                    return
                query += f" ORDER BY {service_map[service]} ASC"
            elif sort_by == '3':
                service = input("Sort by time of (1: Oil Change, 2: Water Pump, 3: Belt, 4: Pulleys, 5: Filter): ").strip()
                service_map = {
                    '1': 'oil_change_time', '2': 'water_pump_time', '3': 'belt_change_time',
                    '4': 'pulleys_time', '5': 'filter_change_time'
                }
                if service not in service_map:
                    print("Invalid service.")
                    return
                query += f" ORDER BY {service_map[service]} ASC"
            else:
                query += " ORDER BY user_rating DESC"

            cursor.execute(query, params)
            shops = cursor.fetchall()
            if not shops:
                print("No matching repair shops found.")
                return

            for shop in shops:
                print(f"\nShop: {shop['username']}, Location: {shop['location']}, Rating: {shop['user_rating']}")
                print(f"Specialization: {shop['specialization']}")
                print(f"Prices: Oil: {shop['oil_change_price']}, Water Pump: {shop['water_pump_price']}, "
                      f"Belt: {shop['belt_change_price']}, Pulleys: {shop['pulleys_price']}, "
                      f"Filter: {shop['filter_change_price']}")
                print(f"Times (minutes): Oil: {shop['oil_change_time']}, Water Pump: {shop['water_pump_time']}, "
                      f"Belt: {shop['belt_change_time']}, Pulleys: {shop['pulleys_time']}, "
                      f"Filter: {shop['filter_change_time']}")
        except Exception as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def update_car_info(user):
        conn = DatabaseConfig.connect_db()
        if not conn:
            return
        cursor = conn.cursor()

        try:
            car_brand = input("Enter new car brand (or press Enter to keep current): ").strip()
            car_model = input("Enter new car model (or press Enter to keep current): ").strip()
            car_year = input("Enter new car year (1900-2025, or press Enter to keep current): ").strip()

            updates = []
            params = []
            if car_brand:
                updates.append("car_brand = %s")
                params.append(car_brand)
            if car_model:
                updates.append("car_model = %s")
                params.append(car_model)
            if car_year:
                if not car_year.isdigit() or int(car_year) < 1900 or int(car_year) > 2025:
                    print("Invalid car year.")
                    return
                updates.append("car_year = %s")
                params.append(int(car_year))

            if updates:
                params.append(user['id'])
                query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
                cursor.execute(query, params)
                conn.commit()
                print("Car information updated!")
            else:
                print("No changes made.")
        except Exception as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def rate_repair_shop(user):
        conn = DatabaseConfig.connect_db()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT id, username, location FROM repair_shops")
            shops = cursor.fetchall()
            if not shops:
                print("No repair shops available.")
                return

            print("\nAvailable repair shops:")
            for shop in shops:
                print(f"ID: {shop['id']}, Name: {shop['username']}, Location: {shop['location']}")
            shop_id = input("Enter shop ID to rate: ").strip()
            rating = input("Enter rating (1-5): ").strip()

            if not rating.isdigit() or int(rating) < 1 or int(rating) > 5:
                print("Invalid rating.")
                return

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS shop_ratings (
                user_id INT,
                shop_id INT,
                rating INT,
                PRIMARY KEY (user_id, shop_id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (shop_id) REFERENCES repair_shops(id)
            )
            """)
            cursor.execute("""
            INSERT INTO shop_ratings (user_id, shop_id, rating)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE rating = %s
            """, (user['id'], shop_id, rating, rating))

            cursor.execute("""
            UPDATE repair_shops rs
            SET user_rating = (
                SELECT AVG(rating)
                FROM shop_ratings
                WHERE shop_id = rs.id
            )
            WHERE id = %s
            """, (shop_id,))
            conn.commit()
            print("Rating submitted!")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def view_shop_rating(shop):
        print(f"\nCurrent rating for {shop['username']}: {shop['user_rating']} stars")

    @staticmethod
    def update_shop_prices(shop):
        conn = DatabaseConfig.connect_db()
        if not conn:
            return
        cursor = conn.cursor()

        try:
            print("\nEnter new prices and times (press Enter to keep current):")
            oil_price = input(f"Oil change price ({shop['oil_change_price']}): ").strip()
            water_pump_price = input(f"Water pump price ({shop['water_pump_price']}): ").strip()
            belt_price = input(f"Belt price ({shop['belt_change_price']}): ").strip()
            pulleys_price = input(f"Pulleys price ({shop['pulleys_price']}): ").strip()
            filter_price = input(f"Filter price ({shop['filter_change_price']}): ").strip()
            oil_time = input(f"Oil change time (minutes) ({shop['oil_change_time']}): ").strip()
            water_pump_time = input(f"Water pump time (minutes) ({shop['water_pump_time']}): ").strip()
            belt_time = input(f"Belt time (minutes) ({shop['belt_change_time']}): ").strip()
            pulleys_time = input(f"Pulleys time (minutes) ({shop['pulleys_time']}): ").strip()
            filter_time = input(f"Filter time (minutes) ({shop['filter_change_time']}): ").strip()

            updates = []
            params = []
            if oil_price:
                updates.append("oil_change_price = %s")
                params.append(float(oil_price))
            if water_pump_price:
                updates.append("water_pump_price = %s")
                params.append(float(water_pump_price))
            if belt_price:
                updates.append("belt_change_price = %s")
                params.append(float(belt_price))
            if pulleys_price:
                updates.append("pulleys_price = %s")
                params.append(float(pulleys_price))
            if filter_price:
                updates.append("filter_change_price = %s")
                params.append(float(filter_price))
            if oil_time:
                updates.append("oil_change_time = %s")
                params.append(int(oil_time))
            if water_pump_time:
                updates.append("water_pump_time = %s")
                params.append(int(water_pump_time))
            if belt_time:
                updates.append("belt_change_time = %s")
                params.append(int(belt_time))
            if pulleys_time:
                updates.append("pulleys_time = %s")
                params.append(int(pulleys_time))
            if filter_time:
                updates.append("filter_change_time = %s")
                params.append(int(filter_time))

            if updates:
                params.append(shop['id'])
                query = f"UPDATE repair_shops SET {', '.join(updates)} WHERE id = %s"
                cursor.execute(query, params)
                conn.commit()
                print("Prices and times updated!")
            else:
                print("No changes made.")
        except (mysql.connector.Error, ValueError) as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def manage_shop_availability(shop):
        conn = DatabaseConfig.connect_db()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)

        try:
            print("\n--- Manage Availability ---")
            date_input = input("Enter date (YYYY-MM-DD, or press Enter for today): ").strip()
            available_date = date.today() if not date_input else date.fromisoformat(date_input)

            start_time = input("Enter start time (HH:MM): ").strip()
            end_time = input("Enter end time (HH:MM): ").strip()

            try:
                start_time = datetime.strptime(start_time, "%H:%M").time()
                end_time = datetime.strptime(end_time, "%H:%M").time()
            except ValueError:
                print("Invalid time format. Use HH:MM.")
                return

            if start_time >= end_time:
                print("Start time must be before end time.")
                return

            query = """
            INSERT INTO shop_availability (shop_id, available_date, start_time, end_time)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (shop['id'], available_date, start_time, end_time))
            conn.commit()
            print("Availability added successfully!")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def view_appointment_requests(shop):
        conn = DatabaseConfig.connect_db()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
            SELECT ar.id, u.username, u.car_brand, u.car_model, u.car_year,
                   ar.service_type, ar.requested_time, ar.status
            FROM appointment_requests ar
            JOIN users u ON ar.user_id = u.id
            WHERE ar.shop_id = %s AND ar.status = 'pending'
            """
            cursor.execute(query, (shop['id'],))
            requests = cursor.fetchall()

            if not requests:
                print("No pending appointment requests.")
                return

            print("\n--- Pending Appointment Requests ---")
            for req in requests:
                print(f"Request ID: {req['id']}")
                print(f"User: {req['username']}")
                print(f"Car: {req['car_brand']} {req['car_model']} ({req['car_year']})")
                print(f"Service: {req['service_type'].replace('_', ' ').title()}")
                print(f"Time: {req['requested_time']}")
                print("---")

            request_id = input("Enter request ID to approve/deny (or press Enter to exit): ").strip()
            if request_id:
                action = input("Action (1: Approve, 2: Deny): ").strip()
                if action not in ['1', '2']:
                    print("Invalid action.")
                    return

                status = 'approved' if action == '1' else 'denied'
                cursor.execute("""
                UPDATE appointment_requests
                SET status = %s
                WHERE id = %s AND shop_id = %s
                """, (status, request_id, shop['id']))
                if cursor.rowcount > 0:
                    conn.commit()
                    print(f"Request {status} successfully!")
                else:
                    print("Invalid request ID.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()