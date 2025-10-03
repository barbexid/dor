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
from app.client.ewallet import show_multipayment_v2
from app.client.qris2 import show_qris_payment_v2
from app.type_dict import PaymentItem
from app.config.theme_config import get_theme
from app.menus.anu_util import pause, print_panel, get_rupiah, live_loading

console = Console()


def show_barbex_main_menu():
    theme = get_theme()
    while True:
        clear_screen()

        console.print(Panel(
            Align.center("✨ Menu Paket Lainnya ✨", vertical="middle"),
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
            live_loading(text="Kembali ke menu utama...", theme=theme)
            return
        else:
            print_panel("⚠️ Error", "Input tidak valid. Silahkan coba lagi.")
            pause()

def show_barbex_menu():
    theme = get_theme()
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()

    while True:
        clear_screen()

        barbex_packages = live_loading(
            task=lambda: requests.get("https://raw.githubusercontent.com/dratx1/engsel/refs/heads/main/family/anu.json", timeout=30).json(),
            text="Memuat daftar Paket v1...",
            theme=theme
        )

        if not barbex_packages:
            print_panel("⚠️ Error", "Gagal mengambil data barbex Package.")
            pause()
            return

        console.print(Panel(
            Align.center("✨ Paket v1 ✨", vertical="middle"),
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

        nav_table = Table(show_header=False, box=MINIMAL_DOUBLE_HEAD, expand=True)
        nav_table.add_column(justify="right", style=theme["text_key"], width=4)
        nav_table.add_column(style=theme["text_body"])
        nav_table.add_row("00", f"[{theme['text_sub']}]Kembali ke menu sebelumnya[/]")

        console.print(Panel(
            nav_table,
            border_style=theme["border_info"],
            padding=(0, 1),
            expand=True
        ))

        choice = console.input(f"[{theme['text_sub']}]Pilih paket:[/{theme['text_sub']}] ").strip()
        if choice == "00":
            return

        if choice.isdigit() and 1 <= int(choice) <= len(barbex_packages):
            selected_bm = barbex_packages[int(choice) - 1]
            family_code = selected_bm["family_code"]
            is_enterprise = selected_bm["is_enterprise"]

            family_data = live_loading(
                task=lambda: get_family_v2(api_key, tokens, family_code, is_enterprise),
                text="Memuat data family...",
                theme=theme
            )

            if not family_data:
                print_panel("⚠️ Error", "Gagal mengambil data family.")
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
                    return
                elif result == "BACK":
                    continue
                elif result is True:
                    return
        else:
            print_panel("⚠️ Error", "Input tidak valid. Silahkan coba lagi.")
            pause()


def show_barbex_menu2():
    theme = get_theme()
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()

    while True:
        clear_screen()

        barbex_packages = live_loading(
            task=lambda: requests.get("https://raw.githubusercontent.com/dratx1/engsel/refs/heads/main/family/anu2.json", timeout=30).json(),
            text="Memuat Daftar Paket Barbex v2...",
            theme=theme
        )

        if not barbex_packages:
            print_panel("⚠️ Error", "Gagal mengambil data Barbex Package.")
            pause()
            return

        console.print(Panel(
            Align.center("✨ Paket Barbex v2 ✨", vertical="middle"),
            border_style=theme["border_info"],
            padding=(1, 2),
            expand=True
        ))

        table = Table(box=MINIMAL_DOUBLE_HEAD, expand=True)
        table.add_column("No", justify="right", style=theme["text_key"], width=6)
        table.add_column("Nama Paket", style=theme["text_body"])
        table.add_column("Harga", style=theme["text_money"])

        for idx, p in enumerate(barbex_packages):
            formatted_price = get_rupiah(p["price"])
            table.add_row(str(idx + 1), p["name"], formatted_price)

        console.print(Panel(
            table,
            border_style=theme["border_primary"],
            padding=(0, 0),
            expand=True
        ))

        nav_table = Table(show_header=False, box=MINIMAL_DOUBLE_HEAD, expand=True)
        nav_table.add_column(justify="right", style=theme["text_key"], width=4)
        nav_table.add_column(style=theme["text_body"])
        nav_table.add_row("00", f"[{theme['text_sub']}]Kembali ke menu sebelumnya[/]")

        console.print(Panel(
            nav_table,
            border_style=theme["border_info"],
            padding=(0, 1),
            expand=True
        ))

        choice = console.input(f"[{theme['text_sub']}]Pilih paket:[/{theme['text_sub']}] ").strip()
        if choice == "00":
            return

        if choice.isdigit() and 1 <= int(choice) <= len(barbex_packages):
            selected_package = barbex_packages[int(choice) - 1]
            packages = selected_package.get("packages", [])
            if not packages:
                print_panel("⚠️ Error", "Paket tidak tersedia.")
                pause()
                continue

            payment_items = []
            for package in packages:
                package_detail = live_loading(
                    task=lambda: get_package_details(
                        api_key,
                        tokens,
                        package["family_code"],
                        package["variant_code"],
                        package["order"],
                        package["is_enterprise"],
                    ),
                    text=f"Memuat detail paket {package['family_code']}...",
                    theme=theme
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
                elif input_method == "3":
                    settlement_balance(api_key, tokens, payment_items, "BUY_PACKAGE", True)
                    console.input(f"[{theme['text_sub']}]Tekan enter untuk kembali...[/{theme['text_sub']}] ")
                    return
                elif input_method == "00":
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

