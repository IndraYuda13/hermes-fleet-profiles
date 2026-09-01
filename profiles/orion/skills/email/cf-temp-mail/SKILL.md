---
name: cf-temp-mail
description: Create, read & send emails via temp-mail API (indrayuda).
---

# Cloudflare Temp Mail Skill (`mail.indrayuda.my.id`)

Use this skill when performing tasks requiring temporary email addresses, receiving OTP/verification codes, or sending emails via the self-hosted `cloudflare_temp_email` instance.

## Instance Config

- **API Base URL:** `https://api-tempmail.indrayuda.my.id`
- **Web UI:** `https://mail.indrayuda.my.id`
- **Domain:** `@indrayuda.my.id` (prefix default: `tmp`)

## 1. Create a New Mailbox Programmatically

To create a new email address without accessing the Web UI:

```bash
curl -s -X POST "https://api-tempmail.indrayuda.my.id/api/new_address" \
  -H "Content-Type: application/json" \
  -d '{"name": "mycustomname"}'
```

*Leave `name` empty (`""`) to generate a random address name.*

**Response Output:**
```json
{
  "jwt": "eyJhbG...",
  "address": "tmpmycustomname@indrayuda.my.id",
  "password": null,
  "address_id": 1
}
```
*Save the returned `jwt` for subsequent API calls.*

## 2. Check Inbox / Fetch Verification Emails

To list received emails (with parsed text, subject, HTML, and extracted codes):

```bash
curl -s "https://api-tempmail.indrayuda.my.id/api/parsed_mails?limit=10&offset=0" \
  -H "Authorization: Bearer <ADDRESS_JWT>"
```

To fetch a specific email by ID:

```bash
curl -s "https://api-tempmail.indrayuda.my.id/api/parsed_mail/<MAIL_ID>" \
  -H "Authorization: Bearer <ADDRESS_JWT>"
```

## 3. Polling for Verification Codes / OTP

When waiting for a verification email:
1. Poll `GET /api/parsed_mails?limit=5&offset=0` every 3 seconds.
2. Filter/match emails by `subject` or `source`.
3. Extract verification code or activation link from `text` or `html`.

## 4. Send Email

```bash
curl -s -X POST "https://api-tempmail.indrayuda.my.id/api/send_mail" \
  -H "Authorization: Bearer <ADDRESS_JWT>" \
  -H "Content-Type: application/json" \
  -d '{
    "from_name": "Hermes Agent",
    "to_mail": "recipient@example.com",
    "to_name": "Recipient Name",
    "subject": "Test Email",
    "content": "<p>Hello from Hermes!</p>",
    "is_html": true
  }'
```
