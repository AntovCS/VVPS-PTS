import mysql.connector
from database_config import DatabaseConfig
from datetime import datetime, timedelta, date

class AppointmentManager:
    @staticmethod
    def request_appointment(user):
        conn = DatabaseConfig.connect_db()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT id, username, location FROM repair_shops WHERE FIND_IN_SET(%s, specialization)", (user['car_brand'],))
            shops = cursor.fetchall()
            if not shops:
                print("No compatible repair shops available.")
                return

            print("\nAvailable repair shops:")
            for shop in shops:
                print(f"ID: {shop['id']}, Name: {shop['username']}, Location: {shop['location']}")
            shop_id = input("Enter shop ID: ").strip()

            date_input = input("Enter date (YYYY-MM-DD, or press Enter for today): ").strip()
            available_date = date.today() if not date_input else date.fromisoformat(date_input)

            query = """
            SELECT id, start_time, end_time
            FROM shop_availability
            WHERE shop_id = %s AND available_date = %s
            """
            cursor.execute(query, (shop_id, available_date))
            available_slots = cursor.fetchall()

            if not available_slots:
                print("No available slots for this date.")
                return

            cursor.execute("""
            SELECT ar.requested_time, ar.service_type, rs.oil_change_time, rs.water_pump_time,
                   rs.belt_change_time, rs.pulleys_time, rs.filter_change_time
            FROM appointment_requests ar
            JOIN repair_shops rs ON ar.shop_id = rs.id
            WHERE ar.shop_id = %s AND ar.status = 'approved'
            AND DATE(ar.requested_time) = %s
            """, (shop_id, available_date))
            booked_appointments = cursor.fetchall()

            service_time_map = {
                'oil_change': 'oil_change_time',
                'water_pump': 'water_pump_time',
                'belt_change': 'belt_change_time',
                'pulleys': 'pulleys_time',
                'filter_change': 'filter_change_time'
            }

            print("\nAvailable time slots:")
            for slot in available_slots:
                slot_id = slot['id']
                start_time = slot['start_time']
                end_time = slot['end_time']

                if isinstance(start_time, str):
                    start_time = datetime.strptime(start_time, "%H:%M:%S").time()
                elif isinstance(start_time, timedelta):
                    start_time = (datetime.min + start_time).time()
                if isinstance(end_time, str):
                    end_time = datetime.strptime(end_time, "%H:%M:%S").time()
                elif isinstance(end_time, timedelta):
                    end_time = (datetime.min + end_time).time()

                print(f"Slot ID: {slot_id}, {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")

                slot_start = datetime.combine(available_date, start_time)
                slot_end = datetime.combine(available_date, end_time)
                booked_in_slot = []
                for appt in booked_appointments:
                    appt_start = appt['requested_time']
                    service = appt['service_type']
                    duration = appt[service_time_map[service]]
                    if duration is None:
                        continue
                    appt_end = appt_start + timedelta(minutes=duration)
                    if slot_start <= appt_start < slot_end or slot_start < appt_end <= slot_end:
                        booked_in_slot.append((appt_start, appt_end, service))
                
                if booked_in_slot:
                    print("  Booked:")
                    for start, end, service in booked_in_slot:
                        service_name = service.replace('_', ' ').title()
                        print(f"    {start.strftime('%H:%M')} - {end.strftime('%H:%M')} ({service_name})")

            slot_id = input("Enter slot ID: ").strip()
            cursor.execute("SELECT start_time, end_time FROM shop_availability WHERE id = %s AND shop_id = %s", (slot_id, shop_id))
            slot = cursor.fetchone()
            if not slot:
                print("Invalid slot ID.")
                return

            service_map = {
                '1': 'oil_change', '2': 'water_pump', '3': 'belt_change',
                '4': 'pulleys', '5': 'filter_change'
            }
            service = input("Select service (1: Oil Change, 2: Water Pump, 3: Belt, 4: Pulleys, 5: Filter): ").strip()
            if service not in service_map:
                print("Invalid service.")
                return

            service_type = service_map[service]
            cursor.execute(f"SELECT {service_time_map[service_type]} FROM repair_shops WHERE id = %s", (shop_id,))
            service_duration = cursor.fetchone()[service_time_map[service_type]]
            if service_duration is None:
                print(f"Service {service_type.replace('_', ' ').title()} is not available at this shop.")
                return

            time_input = input("Enter desired time (HH:MM): ").strip()
            try:
                requested_time_obj = datetime.strptime(time_input, "%H:%M").time()
                requested_time = datetime.combine(available_date, requested_time_obj)
            except ValueError:
                print("Invalid time format. Please use HH:MM (e.g., 14:30).")
                return

            start_time = slot['start_time']
            end_time = slot['end_time']
            if isinstance(start_time, str):
                start_time = datetime.strptime(start_time, "%H:%M:%S").time()
            elif isinstance(start_time, timedelta):
                start_time = (datetime.min + start_time).time()
            if isinstance(end_time, str):
                end_time = datetime.strptime(end_time, "%H:%M:%S").time()
            elif isinstance(end_time, timedelta):
                end_time = (datetime.min + end_time).time()

            slot_start = datetime.combine(available_date, start_time)
            slot_end = datetime.combine(available_date, end_time)

            if not (slot_start <= requested_time < slot_end):
                print("Requested time is outside available slot.")
                return

            requested_end = requested_time + timedelta(minutes=service_duration)

            for appt in booked_appointments:
                appt_start = appt['requested_time']
                appt_duration = appt[service_time_map[appt['service_type']]]
                if appt_duration is None:
                    continue
                appt_end = appt_start + timedelta(minutes=appt_duration)
                if not (requested_end <= appt_start or requested_time >= appt_end):
                    print("This time slot is already booked. Please choose another time.")
                    return

            query = """
            INSERT INTO appointment_requests (user_id, shop_id, service_type, requested_time, created_at)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (user['id'], shop_id, service_type, requested_time, datetime.now()))
            conn.commit()
            print("Appointment request submitted successfully!")
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
        except ValueError as ve:
            print(f"Error: {ve}")
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def view_appointment_status(user):
        conn = DatabaseConfig.connect_db()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
            SELECT ar.id, rs.username as shop_name, ar.service_type, ar.requested_time, ar.status
            FROM appointment_requests ar
            JOIN repair_shops rs ON ar.shop_id = rs.id
            WHERE ar.user_id = %s
            ORDER BY ar.created_at DESC
            """
            cursor.execute(query, (user['id'],))
            appointments = cursor.fetchall()

            if not appointments:
                print("No appointment requests found.")
                return

            print("\n--- Your Appointment Requests ---")
            for appt in appointments:
                print(f"Request ID: {appt['id']}")
                print(f"Shop: {appt['shop_name']}")
                print(f"Service: {appt['service_type'].replace('_', ' ').title()}")
                print(f"Time: {appt['requested_time']}")
                print(f"Status: {appt['status'].title()}")
                print("---")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()