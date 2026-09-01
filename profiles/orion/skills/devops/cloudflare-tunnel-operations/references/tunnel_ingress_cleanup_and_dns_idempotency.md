# Cloudflare Tunnel Ingress & DNS Audit / Cleanup

## 1. Idempotent DNS Routing
- `cloudflared tunnel route dns <tunnel-uuid> <hostname>` is completely idempotent when executed against the same tunnel UUID.
- Re-running it will simply log that the hostname is already configured.
- Flag `--overwrite-dns` is required if overwriting an existing DNS record previously pointed to a different tunnel or A record.

## 2. Ingress Cleanup Pattern (502 vs 404)
- Leaving dead/offline local services in `ingress:` causes Cloudflare edge to attempt origin connections and return **HTTP 502 Bad Gateway**.
- Removing dead entries from `config*.yml` lets requests fall through to the terminal `- service: http_status:404` rule.
- Cloudflare edge immediately returns **HTTP 404 Not Found** without waiting for connection timeouts or wasting server resources.

## 3. CNAME Retention vs Deletion
- **Keep CNAME:** If the service is temporarily dormant or internal and may be re-enabled later. Simply add the ingress rule back to `config*.yml` and restart `cloudflared` without re-creating DNS.
- **Delete CNAME:** Only when permanently retiring the subdomain or pointing it to another server / external A record / Cloudflare Pages.
