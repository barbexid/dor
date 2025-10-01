from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import os
from app.config.theme_config import get_theme
import re

console = Console()

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def pause():
    theme = get_theme()
    console.print(f"\n[bold {theme['border_info']}]Tekan Enter untuk melanjutkan...[/]")
    input()

def print_panel(title, content):
    theme = get_theme()
    console.print(Panel(content, title=title, title_align="left", style=theme["border_info"]))

def print_menu(title, options):
    theme = get_theme()
    table = Table(title=title, box=box.SIMPLE, show_header=False)
    for key, label in options.items():
        table.add_row(f"[{theme['text_key']}]{key}[/{theme['text_key']}]", f"[{theme['text_value']}]{label}[/{theme['text_value']}]")
    console.print(table)

def print_info(label, value):
    theme = get_theme()
    console.print(f"[{theme['text_sub']}]{label}:[/{theme['text_sub']}] [{theme['text_body']}]{value}[/{theme['text_body']}]")


def get_rupiah(value) -> str:
    # Konversi ke string dan bersihkan
    value_str = str(value).strip()

    # Tangani input seperti "Rp1000", "Rp1000 (refund)", "1000", dll
    match = re.match(r"(Rp)?\s?(\d+)(.*)", value_str)
    if not match:
        return value_str  # fallback jika format tidak cocok

    number = int(match.group(2))
    suffix = match.group(3).strip()

    # Format angka dengan titik ribuan dan tambahkan ,00
    formatted = f"Rp {number:,}".replace(",", ",")# + ",00"

    return f"{formatted} {suffix}" if suffix else formatted
