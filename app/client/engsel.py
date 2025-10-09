import os
import json
import uuid
import requests

from datetime import datetime, timedelta, timezone
from app.menus.util_helper import live_loading, print_panel
from app.config.theme_config import get_theme

from app.client.encrypt import (
    encryptsign_xdata,
    java_like_timestamp,
    ts_gmt7_without_colon,
    ax_api_signature,
    decrypt_xdata,
    API_KEY,
    load_ax_fp,
    ax_device_id
)

BASE_API_URL = os.getenv("BASE_API_URL")
BASE_CIAM_URL = os.getenv("BASE_CIAM_URL")
if not BASE_API_URL or not BASE_CIAM_URL:
    raise ValueError("BASE_API_URL or BASE_CIAM_URL environment variable not set")

GET_OTP_URL = BASE_CIAM_URL + "/realms/xl-ciam/auth/otp"
BASIC_AUTH = os.getenv("BASIC_AUTH")
AX_DEVICE_ID = ax_device_id()
AX_FP = load_ax_fp()
SUBMIT_OTP_URL = BASE_CIAM_URL + "/realms/xl-ciam/protocol/openid-connect/token"
UA = os.getenv("UA")

def validate_contact(contact: str) -> bool:
    if not contact.startswith("628") or len(contact) > 14:
        print("Invalid number")
        return False
    return True


def get_otp(contact: str) -> str:
    if not validate_contact(contact):
        print_panel("⚠️ Error", "Nomor tidak valid.")
        return None

    url = GET_OTP_URL
    querystring = {
        "contact": contact,
        "contactType": "SMS",
        "alternateContact": "false"
    }

    now = datetime.now(timezone(timedelta(hours=7)))
    ax_request_at = java_like_timestamp(now)
    ax_request_id = str(uuid.uuid4())

    payload = ""
    headers = {
        "Accept-Encoding": "gzip, deflate, br",
        "Authorization": f"Basic {BASIC_AUTH}",
        "Ax-Device-Id": AX_DEVICE_ID,
        "Ax-Fingerprint": AX_FP,
        "Ax-Request-At": ax_request_at,
        "Ax-Request-Device": "samsung",
        "Ax-Request-Device-Model": "SM-N935F",
        "Ax-Request-Id": ax_request_id,
        "Ax-Substype": "PREPAID",
        "Content-Type": "application/json",
        "Host": BASE_CIAM_URL.replace("https://", ""),
        "User-Agent": UA,
    }

    theme = get_theme()
    try:
        with live_loading("Mengirim OTP ke nomor Anda...", theme):
            response = requests.get(url, data=payload, headers=headers, params=querystring, timeout=30)

        json_body = json.loads(response.text)
        if "subscriber_id" not in json_body:
            print_panel("⚠️ Error", json_body.get("error", "Subscriber ID tidak ditemukan."))
            return None

        return json_body["subscriber_id"]
    except Exception as e:
        print_panel("⚠️ Error", f"Gagal mengirim OTP: {e}")
        return None


def submit_otp(api_key: str, contact: str, code: str):
    if not validate_contact(contact):
        print_panel("⚠️ Error", "Nomor tidak valid.")
        return None

    if not code or len(code) != 6:
        print_panel("⚠️ Error", "Format OTP tidak valid. Harus 6 digit angka.")
        return None

    url = SUBMIT_OTP_URL
    now_gmt7 = datetime.now(timezone(timedelta(hours=7)))
    ts_for_sign = ts_gmt7_without_colon(now_gmt7)
    ts_header = ts_gmt7_without_colon(now_gmt7 - timedelta(minutes=5))
    signature = ax_api_signature(api_key, ts_for_sign, contact, code, "SMS")

    payload = f"contactType=SMS&code={code}&grant_type=password&contact={contact}&scope=openid"
    headers = {
        "Accept-Encoding": "gzip, deflate, br",
        "Authorization": f"Basic {BASIC_AUTH}",
        "Ax-Api-Signature": signature,
        "Ax-Device-Id": AX_DEVICE_ID,
        "Ax-Fingerprint": AX_FP,
        "Ax-Request-At": ts_header,
        "Ax-Request-Device": "samsung",
        "Ax-Request-Device-Model": "SM-N935F",
        "Ax-Request-Id": str(uuid.uuid4()),
        "Ax-Substype": "PREPAID",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": UA,
    }

    theme = get_theme()
    try:
        with live_loading("Memverifikasi OTP dan login...", theme):
            response = requests.post(url, data=payload, headers=headers, timeout=30)

        json_body = json.loads(response.text)
        if "error" in json_body:
            print_panel("⚠️ Error", json_body.get("error_description", "Gagal login."))
            return None

        print_panel("✅ Sukses", "Login berhasil.")
        return json_body
    except requests.RequestException as e:
        print_panel("⚠️ Error", f"Gagal login: {e}")
        return None

