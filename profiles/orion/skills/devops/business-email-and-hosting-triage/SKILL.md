---
name: business-email-and-hosting-triage
description: Use when business email or hosting gets suspended or locked.
---

# Business Email & Hosting Operations Playbook

Use this skill when diagnosing, mitigating, or resolving domain email outages, provider-level outbound delivery suspensions (e.g. Hostinger, cPanel/WHM, Google Workspace, Microsoft 365), high-bounce rate lockouts, and legacy IT account ownership transfers.

## 1. Outbound Suspension Triage (Error 554 5.7.1)

### Root Cause Identification
- **Error Code:** `554 5.7.1 Outbound sending is disabled for this account`
- **Common Trigger:** Mass sending (e.g. logistics line-ups, marketing blasts, transactional statements) containing obsolete, typoed, or non-existent recipient addresses causing a spike in hard bounces (>5-10%).
- **Security Action by Host:** The mail server automatically suspends outgoing SMTP traffic to protect domain reputation and prevent IP blacklisting on Spamhaus/Barracuda. Incoming mail (IMAP/POP3) typically remains unaffected.

### Critical Immediate Pitfall: The Outbox Re-Trigger Trap
Before requesting an unsuspend or waiting for automatic cooldown:
1. **Purge the Client Outbox First:** User MUST inspect the local email client (Outlook, Thunderbird, Apple Mail) and immediately delete or move to Drafts the queued/unsent email blast that failed in the `Outbox` folder.
2. **Consequence of Neglect:** If the provider unsuspends the account while the corrupted queue remains in the local Outbox, the client will immediately attempt redelivery, re-triggering the bounce threshold and causing an instant re-suspension.

## 2. Hostinger-Specific Account Delegation & Support Rules

- **Account Sharing Limitation:** Hostinger allows delegating "Admin Access" to third parties. However, support policies strictly forbid security-level actions (unsuspending accounts, resetting abuse locks, domain transfers) requested by delegated accounts.
- **Master Owner Requirement:** Such actions require communication from the primary registrant/purchaser email (Master Account).
- **Automated Cooldown:** If the Master Account is unreachable, Hostinger's automated reputation filter typically releases outbound blocks within 6 to 24 hours, provided no further bounced traffic is generated.

## 3. Zero-Downtime Emergency Mitigation Workarounds

When the primary mailbox is suspended and the business cannot wait:

### Strategy A: Temporary Mailbox + Dual Account View (Fastest, 3 Minutes)
1. Do **NOT** delete the suspended mailbox. Deleting a mailbox deletes all server-side historical mail, sent items, and folders permanently.
2. Create a fresh temporary mailbox in the hosting panel (e.g. `commercial@domain.com` or `ops@domain.com`).
3. Set an automatic forwarder from `suspended@domain.com` -> `temporary@domain.com`.
4. Add the temporary account into the user's desktop client (Outlook) alongside the existing account:
   - Historical emails, attachments, and records remain accessible and searchable in the original profile.
   - Immediate outgoing communication resumes seamlessly through the new profile.

### Hostinger Live Chat Bypass (Bypassing AI Bot "Kodee")
When contacting Hostinger support through the web chat widget, the AI bot ("Kodee") will aggressively intercept and attempt to deflect tickets with generic articles:
1. Immediately type keyword triggers: `Bicara dengan agen manusia` or `Live agent please, transfer to human`.
2. If offered articles or suggested FAQs, explicitly reject them by selecting: `Bukan, saya masih butuh bantuan` or `Tidak membantu`.
3. Re-type: `Saya butuh agen manusia sekarang untuk unsuspend email server`.
4. After 2 rejections, the automated queue transfers to a human technical support agent.
5. In the opening message to the human agent, immediately state that the mailbox password has already been changed and client devices verified clean—this bypasses repetitive first-tier troubleshooting scripts.

### Strategy B: Full Archive Mirroring (Import Email)
1. Use the hosting provider's "Import Email" / IMAP sync utility in the control panel.
2. Source: `suspended@domain.com` (with freshly updated password).
3. Target: `temporary@domain.com`.
4. Complete historical mailboxes copy over in the background without affecting production integrity.

### Strategy C: Client-Side Offline Archival (.PST Export in Outlook)
Before any major mailbox migration or server-side intervention, create a durable local backup:
1. In Outlook: `File` -> `Open & Export` -> `Import/Export` -> `Export to a file` -> `Outlook Data File (.pst)`.
2. Select the top-level mailbox root (`account@domain.com`) and ensure **"Include subfolders" is checked**.
3. Save to local disk or external storage (e.g. `Backup_Email_Date.pst`).
4. Skip the password prompt (leave empty) for seamless offline restoration or cross-machine transfer.

### Strategy D: Unresponsive IT Legacy Account Escalation Protocol
When a former IT administrator holding the hosting master account (`Master Owner`) is unresponsive or refuses to cooperate:
1. **Never Cite Security Incidents in Chats:** When drafting WhatsApp requests for the user to send into corporate groups or directly to previous IT, frame the transfer strictly around standard ongoing maintenance, DNS configuration, and operational full-access requirements. Citing suspensions or security breaches creates unnecessary panic and defensive stonewalling.
2. **Operational Continuity First:** Immediately deploy Strategy A (fresh temporary mailbox + server-side forwarder + dual client configuration) so day-to-day business operations are zero-downtime while administrative negotiations occur.
3. **Legal Account Recovery Escalation:** If former IT remains permanently uncontactable, advise the business owners to initiate the provider's official account ownership claim (e.g. Hostinger Account Recovery) using corporate proof of payment (billing bank statements), business registration documents, and director identification. Providers have dedicated legal/abuse teams to re-assign master ownership away from personal accounts.

## 4. Communication Etiquette for WhatsApp Support
When drafting messages for users to communicate with company owners or legacy IT:
- Avoid overly bureaucratic or rigid language ("Dengan hormat", long administrative preambles).
- Use natural, respectful, and clear messaging suitable for WhatsApp.
- Check and adapt honorifics to match the owner/stakeholder relationship (e.g. use 'Kak <Name>' instead of 'Pak' when requested).
- Frame credential/account transfers around technical necessity and operational efficiency, never assigning blame for existing incidents.
- When drafting internal requests to take over master accounts from former IT personnel, focus purely on maintenance/full-access requirements without citing active incidents or security panics.

## 5. Web Assets & Embedded Media Operations
See `references/youtube-embed-and-hero-carousel-invariants.md` for technical invariants on resolving YouTube embed Error 153 via Smart Facade Players, handling user-mandated inline autoplay/loop iframe syntax, and preventing initial black-screen hero background bugs on client landing pages.


