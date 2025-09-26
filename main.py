import os
import signal
import sys
import subprocess
from cryptography.fernet import Fernet

def load_key():
    try:
        return open("secret.key", "rb").read()
    except FileNotFoundError:
        sys.exit(1)
    except Exception:
        sys.exit(1)

def encrypt_file(file_path, cipher):
    try:
        with open(file_path, 'rb') as file:
            file_data = file.read()
        encrypted_data = cipher.encrypt(file_data)
        with open(file_path, 'wb') as file:
            file.write(encrypted_data)
    except Exception:
        pass

def decrypt_file(file_path, cipher):
    try:
        with open(file_path, 'rb') as file:
            encrypted_data = file.read()
        decrypted_data = cipher.decrypt(encrypted_data)
        with open(file_path, 'wb') as file:
            file.write(decrypted_data)
    except Exception:
        pass

def decrypt_all_files_in_directory(directory, cipher, exceptions):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file != "secret.key" and file not in exceptions:
                decrypt_file(os.path.join(root, file), cipher)

def encrypt_all_files_in_directory(directory, cipher, exceptions):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file != "secret.key" and file not in exceptions:
                encrypt_file(os.path.join(root, file), cipher)

def signal_handler(sig, frame):
    encrypt_all_files_in_directory(os.getcwd(), cipher, exceptions)
    sys.exit(0)

def main():
    global cipher, exceptions
    key = load_key()
    cipher = Fernet(key)

    exceptions = ['main.py', 'setup.sh', 'update.sh', 'requirements.txt', '.env']

    decrypt_all_files_in_directory(os.getcwd(), cipher, exceptions)

    signal.signal(signal.SIGINT, signal_handler)

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

