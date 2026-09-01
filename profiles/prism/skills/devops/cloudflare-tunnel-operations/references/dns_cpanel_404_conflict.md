# Cloudflare Tunnel vs cPanel 404 Conflict

## Symptom
After successfully routing a subdomain to a tunnel (`cloudflared tunnel route dns <id> <subdomain>`) and restarting the daemon, visiting the URL returns a **cPanel 404 Not Found** page (or hits the origin Apache/Nginx server) instead of the tunneled service.

## Root Cause
A conflicting A or CNAME record for the exact same subdomain still exists in the Cloudflare Dashboard's DNS settings, pointing directly to the web hosting IP. Cloudflare prioritizes this direct A/CNAME record over the Argon/Cloudflared Tunnel routing.

## Fix
1. Log into the Cloudflare Dashboard.
2. Navigate to **DNS > Records**.
3. Locate the manual A or CNAME record for the subdomain pointing to the host IP.
4. **Delete** it.
5. Ensure the auto-generated CNAME record pointing to `<TUNNEL_UUID>.cfargotunnel.com` is the only one remaining. Traffic will immediately begin flowing through the tunnel.