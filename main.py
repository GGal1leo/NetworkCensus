import os
import socket
import subprocess
import re
import json
import requests
from concurrent.futures import ThreadPoolExecutor
#from datetime import datetime 
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Network Scanner")
    parser.add_argument("-t", "--workers", type=int, default=4, help="Number of threads to use for scanning")
    return parser.parse_args()

args = parse_args()

# Helper functions to convert IP to integer and vice versa
def ip_to_int(ip):
    octets = list(map(int, ip.split('.')))
    return (octets[0] << 24) | (octets[1] << 16) | (octets[2] << 8) | octets[3]

def int_to_ip(n):
    return '.'.join(map(str, [(n >> 24) & 0xFF, (n >> 16) & 0xFF, (n >> 8) & 0xFF, n & 0xFF]))

# get wlan0 ip 
def get_ip():
    try:
        ip = subprocess.check_output("ip addr show wlan0 | grep 'inet ' | awk '{print $2}' | cut -d'/' -f1", shell=True).decode().strip()
        return ip
    except subprocess.CalledProcessError:
        return None

# get wlan0 subnet (CIDR)
def get_subnet():
    try:
        subnet = subprocess.check_output("ip addr show wlan0 | grep 'inet ' | awk '{print $2}' | cut -d'/' -f2", shell=True).decode().strip()
        return int(subnet)
    except subprocess.CalledProcessError:
        return None

# get wlan0 gateway
def get_gateway():
    try:
        gateway = subprocess.check_output("ip route | grep default | awk '{print $3}'", shell=True).decode().strip()
        return gateway
    except subprocess.CalledProcessError:
        return None

def calculate_network(ip, cidr):
    ip_int = ip_to_int(ip)
    mask = (0xFFFFFFFF << (32 - cidr)) & 0xFFFFFFFF
    network_int = ip_int & mask
    broadcast_int = network_int | (0xFFFFFFFF >> cidr)
    return network_int, broadcast_int

def get_available_ips(network_int, broadcast_int):
    available_ips = []
    for ip_int in range(network_int + 1, broadcast_int):
        available_ips.append(int_to_ip(ip_int))
    return available_ips

def probe_ip(ip):
    """Thread worker function to check a single IP"""
    try:
        out = subprocess.check_output(f"sudo arping -c 1 {ip}", shell=True, stderr=subprocess.DEVNULL)
        if "Received 1 response" in out.decode():
            # Extract MAC address
            mac_line = out.decode().split("\n")[1]
            mac = mac_line.split()[4].split("[")[1].split("]")[0]
            
            # Get vendor
            mac_clean = mac.replace(":", "").upper()
            try:
                res = requests.get(f"https://api.macvendors.com/{mac_clean}", timeout=2)
                vendor = res.text if res.status_code == 200 else "Unknown"
            except:
                vendor = "Unknown"
            
            print(f"Active: {ip} | MAC: {mac} | Vendor: {vendor}")
    except subprocess.CalledProcessError:
        pass


# Main execution
ip = get_ip()
subnet = get_subnet()
gateway = get_gateway()

if ip and subnet is not None:
    print("IP: ", ip)
    print("Subnet (CIDR): /", subnet)
    network_int, broadcast_int = calculate_network(ip, subnet)
    network_ip = int_to_ip(network_int)
    broadcast_ip = int_to_ip(broadcast_int)
    print("Network IP: ", network_ip)
    print("Broadcast IP: ", broadcast_ip)
    available_ips = get_available_ips(network_int, broadcast_int)
    print("Available IPs count: ", len(available_ips))
    # Uncomment to print all IPs (could be lengthy)
    #print("Available IPs: ", available_ips)
    # Multithreaded arping with 4 workers
#    now = datetime.now()
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        executor.map(probe_ip, available_ips)
#    end = datetime.now()
#    print(f"Scan completed in {end - now}")
else:
    print("Could not retrieve IP or subnet information.")

if gateway:
    print("Gateway: ", gateway)
else:
    print("Gateway not found.")
