import requests
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from rich.align import Align
from rich.box import MINIMAL_DOUBLE_HEAD
from rich.text import Text
from app.client.balance import settlement_balance
from app.client.engsel2 import get_family_v2, get_package_details
from app.menus.package_p import show_package_details
from app.service.auth import AuthInstance
from app.menus.util import clear_screen
from app.menus.anu_util import pause, print_panel, get_rupiah
from app.client.ewallet import show_multipayment_v2
from app.client.qris2 import show_qris_payment_v2
from app.type_dict import PaymentItem
from app.config.theme_config import get_theme

import json
import os

from rich.live import Live
from rich.spinner import Spinner
import time


console = Console()

def loading_animation(text="Memuat..."):
    with Live(Spinner("dots", text=text), refresh_per_second=10):
        time.sleep(1.5)


def show_hot_main_menu():
    theme = get_theme()
    in_main_menu = True
    while in_main_menu:
        clear_screen()

        # Panel judul terpisah
        console.print(Panel(
            Align.center("✨ Paket HOT ✨", vertical="middle"),
            border_style=theme["border_info"],
            padding=(1, 2),
            expand=True
        ))

        # Tabel menu paket
        menu_table = Table(box=MINIMAL_DOUBLE_HEAD, expand=True)
        menu_table.add_column("Kode", justify="right", style=theme["text_key"], width=6)
        menu_table.add_column("Menu Paket", style=theme["text_body"])
        menu_table.add_row("1", "Paket HOT v1")
        menu_table.add_row("2", "Paket HOT v2")
        menu_table.add_row("00", f"[{theme['text_err']}]Kembali ke menu utama[/]")

        console.print(Panel(
            menu_table,
            border_style=theme["border_primary"],
            padding=(0, 1),
            expand=True
        ))

        # Input pilihan
        choice = console.input(f"[{theme['text_sub']}]Pilih menu:[/{theme['text_sub']}] ").strip()
        if choice == "1":
            show_hot_menu()
        elif choice == "2":
            show_hot_menu2()
        elif choice == "00":
            loading_animation("Kembali ke menu utama...")
            in_main_menu = False
        else:
            print_panel("⚠️ Error", "Input tidak valid. Silahkan coba lagi.")
            pause()



CACHE_FILE = "family_cache.json"

