import requests
import json
import sys
from app.service.auth import AuthInstance
from app.client.engsel2 import get_family, get_family_v2, get_package, get_addons, get_package_details, purchase_package, send_api_request
from app.service.bookmark import BookmarkInstance
from app.client.purchase import show_qris_payment, settlement_bounty
from app.client.ewallet import show_multipayment
from app.menus.util import display_html, clear_screen
from app.client.qris import show_qris_payment_v2
from app.client.ewallet import show_multipayment_v2
from app.client.balance import settlement_balance
from app.type_dict import PaymentItem

from app.menus.anu_util import pause, print_panel, get_rupiah
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from rich.align import Align
from rich.box import MINIMAL_DOUBLE_HEAD
from rich.text import Text
from app.config.theme_config import get_theme

console = Console()


def show_package_details(api_key, tokens, package_option_code, is_enterprise, option_order=-1):
    clear_screen()
    theme = get_theme()
    package = get_package(api_key, tokens, package_option_code)

    if not package:
        print_panel("⚠️ Error", "Gagal memuat detail paket.")
        pause()
        return False

    price = package["package_option"]["price"]
    formatted_price = get_rupiah(price)
    validity = package["package_option"]["validity"]
    detail = display_html(package["package_option"]["tnc"])
    point = package["package_option"]["point"]
    plan_type = package["package_family"]["plan_type"]
    payment_for = package["package_family"]["payment_for"] or "BUY_PACKAGE"
    token_confirmation = package["token_confirmation"]
    ts_to_sign = package["timestamp"]

    option_name = package["package_option"].get("name", "")
    family_name = package["package_family"].get("name", "")
    variant_name = package.get("package_detail_variant", {}).get("name", "")
    title = f"{family_name} - {variant_name} - {option_name}".strip()

    payment_items = [
        PaymentItem(
            item_code=package_option_code,
            product_type="",
            item_price=price,
            item_name=f"{variant_name} {option_name}".strip(),
            tax=0,
            token_confirmation=token_confirmation,
        )
    ]
    # Panel judul
    console.print(Panel(
        Align.center(f"[{theme['text_title']}]📦 Paket {family_name}[/]", vertical="middle"),
        border_style=theme["border_primary"],
        padding=(1, 2),
        expand=True
    ))

    # Panel informasi paket
    info_table = Table.grid(padding=(0, 1))
    info_table.add_column(justify="left", style=theme["text_body"])
    info_table.add_column(justify="left")

    info_table.add_row("Nama", f": [bolt {theme['text_body']}]{title}[/]")
    info_table.add_row("Harga", f": [{theme['text_money']}]{formatted_price}[/]")
    info_table.add_row("Masa Aktif", f": [{theme['text_date']}]{validity}[/]")
    info_table.add_row("Point", f": [{theme['text_body']}]{point}[/]")
    info_table.add_row("Plan Type", f": [{theme['text_body']}]{plan_type}[/]")

    info_panel = Panel(
        info_table,
        title=f"[{theme['text_title']}]✨ Informasi Paket ✨[/]",
        title_align="center",
        border_style=theme["border_info"],
        padding=(0, 1),
        expand=True
    )

    console.print(info_panel)

    # Tabel benefit
    benefits = package["package_option"].get("benefits", [])
    if benefits:
        benefit_table = Table(box=MINIMAL_DOUBLE_HEAD, expand=True)
        benefit_table.add_column("Nama", style=theme["text_body"])
        benefit_table.add_column("Jenis", style=theme["border_info"])
        benefit_table.add_column("Unli", style=theme["text_key"], justify="center")
        benefit_table.add_column("Total", style=theme["text_date"], justify="right")

        for benefit in benefits:
            dt = benefit["data_type"]
            total = benefit["total"]
            is_unlimited = benefit["is_unlimited"]

            # Tentukan total_str hanya jika bukan unlimited
            if is_unlimited:
                if dt == "VOICE":
                    total_str = "menit"
                elif dt == "TEXT":
                    total_str = "SMS"
                elif dt == "DATA":
                    total_str = "kuota"
                else:
                    total_str = dt
            else:
                if dt == "VOICE":
                    total_str = f"{total / 60:.0f} menit"
                elif dt == "TEXT":
                    total_str = f"{total} SMS"
                elif dt == "DATA":
                    if total >= 1_000_000_000:
                        total_str = f"{total / (1024 ** 3):.2f} GB"
                    elif total >= 1_000_000:
                        total_str = f"{total / (1024 ** 2):.2f} MB"
                    elif total >= 1_000:
                        total_str = f"{total / 1024:.2f} KB"
                    else:
                        total_str = f"{total} B"
                else:
                    total_str = f"{total} ({dt})"

            benefit_table.add_row(
                benefit["name"],
                dt,
                "✅" if is_unlimited else "-",
                total_str
            )


        console.print(Panel(
            benefit_table,
            title=f"[{theme['text_title']}]Benefit Paket[/]",
            border_style=theme["border_success"],
            padding=(0, 0),
            expand=True
        ))


    # Panel SnK
    console.print(Panel(
        detail,
        title=f"[{theme['text_title']}]✨ Syarat & Ketentuan ✨[/]",
        border_style=theme["border_warning"],
        padding=(0, 1),
        expand=True
    ))

    # Tabel opsi pembelian
    option_table = Table(show_header=False, box=MINIMAL_DOUBLE_HEAD, expand=True)
    option_table.add_column(justify="right", style=theme["text_key"], width=6)
    option_table.add_column(justify="left", style=theme["text_body"])
    option_table.add_row("1", "Beli dengan Pulsa")
    option_table.add_row("2", "Beli dengan E-Wallet")
    option_table.add_row("3", "Bayar dengan QRIS")
    if payment_for == "REDEEM_VOUCHER":
        option_table.add_row("4", "Ambil sebagai bonus")
    if option_order != -1:
        option_table.add_row("0", "Tambah ke Bookmark")
    option_table.add_row("00", f"[{theme['text_err']}]Kembali ke daftar paket[/]")

    console.print(Panel(
        option_table,
        title=f"[{theme['text_title']}]🛒 Opsi Pembelian[/]",
        border_style=theme["border_info"],
        padding=(0, 0),
        expand=True
    ))

    # Input pilihan
    in_package_detail_menu = True
    while in_package_detail_menu:
        choice = console.input(f"[{theme['text_sub']}]Pilihan:[/{theme['text_sub']}] ").strip()
        if choice == "00":
            return False
        elif choice == "0" and option_order != -1:
            success = BookmarkInstance.add_bookmark(
                family_code=package["package_family"]["package_family_code"],
                family_name=family_name,
                is_enterprise=is_enterprise,
                variant_name=variant_name,
                option_name=option_name,
                order=option_order,
            )
            msg = "Paket berhasil ditambahkan ke bookmark." if success else "Paket sudah ada di bookmark."
            print_panel("✅ Info", msg)
            pause()
        elif choice == "1":
            settlement_balance(api_key, tokens, payment_items, payment_for, True, amount_used="first")
            console.input(f"[{theme['text_sub']}]Tekan enter untuk kembali...[/{theme['text_sub']}] ")
            return True
        elif choice == "2":
            show_multipayment_v2(api_key, tokens, payment_items, payment_for, True, amount_used="first")
            console.input(f"[{theme['text_sub']}]Tekan enter untuk kembali...[/{theme['text_sub']}] ")
            return True
        elif choice == "3":
            show_qris_payment_v2(api_key, tokens, payment_items, payment_for, True, amount_used="first")
            console.input(f"[{theme['text_sub']}]Tekan enter untuk kembali...[/{theme['text_sub']}] ")
            return True
        elif choice == "4" and payment_for == "REDEEM_VOUCHER":
            settlement_bounty(
                api_key=api_key,
                tokens=tokens,
                token_confirmation=token_confirmation,
                ts_to_sign=ts_to_sign,
                payment_target=package_option_code,
                price=price,
                item_name=variant_name
            )
        else:
            print_panel("⚠️ Error", "Pilihan tidak valid.")
            pause()


