import json
from app.service.auth import AuthInstance
from app.client.engsel import get_family, get_package, get_addons, purchase_package, send_api_request
from app.service.bookmark import BookmarkInstance
from app.client.purchase import show_qris_payment, settlement_bounty
from app.client.ewallet import show_multipayment
from app.menus.util import clear_screen, pause, display_html
from app.client.qris import show_qris_payment_v2
from app.client.ewallet import show_multipayment_v2
from app.type_dict import PaymentItem
from app.menus.util import clear_screen, pause, display_html, pesan_error, pesan_sukses, pesan_info
from app.theme import _c, console
from rich.panel import Panel
from rich.table import Table
from rich.box import MINIMAL_DOUBLE_HEAD
from rich.align import Align


def show_package_details(api_key, tokens, package_option_code, is_enterprise, option_order = -1):
    clear_screen()
    package = get_package(api_key, tokens, package_option_code)
    if not package:
        pesan_error("Gagal memuat detail paket.")
        pause()
        return False

    variant_name = package.get("package_detail_variant", {}).get("name", "")
    option_name = package.get("package_option", {}).get("name", "")
    family_name = package.get("package_family", {}).get("name", "")
    title = f"{variant_name} {option_name}".strip()
    item_name = f"{variant_name} {option_name}".strip()
    price = package["package_option"]["price"]
    validity = package["package_option"]["validity"]
    token_confirmation = package["token_confirmation"]
    ts_to_sign = package["timestamp"]
    payment_for = package["package_family"]["payment_for"]
    detail = display_html(package["package_option"]["tnc"])

    console.print(Panel(f"[{_c('text_title')}]📦 Paket {family_name}[/]", border_style=_c("border_primary"), padding=(1, 4), expand=True))

    info = Table.grid(padding=(0, 2))
    info.add_column(justify="right", style=_c("text_sub"))
    info.add_column(style=_c("text_body"))
    info.add_row("Nama", f"[{_c('text_value')}]{title}[/]")
    info.add_row("Harga", f"[{_c('text_money')}]Rp {price:,}[/]")
    info.add_row("Masa Aktif", f"[{_c('text_date')}]{validity}[/]")
    console.print(Panel(info, title=f"[{_c('text_title')}]Detail Paket[/]", border_style=_c("border_info"), padding=(0, 0), expand=True))

    benefits = package["package_option"].get("benefits", [])
    if benefits:
        benefit_table = Table(box=MINIMAL_DOUBLE_HEAD, expand=True)
        benefit_table.add_column("Nama", style=_c("text_body"))
        benefit_table.add_column("Jumlah", style=_c("text_value"), justify="right")
        for benefit in benefits:
            name = benefit.get("name", "")
            total = benefit.get("total", 0)
            if "Call" in name:
                value = f"{total / 60:.0f} menit"
            else:
                if total >= 1_000_000_000:
                    value = f"{total / (1024 ** 3):.2f} GB"
                elif total >= 1_000_000:
                    value = f"{total / (1024 ** 2):.2f} MB"
                elif total >= 1_000:
                    value = f"{total / 1024:.2f} KB"
                else:
                    value = str(total)
            benefit_table.add_row(name, value)
        console.print(Panel(benefit_table, title=f"[{_c('text_title')}]Benefit Paket[/]", border_style=_c("border_success"), padding=(0, 0), expand=True))

    addons = get_addons(api_key, tokens, package_option_code)
    if addons:
        addon_text = json.dumps(addons, indent=2)
        console.print(Panel(addon_text, title=f"[{_c('text_title')}]Addons[/]", border_style=_c("border_info"), padding=(0, 1), expand=True))

    console.print(Panel(detail, title=f"[{_c('text_title')}]Syarat & Ketentuan[/]", border_style=_c("border_warning"), padding=(0, 1), expand=True))

    while True:
        #clear_screen()
        menu = Table(show_header=False, box=MINIMAL_DOUBLE_HEAD, expand=True)
        menu.add_column("Kode", justify="right", style=_c("text_number"), width=6)
        menu.add_column("Aksi", style=_c("text_body"))
        menu.add_row("1", "Beli dengan Pulsa")
        menu.add_row("2", "Beli dengan E-Wallet")
        menu.add_row("3", "Bayar dengan QRIS")
        if payment_for == "REDEEM_VOUCHER":
            menu.add_row("4", "Ambil sebagai bonus")
        if option_order != -1:
            menu.add_row("0", f"[{_c('text_sub')}]Tambah ke Bookmark[/]")
        menu.add_row("00", f"[{_c('text_err')}]Kembali ke daftar paket[/]")
        console.print(Panel(menu, title=f"[{_c('text_title')}]Aksi Pembelian[/]", border_style=_c("border_primary"), padding=(0, 0), expand=True))

        choice = console.input(f"[{_c('text_sub')}]Pilihan:[/{_c('text_sub')}] ").strip()
        if choice == "00":
            return False
        elif choice == "0" and option_order != -1:
            success = BookmarkInstance.add_bookmark(
                family_code=package.get("package_family", {}).get("package_family_code", ""),
                family_name=family_name,
                is_enterprise=is_enterprise,
                variant_name=variant_name,
                option_name=option_name,
                order=option_order,
            )
            msg = "Paket berhasil ditambahkan ke bookmark." if success else "Paket sudah ada di bookmark."
            console.print(f"[{_c('text_ok') if success else _c('text_warn')}] {msg} [/{_c('text_ok') if success else _c('text_warn')}]")
            pause()
        elif choice == "1":
            purchase_package(api_key, tokens, package_option_code, is_enterprise)
            console.input("Cek hasil pembelian di aplikasi MyXL. Tekan Enter untuk kembali.")
            return True
        elif choice == "2":
            show_multipayment(api_key, tokens, package_option_code, token_confirmation, price, title)
            console.input("Lakukan pembayaran & cek hasil pembelian di aplikasi MyXL. Tekan Enter untuk kembali.")
            return True
        elif choice == "3":
            show_qris_payment(api_key, tokens, package_option_code, token_confirmation, price, title)
            console.input("Lakukan pembayaran & cek hasil pembelian di aplikasi MyXL. Tekan Enter untuk kembali.")
            return True
        elif choice == "4":
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
            console.print(f"[{_c('text_err')}]Pilihan tidak valid.[/{_c('text_err')}]")
            pause()


