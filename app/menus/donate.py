from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.table import Table
from app.config.theme_config import get_theme
from app.menus.util import pause, clear_screen
from rich.console import Console
import qrcode
import io

console = Console()

def show_donate_menu():
    clear_screen()
    theme = get_theme()
    qris_url = "https://link.dana.id/minta?full_url=https://qr.dana.id/v1/281012012022051849509828"

    # Generate QR code ASCII
    qr = qrcode.QRCode(border=1)
    qr.add_data(qris_url)
    qr.make(fit=True)
    qr_ascii = io.StringIO()
    qr.print_ascii(out=qr_ascii)
    qr_code_ascii = qr_ascii.getvalue()

    # Panel informasi donasi
    donate_info = Text()
    donate_info.append("Dukung Pengembangan MyXL CLI!\n\n", style=f"{theme['text_title']} bold")
    donate_info.append("Jika Anda butuh Kode Unlock untuk menambahkan akun, Hubungi saya di Telegram ( @barbex_id )\n\n", style=theme["text_body"])
    donate_info.append("Dan jika ingin memberikan donasi untuk mendukung pengembangan tool ini, silakan gunakan metode berikut:\n\n", style=theme["text_body"])
    donate_info.append("- Dana: 0831-1921-5545\n", style=theme["text_body"])
    donate_info.append("  A/N Joko S\n", style=theme["text_body"])
    donate_info.append("- QRIS tersedia di bawah\n\n", style=theme["text_body"])
    donate_info.append("Terima kasih atas dukungan Anda! 🙏", style=theme["text_sub"])

    console.print(Panel(
        Align.left(donate_info),
        title=f"[{theme['text_title']}]💰 Donasi Seikhlasnya[/]",
        border_style=theme["border_success"],
        padding=(1, 2),
        expand=True,
        title_align="center"
    ))

    # Panel QR code
    console.print(Panel(
        Align.center(qr_code_ascii),
        title=f"[{theme['text_title']}]📱 Scan QRIS Dana[/]",
        border_style=theme["border_info"],
        padding=(1, 2),
        expand=True,
        title_align="center"
    ))

    pause()
