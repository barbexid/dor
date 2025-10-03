import os
import json
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.text import Text
from rich.box import MINIMAL_DOUBLE_HEAD

from app.client.balance import settlement_balance
from app.client.engsel2 import get_family_v2
from app.menus.package_p import show_package_details
from app.service.auth import AuthInstance
from app.menus.util import clear_screen
from app.menus.anu_util import pause, print_panel, get_rupiah, live_loading
from app.client.ewallet import show_multipayment_v2
from app.client.qris2 import show_qris_payment_v2
from app.type_dict import PaymentItem
from app.config.theme_config import get_theme

console = Console()
CACHE_FILE = "family_cache.json"

def load_family_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_family_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def show_hot_main_menu():
    theme = get_theme()
    while True:
        clear_screen()

        console.print(Panel(
            Align.center("✨ Paket HOT ✨", vertical="middle"),
            border_style=theme["border_info"],
            padding=(1, 2),
            expand=True
        ))

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

        choice = console.input(f"[{theme['text_sub']}]Pilih menu:[/{theme['text_sub']}] ").strip()
        if choice == "1":
            show_hot_menu()
        elif choice == "2":
            show_hot_menu2()  # jika tersedia
        elif choice == "00":
            live_loading(text="Kembali ke menu utama...", theme=theme)
            return
        else:
            print_panel("⚠️ Error", "Input tidak valid. Silahkan coba lagi.")
            pause()

def validate_family_data(data):
    return (
        data and
        isinstance(data, dict) and
        "package_variants" in data
    )

def refresh_family_data(family_code, is_enterprise, api_key, tokens, cache):
    data = get_family_v2(api_key, tokens, family_code, is_enterprise)
    if validate_family_data(data):
        cache[(family_code, is_enterprise)] = data
    return data

def show_hot_menu():
    theme = get_theme()
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()

    if not tokens:
        print_panel("⚠️ Error", "Token pengguna tidak ditemukan.")
        pause()
        return

    raw_cache = load_family_cache()
    try:
        family_cache = {eval(k): v for k, v in raw_cache.items()}
    except Exception:
        family_cache = {}

    while True:
        clear_screen()

        try:
            hot_packages = live_loading(
                task=lambda: requests.get("https://me.mashu.lol/pg-hot.json", timeout=30).json(),
                text="Mengambil data HOT Package...",
                theme=theme
            )
        except Exception:
            print_panel("⚠️ Error", "Gagal mengambil data HOT Package.")
            pause()
            return

        if not hot_packages:
            print_panel("⚠️ Error", "Tidak ada data paket tersedia.")
            pause()
            return

        enriched_packages = []

        def enrich_packages():
            for p in hot_packages:
                fc_key = (p["family_code"], p["is_enterprise"])
                family_data = family_cache.get(fc_key)

                if not validate_family_data(family_data):
                    family_data = refresh_family_data(p["family_code"], p["is_enterprise"], api_key, tokens, family_cache)

                if not validate_family_data(family_data):
                    continue

                for variant in family_data.get("package_variants", []):
                    if variant.get("name") == p.get("variant_name"):
                        for option in variant.get("package_options", []):
                            if option.get("order") == p.get("order"):
                                p["option_code"] = option.get("package_option_code")
                                p["price"] = option.get("price")
                                p["option_name"] = option.get("name", "-")
                                break
                enriched_packages.append(p)

        live_loading(task=enrich_packages, text="Memproses data paket...", theme=theme)
        save_family_cache({str(k): v for k, v in family_cache.items()})

        if not enriched_packages:
            print_panel("⚠️ Error", "Gagal memproses data paket. Silakan coba lagi nanti.")
            pause()
            return

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
            label = f"{p.get('family_name', '-') } - {p.get('variant_name', '-') } - {p.get('option_name', '-') }"
            harga = get_rupiah(p.get("price", 0))
            table.add_row(str(idx + 1), label, harga)

        console.print(Panel(table, border_style=theme["border_primary"], padding=(0, 0), expand=True))

        nav_table = Table(show_header=False, box=MINIMAL_DOUBLE_HEAD, expand=True)
        nav_table.add_column(justify="right", style=theme["text_key"], width=4)
        nav_table.add_column(style=theme["text_body"])
        nav_table.add_row("00", f"[{theme['text_sub']}]Kembali ke menu sebelumnya[/]")

        console.print(Panel(nav_table, border_style=theme["border_info"], padding=(0, 1), expand=True))

        choice = console.input(f"[{theme['text_sub']}]Pilih paket:[/{theme['text_sub']}] ").strip()
        if choice == "00":
            live_loading(text="Kembali ke menu sebelumnya...", theme=theme)
            return

        if choice.isdigit() and 1 <= int(choice) <= len(enriched_packages):
            selected_pkg = enriched_packages[int(choice) - 1]
            option_code = selected_pkg.get("option_code")
            if not option_code:
                print_panel("⚠️ Error", "Kode paket tidak ditemukan.")
                pause()
                continue

            try:
                result = show_package_details(api_key, tokens, option_code, selected_pkg.get("is_enterprise", False))
            except Exception:
                print_panel("⚠️ Error", "Gagal menampilkan detail paket.")
                pause()
                continue

            if result == "MAIN":
                return
            elif result in ("BACK", True):
                continue
        else:
            print_panel("⚠️ Error", "Input tidak valid. Silakan masukkan nomor yang tersedia.")
            pause()

