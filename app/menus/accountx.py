from app.client.engsel import get_otp, submit_otp
from app.menus.util import clear_screen, pause
from app.service.auth import AuthInstance
from app.service.unlock import load_unlock_status, save_unlock_status

MAX_FREE_ACCOUNTS = 2
UNLOCK_CODE = "@barbex_id"

def login_prompt(api_key: str):
    clear_screen()
    print("-------------------------------------------------------")
    print("-------------------- Login ke MyXL --------------------")
    print("-------------------------------------------------------")
    print("Masukan nomor XL Prabayar (Contoh 6281234567890):")
    phone_number = input("Nomor: ")

    if not phone_number.startswith("628") or len(phone_number) < 10 or len(phone_number) > 14:
        print("Nomor tidak valid. Pastikan nomor diawali dengan '628' dan memiliki panjang yang benar.")
        return None, None

    try:
        subscriber_id = get_otp(phone_number)
        if not subscriber_id:
            print("Gagal mengirim OTP.")
            pause()
            return None, None

        print("OTP Berhasil dikirim ke nomor Anda.")
        max_attempts = 5
        attempts = 0

        while attempts < max_attempts:
            otp = input(f"Masukkan OTP (percobaan {attempts+1}/5): ")
            if otp == "00":
                print("Login dibatalkan oleh pengguna.")
                pause()
                return None, None
            if not otp.isdigit() or len(otp) != 6:
                print("OTP tidak valid. Harus 6 digit angka.")
                attempts += 1
                continue

            tokens = submit_otp(api_key, phone_number, otp)
            if tokens:
                print("Berhasil login!")
                return phone_number, tokens["refresh_token"]
            else:
                print("OTP salah atau sudah kedaluwarsa.")
                attempts += 1

        print("Melebihi batas percobaan OTP (5x). Silakan kirim ulang OTP.")
        pause()
        return None, None

    except Exception:
        print("Terjadi kesalahan saat login.")
        pause()
        return None, None

def show_account_menu():
    clear_screen()
    AuthInstance.load_tokens()
    users = AuthInstance.refresh_tokens
    active_user = AuthInstance.get_active_user()

    unlock_data = load_unlock_status()
    is_unlocked = unlock_data.get("is_unlocked", False)

    in_account_menu = True
    add_user = False

    while in_account_menu:
        clear_screen()

        if add_user and len(users) >= MAX_FREE_ACCOUNTS and not is_unlocked:
            print("-------------------------------------------------------")
            print("-----   !!! Batas maksimal akun sudah tercapai.   -----")
            print(" Masukkan kode unlock untuk menambah lebih banyak akun.")
            print("-------------------------------------------------------")
            unlock_input = input("Kode Unlock: ").strip()
            if unlock_input != UNLOCK_CODE:
                print("Kode unlock salah. Tidak dapat menambah akun.")
                pause()
                add_user = False
                continue
            else:
                save_unlock_status(True)
                is_unlocked = True
                print("Akses akun tambahan telah dibuka.")
                pause()

        if AuthInstance.get_active_user() is None or add_user:
            number, refresh_token = login_prompt(AuthInstance.api_key)
            if not refresh_token:
                print("Login dibatalkan atau gagal.")
                pause()
                add_user = False
                continue

            AuthInstance.add_refresh_token(int(number), refresh_token)
            AuthInstance.load_tokens()
            users = AuthInstance.refresh_tokens
            active_user = AuthInstance.get_active_user()
            add_user = False
            continue

        print("-------------------------------------------------------")
        print("Akun Tersimpan: ")
        if not users:
            print("Tidak ada akun tersimpan.")
        else:
            for idx, user in enumerate(users):
                is_active = active_user and user["number"] == active_user["number"]
                status = f" ({'Aktif'})" if is_active else ""
                print(f"{idx + 1}. {user['number']}{status}")

        print("----------------------------------")
        print("Command:")
        print("0: Tambah Akun")
        print("00: Kembali ke menu utama")
        print("99: Hapus Akun aktif")
        print("Masukan nomor akun untuk berganti.")
        input_str = input("Pilihan: ").strip()

        if input_str == "00":
            in_account_menu = False
            return active_user["number"] if active_user else None
        elif input_str == "0":
            add_user = True
        elif input_str == "99":
            if not active_user:
                print("Tidak ada akun aktif untuk dihapus.")
                pause()
                continue
            confirm = input(f"Yakin ingin menghapus akun {active_user['number']}? (y/n): ").strip().lower()
            if confirm == "y":
                AuthInstance.remove_refresh_token(active_user["number"])
                AuthInstance.load_tokens()
                users = AuthInstance.refresh_tokens
                active_user = AuthInstance.get_active_user()
                print("Akun berhasil dihapus.")
                pause()
            else:
                print("Penghapusan akun dibatalkan.")
                pause()
        elif input_str.isdigit() and 1 <= int(input_str) <= len(users):
            selected_user = users[int(input_str) - 1]
            return selected_user['number']
        else:
            print("Input tidak valid. Silahkan coba lagi.")
            pause()
