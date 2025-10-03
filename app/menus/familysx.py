import os
import json
from app.menus.package import get_packages_by_family
from app.menus.util import clear_screen, pause

FAMILY_FILE = os.path.abspath("family_codes.json")

def ensure_family_file():
    default_data = {"codes": []}
    if not os.path.exists(FAMILY_FILE):
        with open(FAMILY_FILE, "w") as f:
            json.dump(default_data, f, indent=2)
        return default_data

    try:
        with open(FAMILY_FILE, "r") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "codes" not in data or not isinstance(data["codes"], list):
            raise ValueError("Struktur tidak valid")
        return data
    except (json.JSONDecodeError, ValueError):
        with open(FAMILY_FILE, "w") as f:
            json.dump(default_data, f, indent=2)
        return default_data

def list_family_codes():
    return ensure_family_file()["codes"]

def add_family_code(code, name):
    if not code.strip() or not name.strip():
        return False
    data = ensure_family_file()
    if any(item["code"] == code for item in data["codes"]):
        return False
    data["codes"].append({"code": code.strip(), "name": name.strip()})
    with open(FAMILY_FILE, "w") as f:
        json.dump(data, f, indent=2)
    return True

def remove_family_code(index):
    data = ensure_family_file()
    if 0 <= index < len(data["codes"]):
        removed = data["codes"].pop(index)
        with open(FAMILY_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return removed["code"]
    return None

def edit_family_name(index, new_name):
    if not new_name.strip():
        return False
    data = ensure_family_file()
    if 0 <= index < len(data["codes"]):
        data["codes"][index]["name"] = new_name.strip()
        with open(FAMILY_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return True
    return False

def show_family_menu():
    while True:
        clear_screen()
        semua_kode = list_family_codes()

        print("-------------------------------------------------------")
        print("Kode Yang Terdaftar")
        print("-------------------------------------------------------")

        packages = []
        if semua_kode:
            for i, item in enumerate(semua_kode, start=1):
                print(f"{i}. {item['name']} - {item['code']}")
                packages.append({
                    "number": i,
                    "code": item["code"],
                    "name": item["name"]
                })
        else:
            print("Belum ada family code yang terdaftar.")

        print("-------------------------------------------------------")
        print("T: Tambah family code")
        print("E: Edit nama family code")
        print("H: Hapus family code")
        print("00: Kembali ke menu utama")
        print("Masukkan nomor untuk melihat paket")
        print("-------------------------------------------------------")

        aksi = input("Pilihan: ").strip().lower()

        if aksi == "t":
            code = input("Masukkan family code: ").strip()
            name = input("Masukkan nama family: ").strip()
            if add_family_code(code, name):
                print("Berhasil menambahkan family code.")
            else:
                print("Family code sudah ada atau input tidak valid.")
            pause()

        elif aksi == "h":
            if not semua_kode:
                print("Tidak ada kode untuk dihapus.")
                pause()
                continue
            idx = input("Masukkan nomor kode yang ingin dihapus: ").strip()
            if not idx.isdigit() or not (1 <= int(idx) <= len(semua_kode)):
                print("Nomor tidak ditemukan.")
            else:
                index = int(idx) - 1
                nama = semua_kode[index]["name"]
                kode = semua_kode[index]["code"]
                konfirmasi = input(f"Yakin ingin menghapus '{nama}' ({kode})? (y/n): ").strip().lower()
                if konfirmasi == "y":
                    removed = remove_family_code(index)
                    if removed:
                        print(f"Berhasil menghapus {removed}.")
                    else:
                        print("Gagal menghapus kode.")
                else:
                    print("Penghapusan dibatalkan.")
            pause()

        elif aksi == "e":
            if not semua_kode:
                print("Tidak ada kode untuk diedit.")
                pause()
                continue
            idx = input("Masukkan nomor kode yang ingin diubah namanya: ").strip()
            if not idx.isdigit() or not (1 <= int(idx) <= len(semua_kode)):
                print("Nomor tidak ditemukan.")
            else:
                new_name = input("Masukkan nama baru: ").strip()
                if edit_family_name(int(idx) - 1, new_name):
                    print("Nama berhasil diperbarui.")
                else:
                    print("Gagal memperbarui nama.")
            pause()

        elif aksi == "00":
            return

        elif aksi.isdigit():
            nomor = int(aksi)
            selected = next((p for p in packages if p["number"] == nomor), None)
            if selected:
                try:
                    result = get_packages_by_family(selected["code"])
                    if result == "MAIN":
                        return
                    elif result == "BACK":
                        #continue
                except Exception as e:
                    print(f"Gagal menampilkan paket: {e}")
            else:
                print("Nomor tidak valid.")
            pause()

        else:
            print("Pilihan tidak valid.")
            pause()
