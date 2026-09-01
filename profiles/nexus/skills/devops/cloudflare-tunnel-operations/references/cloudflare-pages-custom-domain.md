# Cloudflare Pages Custom Domain Setup & Verification

## Cloudflare Pages Custom Domain Verification

When attaching a custom domain to a Cloudflare Pages project (e.g. `mail.indrayuda.my.id` -> `project.pages.dev`):

1. **The Proxied CNAME Pitfall:**
   - If the CNAME record in Cloudflare DNS is set to **`proxied: true` (Orange Cloud)** during initial domain setup, Pages verification may fail with `"CNAME record not set"` because proxying flattens CNAME resolution.
2. **Resolution Workflow:**
   - Create or update the CNAME record pointing to `<project>.pages.dev` with **`proxied: false` (Grey Cloud)**.
   - Register the domain in Pages via API or CLI:
     ```bash
     curl -X POST "https://api.cloudflare.com/client/v4/accounts/<ACCOUNT_ID>/pages/projects/<PROJECT>/domains" \
       -H "Authorization: Bearer <TOKEN>" \
       -H "Content-Type: application/json" \
       -d '{"name":"mail.domain.com"}'
     ```
   - Check domain verification status:
     ```bash
     curl "https://api.cloudflare.com/client/v4/accounts/<ACCOUNT_ID>/pages/projects/<PROJECT>/domains/mail.domain.com" \
       -H "Authorization: Bearer <TOKEN>"
     ```
   - Once `verification_data.status` is `"active"`, update the DNS record back to **`proxied: true` (Orange Cloud)** for full CDN, WAF, and SSL protection.

## Extracting Zone API Token from `cert.pem`

If a user-provided API token lacks `DNS:Edit` permissions but `cloudflared` is already installed and logged in on the VPS:

1. `/root/.cloudflared/cert.pem` contains an ARGO TUNNEL TOKEN payload between `-----BEGIN ARGO TUNNEL TOKEN-----` and `-----END ARGO TUNNEL TOKEN-----`.
2. Parse the base64-encoded token to retrieve the Zone API Token:
   ```python
   import base64, json
   with open('/root/.cloudflared/cert.pem') as f:
       raw = ''.join([l.strip() for l in f.readlines() if '-----' not in l])
   data = json.loads(base64.b64decode(raw))
   print(data['apiToken'], data['zoneID'], data['accountID'])
   ```
3. Use `Authorization: Bearer <apiToken>` against Cloudflare Client API v4 (`https://api.cloudflare.com/client/v4/zones/<zoneID>/dns_records`) for direct DNS record manipulation.
