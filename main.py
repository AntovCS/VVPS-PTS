from user_manager import UserManager
from repair_shop_manager import RepairShopManager
from feedback_manager import FeedbackManager
from appointment_manager import AppointmentManager
from admin_manager import AdminManager

class CarRepairApp:
    @staticmethod
    def main():
        while True:
            print("\n--- Car Repair App ---")
            print("1. Register")
            print("2. Login")
            print("3. Exit")
            choice = input("Select option: ").strip()

            if choice == '1':
                UserManager.register()
            elif choice == '2':
                user, role = UserManager.login()
                if user:
                    while True:
                        if role == 'user':
                            print("\n--- User Menu ---")
                            print("1. List repair shops")
                            print("2. Update car info")
                            print("3. Rate repair shop")
                            print("4. Submit feedback")
                            print("5. Request appointment")
                            print("6. View appointment status")
                            print("7. Logout")
                            user_choice = input("Select option: ").strip()
                            if user_choice == '1':
                                RepairShopManager.list_repair_shops(user)
                            elif user_choice == '2':
                                RepairShopManager.update_car_info(user)
                            elif user_choice == '3':
                                RepairShopManager.rate_repair_shop(user)
                            elif user_choice == '4':
                                FeedbackManager.submit_feedback(user)
                            elif user_choice == '5':
                                AppointmentManager.request_appointment(user)
                            elif user_choice == '6':
                                AppointmentManager.view_appointment_status(user)
                            elif user_choice == '7':
                                break
                            else:
                                print("Invalid option.")
                        elif role == 'repair_shop':
                            print("\n--- Repair Shop Menu ---")
                            print("1. View rating")
                            print("2. Update prices and times")
                            print("3. Manage availability")
                            print("4. View appointment requests")
                            print("5. Logout")
                            shop_choice = input("Select option: ").strip()
                            if shop_choice == '1':
                                RepairShopManager.view_shop_rating(user)
                            elif shop_choice == '2':
                                RepairShopManager.update_shop_prices(user)
                            elif shop_choice == '3':
                                RepairShopManager.manage_shop_availability(user)
                            elif shop_choice == '4':
                                RepairShopManager.view_appointment_requests(user)
                            elif shop_choice == '5':
                                break
                            else:
                                print("Invalid option.")
                        elif role == 'admin':
                            print("\n--- Admin Menu ---")
                            print("1. Run queries")
                            print("2. Logout")
                            admin_choice = input("Select option: ").strip()
                            if admin_choice == '1':
                                AdminManager.admin_queries()
                            elif admin_choice == '2':
                                break
                            else:
                                print("Invalid option.")
            elif choice == '3':
                print("Goodbye!")
                break
            else:
                print("Invalid option.")

if __name__ == "__main__":
    CarRepairApp.main()