from app.client.engsel import get_otp, submit_otp
from app.menus.util import clear_screen, pause
from app.service.auth import AuthInstance
from app.theme import _c, console
from rich.table import Table
from rich.panel import Panel
from rich.box import MINIMAL_DOUBLE_HEAD

def pesan_error(msg):
    console.print(f"[{_c('text_err')}]{msg}[/{_c('text_err')}]")

def pesan_sukses(msg):
    console.print(f"[{_c('text_ok')}]{msg}[/{_c('text_ok')}]")

def pesan_info(msg):
    console.print(f"[{_c('text_warn')}]{msg}[/{_c('text_warn')}]")

def login_prompt(api_key: str):
    clear_screen()
    console.print(Panel("Login ke MyXL", title="[bold]Login[/]", border_style=_c("border_primary"), padding=(1, 4), expand=True))
    phone_number = console.input(f"[{_c('text_key')}]Masukkan nomor XL (628xxx):[/{_c('text_key')}] ").strip()

    if not phone_number.startswith("628") or not phone_number.isdigit() or not (10 <= len(phone_number) <= 14):
        pesan_error("Nomor tidak valid.")
        pause()
        return None, None

    try:
        subscriber_id = get_otp(phone_number)
        if not subscriber_id:
            pesan_error("Gagal mengirim OTP.")
            pause()
            return None, None

        pesan_info("OTP dikirim. Silakan cek SMS.")
        otp = console.input(f"[{_c('text_key')}]Masukkan OTP (6 digit):[/{_c('text_key')}] ").strip()

        if not otp.isdigit() or len(otp) != 6:
            pesan_error("OTP tidak valid.")
            pause()
            return None, None

        tokens = submit_otp(api_key, phone_number, otp)
        if not tokens:
            pesan_error("Login gagal. Periksa OTP.")
            pause()
            return None, None

        pesan_sukses("Login berhasil!")
        return phone_number, tokens["refresh_token"]
    except Exception as e:
        pesan_error(f"Error saat login: {e}")
        pause()
        return None, None

def show_account_menu():
    clear_screen()
    AuthInstance.load_tokens()
    users = AuthInstance.refresh_tokens
    active_user = AuthInstance.get_active_user()

    in_account_menu = True
    add_user = False

    while in_account_menu:
        clear_screen()

        if active_user is None or add_user:
            number, refresh_token = login_prompt(AuthInstance.api_key)
            if not refresh_token:
                pesan_error("Gagal menambah akun.")
                pause()
                continue

            AuthInstance.add_refresh_token(int(number), refresh_token)
            AuthInstance.load_tokens()
            users = AuthInstance.refresh_tokens
            active_user = AuthInstance.get_active_user()
            add_user = False
            continue

        # Tabel akun tersimpan
        akun_table = Table(box=MINIMAL_DOUBLE_HEAD, expand=True)
        akun_table.add_column("", justify="right", style=_c("text_number"), width=6)
        akun_table.add_column("Nomor", style=_c("text_body"))

        if not users:
            akun_table.add_row("-", "Belum ada akun.")
        else:
            for idx, user in enumerate(users):
                is_active = active_user and user["number"] == active_user["number"]
                marker = f"[{_c('text_sub')}] (Aktif)[/{_c('text_sub')}]" if is_active else ""
                akun_table.add_row(str(idx + 1), f"{user['number']}{marker}")

        akun_panel = Panel(
            akun_table,
            title="",  # judul
            border_style=_c("border_info"),
            padding=(0, 0),
            expand=True
        )
        console.print(akun_panel)

        # Tabel command
        cmd_table = Table(show_header=False, box=MINIMAL_DOUBLE_HEAD, expand=True)
        cmd_table.add_column("Kode", justify="right", style=_c("text_number"), width=6)
        cmd_table.add_column("Deskripsi", style=_c("text_body"))
        cmd_table.add_row("0", "Tambah Akun")
        cmd_table.add_row("00", "Kembali ke Menu Utama")
        cmd_table.add_row("99", "Hapus Akun Aktif")
        cmd_table.add_row("-", "Masukkan nomor akun untuk berganti")

        cmd_panel = Panel(
            cmd_table,
            title="",  # judul
            border_style=_c("border_primary"),
            padding=(0, 0),
            expand=True
        )
        console.print(cmd_panel)

        input_str = console.input(f"[{_c('text_sub')}]Pilihan:[/{_c('text_sub')}] ").strip()

        if input_str == "00":
            in_account_menu = False
            return active_user["number"] if active_user else None
        elif input_str == "0":
            add_user = True
            continue
        elif input_str == "99":
            if not active_user:
                pesan_error("Tidak ada akun aktif.")
                pause()
                continue
            confirm = console.input(f"[{_c('text_warn')}]Yakin hapus akun {active_user['number']}? (y/n):[/{_c('text_warn')}] ").strip().lower()
            if confirm == 'y':
                AuthInstance.remove_refresh_token(active_user["number"])
                AuthInstance.load_tokens()
                users = AuthInstance.refresh_tokens
                active_user = AuthInstance.get_active_user()
                pesan_sukses("Akun dihapus.")
            else:
                pesan_info("Penghapusan dibatalkan.")
            pause()
            continue
        elif input_str.isdigit() and 1 <= int(input_str) <= len(users):
            selected_user = users[int(input_str) - 1]
            return selected_user['number']
        else:
            pesan_error("Input tidak valid.")
            pause()
            continue
