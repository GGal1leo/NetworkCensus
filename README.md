# NetworkCensus 📡

A Python-based network device discovery tool that uses ARP probing to identify active devices, even when ICMP (ping) is blocked. Retrieves MAC addresses, hardware vendors, and supports configurable multithreaded scanning.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-GPL%20v3.0-red)

## Features✨
- **Configurable threading** - Adjust worker count with `-t`/`--workers`
- **ARP-based scanning** - Bypasses ICMP restrictions
- **Multithreaded probing** - 4x faster than sequential scanning
- **MAC address extraction** - With vendor identification
- **Subnet analysis** - Automatic network range calculation
- **Reverse scanning** - Checks IPs from high to low
- **Vendor API lookup** - Uses macvendors.com API

## Installation 🔧
### Requirements
- Python 3.8+
- Linux system (Tested on Ubuntu/Debian)

```bash
# Install dependencies
sudo apt install arping iproute2

# Python packages
pip install requests
```

## Usage 🚀
```bash
# Run with sudo (arping requires root privileges)
sudo python3 arpscout.py

Sample Output:
IP: 192.168.1.23 | MAC: dc:a6:32:01:02:03 | Vendor: Raspberry Pi Trading Ltd.
IP: 192.168.1.42 | MAC: 00:11:22:33:44:55 | Vendor: ASUStek Computer Inc.
IP: 192.168.1.100 | MAC: aa:bb:cc:dd:ee:ff | Vendor: Unknown

# Aggressive scan with 60 workers
sudo python3 arpscout.py -t 60

# Custom worker count (15 threads)
sudo python3 arpscout.py --workers 15

Options:
  -t, --workers  Number of concurrent scanning threads [default: 4]

```

## Technical Details 🔬
### Scanning Proces
1. Network Analysis - Calculates subnet range from host IP
2. Reverse IP Generation - Checks high-numbered IPs first
3. Multithreaded ARP Probes - 4 concurrent threads
4. MAC Extraction - Parses arping responses
5. Vendor Lookup - API call to macvendors.com

### Considerations ⚠️
| Workers   | Speed (/24) | Risk Level | Use Case               |
|-----------|-------------|------------|------------------------|
| 4-20      | 30-10 sec   | Low        | Default networks       |
| 20-50     | 10-5 sec    | Medium     | Controlled environments|
| 50-100    | <5 sec      | High       | Lab testing only       |
> Table: Recommended worker thread configurations and their performance characteristics


### Performance 🏎️
- Scans /24 subnet (~250 IPs) in ~30 seconds (8-15 sec if you increase the worker number to 60)
- Thread-safe design prevents network flooding

## Contributing 🤝
Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create your feature branch (git checkout -b feature/poop)
3. Commit your changes (git commit -am 'Add some poop')
4. Push to the branch (git push origin feature/poop)
5. Open a Pull Request

## License 📜
Distributed under the GNU General Public License v3.0. See `LICENSE` for more information.

