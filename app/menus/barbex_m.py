import requests
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from rich.align import Align
from rich.box import MINIMAL_DOUBLE_HEAD
from rich.text import Text
from app.client.balance import settlement_balance
from app.client.engsel2 import get_family_v2, get_package_details
from app.menus.package_m import show_package_details
from app.service.auth import AuthInstance
from app.menus.util import clear_screen
from app.menus.anu_util import pause, print_panel, get_rupiah
from app.client.ewallet import show_multipayment_v2
from app.client.qris2 import show_qris_payment_v2
from app.type_dict import PaymentItem
from app.config.theme_config import get_theme

console = Console()

def show_barbex_main_menu():
    theme = get_theme()
    while True:
        clear_screen()

        console.print(Panel(
            Align.center("Menu Paket Lainnya", vertical="middle"),
            border_style=theme["border_info"],
            padding=(1, 2),
            expand=True
        ))

        menu_table = Table(show_header=False, box=MINIMAL_DOUBLE_HEAD, expand=True)
        menu_table.add_column("No", justify="right", style=theme["text_key"], width=4)
        menu_table.add_column("Daftar Paket", style=theme["text_body"])
        menu_table.add_row("1", "Paket v1")
        menu_table.add_row("2", "Paket v2")
        menu_table.add_row("00", f"[{theme['text_sub']}]Kembali ke menu awal[/]")

        console.print(Panel(
            menu_table,
            border_style=theme["border_primary"],
            padding=(0, 0),
            expand=True
        ))

        choice = console.input(f"[{theme['text_sub']}]Pilih menu:[/{theme['text_sub']}] ").strip()
        if choice == "1":
            show_barbex_menu()
        elif choice == "2":
            show_barbex_menu2()
        elif choice == "00":
            return  # keluar ke menu utama
        else:
            print_panel("Error", "Input tidak valid. Silahkan coba lagi.")
            pause()

def show_barbex_menu():
    theme = get_theme()
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()

    while True:
        clear_screen()

        console.print(Panel(
            "[bold]Memuat Daftar Paket v1...[/]",
            border_style=theme["border_info"],
            padding=(0, 1),
            expand=True
        ))

        url = "https://raw.githubusercontent.com/dratx1/engsel/refs/heads/main/family/anu.json"
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            print_panel("Error", "Gagal mengambil data barbex Package.")
            pause()
            return

        barbex_packages = response.json()

        console.print(Panel(
            Align.center("Paket v1", vertical="middle"),
            border_style=theme["border_info"],
            padding=(1, 2),
            expand=True
        ))

        table = Table(box=MINIMAL_DOUBLE_HEAD, expand=True)
        table.add_column("No", justify="right", style=theme["text_key"], width=6)
        table.add_column("Nama Paket", style=theme["text_body"])

        for idx, p in enumerate(barbex_packages):
            label = f"{p['family_name']} - {p['variant_name']} - {p['option_name']}"
            table.add_row(str(idx + 1), label)

        console.print(Panel(
            table,
            border_style=theme["border_primary"],
            padding=(0, 0),
            expand=True
        ))

        # Panel navigasi terpisah
        nav_table = Table(show_header=False, box=MINIMAL_DOUBLE_HEAD, expand=True)
        nav_table.add_column(justify="right", style=theme["text_key"], width=4)
        nav_table.add_column(style=theme["text_body"])
        nav_table.add_row("00", f"[{theme['text_sub']}]Kembali ke menu sebelumnya[/]")
        #nav_table.add_row("99", f"[{theme['text_err']}]Kembali ke menu utama[/]")

        console.print(Panel(
            nav_table,
            border_style=theme["border_info"],
            padding=(0, 1),
            expand=True
        ))

        choice = console.input(f"[{theme['text_sub']}]Pilih paket:[/{theme['text_sub']}] ").strip()
        if choice == "00":
            return  # kembali ke menu sebelumnya
        #if choice == "99":
            #return  # kembali ke menu utama

        if choice.isdigit() and 1 <= int(choice) <= len(barbex_packages):
            selected_bm = barbex_packages[int(choice) - 1]
            family_code = selected_bm["family_code"]
            is_enterprise = selected_bm["is_enterprise"]

            family_data = get_family_v2(api_key, tokens, family_code, is_enterprise)
            if not family_data:
                print_panel("Error", "Gagal mengambil data family.")
                pause()
                continue

            package_variants = family_data["package_variants"]
            option_code = None
            for variant in package_variants:
                if variant["name"] == selected_bm["variant_name"]:
                    for option in variant["package_options"]:
                        if option["order"] == selected_bm["order"]:
                            option_code = option["package_option_code"]
                            break

            if option_code:
                result = show_package_details(api_key, tokens, option_code, is_enterprise)
                if result == "MAIN":
                    return  # keluar ke menu utama
                elif result == "BACK":
                    continue  # reload ulang daftar paket
                elif result is True:
                    return  # selesai pembelian
        else:
            print_panel("Error", "Input tidak valid. Silahkan coba lagi.")
            pause()



