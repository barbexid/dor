from dotenv import load_dotenv

load_dotenv()

import sys
import json
from datetime import datetime

from app.client.engsel2 import *
from app.service.auth import AuthInstance
from app.menus.bookmark2 import show_bookmark_menu
from app.menus.account2 import show_account_menu
from app.menus.package2 import (
    fetch_my_packages,
    get_packages_by_family,
    show_package_details,
)
from app.menus.hot2 import show_hot_menu, show_hot_menu2
from app.menus.familys import show_family_menu
from app.menus.barbex import show_barbex_main_menu
from app.service.sentry import enter_sentry_mode
from app.config.theme_config import (
    get_active_theme_name,
    set_theme,
    get_theme,
    get_all_presets,
)
from app.menus.anu_util import pause, print_panel, print_menu, get_rupiah
from app.menus.util import clear_screen
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich.box import MINIMAL_DOUBLE_HEAD
from rich.text import Text

console = Console()


def show_banner():
    clear_screen()
    theme = get_theme()
    terminal_width = console.size.width

    title_panel = Panel(
        Align.center(
            f"[bold {theme['text_title']}]Selamat Datang di myXL CLI v.8.7.0 gen.2[/]"
        ),
        style=theme["border_warning"],
        width=terminal_width,
        #title=f"[{theme['border_primary']}]FuyukiXT x Barbex_ID[/]",
        title_align="center",
        padding=(1, 4),
    )

    console.print(title_panel)


def show_main_menu(number, balance, display_quota, balance_expired_at):
    clear_screen()
    show_banner()

    theme = get_theme()
    expired_at_dt = datetime.fromtimestamp(balance_expired_at).strftime("%Y-%m-%d %H:%M:%S")

    # Panel informasi akun
    info_table = Table.grid(padding=(0, 1))
    info_table.add_column(justify="left", style=theme["text_body"])
    info_table.add_column(justify="left", style=theme["text_body"])
    info_table.add_row("Nomor", f": [bold {theme['text_body']}]{number}[/]")
    info_table.add_row("Pulsa", f": [{theme['text_money']}]{get_rupiah(balance)}[/]")
    info_table.add_row("Kuota", f": [{theme['text_body']}]{display_quota or '-'}[/]")
    info_table.add_row("Masa Aktif", f": [{theme['text_date']}]{expired_at_dt}[/]")

    info_panel = Panel(
        info_table,
        title=f"[{theme['text_title']}]✨ Informasi Akun ✨[/]",
        title_align="center",
        border_style=theme["border_info"],
        padding=(0, 2),
        expand=True,
    )
    console.print(info_panel)

    # Tabel menu utama 
    menu_table = Table(show_header=False, box=MINIMAL_DOUBLE_HEAD, expand=True)
    #menu_table.add_column("Kode", justify="right", width=6)  # tanpa style
    #menu_table.add_column("Aksi")  # tanpa style
    menu_table.add_column("Kode", justify="right", style=theme["text_key"], width=6)
    menu_table.add_column("Aksi", style=theme["text_body"])

    menu_table.add_row("1", "Login/Ganti akun")
    menu_table.add_row("2", "Lihat Paket Saya")
    menu_table.add_row("3", "Beli Paket HOT 🔥")
    menu_table.add_row("4", "Beli Paket HOT-2 🔥")
    menu_table.add_row("5", "Beli Paket Lainnya..")
    menu_table.add_row("6", "Daftar/Tambah Family Code")
    menu_table.add_row("7", "Beli Paket Berdasarkan Family Code")
    menu_table.add_row("00", f"[{theme['text_body']}]Bookmark Paket[/]")
    menu_table.add_row("69", f"[{theme['text_sub']}]Ganti Tema CLI[/]")
    menu_table.add_row("99", f"[{theme['text_err']}]Tutup aplikasi[/]")

    menu_panel = Panel(
        menu_table,
        title=f"[{theme['text_title']}]✨ Menu Utama ✨[/]",
        title_align="center",
        border_style=theme["border_primary"],
        padding=(0, 1),
        expand=True,
    )
    console.print(menu_panel)