def get_packages_by_family(
    family_code: str,
    is_enterprise: bool | None = None,
    migration_type: str | None = None
):
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    theme = get_theme()
    console = Console()

    if not tokens:
        print_panel("⚠️ Error", "Tidak ditemukan token pengguna aktif.")
        pause()
        return None

    packages = []

    data = get_family_v2(api_key, tokens, family_code, is_enterprise, migration_type)
    if not data:
        print_panel("⚠️ Error", "Gagal memuat data paket family.")
        return None

    in_package_menu = True
    while in_package_menu:
        clear_screen()

        # Panel info family
        info_text = Text()
        info_text.append(f"Nama: {data['package_family']['name']}\n", style="bold")
        info_text.append("Kode: ", style=theme["text_body"])
        info_text.append(f"{family_code}\n", style=theme["border_warning"])
        info_text.append(f"Tipe: {data['package_family']['package_family_type']}\n", style=theme["text_body"])
        info_text.append(f"Jumlah Varian: {len(data['package_variants'])}\n", style=theme["text_body"])

        console.print(Panel(
            info_text,
            title=f"[{theme['text_title']}]✨ Info Paket Family ✨[/]",
            border_style=theme["border_info"],
            padding=(0, 2),
            expand=True
        ))

        # Tabel daftar paket
        package_table = Table(box=MINIMAL_DOUBLE_HEAD, expand=True)
        package_table.add_column("No", justify="right", style=theme["text_key"], width=4)
        package_table.add_column("Varian", style=theme["text_body"])
        package_table.add_column("Nama Paket", style=theme["text_body"])
        package_table.add_column("Harga", style=theme["text_money"], justify="left")

        option_number = 1
        for variant in data["package_variants"]:
            variant_name = variant["name"]
            for option in variant["package_options"]:
                option_name = option["name"]
                formatted_price = get_rupiah(option["price"])
                packages.append({
                    "number": option_number,
                    "variant_name": variant_name,
                    "option_name": option_name,
                    "price": option["price"],
                    "code": option["package_option_code"],
                    "option_order": option["order"]
                })
                package_table.add_row(
                    str(option_number),
                    variant_name,
                    option_name,
                    formatted_price
                )
                option_number += 1

        console.print(Panel(
            package_table,
            #title=f"[{theme['text_title']}]📦 Daftar Paket Tersedia[/]",
            border_style=theme["border_primary"],
            padding=(0, 1),
            expand=True
        ))

        # Panel terpisah untuk navigasi
        #back_panel = Panel(
            #Align.center(f"[{theme['text_body']}]00[/]. [{theme['text_err']}]Kembali ke menu awal", vertical="middle"),
            #title=f"[{theme['text_title']}]🔙 Navigasi[/]",
            #border_style=theme["border_info"],
            #padding=(1, 2),
            #expand=True
        #)
        #console.print(back_panel)

        # Panel navigasi
        nav_table = Table(show_header=False, box=MINIMAL_DOUBLE_HEAD, expand=True)
        nav_table.add_column(justify="right", style=theme["text_key"], width=6)
        nav_table.add_column(style=theme["text_body"])
        nav_table.add_row("00", f"[{theme['text_err']}]Kembali ke menu utama")

        console.print(Panel(
            nav_table,
            #title=f"[{theme['text_title']}]⚙️ Menu Aksi[/]",
            border_style=theme["border_info"],
            padding=(0, 1),
            expand=True
        ))


        # Input pilihan
        pkg_choice = console.input(f"[{theme['text_sub']}]Pilih paket (nomor):[/{theme['text_sub']}] ").strip()
        if pkg_choice == "00":
            in_package_menu = False
            return None

        if not pkg_choice.isdigit():
            print_panel("⚠️ Error", "Input tidak valid. Masukkan nomor paket.")
            pause()
            continue

        selected_pkg = next((p for p in packages if p["number"] == int(pkg_choice)), None)
        if not selected_pkg:
            print_panel("⚠️ Error", "Paket tidak ditemukan. Silakan masukkan nomor yang benar.")
            pause()
            continue

        is_done = show_package_details(
            api_key,
            tokens,
            selected_pkg["code"],
            is_enterprise,
            option_order=selected_pkg["option_order"]
        )
        if is_done:
            in_package_menu = False
            return None

    return packages



