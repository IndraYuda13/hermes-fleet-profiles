#!/usr/bin/env python3
"""
Audit all ingress hostnames in a Cloudflare Tunnel configuration.
Checks local TCP listening status and public HTTPS status for each hostname.
"""

import sys, os, yaml, socket, subprocess, json, argparse

def audit_tunnel(config_path=None):
    if not config_path:
        # Default config lookup
        candidates = [
            "/etc/cloudflared/config-vps-baru.yml",
            "/etc/cloudflared/config.yml",
            "/etc/cloudflared/config.yaml"
        ]
        for c in candidates:
            if os.path.exists(c):
                config_path = c
                break
                
    if not config_path or not os.path.exists(config_path):
        print(f"Error: Config file not found ({config_path})", file=sys.stderr)
        sys.exit(1)
        
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
        
    ingress = [r for r in cfg.get("ingress", []) if "hostname" in r]
    print(f"=== Auditing {len(ingress)} Hostnames from {config_path} ===\n")
    
    active_list = []
    inactive_list = []
    
    for r in ingress:
        host = r["hostname"]
        svc = r.get("service", "")
        
        target_host = "127.0.0.1"
        target_port = 80
        if "://" in svc:
            part = svc.split("://")[1]
            if ":" in part:
                h, p = part.split(":")
                target_host = "127.0.0.1" if h in ["localhost", "127.0.0.1"] else h
                try:
                    target_port = int(p.split("/")[0])
                except ValueError:
                    target_port = 80
            else:
                target_port = 80
                
        # Check local TCP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.3)
        local_alive = False
        try:
            s.connect((target_host, target_port))
            local_alive = True
            s.close()
        except Exception:
            local_alive = False
            
        # Check public HTTP status code via curl
        pub_code = "ERR"
        try:
            res = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--connect-timeout", "4", "--max-time", "6", f"https://{host}"],
                capture_output=True, text=True
            )
            pub_code = res.stdout.strip()
        except Exception:
            pub_code = "ERR"
            
        entry = {
            "hostname": host,
            "service": svc,
            "port": target_port,
            "local_alive": local_alive,
            "public_code": pub_code
        }
        
        # Categorize
        if pub_code in ["200", "201", "204", "301", "302", "303", "307", "308", "401", "403", "404", "407"] and local_alive:
            if pub_code == "407":
                note = "HTTP 407 (Proxy Auth Required)"
            elif pub_code == "404":
                note = "HTTP 404 (App running, root route 404)"
            elif pub_code.startswith("3"):
                note = f"HTTP {pub_code} (Redirect)"
            else:
                note = f"HTTP {pub_code} (OK)"
            active_list.append((entry, note))
        else:
            if not local_alive:
                note = f"HTTP {pub_code} (Port {target_port} not listening)"
            else:
                note = f"HTTP {pub_code} (Local port up, app error/crash)"
            inactive_list.append((entry, note))
            
    print(f"Total Configured: {len(ingress)}")
    print(f"Active (Online): {len(active_list)}")
    print(f"Inactive (Down / Error): {len(inactive_list)}\n")
    
    print("=== ACTIVE HOSTNAMES ===")
    for e, note in active_list:
        print(f"✓ {e['hostname']:<38} | {e['service']:<25} | {note}")
        
    print("\n=== INACTIVE HOSTNAMES ===")
    for e, note in inactive_list:
        print(f"✗ {e['hostname']:<38} | {e['service']:<25} | {note}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit Cloudflare Tunnel ingress hostnames")
    parser.add_argument("--config", "-c", help="Path to cloudflared config YAML", default=None)
    args = parser.parse_args()
    audit_tunnel(args.config)
