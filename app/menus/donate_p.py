from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.table import Table
from app.config.theme_config import get_theme
from app.menus.util import clear_screen
from app.menus.anu_util import pause, live_loading
from rich.console import Console
import qrcode
import io

console = Console()

def show_donate_menu():
    clear_screen()
    theme = get_theme()
    qris_url = "https://link.dana.id/minta?full_url=https://qr.dana.id/v1/281012012022051849509828"

    # Generate QR code ASCII dengan spinner
    qr_code_ascii = live_loading(
        task=lambda: generate_qr_ascii(qris_url),
        text="Menyiapkan QRIS Dana...",
        theme=theme
    )

    # Panel informasi donasi
    donate_info = Text()
    donate_info.append("Dukung Pengembangan MyXL CLI!\n\n", style=f"{theme['text_title']} bold")
    donate_info.append("Jika Anda butuh Kode Unlock untuk menambahkan banyak akun, Hubungi saya di Telegram ( @barbex_id ) bayar seikhlasnya.\n\n", style=theme["text_body"])
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

    live_loading(text="Kembali ke menu utama...", theme=theme)
    pause()


def generate_qr_ascii(data: str) -> str:
    import qrcode
    import io
    qr = qrcode.QRCode(border=1)
    qr.add_data(data)
    qr.make(fit=True)
    qr_ascii = io.StringIO()
    qr.print_ascii(out=qr_ascii)
    return qr_ascii.getvalue()