def show_barbex_menu2():
    theme = get_theme()
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()

    while True:
        clear_screen()

        console.print(Panel(
            "[bold]Memuat Daftar Paket v2...[/]",
            border_style=theme["border_info"],
            padding=(0, 1),
            expand=True
        ))

        url = "https://raw.githubusercontent.com/dratx1/engsel/refs/heads/main/family/anu2.json"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            barbex_packages = response.json()
        except Exception:
            print_panel("Error", "Gagal mengambil daftar paket dari server.")
            pause()
            continue

        console.print(Panel(
            Align.center("Paket v2", vertical="middle"),
            border_style=theme["border_info"],
            padding=(1, 2),
            expand=True
        ))

        table = Table(box=MINIMAL_DOUBLE_HEAD, expand=True)
        table.add_column("No", justify="right", style=theme["text_key"], width=6)
        table.add_column("Nama Paket", style=theme["text_body"])
        table.add_column("Harga", style=theme["text_money"])

        for idx, p in enumerate(barbex_packages):
            formatted_price = get_rupiah(p.get("price", 0))
            table.add_row(str(idx + 1), p.get("name", "Tanpa Nama"), formatted_price)

        console.print(Panel(table, border_style=theme["border_primary"], padding=(0, 0), expand=True))

        nav_table = Table(show_header=False, box=MINIMAL_DOUBLE_HEAD, expand=True)
        nav_table.add_column(justify="right", style=theme["text_key"], width=4)
        nav_table.add_column(style=theme["text_body"])
        nav_table.add_row("00", f"[{theme['text_sub']}]Kembali ke menu sebelumnya[/]")

        console.print(Panel(nav_table, border_style=theme["border_info"], padding=(0, 1), expand=True))

        choice = console.input(f"[{theme['text_sub']}]Pilih paket:[/{theme['text_sub']}] ").strip()
        if choice == "00":
            return

        if not choice.isdigit() or not (1 <= int(choice) <= len(barbex_packages)):
            print_panel("Error", "Input tidak valid. Silahkan pilih nomor yang tersedia.")
            pause()
            continue

        selected_package = barbex_packages[int(choice) - 1]
        packages = selected_package.get("packages", [])
        if not packages:
            print_panel("Error", "Paket tidak memiliki detail pembelian.")
            pause()
            continue

        payment_items = []
        for package in packages:
            if not all(k in package for k in ("family_code", "variant_code", "order", "is_enterprise")):
                continue  # skip silently

            try:
                detail = get_package_details(
                    api_key,
                    tokens,
                    package["family_code"],
                    package["variant_code"],
                    package["order"],
                    package["is_enterprise"],
                )
            except Exception:
                continue  # skip silently

            if not detail or "package_option" not in detail or "token_confirmation" not in detail:
                continue

            option = detail["package_option"]
            if not all(k in option for k in ("package_option_code", "price", "name")):
                continue

            payment_items.append(PaymentItem(
                item_code=option["package_option_code"],
                product_type="",
                item_price=option["price"],
                item_name=option["name"],
                tax=0,
                token_confirmation=detail["token_confirmation"],
            ))

        if not payment_items:
            print_panel("Error", "Gagal memuat detail paket. Tidak ada item pembayaran yang valid.")
            pause()
            continue

        clear_screen()

        info_text = Text()
        info_text.append(f"{selected_package.get('name', 'Tanpa Nama')}\n", style="bold")
        info_text.append(f"Harga: {get_rupiah(selected_package.get('price', 0))}\n", style=theme["text_money"])
        info_text.append("Detail:\n", style=theme["text_body"])

        for line in selected_package.get("detail", "").split("\n"):
            cleaned = line.strip()
            if cleaned:
                info_text.append(f"- {cleaned}\n", style=theme["text_body"])

        console.print(Panel(info_text, title=f"[{theme['text_title']}]Detail Paket[/]", border_style=theme["border_info"], padding=(1, 2), expand=True))

        while True:
            payment_table = Table(show_header=False, box=MINIMAL_DOUBLE_HEAD, expand=True)
            payment_table.add_column(justify="right", style=theme["text_key"], width=6)
            payment_table.add_column(justify="left", style=theme["text_body"])
            payment_table.add_row("1", "E-Wallet")
            payment_table.add_row("2", "QRIS")
            payment_table.add_row("3", "Saldo")
            payment_table.add_row("00", f"[{theme['text_sub']}]Kembali ke daftar paket[/]")
            payment_table.add_row("99", f"[{theme['text_err']}]Kembali ke menu utama[/]")

            console.print(Panel(payment_table, title=f"[{theme['text_title']}]Pilih Metode Pembayaran[/]", border_style=theme["border_primary"], padding=(0, 1), expand=True))

            input_method = console.input(f"[{theme['text_sub']}]Pilih metode:[/{theme['text_sub']}] ").strip()
            if input_method == "1":
                try:
                    show_multipayment_v2(api_key, tokens, payment_items, "BUY_PACKAGE", True)
                except Exception:
                    print_panel("Error", "Gagal memproses pembayaran.")
                console.input(f"[{theme['text_sub']}]Tekan enter untuk kembali...[/] ")
                break
            elif input_method == "2":
                try:
                    show_qris_payment_v2(api_key, tokens, payment_items, "BUY_PACKAGE", True)
                except Exception:
                    print_panel("Error", "Gagal memproses QRIS.")
                console.input(f"[{theme['text_sub']}]Tekan enter untuk kembali...[/] ")
                break
            elif input_method == "3":
                try:
                    settlement_balance(api_key, tokens, payment_items, "BUY_PACKAGE", True)
                except Exception:
                    print_panel("Error", "Gagal memproses saldo.")
                console.input(f"[{theme['text_sub']}]Tekan enter untuk kembali...[/] ")
                break
            elif input_method == "00":
                break
            elif input_method == "99":
                return
            else:
                print_panel("Error", "Metode tidak valid. Silahkan coba lagi.")
                pause()

