import os
import signal
import sys
import subprocess
import atexit

decrypted_files = []

def xor_encrypt_decrypt(input_file, output_file, key):
    with open(input_file, 'rb') as f:
        data = f.read()

    encrypted_data = bytearray(byte ^ key for byte in data)

    with open(output_file, 'wb') as f:
        f.write(encrypted_data)

def encrypt_file(file_path, key):
    try:
        xor_encrypt_decrypt(file_path, file_path, key)
    except Exception:
        pass

def decrypt_file(file_path, key):
    try:
        xor_encrypt_decrypt(file_path, file_path, key)
        decrypted_files.append(file_path)
    except Exception:
        pass

def decrypt_all_files_in_directory(directory, key, exceptions):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file != "secret.key" and file not in exceptions:
                decrypt_file(os.path.join(root, file), key)

def encrypt_decrypted_files(key):
    for file_path in decrypted_files:
        encrypt_file(file_path, key)

def signal_handler(sig, frame):
    encrypt_decrypted_files(key)
    sys.exit(0)

def main():
    global key, exceptions
    key = 101
    exceptions = ['main.py', 'setup.sh', 'update.sh', 'requirements.txt', '.env']

    decrypt_all_files_in_directory(os.getcwd(), key, exceptions)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    atexit.register(lambda: encrypt_decrypted_files(key))

    try:
        process = subprocess.Popen(["python", "update.py"])
        process.wait()
    except Exception:
        pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception:
        pass
