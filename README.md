# 🛠️ MYnyak Engsel

![banner](bnr.png)

**MYnyak Engsel** adalah aplikasi CLI untuk mengakses layanan internet seluler tertentu di Indonesia secara efisien dan fleksibel melalui Termux.

---

## 🔑 Cara Mendapatkan API Key

1. Buka Telegram dan cari bot [@fykxt_bot](https://t.me/fykxt_bot).
2. Kirim pesan `/viewkey`.
3. Salin API key yang diberikan oleh bot.

---

## 📦 Instalasi di Termux

Ikuti langkah-langkah berikut untuk menginstal dan menjalankan aplikasi:

## 1. Perbarui Termux
```bash
pkg update && pkg upgrade -y
```
## 2. Instal Git
```
pkg install git -y
```
## 3. Kloning repositori, Sesuaikan dengan arsitektur android kalian
cek arsitektur 
```
uname -m
```
Untuk android ARMv7 (32-bit)
```
git clone https://github.com/barbexid/xldor/tree/main/arm7/dor
```
Untuk android aarch64/ARMv8 (64-bit)
```
git clone https://github.com/barbexid/xldor/tree/main/arm8/dor
```

## 4. Masuk ke folder
```
cd dor
```
## 5. Jalankan setup
```
bash setup.sh
```
## 6. Konfigurasi Environment Variables
```
nano .env
```
## 7. Jalankan skrip
```
python main.py
```
# 💡 Masukkan API key saat diminta setelah menjalankan skrip.

---

## ℹ️ Catatan Teknis

> Untuk penyedia layanan internet seluler tertentu

---

## 📬 Kontak

Jika ada pertanyaan atau masukan, silakan hubungi:

**Email:** [contact@mashu.lol](mailto:contact@mashu.lol)

---