def validate_package_detail(detail):
    return (
        detail and
        isinstance(detail, dict) and
        "package_option" in detail and
        "token_confirmation" in detail and
        isinstance(detail["package_option"], dict) and
        "package_option_code" in detail["package_option"] and
        "price" in detail["package_option"] and
        "name" in detail["package_option"]
    )

def show_hot_menu2():
    theme = get_theme()
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()

    while True:
        clear_screen()

        try:
            hot_packages = live_loading(
                task=lambda: requests.get("https://me.mashu.lol/pg-hot2.json", timeout=30).json(),
                text="Mengambil daftar paket HOT v2...",
                theme=theme
            )
        except Exception:
            print_panel("⚠️ Error", "Gagal mengambil data HOT Package.")
            pause()
            return

        if not hot_packages:
            print_panel("⚠️ Error", "Tidak ada data paket tersedia.")
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
            live_loading(text="Kembali ke menu sebelumnya...", theme=theme)
            return

        if choice.isdigit() and 1 <= int(choice) <= len(hot_packages):
            selected_package = hot_packages[int(choice) - 1]
            packages = selected_package.get("packages", [])
            if not packages:
                print_panel("⚠️ Error", "Paket tidak tersedia.")
                pause()
                continue

            def fetch_payment_items():
                items = []
                for package in packages:
                    detail = get_package_details(
                        api_key,
                        tokens,
                        package["family_code"],
                        package["variant_code"],
                        package["order"],
                        package["is_enterprise"],
                    )
                    if validate_package_detail(detail):
                        items.append(PaymentItem(
                            item_code=detail["package_option"]["package_option_code"],
                            product_type="",
                            item_price=detail["package_option"]["price"],
                            item_name=detail["package_option"]["name"],
                            tax=0,
                            token_confirmation=detail["token_confirmation"],
                        ))
                return items

            payment_items = live_loading(task=fetch_payment_items, text="Mengambil detail paket...", theme=theme)

            if not payment_items:
                print_panel("⚠️ Error", "Gagal memuat data pembayaran. Silakan coba lagi nanti.")
                pause()
                continue

            clear_screen()

            info_text = Text()
            info_text.append(f"{selected_package['name']}\n", style="bold")
            info_text.append(f"Harga: {get_rupiah(selected_package['price'])}\n", style=theme["text_money"])
            info_text.append("Detail:\n", style=theme["text_body"])

            for line in selected_package.get("detail", "").split("\n"):
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

            while True:
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
                    live_loading(text="Kembali ke daftar paket HOT v2...", theme=theme)
                    break
                elif input_method == "99":
                    live_loading(text="Kembali ke menu utama...", theme=theme)
                    return
                else:
                    print_panel("⚠️ Error", "Metode tidak valid. Silahkan coba lagi.")
                    pause()
        else:
            print_panel("⚠️ Error", "Input tidak valid. Silahkan coba lagi.")
            pause()
