import requests

from app.client.engsel import get_family, get_package_details
from app.menus.package import show_package_details
from app.service.auth import AuthInstance
from app.menus.util import clear_screen, pause, pesan_error
from app.client.ewallet import show_multipayment_v2
from app.client.qris import show_qris_payment_v2
from app.type_dict import PaymentItem
from app.theme import _c, console

from rich.panel import Panel
from rich.table import Table
from rich.box import MINIMAL_DOUBLE_HEAD
from rich.align import Align
from rich.text import Text


def tampilkan_header_hot(title="🔥 Paket Hot 🔥"):
    header_text = Align.center(f"[{_c('text_title')}]{title}[/]")
    panel = Panel(
        header_text,
        border_style=_c("border_primary"),
        padding=(1, 4),
        expand=True
    )
    console.print(panel)


def tampilkan_hot_packages(hot_packages):
    table = Table(box=MINIMAL_DOUBLE_HEAD, expand=True)
    table.add_column("No", justify="right", style=_c("text_number"), width=4)
    table.add_column("Family", style=_c("text_body"))
    table.add_column("Variant", style=_c("text_body"))
    table.add_column("Option", style=_c("text_body"))

    for idx, p in enumerate(hot_packages, 1):
        table.add_row(str(idx), p["family_name"], p["variant_name"], p["option_name"])

    panel = Panel(
        table,
        border_style=_c("border_info"),
        padding=(0, 0),
        expand=True
    )
    console.print(panel)


def tampilkan_hot2_packages(hot_packages):
    table = Table(box=MINIMAL_DOUBLE_HEAD, expand=True)
    table.add_column("No", justify="right", style=_c("text_number"), width=4)
    table.add_column("Nama Paket", style=_c("text_body"))
    table.add_column("Harga", style=_c("text_body"))

    for idx, p in enumerate(hot_packages, 1):
        table.add_row(str(idx), p["name"], str(p["price"]))

    panel = Panel(
        table,
        border_style=_c("border_info"),
        padding=(0, 0),
        expand=True
    )
    console.print(panel)


def tampilkan_menu_opsi_hot():
    kode_text = Text("00", style=_c("text_number"))
    aksi_text = Text("Kembali ke menu utama", style=_c("text_err"))
    kombinasi_text = Text.assemble(kode_text, " ", aksi_text)

    panel = Panel(
        Align.center(kombinasi_text),
        border_style=_c("border_primary"),
        expand=True,
        padding=(0, 1)
    )
    console.print(panel)


def tampilkan_info_hot2_package(selected_package):
    info_text = Text()
    info_text.append(f"Harga: {selected_package['price']}\n", style=_c("text_value"))
    info_text.append("Detail:\n", style=_c("text_body"))

    detail_lines = selected_package["detail"].split("\n")
    for line in detail_lines:
        info_text.append(f"- {line.strip()}\n", style=_c("text_body"))

    panel = Panel(
        info_text,
        border_style=_c("border_info"),
        title=f"[{_c('text_title')}]✨Info Paket✨[/]",
        padding=(0, 1),
        expand=True
    )
    console.print(panel)


def tampilkan_menu_metode_pembelian():
    table = Table(box=MINIMAL_DOUBLE_HEAD, expand=True, show_header=False)
    table.add_column("Kode", justify="right", style=_c("text_number"), width=4)
    table.add_column("Metode", style=_c("text_body"))

    table.add_row("1", "E-Wallet")
    table.add_row("2", "QRIS")
    table.add_row("00", f"[{_c('text_err')}]Kembali ke menu sebelumnya[/]")

    panel = Panel(
        table,
        border_style=_c("border_primary"),
        title=f"[{_c('text_title')}]🛒 Pilih Metode Pembelian[/]",
        padding=(0, 1),
        expand=True
    )
    console.print(panel)


