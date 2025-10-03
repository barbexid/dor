from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.table import Table
from rich.text import Text
from rich.box import MINIMAL_DOUBLE_HEAD

from app.client.engsel2 import get_otp, submit_otp
from app.service.auth import AuthInstance
from app.service.unlock import load_unlock_status, save_unlock_status
from app.config.theme_config import get_theme
from app.menus.util import clear_screen
from app.menus.anu_util import pause, print_panel, live_loading

console = Console()

def normalize_number(raw_input: str) -> str:
    raw_input = raw_input.strip()
    if raw_input.startswith("08"):
        return "628" + raw_input[2:]
    elif raw_input.startswith("+628"):
        return "628" + raw_input[4:]
    elif raw_input.startswith("628"):
        return raw_input
    return raw_input

def login_prompt(api_key: str):
    clear_screen()
    theme = get_theme()

    console.print(Panel(
        Align.center("🔐 Login ke myXL CLI\nMasukkan nomor XL, Support 08xx/628xx/+628xx", vertical="middle"),
        border_style=theme["border_info"],
        style=theme["text_title"],
        padding=(1, 2),
        expand=True
    ))

    while True:
        raw_input = console.input(f"[{theme['text_sub']}]Masukan nomor XL:[/{theme['text_sub']}] ").strip()
        if raw_input == "00":
            print_panel("ℹ️ Dibatalkan", "Login dibatalkan oleh pengguna.")
            return None, None

        phone_number = normalize_number(raw_input)
        if len(phone_number) < 10 or len(phone_number) > 14:
            print_panel("⚠️ Error", "Nomor tidak valid. Coba lagi atau ketik 00 untuk batal.")
            continue
        break

    try:
        subscriber_id = live_loading(
            task=lambda: get_otp(phone_number),
            text="Mengirim OTP...",
            theme=theme
        )
        if not subscriber_id:
            print_panel("⚠️ Error", "Gagal mengirim OTP.")
            pause()
            return None, None

        print_panel("✅ Info", "OTP berhasil dikirim ke nomor Anda.")

        max_attempts = 5
        attempts = 0

        while attempts < max_attempts:
            otp = console.input(f"[{theme['text_sub']}]Masukkan OTP (percobaan {attempts+1}/5):[/{theme['text_sub']}] ").strip()
            if otp == "00":
                print_panel("ℹ️ Dibatalkan", "Login dibatalkan oleh pengguna.")
                return None, None
            if not otp.isdigit() or len(otp) != 6:
                print_panel("⚠️ Error", "OTP tidak valid. Harus 6 digit angka.")
                attempts += 1
                continue

            tokens = live_loading(
                task=lambda: submit_otp(api_key, phone_number, otp),
                text="Memverifikasi OTP...",
                theme=theme
            )
            if tokens:
                AuthInstance.add_refresh_token(int(phone_number), tokens["refresh_token"], name="Tanpa Nama")
                print_panel("✅ Berhasil", "Login berhasil!")
                return phone_number, tokens["refresh_token"]
            else:
                print_panel("⚠️ Error", "OTP salah atau sudah kedaluwarsa.")
                attempts += 1

        print_panel("❌ Gagal", "Melebihi batas percobaan OTP (5x). Silakan kirim ulang OTP.")
        pause()
        return None, None

    except Exception:
        print_panel("⚠️ Error", "Terjadi kesalahan saat login.")
        pause()
        return None, None

