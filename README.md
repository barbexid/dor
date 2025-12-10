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
git clone https://github.com/barbexid/dor7
```
Untuk android aarch64/ARMv8 (64-bit)
```
git clone https://github.com/barbexid/dor8
```

## 4. Masuk ke folder
ARMv7 (32-bit)
```
cd dor7
```
ARMv8 (64-bit)
```
cd dor8
```
## 5. Jalankan setup
```
bash setup.sh
```
## 6. Konfigurasi Environment Variables
Hubungi saya di  [TELEGRAM](https://t.me/barbex_id)
 untuk mendapatkan environment variables
```
nano .env
```
Lalu isi dan simpan
## 7. Jalankan skrip
```
python main.py
```

##  Shortcut (jalan pintas)
```
chmod +x dor.sh
```
ARMv7 (32-bit)
```
mv ~/dor7/dor.sh $PREFIX/bin/dor
```
ARMv8 (64-bit)
```
mv ~/dor8/dor.sh $PREFIX/bin/dor
```
Untuk menjalankan cukup panggil dor dimana  saja
```
dor
```
---
# 💡 Pastikan semua perintah di atas dijalankan dengan benar.

## ℹ️ Catatan Teknis

> Untuk penyedia layanan internet seluler tertentu

---
