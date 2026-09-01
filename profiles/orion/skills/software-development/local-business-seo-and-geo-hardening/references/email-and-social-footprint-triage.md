# Email & Social Media Digital Footprint Triage Reference

## 1. Overview & Triage Workflow

When investigating email addresses or usernames associated with fraud, spam, or identity verification:
1. **Cryptographic Hash Derivation:** Derive MD5 hash of lowercase trimmed email (`hashlib.md5(email.strip().lower().encode()).hexdigest()`).
2. **Avatar & Gravatar/WordPress Profiling:** Query `https://en.gravatar.com/{md5_hash}.json` to extract registered display names, bio links, social accounts, and profile photos.
3. **Handle Extraction & Permutation Generation:**
   - Extract local-part handle (e.g. `husenishahab7` from `husenishahab7@gmail.com`).
   - Generate canonical variants: `handle`, `handle_clean` (strip trailing numbers), `first.last`, `first_last`, `lastfirst`.

---

## 2. Multi-Platform Direct Probing Vectors

| Platform | Endpoint / Probe Pattern | Detection Indicator |
| :--- | :--- | :--- |
| **Pinterest** | `https://www.pinterest.com/{username}/` | HTTP 200 + `<title>` contains Display Name and `(username) - Profile` |
| **Instagram** | `https://www.instagram.com/{username}/` | HTTP 200 (Registered in Meta ecosystem) vs HTTP 404 (Available) |
| **TikTok** | `https://www.tiktok.com/@{username}` | HTTP 200 (Account exists) vs HTTP 404 |
| **Twitter / X** | `https://twitter.com/{username}` | HTTP 200 vs HTTP 404 |
| **GitHub** | `https://api.github.com/users/{username}` | JSON payload (`name`, `bio`, `location`, `created_at`) vs HTTP 404 |
| **GitHub Commits** | `https://api.github.com/search/commits?q=author-email:{email}` | Uncovers public repository commits authored by target email |
| **Telegram** | `https://t.me/{username}` | HTTP 200 + presence of `tgme_page_title` and `tgme_page_extra` |
| **Steam** | `https://steamcommunity.com/id/{username}` | Absence of "The specified profile could not be found" |

---

## 3. Fraud Actor Persona Classification

1. **Low-Tech Scammer / Personal Identity Leak:**
   - Characteristic: Uses real personal email or recurring handle with lucky/birth digits (`johnsmith7@gmail.com`).
   - Indicators: Same handle found on non-anonymized visual platforms (Pinterest, TikTok, Instagram).
   - Investigative Pivot: Look for mutual followers, tagged photos, or family surname correlations (e.g. Arab/regional clan names).
2. **High-Tech / Burner Disposable Identity:**
   - Characteristic: Random character strings (`a9x8k21q@gmail.com`) or throwaway temp-mail.
   - Indicators: Zero footprint across social platforms; no Gravatar; no username reuse.
   - Investigative Pivot: Focus on payment rails, crypto address clustering, or IP logs rather than username OSINT.

---

## 4. E-Wallet & Bank Account Name Enumeration (KYC De-anonymization)

When social footprint leads to dead ends, pivot to financial transfer inquiry:
- **Indonesian Payment Rails (DANA, OVO, GoPay, ShopeePay, LinkAja, BCA VA, Bank Transfer):**
  - Initiate a simulated 1-Rupiah / 10.000-Rupiah transfer inquiry via banking app or payment gateway API.
  - The switch returns the authoritative bank account holder / KYC registered name (e.g. `M. HUSENI SHAHAB`).
  - Cross-reference the verified KYC name against previously identified social media handles.
