import socket
import threading
import zipfile
import os
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

# Define groups with clients (IP and port pairs)
groups = {
    'group1': [('127.0.0.1', 9000), ('127.0.0.1', 9001)],
    'group2': [('127.0.0.1', 9002)],
    # Add more groups and clients as needed
}

client_ip = '127.0.0.1'

key = b'Sixteen byte key'  # 16 bytes AES key
iv = b'16 bytes iv45678'  # 16 bytes AES IV
ACK_TIMEOUT = 2  # Seconds to wait for an acknowledgment
MAX_RETRIES = 5  # Maximum number of retries for each packet
admin_token = "12345"

def calculate_checksum(file_path, algorithm='sha256'):
    hash_algo = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hash_algo.update(chunk)
    return hash_algo.hexdigest()

def zip_text_files(file_paths, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in file_paths:
            zipf.write(file_path, arcname=os.path.basename(file_path))
    print(f"Files have been compressed into {zip_path}")

def encrypt_data(data):
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return encrypted_data

def send_file_to_client_rudp(client_ip, client_port, file_path):
    try:
        checksum = calculate_checksum(file_path)
        
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(ACK_TIMEOUT)
            with open(file_path, 'rb') as f:
                seq_num = 0
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    
                    encrypted_data = encrypt_data(data)
                    packet = f"{seq_num:04d}".encode() + encrypted_data
                    
                    for _ in range(MAX_RETRIES):
                        s.sendto(packet, (client_ip, client_port))
                        try:
                            ack, _ = s.recvfrom(1024)
                            if ack.decode() == f"ACK{seq_num:04d}":
                                seq_num += 1
                                break
                        except socket.timeout:
                            print(f"Timeout, resending packet {seq_num} to {client_ip}:{client_port}")
                    else:
                        print(f"Failed to send packet {seq_num} after {MAX_RETRIES} retries")
                        return

            s.sendto(f"CHECKSUM{checksum}".encode(), (client_ip, client_port))
        print(f"File {file_path} sent to {client_ip}:{client_port}")
    except Exception as e:
        print(f"Failed to send file {file_path} to {client_ip}:{client_port} - {e}")

def authenticate__admin(password):
    
    if password == admin_token :
        choice = input("do you want to add client or group y/n")
        while choice== 'y':
            group_n = input("enter group name: ")
            client_p = input("enter port: ")
            add_client_to_group(group_n, client_ip, client_p)
            choice = input("do you want to add client or group y/n")

        send_files_to_group_rudp(group_name, [zip_path])
    else:
        print("Authentication failed")



def add_client_to_group(group_name, client_ip, client_port):
    if group_name in groups:
        # Check if the client (IP, port) is already in the group
        if (client_ip, client_port) in groups[group_name]:
            print(f"Client {client_ip}:{client_port} is already in group {group_name}")
        else:
            groups[group_name].append((client_ip, client_port))
            print(f"Added client {client_ip}:{client_port} to group {group_name}")
    else:
        print(f"Group {group_name} does not exist. Creating new group.")
        groups[group_name] = [(client_ip, client_port)]
        print(f"Group {group_name} created with client {client_ip}:{client_port}")





def send_files_to_group_rudp(group_name, file_paths):
    if group_name in groups:
        clients = groups[group_name]
        for file_path in file_paths:
            print(f"Sending file {file_path} to group {group_name}")
            threads = []
            for client_ip, client_port in clients:
                thread = threading.Thread(target=send_file_to_client_rudp, args=(client_ip, client_port, file_path))
                thread.start()
                threads.append(thread)
            
            for thread in threads:
                thread.join()
            print(f"File {file_path} sent to group {group_name}")
    else:
        print(f"Group {group_name} does not exist")


if __name__ == "__main__":
    file_paths = ['example1.txt', 'example2.txt']
    zip_path = 'archive.zip'
    zip_text_files(file_paths, zip_path)

    group_name = input("Enter group name: ")
    password = input("Enter admin password: ")
    
    authenticate__admin(password)
    
