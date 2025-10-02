import json
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.table import Table
from rich.box import MINIMAL_DOUBLE_HEAD
from app.client.engsel import get_otp, submit_otp
from app.menus.util import clear_screen
from app.menus.anu_util import pause, print_panel
from app.service.auth import AuthInstance
from app.config.theme_config import get_theme
from app.service.unlock import load_unlock_status, save_unlock_status

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
        Align.center("🔐 Login ke myXL CLI\nMasukkan nomor XL, Support 08xx/ 628xx/ +628xx\nKetik [bold red]00[/] untuk membatalkan", vertical="middle"),
        border_style=theme["border_info"],
        style=theme["text_title"],
        padding=(1, 2),
        expand=True
    ))

    raw_input = console.input(f"[{theme['text_sub']}]Nomor:[/{theme['text_sub']}] ").strip()
    if raw_input == "00":
        print_panel("ℹ️ Dibatalkan", "Login dibatalkan oleh pengguna.")
        #pause()
        return None, None

    phone_number = normalize_number(raw_input)

    if len(phone_number) < 10 or len(phone_number) > 14:
        print_panel("⚠️ Error", "Nomor tidak valid. Pastikan di input dengan benar.")
        pause()
        return None, None

    try:
        console.print(f"[{theme['text_sub']}]Mengirim OTP...[/]")
        subscriber_id = get_otp(phone_number)
        if not subscriber_id:
            print_panel("⚠️ Error", "Gagal mengirim OTP.")
            pause()
            return None, None

        print_panel("✅ Info", "OTP berhasil dikirim ke nomor Anda.")
        otp = console.input(f"[{theme['text_sub']}]Masukkan OTP (6 digit):[/{theme['text_sub']}] ").strip()

        if otp == "00":
            print_panel("ℹ️ Dibatalkan", "Login dibatalkan oleh pengguna.")
            #pause()
            return None, None

        if not otp.isdigit() or len(otp) != 6:
            print_panel("⚠️ Error", "OTP tidak valid. Harus 6 digit angka.")
            pause()
            return None, None

        console.print(f"[{theme['text_sub']}]Memverifikasi OTP...[/]")
        tokens = submit_otp(api_key, phone_number, otp)
        if not tokens:
            print_panel("⚠️ Error", "Gagal login. Periksa OTP dan coba lagi.")
            pause()
            return None, None

        AuthInstance.add_refresh_token(int(phone_number), tokens["refresh_token"])
        print_panel("✅ Berhasil", "Login berhasil!")
        return phone_number, tokens["refresh_token"]

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
    add_user = False

    MAX_FREE_ACCOUNTS = 2
    UNLOCK_CODE = "@barbex_id-vip"
    unlock_data = load_unlock_status()
    is_unlocked = unlock_data.get("is_unlocked", False)  # cache di memori

    while in_account_menu:
        clear_screen()

        if add_user and len(users) >= MAX_FREE_ACCOUNTS and not is_unlocked:
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
                add_user = False
                continue
            else:
                save_unlock_status(True)
                is_unlocked = True
                print_panel("✅ Berhasil", "Akses akun tambahan telah dibuka.")
                pause()

        if AuthInstance.get_active_user() is None or add_user:
            number, refresh_token = login_prompt(AuthInstance.api_key)
            if not refresh_token:
                print_panel("ℹ️ Dibatalkan", "Login dibatalkan. Kembali ke menu akun.")
                pause()
                add_user = False  # pastikan tidak lanjut login
                continue


            AuthInstance.add_refresh_token(int(number), refresh_token)
            AuthInstance.load_tokens()
            users = AuthInstance.refresh_tokens
            active_user = AuthInstance.get_active_user()

            add_user = False
            continue

        # Tampilkan akun tersimpan
        console.print(Panel(
            Align.center("📱 Akun Tersimpan", vertical="middle"),
            border_style=theme["border_info"],
            padding=(1, 2),
            expand=True
        ))

        account_table = Table(box=MINIMAL_DOUBLE_HEAD, expand=True)
        account_table.add_column("No", justify="right", style=theme["text_key"], width=6)
        account_table.add_column("Nomor XL", style=theme["text_body"])
        account_table.add_column("Status", style=theme["text_sub"], justify="center")

        if not users:
            account_table.add_row("-", "[dim]Tidak ada akun tersimpan[/]", "")
        else:
            for idx, user in enumerate(users):
                is_active = active_user and user["number"] == active_user["number"]
                status = "✅ Aktif" if is_active else "-"
                account_table.add_row(str(idx + 1), str(user["number"]), status)

        console.print(Panel(account_table, border_style=theme["border_primary"], padding=(0, 1), expand=True))

        # Tampilkan menu perintah
        command_table = Table(show_header=False, box=MINIMAL_DOUBLE_HEAD, expand=True)
        command_table.add_column("Kode", justify="right", style=theme["text_key"], width=6)
        command_table.add_column("Pilih Aksi", style=theme["text_body"])
        command_table.add_row("⚠️", "Pilih nomor akun, untuk berganti")
        command_table.add_row("T", "Tambah akun")
        command_table.add_row("H", f"[{theme['text_err']}]Hapus akun tersimpan[/]")
        command_table.add_row("00", f"[{theme['text_sub']}]Kembali ke menu utama[/]")

        console.print(Panel(command_table, border_style=theme["border_info"], padding=(0, 1), expand=True))

        input_str = console.input(f"[{theme['text_sub']}]Pilihan:[/{theme['text_sub']}] ").strip()

        if input_str.upper() == "T":
            add_user = True
            continue

        elif input_str.upper() == "H":
            if not users:
                print_panel("⚠️ Error", "Tidak ada akun untuk dihapus.")
                pause()
                continue

            console.print(f"[{theme['text_sub']}]Masukkan nomor akun yang ingin dihapus (1 - {len(users)}):[/{theme['text_sub']}]")
            nomor_input = console.input(f"[{theme['text_sub']}]Nomor:[/{theme['text_sub']}] ").strip()

            if not nomor_input.isdigit() or not (1 <= int(nomor_input) <= len(users)):
                print_panel("⚠️ Error", "Input tidak valid. Silakan masukkan nomor yang sesuai.")
                pause()
                continue

            selected_user = users[int(nomor_input) - 1]
            confirm = console.input(
                f"[{theme['text_sub']}]Yakin ingin hapus akun {selected_user['number']}? (y/n):[/{theme['text_sub']}] "
            ).strip().lower()

            if confirm == "y":
                AuthInstance.remove_refresh_token(selected_user["number"])
                users = AuthInstance.refresh_tokens
                active_user = AuthInstance.get_active_user()
                print_panel("✅ Info", f"Akun {selected_user['number']} berhasil dihapus.")
                pause()
            else:
                print_panel("ℹ️ Info", "Penghapusan akun dibatalkan.")
                pause()
            continue

        elif input_str == "00":
            in_account_menu = False
            return active_user["number"] if active_user else None

        elif input_str.isdigit() and 1 <= int(input_str) <= len(users):
            selected_user = users[int(input_str) - 1]
            return selected_user['number']

        else:
            print_panel("⚠️ Error", "Input tidak valid. Silakan coba lagi.")
            pause()
            continue