def load_family_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_family_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def show_hot_menu():
    theme = get_theme()
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()

    if not tokens:
        print_panel("⚠️ Error", "Token pengguna tidak ditemukan.")
        pause()
        return

    # Load cache awal
    raw_cache = load_family_cache()
    family_cache = {eval(k): v for k, v in raw_cache.items()}

    while True:
        clear_screen()

        # Ambil data HOT dari server
        try:
            response = requests.get("https://me.mashu.lol/pg-hot.json", timeout=30)
            response.raise_for_status()
            hot_packages = response.json()
        except Exception:
            print_panel("⚠️ Error", "Gagal mengambil data HOT Package.")
            pause()
            return

        # Enrich data dengan cache dan API
        enriched_packages = []
        with Live(Spinner("dots", text="Memproses data paket..."), refresh_per_second=10):
            for p in hot_packages:
                fc_key = (p["family_code"], p["is_enterprise"])
                family_data = family_cache.get(fc_key)

                if not family_data:
                    family_data = get_family_v2(api_key, tokens, p["family_code"], p["is_enterprise"])
                    if family_data:
                        family_cache[fc_key] = family_data

                if family_data:
                    for variant in family_data["package_variants"]:
                        if variant["name"] == p["variant_name"]:
                            for option in variant["package_options"]:
                                if option["order"] == p["order"]:
                                    p["option_code"] = option["package_option_code"]
                                    p["price"] = option["price"]
                                    break
                enriched_packages.append(p)

        # Simpan cache terbaru
        save_family_cache({str(k): v for k, v in family_cache.items()})

        # Tampilkan daftar paket HOT
        console.print(Panel(
            Align.center("✨ Paket HOT v1 ✨", vertical="middle"),
            border_style=theme["border_info"],
            padding=(1, 2),
            expand=True
        ))

        table = Table(box=MINIMAL_DOUBLE_HEAD, expand=True)
        table.add_column("No", justify="right", style=theme["text_key"], width=6)
        table.add_column("Nama Paket", style=theme["text_body"])
        table.add_column("Harga", justify="right", style=theme["text_money"], width=10)

        for idx, p in enumerate(enriched_packages):
            label = f"{p['family_name']} - {p['variant_name']} - {p['option_name']}"
            harga = get_rupiah(p.get("price", 0))
            table.add_row(str(idx + 1), label, harga)

        console.print(Panel(table, border_style=theme["border_primary"], padding=(0, 0), expand=True))

        nav_table = Table(show_header=False, box=MINIMAL_DOUBLE_HEAD, expand=True)
        nav_table.add_column(justify="right", style=theme["text_key"], width=4)
        nav_table.add_column(style=theme["text_body"])
        nav_table.add_row("00", f"[{theme['text_sub']}]Kembali ke menu sebelumnya[/]")

        console.print(Panel(nav_table, border_style=theme["border_info"], padding=(0, 1), expand=True))

        # Input pilihan
        choice = console.input(f"[{theme['text_sub']}]Pilih paket:[/{theme['text_sub']}] ").strip()
        if choice == "00":
            loading_animation("Kembali ke menu sebelumnya...")
            return

        if choice.isdigit() and 1 <= int(choice) <= len(enriched_packages):
            selected_pkg = enriched_packages[int(choice) - 1]
            option_code = selected_pkg.get("option_code")
            if not option_code:
                print_panel("⚠️ Error", "Kode paket tidak ditemukan.")
                pause()
                continue

            result = show_package_details(api_key, tokens, option_code, selected_pkg["is_enterprise"])
            if result == "MAIN":
                return
            elif result in ("BACK", True):
                continue  # reload ulang daftar HOT
        else:
            print_panel("⚠️ Error", "Input tidak valid. Silakan masukkan nomor yang tersedia.")
            pause()


