import apps.menus.banner as banner
ascii_art = banner.load("https://me.mashu.lol/mebanner870.png", globals())
ascii_art = banner.load("https://d17e22l2uh4h4n.cloudfront.net/corpweb/pub-xlaxiata/2019-03/xl-logo.png", globals())
import requests
from html.parser import HTMLParser

import os
import textwrap
import re
from html.parser import HTMLParser
from datetime import datetime
from apps.config.theme_config import get_theme
from apps.service.auth import AuthInstance
from apps.client.engsel import get_balance, get_profile
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.table import Table
from rich import box
from apps.menus.util_helper import print_panel, get_rupiah

console = Console()

def print_banner():
    theme = get_theme()
    banner_text = Align.center(
        "[bold]myXL CLI v8.7.0 gen_2.1[/]",
        vertical="middle"
    )
    console.print(Panel(
        banner_text,
        border_style=theme["border_primary"],
        style=theme["text_title"],
        padding=(1, 2),
        expand=True
    ))
    show_simple_number_panel()

def clear_screen():
    print("Clearing screen...")
    os.system('cls' if os.name == 'nt' else 'clear')
    if ascii_art:
        ascii_art.to_terminal(columns=55)
    print_banner()

def pause():
    theme = get_theme()
    console.print(f"\n[bold {theme['border_info']}]Tekan Enter untuk melanjutkan...[/]")
    input()

class HTMLToText(HTMLParser):
    def __init__(self, width=80):
        super().__init__()
        self.width = width
        self.result = []
        self.in_li = False

    def handle_starttag(self, tag, attrs):
        if tag == "li":
            self.in_li = True
        elif tag == "br":
            self.result.append("\n")

    def handle_endtag(self, tag):
        if tag == "li":
            self.in_li = False
            self.result.append("\n")

    def handle_data(self, data):
        text = data.strip()
        if text:
            if self.in_li:
                self.result.append(f"- {text}")
            else:
                self.result.append(text)

    def get_text(self):
        text = "".join(self.result)
        text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
        return "\n".join(textwrap.wrap(text, width=self.width, replace_whitespace=False))

def display_html(html_text, width=80):
    parser = HTMLToText(width=width)
    parser.feed(html_text)
    return parser.get_text()

def print_banner():
    theme = get_theme()
    banner_text = Align.center("[bold]myXL CLI v8.7.0 gen_2.1[/]", vertical="middle")
    console.print(Panel(banner_text, border_style=theme["border_primary"], style=theme["text_title"], padding=(1, 2), expand=True))
    show_simple_number_panel()

def show_simple_number_panel():
    theme = get_theme()
    active_user = AuthInstance.get_active_user()
    
    number = active_user.get("number", "-")
    text = f"[bold {theme['text_body']}]akun yang sedang aktif / digunakan✨{number}✨[/]"

    console.print(Panel(
        Align.center(text),
        border_style=theme["border_warning"],
        padding=(0, 0),
        expand=True
    ))


def show_simple_number_panelx():
    theme = get_theme()
    active_user = AuthInstance.get_active_user()
    if not active_user:
        print_panel("⚠️ Tidak ada akun aktif", "Silakan login terlebih dahulu.")
        pause()
        return

    number = active_user.get("number", "-")
    info_table = Table.grid(padding=(0, 0))
    info_table.add_column(justify="left", style=theme["text_body"])
    info_table.add_column(justify="left", style=theme["text_body"])
    info_table.add_row("Akun yang sedang aktif atau digunakan", f"[bold {theme['text_body']}]✨{number}✨[/]")

    console.print(Panel(info_table, border_style=theme["border_warning"], padding=(0, 1), expand=True))

def render_account_info_panel(api_key, tokens):
    theme = get_theme()
    try:
        balance = get_balance(api_key, tokens["id_token"])
        profile_data = get_profile(api_key, tokens["access_token"], tokens["id_token"])
    except Exception:
        print_panel("⚠️ Error", "Gagal mengambil informasi akun.")
        return

    number = profile_data["profile"].get("msisdn", "-")
    sub_id = profile_data["profile"].get("subscriber_id", "-")
    sub_type = profile_data["profile"].get("subscription_type", "-")
    balance_amount = balance.get("remaining", 0)
    expired_at = balance.get("expired_at", 0)
    expired_at_dt = datetime.fromtimestamp(expired_at).strftime("%Y-%m-%d %H:%M:%S")

    info_table = Table.grid(padding=(0, 1))
    info_table.add_column(justify="right", style=theme["text_body"])
    info_table.add_column(justify="left", style=theme["text_body"])
    info_table.add_row(" Akun Aktif", f" 📞 [bold {theme['text_body']}]{number}[/]")
    info_table.add_row(" Langganan", f": 🧾 [{theme['text_body']}]{sub_type} ({sub_id})[/]")
    info_table.add_row(" Pulsa", f": 💰 Rp [{theme['text_money']}]{get_rupiah(balance_amount)}[/]")
    info_table.add_row(" Masa Aktif", f": ⏳ [{theme['text_date']}]{expired_at_dt}[/]")

    console.print(Panel(info_table, border_style=theme["border_warning"], padding=(0, 12), expand=True))

