from app.client.engsel import get_family
from app.menus.package import show_package_details
from app.service.auth import AuthInstance
from app.service.bookmark import BookmarkInstance
from app.menus.util import clear_screen, pause, pesan_error, pesan_info, pesan_sukses
from app.theme import _c, console

from rich.panel import Panel
from rich.table import Table
from rich.box import MINIMAL_DOUBLE_HEAD
from rich.align import Align

def tampilkan_header():
    header_text = Align.center(f"[{_c('text_title')}]Bookmark Paket[/]")
    panel = Panel(
        header_text,
        border_style=_c("border_primary"),
        padding=(1, 4),
        expand=True
    )
    console.print(panel)

def tampilkan_bookmarks(bookmarks):
    table = Table(box=MINIMAL_DOUBLE_HEAD, expand=True)
    table.add_column("No", justify="right", style=_c("text_number"), width=4)
    table.add_column("Family", style=_c("text_body"))
    table.add_column("Variant", style=_c("text_body"))
    table.add_column("Option", style=_c("text_body"))

    for idx, bm in enumerate(bookmarks, 1):
        table.add_row(str(idx), bm["family_name"], bm["variant_name"], bm["option_name"])

    panel = Panel(
        table,
        title=f"[{_c('text_title')}]Daftar Bookmark[/]",
        border_style=_c("border_info"),
        padding=(1, 2),
        expand=True
    )
    console.print(panel)

def tampilkan_menu_opsi():
    opsi = Table.grid(padding=(0, 2))
    opsi.add_column(justify="right", style=_c("text_number"))
    opsi.add_column(style=_c("text_body"))
    opsi.add_row("00", "Kembali ke menu utama")
    opsi.add_row("000", "Hapus Bookmark")

    panel = Panel(opsi, border_style=_c("border_info"), title="Opsi", title_align="center", expand=True)
    console.print(panel)

def hapus_bookmark(bookmarks):
    del_choice = console.input(f"[{_c('text_sub')}]Masukkan nomor bookmark yang ingin dihapus:[/{_c('text_sub')}] ").strip()
    if del_choice.isdigit() and 1 <= int(del_choice) <= len(bookmarks):
        del_bm = bookmarks[int(del_choice) - 1]
        BookmarkInstance.remove_bookmark(
            del_bm["family_code"],
            del_bm["is_enterprise"],
            del_bm["variant_name"],
            del_bm["order"],
        )
        pesan_sukses("Bookmark berhasil dihapus.")
    else:
        pesan_error("Input tidak valid.")
        pause()

def tampilkan_detail_bookmark(selected_bm, api_key, tokens):
    family_code = selected_bm["family_code"]
    is_enterprise = selected_bm["is_enterprise"]
    family_data = get_family(api_key, tokens, family_code, is_enterprise)
    if not family_data:
        pesan_error("Gagal mengambil data family.")
        pause()
        return

    for variant in family_data["package_variants"]:
        if variant["name"] == selected_bm["variant_name"]:
            for option in variant["package_options"]:
                if option["order"] == selected_bm["order"]:
                    option_code = option["package_option_code"]
                    console.print(f"[{_c('text_value')}]{option_code}[/{_c('text_value')}]")
                    show_package_details(api_key, tokens, option_code, is_enterprise)
                    return
    pesan_error("Paket tidak ditemukan.")
    pause()

def show_bookmark_menu():
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()

    while True:
        clear_screen()
        tampilkan_header()
        bookmarks = BookmarkInstance.get_bookmarks()

        if not bookmarks:
            pesan_info("Tidak ada bookmark tersimpan.")
            pause()
            return

        tampilkan_bookmarks(bookmarks)
        tampilkan_menu_opsi()

        choice = console.input(f"[{_c('text_sub')}]Pilih bookmark (nomor):[/{_c('text_sub')}] ").strip()
        if choice == "00":
            return
        elif choice == "000":
            hapus_bookmark(bookmarks)
            continue
        elif choice.isdigit() and 1 <= int(choice) <= len(bookmarks):
            selected_bm = bookmarks[int(choice) - 1]
            tampilkan_detail_bookmark(selected_bm, api_key, tokens)
        else:
            pesan_error("Input tidak valid.")
            pause()
