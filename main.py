import os
import platform
import subprocess

def detect_arch():
    try:
        plat_arch = platform.machine().lower()
        if "aarch64" in plat_arch or "arm64" in plat_arch:
            return "armv8"
        elif "armv7" in plat_arch or "armeabi" in plat_arch:
            return "armv7"

        with open("/proc/cpuinfo", "r") as f:
            cpuinfo = f.read().lower()

        armv8_keywords = [
            "aarch64", "armv8", "armv8-a", "armv8a",
            "cortex-a53", "cortex-a55", "cortex-a57", "cortex-a72", "cortex-a73", "cortex-a75", "cortex-a76", "cortex-a78", "cortex-x1"
        ]
        if any(k in cpuinfo for k in armv8_keywords):
            return "armv8"

        armv7_keywords = [
            "armv7", "armeabi", "armv7-a", "cortex-a7", "cortex-a8", "cortex-a9", "cortex-a15"
        ]
        if any(k in cpuinfo for k in armv7_keywords):
            return "armv7"

        uname_arch = subprocess.getoutput("uname -m").lower()
        if "aarch64" in uname_arch or "arm64" in uname_arch:
            return "armv8"
        elif "armv7" in uname_arch or "armeabi" in uname_arch:
            return "armv7"

        return "unknown"
    except Exception as e:
        print(f"[!] Error saat mendeteksi arsitektur: {e}")
        return "unknown"

def main():
    arch = detect_arch()
    print(f"[+] Arsitektur terdeteksi: {arch}")

    if arch == "armv7":
        print("[*] Menjalankan main7.py...")
        os.system("python3 main7.py")
    elif arch == "armv8":
        print("[*] Menjalankan main8.py...")
        os.system("python3 main8.py")
    else:
        print("[!] Arsitektur tidak dikenali. Harap cek manual atau tambahkan log debug.")

if __name__ == "__main__":
    main()
