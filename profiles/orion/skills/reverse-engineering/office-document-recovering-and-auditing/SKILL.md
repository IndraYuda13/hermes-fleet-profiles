---
name: office-document-recovering-and-auditing
description: Use when recovering or auditing locked Office files.
---

# Office Document Recovery, Decryption & Security Auditing

A class-level guide for analyzing document security structures, stripping sheet/workbook locks, extracting hash signatures, and executing targeted recovery on Microsoft Office formats (.xls, .xlsx, .doc, .docx, .ppt, .pptx).

---

## 1. Classification of Office Document Protection

Office documents utilize two fundamentally different protection architectures:

| Protection Tier | Scope | File Formats | Recovery Mechanism |
| :--- | :--- | :--- | :--- |
| **Tier A: Structure & Sheet Protection** | Read-only cells, hidden formulas, locked workbook structure. | `.xls`, `.xlsx` | **Instant Bypass (100% Deterministic)**: Edit XML tags or patch XOR/BIFF8 hash bytes. No cracking needed. |
| **Tier B: File Open / Document Encryption** | Entire file stream is encrypted. Document cannot be parsed without key. | `.xls` (BIFF8/CryptoAPI), `.xlsx` (Agile/Standard) | **Cryptographic Recovery**: Extract verifier hash via `office2john.py`, then run targeted mask/dictionary attack via Hashcat. |

---

## 2. Tier A: Instant Sheet & Workbook Unprotect

### Modern `.xlsx` Formats (OpenXML / ZIP)
1. Rename `.xlsx` to `.zip` and extract.
2. For Sheet Protection: Open `xl/worksheets/sheet1.xml` (or respective sheet).
   - Find and delete `<sheetProtection ... />` tag.
3. For Workbook Structure: Open `xl/workbook.xml`.
   - Find and delete `<workbookProtection ... />` tag.
4. Re-zip contents and rename back to `.xlsx`.

### Legacy `.xls` Formats (BIFF8 OLE2)
For legacy `.xls` with protected sheets, modify the `PROTECT` record (`0x0012`) and `PASSWORD` record (`0x0013`) in the binary workbook stream using hex replacement or Python (`olefile`/`xlrd`).

---

## 3. Tier B: Full Document Encryption Cracking (.xls / .xlsx)

### Step 1: Hash Extraction
Extract the verifier hash using `office2john.py`:
```bash
python3 office2john.py "target_document.xls" > hash.txt
# Trim filename prefix for Hashcat:
cut -d: -f2- hash.txt > hashcat_target.txt
```

### Step 2: Hashcat Mode Selection
| Hash Signature | Office Version | Hashcat Mode (`-m`) |
| :--- | :--- | :--- |
| `$oldoffice$0` / `$oldoffice$1` | Office 97-2000 (MD5 + RC4 40-bit) | `9700` |
| `$oldoffice$3` / `$oldoffice$4` | Office 2002/2003 (SHA-1 + RC4) | `9800` |
| `$office$*2007*` | Office 2007 (AES-128 + SHA-1) | `9400` |
| `$office$*2010*` | Office 2010 (AES-128 + SHA-1 100k iter) | `9500` |
| `$office$*2013*` | Office 2013+ (AES-256 + SHA-512 100k iter) | `9600` |

### Step 3: Targeted Search Hierarchy (Enterprise / Indonesian Context)
1. **Targeted Corporate Wordlist + Rules**:
   - Company name, keywords (e.g. `payroll`, `gaji`, `finance`, `admin`, month, year).
   - Apply rule mutations (`-r rules/best64.rule`).
2. **Numeric PIN & Date Sequences**:
   - Dates: `DDMMYYYY`, `YYYYMMDD`, `DDMMYY` (1970–2026).
   - Pure digits 4–8 chars: `?d?d?d?d?d?d`.
3. **Alphanumeric Mask Patterns (7–8 chars)**:
   - `?u?l?l?l?d?d` (e.g. `Gaji26`, `Juni26`)
   - `?u?l?l?l?d?d?d?d` (e.g. `Juni2026`)
   - `?u?l?l?l?l?d?d` (e.g. `Admin26`)

```bash
hashcat -m 9800 -a 0 hashcat_target.txt custom_wordlist.txt -r /usr/share/hashcat/rules/best64.rule --force
```

---

## 4. Privacy & Data Handling Discipline

- **Temporary Dump Purging:** Always immediately delete temporary hashes, dumped spreadsheets, and custom wordlists upon task completion or user request (`rm -f /tmp/hash* /tmp/*wordlist*`).
- **Clear Status Reporting:** Distinguish between *password found*, *keyspace exhausted*, and *process stopped*.
