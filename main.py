from dotenv import load_dotenv
load_dotenv()

import sys
from datetime import datetime
from rich.panel import Panel
from rich.table import Table
from rich.box import MINIMAL_DOUBLE_HEAD
from rich.align import Align

from app.menus.util import clear_screen, pause
from app.client.engsel import *
#from app.client.engsel import get_balance
from app.service.auth import AuthInstance
from app.menus.bookmark import show_bookmark_menu
from app.menus.account import show_account_menu
from app.menus.package import fetch_my_packages, get_packages_by_family, show_package_details
from app.menus.hot import show_hot_menu, show_hot_menu2
from app.menus.anu import show_anu_menu
from app.service.sentry import enter_sentry_mode
from app.menus.package import fetch_my_packages, get_packages_by_family
from app.menus.hot import show_hot_menu
from app.theme import _c, console, set_theme, get_active_theme_name, THEMES

# ========== Utility Pesan ==========
def pesan_error(msg):
    console.print(f"[{_c('text_err')}]{msg}[/{_c('text_err')}]")

def pesan_sukses(msg):
    console.print(f"[{_c('text_ok')}]{msg}[/{_c('text_ok')}]")

def pesan_info(msg):
    console.print(f"[{_c('text_warn')}]{msg}[/{_c('text_warn')}]")

def _print_centered_panel(renderable, title="", border_style=""):
    panel = Panel(
        renderable,
        title=title,
        border_style=border_style,
        padding=(0, 0),
        expand=True,
        title_align="center"
    )
    console.print(panel)

def show_banner():
    clear_screen()
    banner_text = f"[{_c('text_title')}]Selamat Datang di MyXL CLI v8.7.0[/]"
    centered_text = Align.center(banner_text)
    panel = Panel(
        centered_text,
        title="TOOLS INI GRATIS !!!",
        title_align="center",
        border_style=_c("border_primary"),
        padding=(1, 4),
        expand=True
    )
    console.print(panel)

def show_main_menu(number, balance, balance_expired_at):
    clear_screen()
    show_banner()
    expired_at_dt = datetime.fromtimestamp(balance_expired_at).strftime("%Y-%m-%d %H:%M:%S")

    info = Table.grid(padding=(0, 1))
    info.add_column(justify="right", style=_c("text_sub"))
    info.add_column(style=_c("text_body"))
    info.add_row("Nomor", f"[{_c('text_value')}]{number}[/]")
    info.add_row("Pulsa", f"[{_c('text_money')}]Rp {balance:,}[/]")
    info.add_row("Masa Aktif", f"[{_c('text_date')}]{expired_at_dt}[/]")
    _print_centered_panel(info, title=f"[{_c('text_title')}]✨Informasi Akun✨[/]", border_style=_c("border_info"))

    menu = Table(show_header=False, box=MINIMAL_DOUBLE_HEAD, padding=(0, 1), expand=True)
    menu.add_column("key", justify="right", style=_c("text_number"), no_wrap=True, width=4)
    menu.add_column("desc", style=_c("text_body"))
    menu.add_row("[bold]1[/]", "🔑 Login/Ganti akun")
    menu.add_row("[bold]2[/]", "📦 Lihat Paket Saya")
    menu.add_row("[bold]3[/]", "🔥 Beli Paket HOT")
    menu.add_row("[bold]4[/]", "🔥 Beli Paket HOT-2")
    menu.add_row("[bold]5[/]", "🛒 Beli Paket Lainnya..")
    menu.add_row("[bold]6[/]", "🏠 Input Family Code")
    menu.add_row("[bold]7[/]", "🏢 Input Family Code (Enterprise)")
    #menu.add_row("[bold] [/]", " ")
    menu.add_row("[bold]00[/]", "⭐ Bookmark Paket")
    menu.add_row("[bold]69[/]", f"[{_c('text_sub')}]🎨 Ganti Gaya[/]")
    menu.add_row("[bold]99[/]", f"[{_c('text_err')}]⛔ Tutup aplikasi[/]")
    _print_centered_panel(menu, title=f"[{_c('text_title')}]✨Menu Utama✨[/]", border_style=_c("border_primary"))