# ========== Daftar Paket Berdasarkan Family ==========
from rich.text import Text
from rich.align import Align

def get_packages_by_family(family_code: str, is_enterprise: bool = False):
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    if not tokens:
        pesan_error("Token pengguna tidak ditemukan.")
        pause()
        return None

    data = get_family(api_key, tokens, family_code, is_enterprise)
    if not data:
        pesan_error("Gagal memuat data paket keluarga.")
        pause()
        return None

    packages = []
    family_name = data['package_family']["name"]
    package_variants = data["package_variants"]

    while True:
        clear_screen()
        judul_panel = Panel(
            Align.center(f"✨Paket Tersedia - {family_name}✨", vertical="middle"),
            style=_c("text_title"),
            border_style=_c("border_info"),
            padding=(1, 2),
            expand=True
        )
        console.print(judul_panel)

        table = Table(box=MINIMAL_DOUBLE_HEAD, expand=True)
        table.add_column("No", justify="right", style=_c("text_number"), width=6)
        table.add_column("Variant", style=_c("text_sub"))
        table.add_column("Nama Paket", style=_c("text_body"))
        table.add_column("Harga", style=_c("text_money"), justify="left")

        option_number = 1
        for variant in package_variants:
            variant_name = variant["name"]
            for option in variant["package_options"]:
                option_name = option["name"]
                price = option["price"]
                packages.append({
                    "number": option_number,
                    "variant_name": variant_name,
                    "option_name": option_name,
                    "price": price,
                    "code": option["package_option_code"],
                    "option_order": option["order"]
                })
                table.add_row(str(option_number), variant_name, option_name, f"Rp {price:,}")
                option_number += 1

        panel = Panel(table, border_style=_c("border_info"), padding=(0, 0), expand=True)
        console.print(panel)

        kode_text = Text("00", style=_c("text_number"))
        aksi_text = Text("Kembali Kehalaman Utama", style=_c("text_err"))
        kombinasi_text = Text.assemble(kode_text, " ", aksi_text)
        centered_box = Panel(
            Align.center(kombinasi_text),
            border_style=_c("border_primary"),
            expand=True
        )
        console.print(centered_box)

        choice = console.input(f"[{_c('text_sub')}]Pilih paket (nomor):[/{_c('text_sub')}] ").strip()

        if choice == "00":
            return None

        selected_pkg = next((p for p in packages if str(p["number"]) == choice), None)
        if not selected_pkg:
            pesan_error("Paket tidak ditemukan. Silakan coba lagi.")
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
            return None

# ========== Daftar Paket Aktif Saya ==========
def fetch_my_packages():
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    if not tokens:
        pesan_error("Token pengguna tidak ditemukan.")
        pause()
        return None

    id_token = tokens.get("id_token")
    path = "api/v8/packages/quota-details"
    payload = {
        "is_enterprise": False,
        "lang": "en",
        "family_member_id": ""
    }

    console.print("Mengambil daftar paket aktif...", style=_c("text_sub"))
    res = send_api_request(api_key, path, payload, id_token, "POST")
    if res.get("status") != "SUCCESS":
        pesan_error("Gagal mengambil paket.")
        pause()
        return None

    quotas = res["data"]["quotas"]
    my_packages = []

    clear_screen()
    console.print(Panel("Daftar Paket Saya", style=_c("text_title"), border_style=_c("border_info"), padding=(0, 2), expand=True))

    for idx, quota in enumerate(quotas, 1):
        quota_code = quota["quota_code"]
        group_code = quota["group_code"]
        name = quota["name"]
        family_code = "N/A"

        package_details = get_package(api_key, tokens, quota_code)
        if package_details:
            family_code = package_details["package_family"]["package_family_code"]

        isi = (
            f"[bold]{name}[/bold]\n"
            f"[{_c('text_sub')}]Nomor:[/] [bold]{idx}[/bold]\n"
            f"[{_c('text_sub')}]Family Code:[/] [bold]{family_code}[/bold]\n"
            f"[{_c('text_sub')}]Group Code:[/] [bold]{group_code}[/bold]\n"
            f"[{_c('text_sub')}]Quota Code:[/] [bold]{quota_code}[/bold]"
        )

        console.print(Panel(isi, border_style=_c("border_primary"), padding=(1, 2), expand=True))

        my_packages.append({
            "number": idx,
            "quota_code": quota_code,
        })

    console.print(f"[{_c('text_sub')}]Masukkan nomor paket untuk membeli ulang, atau '00' untuk kembali.[/{_c('text_sub')}]")
    choice = console.input(f"[{_c('text_sub')}]Pilihan:[/{_c('text_sub')}] ").strip()

    if choice == "00":
        return None

    selected_pkg = next((pkg for pkg in my_packages if str(pkg["number"]) == choice), None)
    if not selected_pkg:
        pesan_error("Paket tidak ditemukan. Silakan coba lagi.")
        pause()
        return None

    is_done = show_package_details(api_key, tokens, selected_pkg["quota_code"], False)
    if is_done:
        return None

    pause()
