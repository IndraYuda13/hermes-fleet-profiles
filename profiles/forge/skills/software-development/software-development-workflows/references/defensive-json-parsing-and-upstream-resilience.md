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

## Polymorphic LLM Error Lists & Non-Error Sentinels

When prompting multimodal LLMs (e.g. Gemini, Claude, GPT) to return structured lists of defects or transcription errors (e.g. `obvious_transcription_errors: [{"shown": "...", "heard": "..."}]`), models frequently return polymorphic payloads:
- Plain strings instead of dicts: `["salah kata mukabomi bukannya muka bumi"]`
- Affirmative "no-error" sentinel strings: `["tidak ada"]`, `["none"]`, `["clean"]`, `["pass"]`, `[""]`

Iterating blindly with `.get()`:
```python
# CRASHES with AttributeError: 'str' object has no attribute 'get'
for err in obvious_errors:
    shown = err.get("shown", "")
```
And checking `if obvious_errors:` without filtering sentinels causes false failure triggers:
```python
# FAILS VALIDATION even though the model stated there were NO errors!
if obvious_errors: # contains ["tidak ada"]
    status = "FAIL"
```

### Canonical Defensive Handling

1. **Pydantic Schema Typing:**
   ```python
   obvious_transcription_errors: List[Union[Dict[str, Any], str]] = Field(
       default_factory=list,
       description="List of obvious transcription errors {shown, heard} or error descriptions"
   )
   ```

2. **Polymorphic Type Branching & Sentinel Filtering:**
   ```python
   IGNORABLE_SENTINELS = {"none", "tidak ada", "tidak ada kesalahan", "clean", "pass", "no", "n/a", "-", ""}

   real_errors = []
   for err in obvious_errors:
       if isinstance(err, dict):
           shown = err.get("shown", "")
           heard = err.get("heard", "")
           desc = f"Obvious subtitle error: '{shown}' instead of heard '{heard}'"
           real_errors.append(err)
       elif isinstance(err, str):
           if err.lower().strip() in IGNORABLE_SENTINELS:
               continue
           desc = f"Obvious subtitle error: {err}"
           real_errors.append(err)
       else:
           desc = f"Obvious subtitle error: {str(err)}"
           real_errors.append(str(err))
       if desc not in blocking_reasons:
           blocking_reasons.append(desc)

   if real_errors:
       quality_gate_passed = False
   else:
       obvious_errors = []
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
