# Multi-User Session Privacy & Database Sanitization

A protocol for handling multi-user Telegram gateway environments, session isolation, and requested chat history purging.

---

## 1. Multi-User Architecture on Telegram Gateways

When multiple users connect to a shared Hermes instance via Telegram:
1. **Chat Separation (In-Flight)**: Telegram DM sessions are segregated by `chat_id` and `user_id`. One user does not see incoming messages from another user in their active Telegram client.
2. **Persistence Layer (`state.db`)**: Every session and message is archived in SQLite databases across root and profile directories:
   - `/root/.hermes/state.db`
   - `/root/.hermes/profiles/<profile>/state.db`
3. **Pervasive Tool Access**: Tools like `session_search` query historical messages across stored sessions unless explicitly filtered or sanitized.

---

## 2. Definitive History & Account Purge Procedure

When a user requests to remove a contact, deleted account, or specific session from the server:

### Schema Overview:
- `sessions`: Stores session metadata (`id`, `user_id`, `chat_id`, `display_name`, `origin_json`, `started_at`).
- `messages`: Stores turns (`id`, `session_id`, `role`, `content`, `timestamp`).
- `messages_fts` / `messages_fts_trigram`: Full-text search index virtual tables (must be synced or cleaned alongside messages).

### Automated Purge Script (Python / SQLite3):
```python
import sqlite3, glob

dbs = ["/root/.hermes/state.db", "/root/.hermes/profiles/orion/state.db"] + glob.glob("/root/.hermes/profiles/*/state.db")
target_user_id = "TARGET_TELEGRAM_ID"  # or specific name/pattern

for db_path in set(dbs):
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # 1. Identify matching session IDs
        s_ids = [row[0] for row in c.execute(
            "SELECT id FROM sessions WHERE user_id=? OR chat_id=? OR display_name LIKE ?;",
            (target_user_id, target_user_id, f"%{target_user_id}%")
        ).fetchall()]
        
        if s_ids:
            for sid in s_ids:
                # 2. Delete messages & virtual FTS entries
                c.execute("DELETE FROM messages WHERE session_id=?;", (sid,))
                try:
                    c.execute("DELETE FROM messages_fts WHERE session_id=?;", (sid,))
                except Exception:
                    pass
                try:
                    c.execute("DELETE FROM messages_fts_trigram WHERE session_id=?;", (sid,))
                except Exception:
                    pass
                # 3. Delete session parent row
                c.execute("DELETE FROM sessions WHERE id=?;", (sid,))
            
            conn.commit()
            print(f"[{db_path}] Purged {len(s_ids)} sessions successfully.")
    except Exception as e:
        print(f"[{db_path}] Error:", e)
```

---

## 3. Best Practices & Safeguards

- **Never Leave Cached Media/Uploads**:
  When purging user history, also purge attached files in cache:
  ```bash
  rm -f /root/.hermes/profiles/*/cache/images/*
  rm -f /root/.hermes/profiles/*/cache/documents/*
  ```
- **Verify Active Whitelisting**:
  To completely block unauthorized external Telegram accounts from interacting with the bot, restrict allowed chat IDs in `config.yaml` (`telegram.allowed_users: ["YOUR_ID"]`).
