import socket
import os
import hashlib
import zipfile
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

key = b'Sixteen byte key'  # 16 bytes AES key
iv = b'16 bytes iv45678'  # 16 bytes AES IV

def calculate_checksum(file_path, algorithm='sha256'):
    hash_algo = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hash_algo.update(chunk)
    return hash_algo.hexdigest()

def extract_zip(zip_path, extract_to_folder):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to_folder)
    print(f"Files extracted to {extract_to_folder}")

def decrypt_data(encrypted_data):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()
    return data

def receive_file_rudp(port, save_path):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(('0.0.0.0', port))
        print(f"Listening on port {port}")
        
        expected_seq_num = 0
        checksum = None
        
        with open(save_path, 'wb') as f:
            while True:
                packet, addr = s.recvfrom(1028)
                if packet.startswith(b'CHECKSUM'):
                    checksum = packet.decode()[8:]
                    break
                else:
                    seq_num = int(packet[:4].decode())
                    encrypted_data = packet[4:]
                    if seq_num == expected_seq_num:
                        data = decrypt_data(encrypted_data)
                        f.write(data)
                        s.sendto(f"ACK{seq_num:04d}".encode(), addr)
                        expected_seq_num += 1
                    else:
                        s.sendto(f"ACK{expected_seq_num-1:04d}".encode(), addr)
        
        received_checksum = calculate_checksum(save_path)
        if received_checksum == checksum:
            print(f"File received and saved to {save_path}. Checksum verified.")
            extract_zip(save_path, os.path.splitext(save_path)[0])
        else:
            print(f"File received, but checksum does not match. Checksum: {checksum}, Received: {received_checksum}")

if __name__ == "__main__":
    port = 9000  # The port where the client listens
    save_path = 'received_archive.zip'  # The path where the received file will be saved

    receive_file_rudp(port, save_path)
