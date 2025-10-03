from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.text import Text
from rich.box import MINIMAL_DOUBLE_HEAD
from app.client.engsel2 import get_family
from app.menus.package_p import show_package_details
from app.service.auth import AuthInstance
from app.menus.util import clear_screen
from app.service.bookmark import BookmarkInstance
from app.config.theme_config import get_theme
from app.menus.anu_util import pause, print_panel, live_loading

def show_bookmark_menu():
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    theme = get_theme()
    console = Console()

    while True:
        clear_screen()
        bookmarks = BookmarkInstance.get_bookmarks()

        console.print(Panel(
            Align.center("🔖 Bookmark Paket", vertical="middle"),
            border_style=theme["border_info"],
            padding=(1, 2),
            expand=True
        ))

        if not bookmarks:
            print_panel("ℹ️ Info", "Tidak ada bookmark tersimpan.")
            pause()
            return

        table = Table(box=MINIMAL_DOUBLE_HEAD, expand=True)
        table.add_column("No", justify="right", style=theme["text_key"], width=4)
        table.add_column("Family", style=theme["text_body"])
        table.add_column("Varian", style=theme["text_body"])
        table.add_column("Paket", style=theme["text_sub"])

        for idx, bm in enumerate(bookmarks, start=1):
            table.add_row(str(idx), bm["family_name"], bm["variant_name"], bm["option_name"])

        console.print(Panel(table, border_style=theme["border_primary"], padding=(0, 1), expand=True))

        nav_table = Table(show_header=False, box=MINIMAL_DOUBLE_HEAD, expand=True)
        nav_table.add_column(justify="right", style=theme["text_key"], width=6)
        nav_table.add_column(style=theme["text_body"])
        nav_table.add_row("H", f"[{theme['text_err']}]Hapus Bookmark")
        nav_table.add_row("00", f"[{theme['text_sub']}]Kembali ke menu utama")

        console.print(Panel(nav_table, border_style=theme["border_info"], padding=(0, 1), expand=True))

        choice = console.input(f"[{theme['text_sub']}]Masukkan pilihan:[/{theme['text_sub']}] ").strip().upper()

        if choice == "00":
            live_loading(text="Kembali ke menu utama...", theme=theme)
            return

        elif choice == "H":
            del_choice = console.input("Masukkan nomor bookmark yang ingin dihapus: ").strip()
            if del_choice.isdigit() and 1 <= int(del_choice) <= len(bookmarks):
                del_bm = bookmarks[int(del_choice) - 1]
                live_loading(
                    task=lambda: BookmarkInstance.remove_bookmark(
                        del_bm["family_code"],
                        del_bm["is_enterprise"],
                        del_bm["variant_name"],
                        del_bm["order"],
                    ),
                    text="Menghapus bookmark...",
                    theme=theme
                )
                print_panel("✅ Info", "Bookmark berhasil dihapus.")
            else:
                print_panel("❌ Error", "Input tidak valid. Silakan coba lagi.")
            pause()
            continue

        elif choice.isdigit() and 1 <= int(choice) <= len(bookmarks):
            selected_bm = bookmarks[int(choice) - 1]
            family_code = selected_bm["family_code"]
            is_enterprise = selected_bm["is_enterprise"]

            family_data = live_loading(
                task=lambda: get_family(api_key, tokens, family_code, is_enterprise),
                text="Memuat data family...",
                theme=theme
            )

            if not family_data:
                print_panel("❌ Error", "Gagal mengambil data family.")
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
                result = show_package_details(
                    api_key,
                    tokens,
                    option_code,
                    is_enterprise,
                    option_order=selected_bm["order"]
                )
                if result == "MAIN":
                    return
                elif result == "BACK":
                    continue
                elif result is True:
                    return
            else:
                print_panel("❌ Error", "Paket tidak ditemukan.")
                pause()
        else:
            print_panel("❌ Error", "Input tidak valid. Silakan coba lagi.")
            pause()


