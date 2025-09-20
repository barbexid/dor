import app.menus.banner as banner
ascii_art = banner.load("https://d17e22l2uh4h4n.cloudfront.net/corpweb/pub-xlaxiata/2019-03/xl-logo.png", globals())

from html.parser import HTMLParser
import os
import re
import textwrap
from rich.console import Console

console = Console()

def clear_screen():
    print("Clearing screen...")
    os.system('cls' if os.name == 'nt' else 'clear')
    if ascii_art:
        ascii_art.to_terminal(columns=55)

def pause():
    input("\nPress enter to continue...")

def pesan_error(msg):
    console.print(f"[{_c('text_err')}]{msg}[/{_c('text_err')}]")

def pesan_sukses(msg):
    console.print(f"[{_c('text_ok')}]{msg}[/{_c('text_ok')}]")

def pesan_info(msg):
    console.print(f"[{_c('text_warn')}]{msg}[/{_c('text_warn')}]")

def _c(key: str) -> str:
    theme = {
        "text_title": "bold white on dark_green",
        "text_body": "white",
        "text_key": "cyan",
        "text_number": "bold yellow",
        "text_sub": "dim",
        "text_err": "bold red",
        "text_ok": "bold green",
        "text_warn": "yellow",
        "text_value": "bold magenta",
        "text_money": "bold green",
        "text_date": "magenta",
        "border_info": "green",
        "border_primary": "cyan",
        "border_success": "green",
        "border_error": "red",
    }
    return theme.get(key, "white")

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