def show_theme_menu():
    while True:
        clear_screen()
        theme = get_theme()
        presets = get_all_presets()

        theme_names = list(presets.keys())

        judul_panel = Panel(
            Align.center("🎨 Pilih Tema CLI", vertical="middle"),
            style=theme["text_title"],
            border_style=theme["border_info"],
            padding=(1, 2),
            expand=True,
        )
        console.print(judul_panel)

        table = Table(box=MINIMAL_DOUBLE_HEAD, expand=True)
        table.add_column("No", justify="right", style=theme["text_number"], width=6)
        table.add_column("Nama Tema", style=theme["text_body"])
        table.add_column("Preview", justify="left")

        for idx, name in enumerate(theme_names, start=1):
            preset = presets[name]
            preview = (
                f"[{preset['border_primary']}]■[/] "
                f"[{preset['border_info']}]■[/] "
                f"[{preset['border_success']}]■[/] "
                f"[{preset['border_warning']}]■[/] "
                f"[{preset['border_error']}]■[/]"
            )
            table.add_row(str(idx), name.replace("_", " ").title(), preview)

        table.add_row("00", f"[{theme['text_err']}]Kembali[/]", "")

        console.print(Panel(
            table,
            #title=f"[{theme['text_title']}]🖌️ Daftar Tema[/]",
            border_style=theme["border_primary"],
            padding=(0, 0),
            expand=True
        ))

        choice = console.input(
            f"[{theme['text_sub']}]Pilih nomor tema:[/{theme['text_sub']}] "
        ).strip()

        if choice == "00":
            return

        if choice.isdigit() and 1 <= int(choice) <= len(theme_names):
            selected_theme = theme_names[int(choice) - 1]
            selected_preset = presets[selected_theme]

            preview_table = Table.grid(padding=(0, 2))
            preview_table.add_column(justify="right", style=selected_preset["text_sub"])
            preview_table.add_column(justify="left", style=selected_preset["text_body"])
            preview_table.add_row("Judul", f"[{selected_preset['text_title']}]Contoh Judul[/]")
            preview_table.add_row("Sub", f"[{selected_preset['text_sub']}]Contoh Subjudul[/]")
            preview_table.add_row("Nomor", f"[{selected_preset['text_value']}]628123456789[/]")
            preview_table.add_row("Pulsa", f"[{selected_preset['text_money']}]Rp 123.456[/]")
            preview_table.add_row("Kuota", f"[{selected_preset['text_number']}]10.50/500.00 GB[/]")
            preview_table.add_row("Expired", f"[{selected_preset['text_date']}]2035-09-29 23:59:59[/]")
            preview_table.add_row("Error", f"[{selected_preset['text_err']}]Contoh Error[/]")

            console.print(Panel(
                preview_table,
                title=f"[{selected_preset['text_title']}]Preview Tema: {selected_theme.replace('_', ' ').title()}[/]",
                border_style=selected_preset["border_primary"],
                padding=(1, 2),
                expand=True
            ))

            confirm = console.input(
                f"[{theme['text_sub']}]Gunakan tema ini? (y/n):[/{theme['text_sub']}] "
            ).strip().lower()
            if confirm == "y":
                set_theme(selected_theme)
                print_theme_changed(selected_theme)
                pause()
                return
        else:
            print_panel("⚠️ Error", "Pilihan tidak valid.")
            pause()


def print_theme_changed(theme_name):
    theme = get_theme()
    terminal_width = console.size.width

    message_text = (
        f"[{theme['text_ok']}]✅ Tema Diubah[/]\n"
        f"[{theme['text_sub']}]Tema sekarang: {theme_name.replace('_', ' ').title()}[/]"
    )

    aligned_message = Align.left(message_text)

    panel = Panel(
        aligned_message,
        title="",
        title_align="left",
        style=theme["border_success"],
        width=terminal_width,
    )

    console.print(panel)


def main():
    while True:
        active_user = AuthInstance.get_active_user()

        if active_user is not None:
            balance = get_balance(
                AuthInstance.api_key, active_user["tokens"]["id_token"]
            )
            balance_remaining = balance.get("remaining")
            balance_expired_at = balance.get("expired_at")
            quota = (
                get_quota(AuthInstance.api_key, active_user["tokens"]["id_token"]) or {}
            )
            remaining = quota.get("remaining", 0)
            total = quota.get("total", 0)
            has_unlimited = quota.get("has_unlimited", False)
            remaining_gb = remaining / 1e9
            total_gb = total / 1e9
            if (total > 0) or has_unlimited:
                display_quota = (
                    f"{remaining_gb:.2f}/{total_gb:.2f} GB (Unlimited)"
                    if has_unlimited
                    else f"{remaining_gb:.2f}/{total_gb:.2f} GB"
                )
            else:
                display_quota = None

            show_main_menu(
                active_user["number"],
                balance_remaining,
                display_quota,
                balance_expired_at,
            )

            choice = input("Pilih menu: ")
            if choice == "1":
                selected_user_number = show_account_menu()
                if selected_user_number:
                    AuthInstance.set_active_user(selected_user_number)
                else:
                    print_panel("⚠️ Gagal", "Tidak ada akun yang dipilih.")
                continue
            elif choice == "2":
                fetch_my_packages()
            elif choice == "3":
                show_hot_menu()
            elif choice == "4":
                show_hot_menu2()
            elif choice == "5":
                show_barbex_main_menu()
            elif choice == "6":
                show_family_menu()
            elif choice == "7":
                family_code = input("Masukkan Family Code (atau '99' untuk batal): ")
                if family_code != "99":
                    get_packages_by_family(family_code)
            elif choice == "00":
                show_bookmark_menu()
            elif choice == "69":
                show_theme_menu()
            elif choice == "99":
                print_panel("👋 Sampai Jumpa", "Aplikasi ditutup")
                sys.exit(0)
            elif choice == "t":
                res = get_package(AuthInstance.api_key, active_user["tokens"], "")
                print(json.dumps(res, indent=2))
                input("Tekan Enter untuk kembali...")
            elif choice == "s":
                enter_sentry_mode()
            else:
                print_panel("⚠️ Error", "Pilihan tidak valid.")
                pause()
        else:
            selected_user_number = show_account_menu()
            if selected_user_number:
                AuthInstance.set_active_user(selected_user_number)
            else:
                print_panel("⚠️ Gagal", "Tidak ada akun yang dipilih.")
                pause()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_panel("👋 Keluar", "Aplikasi dihentikan oleh pengguna.")