def fetch_my_packages():
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    theme = get_theme()
    console = Console()

    if not tokens:
        print_panel("⚠️ Error", "Tidak ditemukan token pengguna aktif.")
        pause()
        return None

    id_token = tokens.get("id_token")
    path = "api/v8/packages/quota-details"
    payload = {
        "is_enterprise": False,
        "lang": "en",
        "family_member_id": ""
    }

    console.print(Panel(
        "[bold]Mengambil daftar paket aktif Anda...[/]",
        border_style=theme["border_info"],
        padding=(0, 1),
        expand=True
    ))

    res = send_api_request(api_key, path, payload, id_token, "POST")
    if res.get("status") != "SUCCESS":
        print_panel("⚠️ Error", "Gagal mengambil paket.")
        pause()
        return None

    quotas = res["data"]["quotas"]
    clear_screen()

    # Panel judul
    console.print(Panel(
        Align.center("📦 Paket Aktif Saya", vertical="middle"),
        border_style=theme["border_info"],
        padding=(1, 2),
        expand=True
    ))

    my_packages = []
    for num, quota in enumerate(quotas, start=1):
        quota_code = quota["quota_code"]
        group_code = quota["group_code"]
        name = quota["name"]
        family_code = "N/A"

        console.print(f"[dim]Mengambil detail paket no. {num}...[/]")
        package_details = get_package(api_key, tokens, quota_code)
        if package_details:
            family_code = package_details["package_family"]["package_family_code"]

        package_text = Text()
        package_text.append(f"📦 Paket {num}\n", style="bold")
        package_text.append("Nama: ", style=theme["border_info"])
        package_text.append(f"{name}\n", style=theme["text_sub"])
        package_text.append("Quota Code: ", style=theme["border_info"])
        package_text.append(f"{quota_code}\n", style=theme["text_body"])
        package_text.append("Family Code: ", style=theme["border_info"])
        package_text.append(f"{family_code}\n", style=theme["border_warning"])
        package_text.append("Group Code: ", style=theme["border_info"])
        package_text.append(f"{group_code}\n", style=theme["text_body"])

        console.print(Panel(
            package_text,
            border_style=theme["border_primary"],
            padding=(0, 1),
            expand=True
        ))

        my_packages.append({
            "number": num,
            "quota_code": quota_code,
        })

    # Panel navigasi
    #console.print(Panel(
        #Align.center(
            #f"[{theme['text_body']}]00[/]. [{theme['text_err']}]Kembali ke menu utama[/]",
            #vertical="middle"
        #),
        #title=f"[{theme['text_title']}]🔙 Navigasi[/]",
        #border_style=theme["border_info"],
        #padding=(1, 2),
        #expand=True
    #))


    # Panel navigasi
    nav_table = Table(show_header=False, box=MINIMAL_DOUBLE_HEAD, expand=True)
    nav_table.add_column(justify="right", style=theme["text_key"], width=6)
    nav_table.add_column(style=theme["text_body"])
    nav_table.add_row("00", f"[{theme['text_err']}]Kembali ke menu utama")

    console.print(Panel(
        nav_table,
        #title=f"[{theme['text_title']}]⚙️ Menu Aksi[/]",
        border_style=theme["border_info"],
        padding=(0, 1),
        expand=True
    ))


    # Input pilihan
    choice = console.input(f"[{theme['text_sub']}]Pilih nomor paket untuk pembelian ulang:[/{theme['text_sub']}] ").strip()
    if choice == "00":
        return None

    selected_pkg = next((pkg for pkg in my_packages if str(pkg["number"]) == choice), None)
    if not selected_pkg:
        print_panel("⚠️ Error", "Paket tidak ditemukan. Silakan masukkan nomor yang benar.")
        pause()
        return None

    is_done = show_package_details(api_key, tokens, selected_pkg["quota_code"], False)
    if is_done:
        return None

    pause()