def show_hot_menu():
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()

    in_hot_menu = True
    while in_hot_menu:
        clear_screen()
        tampilkan_header_hot("🔥 Paket Hot 🔥")

        url = "https://me.mashu.lol/pg-hot.json"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            hot_packages = response.json()
        except Exception as e:
            pesan_error(f"Gagal mengambil data hot package: {e}")
            pause()
            return

        tampilkan_hot_packages(hot_packages)
        tampilkan_menu_opsi_hot()

        choice = console.input(f"[{_c('text_sub')}]Pilih paket (nomor):[/{_c('text_sub')}] ").strip()
        if choice == "00":
            in_hot_menu = False
            return

        if choice.isdigit() and 1 <= int(choice) <= len(hot_packages):
            selected_bm = hot_packages[int(choice) - 1]
            family_code = selected_bm["family_code"]
            is_enterprise = selected_bm["is_enterprise"]

            family_data = get_family(api_key, tokens, family_code, is_enterprise)
            if not family_data:
                pesan_error("Gagal mengambil data family.")
                pause()
                continue

            option_code = None
            for variant in family_data["package_variants"]:
                if variant["name"] == selected_bm["variant_name"]:
                    for option in variant["package_options"]:
                        if option["order"] == selected_bm["order"]:
                            option_code = option["package_option_code"]
                            break

            if option_code:
                console.print(f"[{_c('text_value')}]{option_code}[/{_c('text_value')}]")
                show_package_details(api_key, tokens, option_code, is_enterprise)
            else:
                pesan_error("Paket tidak ditemukan.")
                pause()
        else:
            pesan_error("Input tidak valid. Silahkan coba lagi.")
            pause()


def show_hot_menu2():
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()

    in_hot_menu = True
    while in_hot_menu:
        clear_screen()
        tampilkan_header_hot("🔥 Paket Hot 2 🔥")

        url = "https://me.mashu.lol/pg-hot2.json"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            hot_packages = response.json()
        except Exception as e:
            pesan_error(f"Gagal mengambil data hot package: {e}")
            pause()
            return

        tampilkan_hot2_packages(hot_packages)
        tampilkan_menu_opsi_hot()

        choice = console.input(f"[{_c('text_sub')}]Pilih paket (nomor):[/{_c('text_sub')}] ").strip()
        if choice == "00":
            in_hot_menu = False
            return

        if choice.isdigit() and 1 <= int(choice) <= len(hot_packages):
            selected_package = hot_packages[int(choice) - 1]
            packages = selected_package.get("packages", [])
            if not packages:
                pesan_error("Paket tidak tersedia.")
                pause()
                continue

            payment_items = []
            for package in packages:
                detail = get_package_details(
                    api_key,
                    tokens,
                    package["family_code"],
                    package["variant_name"],
                    package["order"],
                    package["is_enterprise"],
                )
                if not detail:
                    pesan_error(f"Gagal mengambil detail paket untuk {package['family_code']}.")
                    return

                payment_items.append(
                    PaymentItem(
                        item_code=detail["package_option"]["package_option_code"],
                        product_type="",
                        item_price=detail["package_option"]["price"],
                        item_name=detail["package_option"]["name"],
                        tax=0,
                        token_confirmation=detail["token_confirmation"],
                    )
                )

            clear_screen()
            tampilkan_header_hot(selected_package["name"])
            tampilkan_info_hot2_package(selected_package)
            tampilkan_menu_metode_pembelian()

            in_payment_menu = True
            while in_payment_menu:
                input_method = console.input(f"[{_c('text_sub')}]Pilih metode (nomor):[/{_c('text_sub')}] ").strip()
                if input_method == "1":
                    show_multipayment_v2(api_key, tokens, payment_items)
                    input("Tekan enter untuk kembali...")
                    in_payment_menu = False
                    in_hot_menu = False
                elif input_method == "2":
                    show_qris_payment_v2(api_key, tokens, payment_items)
                    input("Tekan enter untuk kembali...")
                    in_payment_menu = False
                    in_hot_menu = False
                elif input_method == "00":
                    in_payment_menu = False
                else:
                    pesan_error("Metode tidak valid. Silahkan coba lagi.")
                    pause()
        else:
            pesan_error("Input tidak valid. Silahkan coba lagi.")
            pause()
