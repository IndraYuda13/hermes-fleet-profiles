import sys

def generate_proxies():
    proxies = []
    for i in range(1, 18):
        node_id = f"{i:02d}"
        port = f"320{node_id}"
        proxies.append(f"socks5://127.0.0.1:{port}")
    
    with open('/mnt/grass_511_bot/data/proxies.txt', 'w') as f:
        f.write('\n'.join(proxies) + '\n')
    print(f"Generated {len(proxies)} local Surfshark SOCKS5 proxies to data/proxies.txt!")

if __name__ == '__main__':
    generate_proxies()