def show_hot_menu2():
    theme = get_theme()
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()

    in_hot_menu = True
    while in_hot_menu:
        clear_screen()

        with Live(Spinner("dots", text="Mengambil daftar paket HOT v2..."), refresh_per_second=10):
            try:
                response = requests.get("https://me.mashu.lol/pg-hot2.json", timeout=30)
                response.raise_for_status()
                hot_packages = response.json()
            except Exception:
                print_panel("⚠️ Error", "Gagal mengambil data HOT Package.")
                pause()
                return

        console.print(Panel(
            Align.center("✨ Paket HOT v2 ✨", vertical="middle"),
            border_style=theme["border_info"],
            padding=(1, 2),
            expand=True
        ))

        table = Table(box=MINIMAL_DOUBLE_HEAD, expand=True)
        table.add_column("No", justify="right", style=theme["text_key"], width=6)
        table.add_column("Nama Paket", style=theme["text_body"])
        table.add_column("Harga", style=theme["text_money"])

        for idx, p in enumerate(hot_packages):
            formatted_price = get_rupiah(p["price"])
            table.add_row(str(idx + 1), p["name"], formatted_price)

        console.print(Panel(table, border_style=theme["border_primary"], padding=(0, 0), expand=True))

        nav_table = Table(show_header=False, box=MINIMAL_DOUBLE_HEAD, expand=True)
        nav_table.add_column(justify="right", style=theme["text_key"], width=4)
        nav_table.add_column(style=theme["text_body"])
        nav_table.add_row("00", f"[{theme['text_sub']}]Kembali ke menu sebelumnya[/]")

        console.print(Panel(nav_table, border_style=theme["border_info"], padding=(0, 1), expand=True))

        choice = console.input(f"[{theme['text_sub']}]Pilih paket:[/{theme['text_sub']}] ").strip()
        if choice == "00":
            loading_animation("Kembali ke menu sebelumnya...")
            return

        if choice.isdigit() and 1 <= int(choice) <= len(hot_packages):
            selected_package = hot_packages[int(choice) - 1]
            packages = selected_package.get("packages", [])
            if not packages:
                print_panel("⚠️ Error", "Paket tidak tersedia.")
                pause()
                continue

            payment_items = []
            with Live(Spinner("dots", text="Memuat detail semua paket..."), refresh_per_second=10):
                for package in packages:
                    package_detail = get_package_details(
                        api_key,
                        tokens,
                        package["family_code"],
                        package["variant_code"],
                        package["order"],
                        package["is_enterprise"],
                    )

                    if not package_detail:
                        print_panel("⚠️ Error", f"Gagal mengambil detail paket untuk {package['family_code']}.")
                        return

                    payment_items.append(
                        PaymentItem(
                            item_code=package_detail["package_option"]["package_option_code"],
                            product_type="",
                            item_price=package_detail["package_option"]["price"],
                            item_name=package_detail["package_option"]["name"],
                            tax=0,
                            token_confirmation=package_detail["token_confirmation"],
                        )
                    )

            clear_screen()

            info_text = Text()
            info_text.append(f"{selected_package['name']}\n", style="bold")
            info_text.append(f"Harga: {get_rupiah(selected_package['price'])}\n", style=theme["text_money"])
            info_text.append("Detail:\n", style=theme["text_body"])

            for line in selected_package["detail"].split("\n"):
                cleaned = line.strip()
                if cleaned:
                    info_text.append(f"- {cleaned}\n", style=theme["text_body"])

            console.print(Panel(
                info_text,
                title=f"[{theme['text_title']}]📦 Detail Paket[/]",
                border_style=theme["border_info"],
                padding=(1, 2),
                expand=True
            ))

            in_payment_menu = True
            while in_payment_menu:
                payment_table = Table(show_header=False, box=MINIMAL_DOUBLE_HEAD, expand=True)
                payment_table.add_column(justify="right", style=theme["text_key"], width=6)
                payment_table.add_column(justify="left", style=theme["text_body"])
                payment_table.add_row("1", "E-Wallet")
                payment_table.add_row("2", "QRIS")
                payment_table.add_row("00", f"[{theme['text_sub']}]Kembali ke daftar paket[/]")
                payment_table.add_row("99", f"[{theme['text_err']}]Kembali ke menu utama[/]")

                console.print(Panel(
                    payment_table,
                    title=f"[{theme['text_title']}]💳 Pilih Metode Pembayaran[/]",
                    border_style=theme["border_primary"],
                    padding=(0, 1),
                    expand=True
                ))

                input_method = console.input(f"[{theme['text_sub']}]Pilih metode:[/{theme['text_sub']}] ").strip()
                if input_method == "1":
                    show_multipayment_v2(api_key, tokens, payment_items, "BUY_PACKAGE", True)
                    console.input(f"[{theme['text_sub']}]Tekan enter untuk kembali...[/{theme['text_sub']}] ")
                    return
                elif input_method == "2":
                    show_qris_payment_v2(api_key, tokens, payment_items, "BUY_PACKAGE", True)
                    console.input(f"[{theme['text_sub']}]Tekan enter untuk kembali...[/{theme['text_sub']}] ")
                    return
                elif input_method == "00":
                    loading_animation("Kembali ke daftar paket HOT v2...")
                    in_payment_menu = False
                elif input_method == "99":
                    loading_animation("Kembali ke menu utama...")
                    in_hot_menu = False
                    return
                else:
                    print_panel("⚠️ Error", "Metode tidak valid. Silahkan coba lagi.")
                    pause()
        else:
            print_panel("⚠️ Error", "Input tidak valid. Silahkan coba lagi.")
            pause()