def get_new_token(refresh_token: str) -> str:
    url = SUBMIT_OTP_URL

    now = datetime.now(timezone(timedelta(hours=7)))  # GMT+7
    ax_request_at = now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "+0700"
    ax_request_id = str(uuid.uuid4())

    headers = {
        "Host": BASE_CIAM_URL.replace("https://", ""),
        "ax-request-at": ax_request_at,
        "ax-device-id": AX_DEVICE_ID,
        "ax-request-id": ax_request_id,
        "ax-request-device": "samsung",
        "ax-request-device-model": "SM-N935F",
        "ax-fingerprint": AX_FP,
        "authorization": f"Basic {BASIC_AUTH}",
        "user-agent": UA,
        "ax-substype": "PREPAID",
        "content-type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    resp = requests.post(url, headers=headers, data=data, timeout=30)
    if resp.status_code == 400:
        if resp.json().get("error_description") == "Session not active":
            print("Refresh token expired. Pleas remove and re-add the account.")
            return None
        
    resp.raise_for_status()

    body = resp.json()
    
    if "id_token" not in body:
        raise ValueError("ID token not found in response")
    if "error" in body:
        raise ValueError(f"Error in response: {body['error']} - {body.get('error_description', '')}")
    
    return body

def send_api_request(
    api_key: str,
    path: str,
    payload_dict: dict,
    id_token: str,
    method: str = "POST",
):
    encrypted_payload = encryptsign_xdata(
        api_key=api_key,
        method=method,
        path=path,
        id_token=id_token,
        payload=payload_dict
    )
    
    xtime = int(encrypted_payload["encrypted_body"]["xtime"])
    
    now = datetime.now(timezone.utc).astimezone()
    sig_time_sec = (xtime // 1000)

    body = encrypted_payload["encrypted_body"]
    x_sig = encrypted_payload["x_signature"]
    
    headers = {
        "host": BASE_API_URL.replace("https://", ""),
        "content-type": "application/json; charset=utf-8",
        "user-agent": UA,
        "x-api-key": API_KEY,
        "authorization": f"Bearer {id_token}",
        "x-hv": "v3",
        "x-signature-time": str(sig_time_sec),
        "x-signature": x_sig,
        "x-request-id": str(uuid.uuid4()),
        "x-request-at": java_like_timestamp(now),
        "x-version-app": "8.7.0",
    }
    
    

    url = f"{BASE_API_URL}/{path}"
    resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=30)
    
    # print(f"Headers: {json.dumps(headers, indent=2)}")
    # print(f"Response body: {resp.text}")

    try:
        decrypted_body = decrypt_xdata(api_key, json.loads(resp.text))
        # print(f"Decrypted body: {json.dumps(decrypted_body, indent=2)}")
        return decrypted_body
    except Exception as e:
        print("[decrypt err]", e)
        return resp.text


def get_profile(api_key: str, access_token: str, id_token: str) -> dict:
    path = "api/v8/profile"
    raw_payload = {
        "access_token": access_token,
        "app_version": "8.7.0",
        "is_enterprise": False,
        "lang": "en"
    }

    theme = get_theme()
    with live_loading("Mengambil profil pengguna...", theme):
        res = send_api_request(api_key, path, raw_payload, id_token, "POST")

    return res.get("data")


def get_balance(api_key: str, id_token: str) -> dict:
    path = "api/v8/packages/balance-and-credit"
    raw_payload = {
        "is_enterprise": False,
        "lang": "en"
    }

    theme = get_theme()
    with live_loading("Mengambil saldo dan kuota...", theme):
        res = send_api_request(api_key, path, raw_payload, id_token, "POST")

    if "data" in res and "balance" in res["data"]:
        return res["data"]["balance"]
    else:
        print_panel("⚠️ Error", res.get("error", "Gagal mengambil saldo."))
        return None


def get_family(
    api_key: str,
    tokens: dict,
    family_code: str,
    is_enterprise: bool | None = None,
    migration_type: str | None = None
) -> dict:
    theme = get_theme()
    id_token = tokens.get("id_token")
    path = "api/v8/xl-stores/options/list"

    is_enterprise_list = [is_enterprise] if is_enterprise is not None else [False, True]
    migration_type_list = [migration_type] if migration_type is not None else [
        "NONE", "PRE_TO_PRIOH", "PRE_TO_PRIO", "PRIO_TO_PRIOH"
    ]

    family_data = None

    with live_loading("Mengambil data paket family...", theme):
        for mt in migration_type_list:
            if family_data:
                break
            for ie in is_enterprise_list:
                if family_data:
                    break

                payload_dict = {
                    "is_show_tagging_tab": True,
                    "is_dedicated_event": True,
                    "is_transaction_routine": False,
                    "migration_type": mt,
                    "package_family_code": family_code,
                    "is_autobuy": False,
                    "is_enterprise": ie,
                    "is_pdlp": True,
                    "referral_code": "",
                    "is_migration": False,
                    "lang": "en"
                }

                res = send_api_request(api_key, path, payload_dict, id_token, "POST")
                if res.get("status") != "SUCCESS":
                    continue

                family_name = res["data"]["package_family"].get("name", "")
                if family_name:
                    family_data = res["data"]

    if family_data is None:
        print_panel("⚠️ Error", f"Gagal mendapatkan data family untuk kode: {family_code}")
        return None

    return family_data


def get_families(api_key: str, tokens: dict, package_category_code: str) -> dict:
    path = "api/v8/xl-stores/families"
    payload_dict = {
        "migration_type": "",
        "is_enterprise": False,
        "is_shareable": False,
        "package_category_code": package_category_code,
        "with_icon_url": True,
        "is_migration": False,
        "lang": "en"
    }

    theme = get_theme()
    with live_loading("Mengambil daftar paket family...", theme):
        res = send_api_request(api_key, path, payload_dict, tokens["id_token"], "POST")

    if res.get("status") != "SUCCESS":
        print_panel("⚠️ Error", f"Gagal mengambil paket family untuk kategori: {package_category_code}")
        return None

    return res["data"]


def get_package(
    api_key: str,
    tokens: dict,
    package_option_code: str,
    package_family_code: str = "",
    package_variant_code: str = ""
) -> dict:
    path = "api/v8/xl-stores/options/detail"
    raw_payload = {
        "is_transaction_routine": False,
        "migration_type": "NONE",
        "package_family_code": package_family_code,
        "family_role_hub": "",
        "is_autobuy": False,
        "is_enterprise": False,
        "is_shareable": False,
        "is_migration": False,
        "lang": "id",
        "package_option_code": package_option_code,
        "is_upsell_pdp": False,
        "package_variant_code": package_variant_code
    }

    theme = get_theme()
    with live_loading("Mengambil detail paket...", theme):
        res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")

    if "data" not in res:
        print_panel("⚠️ Error", f"Gagal mengambil detail paket: {res.get('error', 'Unknown error')}")
        return None

    return res["data"]


def get_addons(api_key: str, tokens: dict, package_option_code: str) -> dict:
    path = "api/v8/xl-stores/options/addons-pinky-box"
    raw_payload = {
        "is_enterprise": False,
        "lang": "en",
        "package_option_code": package_option_code
    }

    theme = get_theme()
    with live_loading("Mengambil daftar addon paket...", theme):
        res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")

    if "data" not in res:
        print_panel("⚠️ Error", f"Gagal mengambil addon: {res.get('error', 'Unknown error')}")
        return None

    return res["data"]


def intercept_page(
    api_key: str,
    tokens: dict,
    option_code: str,
    is_enterprise: bool = False
):
    path = "misc/api/v8/utility/intercept-page"
    raw_payload = {
        "is_enterprise": is_enterprise,
        "lang": "en",
        "package_option_code": option_code
    }

    theme = get_theme()
    with live_loading("Memeriksa halaman intersepsi...", theme):
        res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")

    if "status" in res:
        print_panel("ℹ️ Status Intercept", res["status"])
    else:
        print_panel("⚠️ Error", "Gagal mengambil status intercept.")


def login_info(
    api_key: str,
    tokens: dict,
    is_enterprise: bool = False
):
    path = "api/v8/auth/login"
    raw_payload = {
        "access_token": tokens["access_token"],
        "is_enterprise": is_enterprise,
        "lang": "en"
    }

    theme = get_theme()
    with live_loading("Mengambil informasi login...", theme):
        res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")

    if "data" not in res:
        print_panel("⚠️ Error", res.get("error", "Gagal mengambil informasi login."))
        return None

    return res["data"]


def get_package_details(
    api_key: str,
    tokens: dict,
    family_code: str,
    variant_code: str,
    option_order: int,
    is_enterprise: bool | None = None,
    migration_type: str | None = None
) -> dict | None:
    theme = get_theme()
    with live_loading("Mengambil detail paket...", theme):
        family_data = get_family(api_key, tokens, family_code, is_enterprise, migration_type)

    if not family_data:
        print_panel("⚠️ Error", f"Gagal mengambil data family untuk {family_code}.")
        return None

    option_code = None
    for variant in family_data.get("package_variants", []):
        if variant.get("package_variant_code") == variant_code:
            for option in variant.get("package_options", []):
                if option.get("order") == option_order:
                    option_code = option.get("package_option_code")
                    break

    if option_code is None:
        print_panel("⚠️ Error", "Gagal menemukan opsi paket yang sesuai.")
        return None

    with live_loading("Mengambil detail opsi paket...", theme):
        package_details_data = get_package(api_key, tokens, option_code)

    if not package_details_data:
        print_panel("⚠️ Error", "Gagal mengambil detail paket.")
        return None

    return package_details_data


def get_quota(api_key: str, id_token: str) -> dict | None:
    path = "api/v8/packages/quota-summary"

    payload = {
        "is_enterprise": False,
        "lang": "en"
    }

    try:
        res = send_api_request(api_key, path, payload, id_token, "POST")
    except Exception:
        return None

    if isinstance(res, dict):
        quota = res.get("data", {}).get("quota", {}).get("data")
        if quota:
            return {
                "remaining": quota.get("remaining", 0),
                "total": quota.get("total", 0),
                "has_unlimited": quota.get("has_unlimited", False)
            }

    return None
