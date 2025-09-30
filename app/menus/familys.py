import os
import json
from app.menus.package import get_packages_by_family
from app.menus.util import clear_screen

from app.menus.anu_util import pause, print_panel, get_rupiah
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from rich.align import Align
from rich.box import MINIMAL_DOUBLE_HEAD
from rich.text import Text
from app.config.theme_config import get_theme

console = Console()

FAMILY_FILE = os.path.abspath("family_codes.json")

def ensure_family_file():
    default_data = {"codes": []}
    if not os.path.exists(FAMILY_FILE):
        with open(FAMILY_FILE, "w") as f:
            json.dump(default_data, f, indent=2)
        return default_data

    try:
        with open(FAMILY_FILE, "r") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "codes" not in data or not isinstance(data["codes"], list):
            raise ValueError("Struktur tidak valid")
        return data
    except (json.JSONDecodeError, ValueError):
        with open(FAMILY_FILE, "w") as f:
            json.dump(default_data, f, indent=2)
        return default_data

def list_family_codes():
    data = ensure_family_file()
    return data["codes"]

def add_family_code(code, name):
    if not code or not name:
        return False
    data = ensure_family_file()
    if any(item["code"] == code for item in data["codes"]):
        return False
    data["codes"].append({"code": code, "name": name})
    with open(FAMILY_FILE, "w") as f:
        json.dump(data, f, indent=2)
    return True

def remove_family_code(index):
    data = ensure_family_file()
    if 0 <= index < len(data["codes"]):
        removed = data["codes"].pop(index)
        with open(FAMILY_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return removed["code"]
    return None

def edit_family_name(index, new_name):
    if not new_name:
        return False
    data = ensure_family_file()
    if 0 <= index < len(data["codes"]):
        data["codes"][index]["name"] = new_name
        with open(FAMILY_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return True
    return False

def show_family_menu():
    while True:
        clear_screen()
        semua_kode = list_family_codes()
        theme = get_theme()
        console = Console()

        # Panel judul
        console.print(Panel(
            Align.center("📋 Kode Yang Terdaftar", vertical="middle"),
            border_style=theme["border_primary"],
            padding=(1, 2),
            expand=True
        ))

        # Tabel daftar kode
        packages = []
        if semua_kode:
            table = Table(box=MINIMAL_DOUBLE_HEAD, expand=True)
            table.add_column("No", justify="right", style=theme["text_key"], width=3)
            table.add_column("Nama FC", style=theme["text_body"])
            table.add_column("Family Code", style=theme["text_sub"])

            for i, item in enumerate(semua_kode, start=1):
                table.add_row(str(i), item["name"], item["code"])
                packages.append({
                    "number": i,
                    "code": item["code"],
                    "name": item["name"]
                })

            console.print(Panel(
                table,
                #title=f"[{theme['text_title']}]📦 Daftar Family Code[/]",
                border_style=theme["border_success"],
                padding=(0, 0),
                expand=True
            ))
        else:
            console.print(Panel(
                "[italic]Belum ada family code yang terdaftar.[/italic]",
                border_style=theme["border_warning"],
                padding=(1, 2),
                expand=True
            ))

        # Panel navigasi
        nav_table = Table(show_header=False, box=MINIMAL_DOUBLE_HEAD, expand=True)
        nav_table.add_column(justify="right", style=theme["text_key"], width=6)
        nav_table.add_column(style=theme["text_body"])
        nav_table.add_row("T", "Tambah family code")
        nav_table.add_row("H", "Hapus family code")
        nav_table.add_row("E", "Edit nama family code")
        nav_table.add_row("00", f"[{theme['text_err']}]Kembali ke menu utama")

        console.print(Panel(
            nav_table,
            #title=f"[{theme['text_title']}]⚙️ Menu Aksi[/]",
            border_style=theme["border_primary"],
            padding=(0, 1),
            expand=True
        ))

        # Input pilihan
        aksi = console.input(f"[{theme['text_sub']}]Pilih aksi atau nomor kode:[/{theme['text_sub']}] ").strip().lower()

        if aksi == "t":
            code = console.input("Masukkan family code: ").strip()
            name = console.input("Masukkan nama family: ").strip()
            if add_family_code(code, name):
                print_panel("✅ Info", "Berhasil menambahkan family code.")
            else:
                print_panel("❌ Error", "Sudah ada dengan family yang sama.")
            pause()

        elif aksi == "h":
            if not semua_kode:
                print_panel("ℹ️ Info", "Tidak ada kode untuk dihapus.")
                pause()
                continue
            idx = console.input("Masukkan nomor kode yang ingin dihapus: ").strip()
            if not idx.isdigit() or int(idx) < 1 or int(idx) > len(semua_kode):
                print_panel("❌ Error", "Nomor tidak ditemukan.")
            else:
                index = int(idx) - 1
                nama = semua_kode[index]["name"]
                kode = semua_kode[index]["code"]
                konfirmasi = console.input(f"Yakin ingin menghapus '{nama}' ({kode})? (y/n): ").strip().lower()
                if konfirmasi == "y":
                    removed = remove_family_code(index)
                    if removed:
                        print_panel("✅ Info", f"Berhasil menghapus {removed}.")
                    else:
                        print_panel("❌ Error", "Gagal menghapus kode.")
                else:
                    print_panel("❎ Info", "Penghapusan dibatalkan.")
            pause()

        elif aksi == "e":
            if not semua_kode:
                print_panel("ℹ️ Info", "Tidak ada kode untuk diedit.")
                pause()
                continue
            idx = console.input("Masukkan nomor kode yang ingin diubah namanya: ").strip()
            if not idx.isdigit() or int(idx) < 1 or int(idx) > len(semua_kode):
                print_panel("❌ Error", "Nomor tidak ditemukan.")
            else:
                new_name = console.input("Masukkan nama baru: ").strip()
                if edit_family_name(int(idx) - 1, new_name):
                    print_panel("✅ Info", "Nama berhasil diperbarui.")
                else:
                    print_panel("❌ Error", "Gagal memperbarui nama.")
            pause()

        elif aksi == "00":
            break

        elif aksi.isdigit():
            nomor = int(aksi)
            selected = next((p for p in packages if p["number"] == nomor), None)
            if selected:
                try:
                    get_packages_by_family(selected["code"])
                except Exception as e:
                    print_panel("❌ Error", f"Gagal menampilkan paket: {e}")
            else:
                print_panel("❌ Error", "Nomor tidak valid.")
            pause()

        else:
            print_panel("❌ Error", "Pilihan tidak valid.")
            pause()
