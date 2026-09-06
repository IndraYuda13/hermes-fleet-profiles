# Defensive JSON Parsing & Upstream API Resilience

## The `dict.get(key, default)` Trap with External APIs

When consuming upstream JSON APIs (Bstation, external microservices, payment gateways, scrapers), keys often exist explicitly with `null` values:

```json
{
  "day_of_week": "Sen",
  "cards": null
}
```

In Python, `d.get("cards", [])` **does not return `[]`**. It returns `None` because the key `"cards"` exists in the dictionary and its value is `None`.

Iterating directly:
```python
# FAILS with TypeError: 'NoneType' object is not iterable
for card in day.get('cards', []):
    ...
```

### Canonical Defensive Patterns

1. **List iteration:**
   ```python
   for item in (parent.get("items") or []):
       ...
   ```

2. **Nested object navigation:**
   ```python
   # Robust against missing or null data/modules
   modules = (res.get("data") or {}).get("modules") or []
   ```

3. **String handling:**
   ```python
   title = (item.get("title") or "").strip()
   ```

4. **Multi-level nested extraction:**
   ```python
   for parent in (module.get("items") or []):
       for season in (parent.get("seasons") or []):
           season_id = str(season.get("season_id") or "")
   ```

---

## Service Configuration & Verification Protocol

When updating service environment parameters (e.g., proxy ports, cookies, upstream endpoints):

1. **Synchronize unit files:** Update the in-repo unit file and copy/symlink to `/etc/systemd/system/<service>.service`.
2. **Reload daemon & restart:**
   ```bash
   systemctl daemon-reload && systemctl restart <service>
   ```
3. **Verify live runtime state:**
   - Query `/api/health` to confirm the new configuration is actively reported by workers.
   - Test previously failing endpoints (e.g., `/api/seasonal`) directly against the live port.
   - Run project test suites (`test_suite.py`, `test_v2_suite.py`, regression suites).
4. **Commit & push gate:**
   - Commit only after live runtime verification and automated tests are 100% PASS.
