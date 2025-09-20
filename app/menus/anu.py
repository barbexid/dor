import requests
from app.client.engsel import get_family
from app.menus.package import show_package_details
from app.service.auth import AuthInstance
from app.menus.util import clear_screen, pause, pesan_error, pesan_info
from app.theme import _c, console

from rich.panel import Panel
from rich.table import Table
from rich.box import MINIMAL_DOUBLE_HEAD
from rich.align import Align

def tampilkan_header():
    header_text = Align.center(f"[{_c('text_title')}]✨Daftar Paket Lainnya..✨[/]")
    panel = Panel(
        header_text,
        border_style=_c("border_primary"),
        padding=(1, 4),
        expand=True
    )
    console.print(panel)

def tampilkan_anu_packages(anu_packages):
    table = Table(box=MINIMAL_DOUBLE_HEAD, expand=True)
    table.add_column("No", justify="right", style=_c("text_number"), width=4)
    table.add_column("Family", style=_c("text_body"))
    table.add_column("Variant", style=_c("text_body"))
    table.add_column("Option", style=_c("text_body"))

    for idx, p in enumerate(anu_packages, 1):
        table.add_row(str(idx), p["family_name"], p["variant_name"], p["option_name"])

    panel = Panel(
        table,
        #title=f"[{_c('text_title')}]judul tabel[/]",
        border_style=_c("border_info"),
        padding=(0, 0),
        expand=True
    )
    console.print(panel)

from rich.text import Text
from rich.align import Align

def tampilkan_menu_opsi():
    kode_text = Text("00", style=_c("text_number"))
    aksi_text = Text("Kembali ke menu utama", style=_c("text_err"))
    kombinasi_text = Text.assemble(kode_text, " ", aksi_text)

    panel = Panel(
        Align.center(kombinasi_text),
        border_style=_c("border_primary"),
        title="",
        title_align="center",
        expand=True,
        padding=(0, 1)
    )
    console.print(panel)

def show_anu_menu():
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    in_anu_menu = True

    while in_anu_menu:
        clear_screen()
        tampilkan_header()

        url = "https://raw.githubusercontent.com/barbexid/apaandah/refs/heads/main/anu.json"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except Exception as e:
            pesan_error(f"Gagal mengambil data anu package: {e}")
            pause()
            return

        anu_packages = response.json()
        tampilkan_anu_packages(anu_packages)
        tampilkan_menu_opsi()

        choice = console.input(f"[{_c('text_sub')}]Pilih paket (nomor):[/{_c('text_sub')}] ").strip()
        if choice == "00":
            in_anu_menu = False
            return

        if choice.isdigit() and 1 <= int(choice) <= len(anu_packages):
            selected_bm = anu_packages[int(choice) - 1]
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
