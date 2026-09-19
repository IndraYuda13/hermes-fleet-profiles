# Business Email Outbound Suspension & hPanel Troubleshooting (Hostinger / cPanel)

Operational reference for diagnosing and resolving outgoing email blockages (`554 5.7.1 Outbound sending is disabled for this account`) across hosted domains (e.g. `bg-maritim.com`).

---

## 1. Diagnostics & Signal Matching
- **Client Error:** Outlook / Thunderbird / Apple Mail bounces with:
  `554 5.7.1 Outbound sending is disabled for this account`
- **Root Cause Indicators:**
  - Security notification from host (e.g. `team@info.hostinger.com` stating *"Pengiriman email ditangguhkan sementara"* / *"Email sending temporarily suspended"*).
  - Automated spam/malware detection triggered by high outbound velocity, suspicious links, or subtle unauthorized email signature modifications.
  - hPanel mailbox status shows red badge: `Ditangguhkan` / `Suspended`.

## 2. Recovery Workflow
1. **Mandatory Credential Reset (First Action):**
   - In hPanel (`hpanel.hostinger.com` -> Emails -> Manage Mailbox), click `⋮` next to the suspended account -> `Ubah Password` / `Change Password`.
   - Set a strong password immediately to sever any active hijacked SMTP sessions or infostealer bot connections. Hostinger security policies require password changes prior to unsuspending mailboxes.
2. **Unsuspend / Outbound Enablement:**
   - Check if clicking the red `Ditangguhkan` badge reveals a review/re-enable button.
   - If the `⋮` context menu only shows `Ubah Password`, `Buat Forwarder`, `Buat Auto Reply`, `Hapus` (no direct Unsuspend option), Hostinger has locked the mailbox at the backend security tier.
   - **Action:** Open Hostinger Live Chat (`?` icon -> Email -> Live Agent) and submit:
     > *"Halo tim Hostinger, akun email [address] ditangguhkan karena isu outbound security/spam. Kami sudah mengganti password baru dan membersihkan perangkat lokal pengguna. Mohon bantuannya untuk mengaktifkan kembali (unsuspend) pengiriman email akun ini. Terima kasih."*
   - Backend agents typically verify the password reset and unblock the SMTP queue within 2–5 minutes.
3. **Local Client Sanitization:**
   - In Outlook: File -> Options -> Mail -> Signatures. Purge any rogue URLs or unauthorized text.
   - Update Outlook credential manager with the new password.
   - Toggle off "Work Offline" in Outlook top bar to restore live server sync.
