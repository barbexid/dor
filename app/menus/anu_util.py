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

def loading_animation(text="Memuat ulang...", delay=0.05, repeat=3):
    from time import sleep
    console = Console()
    for _ in range(repeat):
        for dots in [".", "..", "..."]:
            console.print(f"[bold cyan]{text}{dots}[/]", end="\r")
            sleep(delay)
    clear_screen()

import re

def get_rupiah(value) -> str:
    value_str = str(value).strip()

    # Tangani input seperti "Rp1000", "Rp 1,000", "1000", "Rp1000 (refund)"
    match = re.match(r"(Rp)?\s?([\d,]+)(.*)", value_str)
    if not match:
        return value_str  # fallback jika format tidak cocok

    raw_number = match.group(2).replace(",", "")  # hilangkan koma jika ada
    suffix = match.group(3).strip()

    try:
        number = int(raw_number)
    except ValueError:
        return value_str  # fallback jika bukan angka

    # Format angka dengan titik ribuan dan tambahkan ,00
    formatted = f"Rp {number:,}".replace(",", ".")# + ",00"

    return f"{formatted} {suffix}" if suffix else formatted

# banner
import shutil

def center_ascii(ascii_art):
    terminal_width = shutil.get_terminal_size().columns
    centered_lines = []
    for line in str(ascii_art).splitlines():
        padding = max((terminal_width - len(line)) // 2, 0)
        centered_lines.append(" " * padding + line)
    return "\n".join(centered_lines)