def show_account_menu():
    clear_screen()
    theme = get_theme()
    AuthInstance.load_tokens()
    users = AuthInstance.refresh_tokens
    active_user = AuthInstance.get_active_user()

    in_account_menu = True
    is_adding_user = False

    MAX_FREE_ACCOUNTS = 2
    UNLOCK_CODE = "@barbex_id"
    unlock_data = load_unlock_status()
    is_unlocked = unlock_data.get("is_unlocked", False)

    while in_account_menu:
        clear_screen()

        if is_adding_user and len(users) >= MAX_FREE_ACCOUNTS and not is_unlocked:
            console.print(Panel(
                Align.center("🚫 Batas maksimal akun sudah tercapai.\nMasukkan kode unlock untuk menambah lebih banyak akun.", vertical="middle"),
                border_style=theme["border_warning"],
                padding=(1, 2),
                expand=True
            ))

            unlock_input = console.input(f"[{theme['text_sub']}]Kode Unlock:[/{theme['text_sub']}] ").strip()
            if unlock_input != UNLOCK_CODE:
                print_panel("⚠️ Gagal", "Kode unlock salah. Tidak dapat menambah akun.")
                pause()
                is_adding_user = False
                continue
            else:
                live_loading(
                    task=lambda: save_unlock_status(True),
                    text="Menyimpan status unlock...",
                    theme=theme
                )
                is_unlocked = True
                print_panel("✅ Berhasil", "Akses akun tambahan telah dibuka.")
                pause()

        if AuthInstance.get_active_user() is None or is_adding_user:
            number, refresh_token = login_prompt(AuthInstance.api_key)
            if not refresh_token:
                print_panel("ℹ️ Dibatalkan", "Login dibatalkan. Kembali ke menu akun.")
                pause()
                is_adding_user = False
                continue

            AuthInstance.add_refresh_token(int(number), refresh_token)
            AuthInstance.load_tokens()
            users = AuthInstance.refresh_tokens
            active_user = AuthInstance.get_active_user()
            is_adding_user = False
            continue

        console.print(Panel(
            Align.center("📱 Akun Tersimpan", vertical="middle"),
            border_style=theme["border_info"],
            padding=(1, 2),
            expand=True
        ))

        account_table = Table(box=MINIMAL_DOUBLE_HEAD, expand=True)
        
        #account_table.add_column("No", justify="right", style=theme["text_key"], width=6)
        #account_table.add_column("Nomor XL", style=theme["text_body"])
        #account_table.add_column("Status", style=theme["text_sub"], justify="center")

        account_table.add_column("No", justify="right", style=theme["text_key"], width=6)
        account_table.add_column("Nama", style=theme["text_body"])
        account_table.add_column("Nomor XL", style=theme["text_body"])
        account_table.add_column("Status", style=theme["text_sub"], justify="center")

        if not users:
            account_table.add_row("-", "[dim]Tidak ada akun tersimpan[/]", "")
        else:
            for idx, user in enumerate(users):
                is_active = active_user and user["number"] == active_user["number"]
                status = "✅ Aktif" if is_active else "❌"
                account_table.add_row(
                    str(idx + 1),
                    user.get("name", "Tanpa Nama"),
                    str(user["number"]),
                    status
                )

        console.print(Panel(account_table, border_style=theme["border_primary"], padding=(0, 1), expand=True))

        command_table = Table(show_header=False, box=MINIMAL_DOUBLE_HEAD, expand=True)
        command_table.add_column("Kode", justify="right", style=theme["text_key"], width=8)
        command_table.add_column("Pilih Aksi", style=theme["text_body"])
        command_table.add_row(f"(1 - {len(users)})", "Pilih nomor akun untuk berganti")
        command_table.add_row("T", "Tambah akun")
        command_table.add_row("E", "Edit nama akun")
        command_table.add_row("H", f"[{theme['text_err']}]Hapus akun tersimpan[/]")
        command_table.add_row("00", f"[{theme['text_sub']}]Kembali ke menu utama[/]")

        console.print(Panel(command_table, border_style=theme["border_info"], padding=(0, 1), expand=True))

        user_input = console.input(f"[{theme['text_sub']}]Pilihan:[/{theme['text_sub']}] ").strip()

        if user_input == "00":
            live_loading(text="Kembali ke menu utama...", theme=theme)
            return active_user["number"] if active_user else None

        elif user_input.upper() == "T":
            is_adding_user = True

        elif user_input.upper() == "E":
            if not users:
                print_panel("⚠️ Error", "Tidak ada akun untuk diedit.")
                pause()
                continue

            nomor_input = console.input(f"[{theme['text_sub']}]Nomor akun yang ingin diedit (1 - {len(users)}):[/{theme['text_sub']}] ").strip()
            if nomor_input == "00":
                print_panel("ℹ️ Dibatalkan", "Edit nama akun dibatalkan.")
                pause()
                continue

            if nomor_input.isdigit():
                nomor = int(nomor_input)
                if 1 <= nomor <= len(users):
                    selected_user = users[nomor - 1]
                    new_name = console.input(f"[{theme['text_sub']}]Masukkan nama baru untuk akun {selected_user['number']}:[/{theme['text_sub']}] ").strip()
                    if new_name:
                        AuthInstance.edit_account_name(selected_user["number"], new_name)
                        AuthInstance.load_tokens()
                        users = AuthInstance.refresh_tokens
                        active_user = AuthInstance.get_active_user()
                        print_panel("✅ Berhasil", f"Nama akun berhasil diubah menjadi '{new_name}'.")
                        pause()
                    else:
                        print_panel("⚠️ Error", "Nama tidak boleh kosong.")
                        pause()
                else:
                    print_panel("⚠️ Error", f"Nomor akun di luar jangkauan (1 - {len(users)}).")
                    pause()
            else:
                print_panel("⚠️ Error", "Input tidak valid. Masukkan angka atau 00 untuk batal.")
                pause()


        elif user_input.upper() == "H":
            if not users:
                print_panel("⚠️ Error", "Tidak ada akun untuk dihapus.")
                pause()
                continue

            nomor_input = console.input(f"[{theme['text_sub']}]Nomor akun yang ingin dihapus (1 - {len(users)}):[/{theme['text_sub']}] ").strip()
            if nomor_input == "00":
                print_panel("ℹ️ Dibatalkan", "Penghapusan akun dibatalkan.")
                pause()
                continue

            if nomor_input.isdigit():
                nomor = int(nomor_input)
                if 1 <= nomor <= len(users):
                    selected_user = users[nomor - 1]
                    confirm = console.input(
                        f"[{theme['text_sub']}]Yakin ingin hapus akun {selected_user['number']}? (y/n):[/{theme['text_sub']}] "
                    ).strip().lower()
                    if confirm == "y":
                        live_loading(
                            task=lambda: AuthInstance.remove_refresh_token(selected_user["number"]),
                            text=f"Menghapus akun {selected_user['number']}...",
                            theme=theme
                        )
                        AuthInstance.load_tokens()
                        users = AuthInstance.refresh_tokens
                        active_user = AuthInstance.get_active_user()
                        print_panel("✅ Info", f"Akun {selected_user['number']} berhasil dihapus.")
                        pause()
                        continue
                    else:
                        print_panel("ℹ️ Info", "Penghapusan akun dibatalkan.")
                        pause()
                else:
                    print_panel("⚠️ Error", f"Nomor akun di luar jangkauan (1 - {len(users)}).")
                    pause()
            else:
                print_panel("⚠️ Error", "Input tidak valid. Masukkan angka atau 00 untuk batal.")
                pause()

        elif user_input.isdigit():
            nomor = int(user_input)
            if 1 <= nomor <= len(users):
                selected_user = users[nomor - 1]
                return selected_user['number']
            else:
                print_panel("⚠️ Error", f"Nomor akun di luar jangkauan (1 - {len(users)}).")
                pause()

        else:
            print_panel("⚠️ Error", "Input tidak dikenali. Silakan pilih opsi yang tersedia.")
            pause()
