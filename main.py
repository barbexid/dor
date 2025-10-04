from dotenv import load_dotenv

load_dotenv() 

import sys
from app.menus.util import clear_screen, pause
from app.client.engsel import *
from app.service.auth import AuthInstance
from app.menus.bookmark import show_bookmark_menu
from app.menus.accountx import show_account_menu
from app.menus.familysx import show_family_menu
from app.menus.package import fetch_my_packages, get_packages_by_family, show_package_details
from app.menus.hot import show_hot_menu, show_hot_menu2
from app.service.sentry import enter_sentry_mode

def show_main_menu(profile):
    clear_screen()
    #phone_number = number
    #remaining_balance = balance
    #expired_at = balance_expired_at
    expired_at_dt = datetime.fromtimestamp(profile["balance_expired_at"]).strftime("%Y-%m-%d %H:%M:%S")
    
    print("-------------------------------------------------------")
    print("Informasi Akun")
    print(f"Nomor: {profile['number']}")
    print(f"Type: {profile['subscription_type']}({profile['subscriber_id']})")
    print(f"Pulsa: Rp {profile['balance']}")
    print(f"Masa aktif: {expired_at_dt}")
    print("-------------------------------------------------------")
    print("Menu:")
    print("1. Login/Ganti akun")
    print("2. Lihat Paket Saya")
    print("3. Beli Paket 🔥 HOT 🔥")
    print("4. Beli Paket 🔥 HOT-2 🔥")
    print("5. Beli Paket Berdasarkan Family Code")
    print("6. Simpan/Kelola Family Code")
    print("00. Bookmark Paket")
    print("99. Tutup aplikasi")
    print("-------------------------------------------------------")

show_menu = True
def main():
    
    while True:
        active_user = AuthInstance.get_active_user()

        # Logged in
        if active_user is not None:
            balance = get_balance(AuthInstance.api_key, active_user["tokens"]["id_token"])
            balance_remaining = balance.get("remaining")
            balance_expired_at = balance.get("expired_at")

            profile_data = get_profile(AuthInstance.api_key, active_user["tokens"]["access_token"], active_user["tokens"]["id_token"])
            sub_id = profile_data["profile"]["subscriber_id"]
            sub_type = profile_data["profile"]["subscription_type"]
            print(f"Subscriber ID: {sub_id}, Type: {sub_type}")
            
            profile = {
                "number": active_user["number"],
                "subscriber_id": sub_id,
                "subscription_type": sub_type,
                "balance": balance_remaining,
                "balance_expired_at": balance_expired_at,
            }

            show_main_menu(profile)

            choice = input("Pilih menu: ")
            if choice == "1":
                selected_user_number = show_account_menu()
                if selected_user_number:
                    AuthInstance.set_active_user(selected_user_number)
                else:
                    print("No user selected or failed to load user.")
                continue
            elif choice == "2":
                fetch_my_packages()
                continue
            elif choice == "3":
                show_hot_menu()
            elif choice == "4":
                show_hot_menu2()
            elif choice == "5":
                family_code = input("Enter family code (or '99' to cancel): ")
                if family_code == "99":
                    continue
                get_packages_by_family(family_code)
            elif choice == "6":
                show_family_menu()
            elif choice == "00":
                show_bookmark_menu()
            elif choice == "99":
                print("Exiting the application.")
                sys.exit(0)
            elif choice == "t":
                res = get_package(
                    AuthInstance.api_key,
                    active_user["tokens"],
                    ""
                )
                print(json.dumps(res, indent=2))
                input("Press Enter to continue...")
                pass
            elif choice == "s":
                enter_sentry_mode()
            else:
                print("Invalid choice. Please try again.")
                pause()
        else:
            # Not logged in
            selected_user_number = show_account_menu()
            if selected_user_number:
                AuthInstance.set_active_user(selected_user_number)
            else:
                print("No user selected or failed to load user.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting the application.")
    # except Exception as e:
    #     print(f"An error occurred: {e}")