def menu_ganti_theme():
    clear_screen()
    theme_names = list(THEMES.keys())
    active_theme = get_active_theme_name()

    table = Table(box=MINIMAL_DOUBLE_HEAD, expand=True)
    table.add_column("", justify="right", style=_c("text_number"), width=6)
    table.add_column("Nama Tema", style=_c("text_body"))
    table.add_column("Preview", style=_c("text_body"))

    for idx, name in enumerate(theme_names, 1):
        preset = THEMES[name]
        preview = (
            f"[{preset['border_primary']}]■[/] "
            f"[{preset['border_info']}]■[/] "
            f"[{preset['border_success']}]■[/] "
            f"[{preset['border_error']}]■[/] "
            f"[{preset['text_title']}]A[/]"
        )
        aktif = f"[{_c('text_sub')}] (aktif)[/{_c('text_sub')}]" if name == active_theme else ""
        table.add_row(str(idx), f"{name}{aktif}", preview)

    panel = Panel(table, title="", border_style=_c("border_info"), padding=(1, 0), expand=True)
    console.print(panel)

    pilihan = console.input(f"\n[{_c('text_sub')}]Masukkan nomor tema yang diinginkan:[/{_c('text_sub')}] ").strip()
    try:
        idx = int(pilihan) - 1
        if idx < 0 or idx >= len(theme_names):
            pesan_error("Pilihan tema tidak valid.")
        else:
            nama_tema = theme_names[idx]
            set_theme(nama_tema)
            pesan_sukses(f"Tema berhasil diganti ke '{nama_tema}'.")
    except Exception:
        pesan_error("Input tidak valid.")
    pause()

def main():
    while True:
        active_user = AuthInstance.get_active_user()
        if active_user:
            try:
                balance = get_balance(AuthInstance.api_key, active_user["tokens"]["id_token"])
                if balance is None:
                    pesan_error("Gagal mengambil data saldo: data tidak ditemukan atau API error.")
                    pause()
                    continue
                balance_remaining = balance.get("remaining", 0)
                balance_expired_at = balance.get("expired_at", 0)
            except Exception as e:
                pesan_error(f"Gagal mengambil data saldo: {e}")
                pause()
                continue

            show_main_menu(active_user["number"], balance_remaining, balance_expired_at)

            choice = console.input(f"[{_c('text_sub')}]Pilih menu:[/{_c('text_sub')}] ").strip()
            if choice == "1":
                selected_user_number = show_account_menu()
                if selected_user_number:
                    AuthInstance.set_active_user(selected_user_number)
                    pesan_sukses("Akun berhasil diganti.")
                else:
                    pesan_error("Tidak ada user yang dipilih atau gagal memuat user.")
            elif choice == "2":
                try:
                    fetch_my_packages()
                except Exception as e:
                    pesan_error(f"Gagal menampilkan paket: {e}")
            elif choice == "3":
                try:
                    show_hot_menu()
                except Exception as e:
                    pesan_error(f"Gagal menampilkan menu HOT: {e}")
            elif choice == "4":
                try:
                    show_hot_menu2()
                except Exception as e:
                    pesan_error(f"Gagal menampilkan menu HOT-2: {e}")
            elif choice == "5":
                try:
                    show_anu_menu()
                except Exception as e:
                    pesan_error(f"Gagal menampilkan paket lainnya: {e}")
            elif choice == "6":
                family_code = console.input(f"[{_c('text_sub')}]Masukkan family code (atau '99' untuk batal):[/{_c('text_sub')}] ").strip()
                if family_code != "99":
                    try:
                        get_packages_by_family(family_code)
                    except Exception as e:
                        pesan_error(f"Gagal menampilkan paket: {e}")
                else:
                    pesan_info("Aksi dibatalkan.")
            elif choice == "7":
                family_code = console.input(f"[{_c('text_sub')}]Masukkan family code (Enterprise):[/{_c('text_sub')}] ").strip()
                if family_code != "99":
                    try:
                        get_packages_by_family(family_code, is_enterprise=True)
                    except Exception as e:
                        pesan_error(f"Gagal menampilkan paket enterprise: {e}")
                else:
                    pesan_info("Aksi dibatalkan.")
            elif choice == "00":
                try:
                    show_bookmark_menu()
                except Exception as e:
                    pesan_error(f"Gagal menampilkan menu bookmark: {e}")
            elif choice == "69":
                menu_ganti_theme()
            elif choice == "99":
                pesan_info("Keluar dari aplikasi.")
                sys.exit(0)
            else:
                pesan_error("Pilihan tidak valid. Silakan coba lagi.")
                pause()
        else:
            pesan_info("Silakan login terlebih dahulu.")
            selected_user_number = show_account_menu()
            if selected_user_number:
                AuthInstance.set_active_user(selected_user_number)
                pesan_sukses("Login berhasil.")
            else:
                pesan_error("Tidak ada user yang dipilih atau gagal memuat user.")
                pause()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pesan_info("Keluar dari aplikasi.")
    except Exception as e:
        pesan_error(f"Terjadi kesalahan: {e}")
