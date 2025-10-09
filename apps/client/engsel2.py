import json
from apps.client.engsel import send_api_request
from apps.menus.util_helper import live_loading
from apps.config.theme_config import get_theme


def get_pending_transaction(api_key: str, tokens: dict) -> dict:
    path = "api/v8/profile"
    raw_payload = {
        "is_enterprise": False,
        "lang": "en"
    }

    theme = get_theme()
    with live_loading("Mengambil transaksi tertunda...", theme):
        res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")

    return res.get("data")


def get_transaction_history(api_key: str, tokens: dict) -> dict:
    path = "payments/api/v8/transaction-history"
    raw_payload = {
        "is_enterprise": False,
        "lang": "en"
    }

    theme = get_theme()
    with live_loading("Mengambil riwayat transaksi...", theme):
        res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")

    return res.get("data")


def get_tiering_info(api_key: str, tokens: dict) -> dict:
    path = "gamification/api/v8/loyalties/tiering/info"
    raw_payload = {
        "is_enterprise": False,
        "lang": "en"
    }

    theme = get_theme()
    with live_loading("Mengambil info tiering...", theme):
        res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")

    if res:
        return res.get("data", {})
    return {}

def segments(api_key: str, id_token: str, access_token: str, balance: int = 0) -> dict | None:
    """
    Mengambil data segmentasi pengguna: loyalty, notifikasi, dan paket spesial (SFY).
    """
    path = "dashboard/api/v8/segments"
    payload = {
        "access_token": access_token,
        "app_version": "8.7.0",
        "current_balance": balance,
        "family_plan_role": "NO_ROLE",
        "is_enterprise": False,
        "lang": "id",
        "manufacturer_name": "samsung",
        "model_name": "SM-N935F"
    }

    theme = get_theme()
    with live_loading("Mengambil data segmen pengguna...", theme):
        try:
            res = send_api_request(api_key, path, payload, id_token, "POST")
        except Exception as e:
            print(f"❌ Gagal kirim request segments: {e}")
            return None

    if not (isinstance(res, dict) and "data" in res):
        err = res.get("error", "Unknown error") if isinstance(res, dict) else res
        print(f"❌ Error respons segments: {err}")
        return None

    data = res["data"]

    # Loyalty
    loyalty_data = data.get("loyalty", {}).get("data", {})
    loyalty_info = {
        "current_point": loyalty_data.get("current_point", 0),
        "tier_name": loyalty_data.get("detail_tier", {}).get("name", "")
    }

    # Notification
    notifications = data.get("notification", {}).get("data", [])

    # Special For You
    sfy_data = data.get("special_for_you", {}).get("data", {})
    sfy_banners = sfy_data.get("banners", [])
    special_packages = []

    for pkg in sfy_banners:
        try:
            if not pkg.get("action_param"):
                continue  # skip jika tidak ada kode paket

            kuota_total = sum(
                int(benefit.get("total", 0))
                for benefit in pkg.get("benefits", [])
                if benefit.get("data_type") == "DATA"
            )
            kuota_gb = kuota_total / (1024 ** 3)

            original_price = int(pkg.get("original_price", 0))
            discounted_price = int(pkg.get("discounted_price", original_price))
            diskon_percent = int(round((original_price - discounted_price) / original_price * 100)) if original_price else 0

            formatted_pkg = {
                "name": f"{pkg.get('family_name', '')} ({pkg.get('title', '')}) {pkg.get('validity', '')}",
                "kode_paket": pkg.get("action_param", ""),
                "original_price": original_price,
                "diskon_price": discounted_price,
                "diskon_percent": diskon_percent,
                "kuota_gb": kuota_gb
            }
            special_packages.append(formatted_pkg)
        except Exception as e:
            print(f"⚠️ Gagal parse paket SFY: {e}")
            continue

    return {
        "loyalty": loyalty_info,
        "notification": notifications,
        "special_packages": special_packages
    }
