import json
from dotenv import load_dotenv
import os
from app.service.auth import AuthInstance
from app.client.engsel import get_family_v2

load_dotenv()  # Load environment variables from .env

def build_package_json(family_code, is_enterprise=False, migration_type=None):
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()

    if not tokens:
        print("❌ Tidak ditemukan token pengguna aktif.")
        return []

    data = get_family_v2(api_key, tokens, family_code, is_enterprise, migration_type)
    if not data:
        print(f"❌ Gagal memuat data untuk family code: {family_code}")
        return []

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

    return [{
        "name": f"{family_name} ({package_type})",
        "price": "Rp 0",
        "detail": f"Generated otomatis dari family code: {family_code}",
        "packages": packages
    }]

def batch_builder():
    print("🔧 Masukkan daftar family code. Ketik 'done' jika sudah selesai.\n")
    all_results = []

    while True:
        code = input("Masukkan family code: ").strip()
        if code.lower() == "done":
            break
        result = build_package_json(code)
        if result:
            all_results.extend(result)

    if all_results:
        with open("generated_packages.json", "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        print("✅ Semua paket berhasil disimpan ke generated_packages.json")
    else:
        print("⚠️ Tidak ada paket yang berhasil diambil.")

if __name__ == "__main__":
    batch_builder()
