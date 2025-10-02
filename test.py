import json
from dotenv import load_dotenv
import os

load_dotenv()  # Ini akan membaca file .env secara otomatis
from app.menus.package2 import get_family_v2
from app.config.auth_config import AuthInstance

def build_package_json(family_code, is_enterprise=False, migration_type=None, output_file="generated_package.json"):
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()

    if not tokens:
        print("❌ Tidak ditemukan token pengguna aktif.")
        return

    data = get_family_v2(api_key, tokens, family_code, is_enterprise, migration_type)
    if not data:
        print("❌ Gagal memuat data dari server.")
        return

    family_name = data["package_family"]["name"]
    package_type = data["package_family"]["package_family_type"]

    packages = []
    for variant in data["package_variants"]:
        variant_name = variant["name"]
        variant_code = variant.get("variant_code", variant_name.lower().replace(" ", "_"))

        for option in variant["package_options"]:
            packages.append({
                "family_name": family_name,
                "family_code": family_code,
                "variant_name": variant_name,
                "variant_code": variant_code,
                "option_name": option["name"],
                "order": option["order"],
                "is_enterprise": is_enterprise
            })

    result = [{
        "name": f"{family_name} ({package_type})",
        "price": "Rp 0",
        "detail": f"Generated otomatis dari family code: {family_code}",
        "packages": packages
    }]

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"✅ Paket berhasil dibuat dan disimpan di: {output_file}")

# Contoh penggunaan
if __name__ == "__main__":
    code = input("Masukkan family code: ").strip()
    build_package_json(code)
