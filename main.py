import os

def detect_arch():
    try:
        with open("/proc/cpuinfo", "r") as f:
            cpuinfo = f.read().lower()

        if "aarch64" in cpuinfo or "armv8" in cpuinfo:
            return "armv8"
        elif "armv7" in cpuinfo or "armeabi" in cpuinfo:
            return "armv7"
        else:
            return "unknown"
    except Exception as e:
        print(f"[!] Error membaca cpuinfo: {e}")
        return "unknown"

def main():
    arch = detect_arch()
    print(f"[+] Arsitektur terdeteksi: {arch}")

    if arch == "armv7":
        os.system("python3 main7.py")
    elif arch == "armv8":
        os.system("python3 main8.py")
    else:
        print("[!] Arsitektur tidak dikenali. Tidak bisa melanjutkan.")

if __name__ == "__main__":
    main()
