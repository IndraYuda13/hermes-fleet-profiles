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

---

## Resilient Upstream LLM Failover & Unified Client Wrapper

When backend services rely on cloud LLM providers (OpenAI, Google Gemini, Anthropic), direct API calls frequently encounter operational failures:
- HTTP 403 / `PermissionDenied` due to missing/unbilled cloud projects or disabled billing accounts.
- Rate limits (HTTP 429) or transient gateway timeouts (HTTP 504).
- Deprecated or sunset SDK libraries.
- Hardcoded local URLs or static API keys causing security vulnerabilities or deployment lock-in.

Instead of allowing upstream failures or unconfigured providers to crash user endpoints, use a **3-tier resilient degradation architecture** based on standard environment variables and official client libraries:

1. **Tier 1 (Primary Official OpenAI SDK):** Use `from openai import OpenAI` configured via `OPENAI_API_KEY`, optional `OPENAI_BASE_URL` (for custom proxies/compatible endpoints), `OPENAI_MODEL` (e.g. `gpt-4o-mini`), and `AI_TIMEOUT`. Never hardcode local daemon IPs (`127.0.0.1:20128`), tokens, or raw HTTP requests. Support both streaming and non-streaming responses.
2. **Tier 2 (Secondary Provider Fallback):** Catch primary exceptions and gracefully attempt a secondary provider if configured (e.g. Google Gemini via `GEMINI_API_KEY` and `GEMINI_MODEL`).
3. **Tier 3 (Offline Deterministic Heuristics):** If all LLM tiers fail or no keys are configured, raise an exception caught by endpoint controllers to fall back to rule-based dictionaries, caches, or static defaults rather than returning HTTP 500.

### Drop-in Response Contract Emulation

Existing application code often accesses provider-specific response attributes (e.g., `response.text` in Google Gemini or string conversion). The fallback adapter must return a lightweight wrapper preserving the exact attribute contract:

```python
import os
from openai import OpenAI
import google.generativeai as genai

class UnifiedAIResponse:
    def __init__(self, text=""):
        self.text = text or ""

    def __str__(self):
        return self.text

class UnifiedAIClient:
    """
    Arsitektur AI Terpadu & Tangguh (Multi-tier Fallback):
    1. Primary: Library resmi OpenAI SDK (mendukung custom OPENAI_BASE_URL & OPENAI_MODEL).
    2. Fallback: Google Gemini SDK jika GEMINI_API_KEY terkonfigurasi.
    3. Failover: Exception dilempar agar endpoint mengeksekusi fungsi fallback manual bawaan.
    """
    def __init__(self, model=None):
        self.openai_base_url = os.getenv('OPENAI_BASE_URL') or None
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        env_openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        self.openai_model = env_openai_model if (model is None or 'gemini' in str(model).lower()) else model
        self.gemini_model = model if (model and 'gemini' in str(model).lower()) else os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')

        try:
            self.timeout = int(os.getenv('AI_TIMEOUT', '30'))
        except (ValueError, TypeError):
            self.timeout = 30

    def generate_content(self, prompt, **kwargs):
        return self.generate(prompt, **kwargs)

    def generate(self, prompt, **kwargs):
        prompt_str = prompt if isinstance(prompt, str) else str(prompt)
        last_error = None

        # Tier 1: Official OpenAI SDK
        if self.openai_api_key:
            try:
                client = OpenAI(
                    api_key=self.openai_api_key,
                    base_url=self.openai_base_url if self.openai_base_url else None,
                    timeout=self.timeout
                )
                stream = kwargs.get('stream', False)
                response = client.chat.completions.create(
                    model=self.openai_model,
                    messages=[{"role": "user", "content": prompt_str}],
                    stream=stream,
                    timeout=self.timeout
                )

                if stream:
                    content = "".join(
                        chunk.choices[0].delta.content or ""
                        for chunk in response
                        if chunk.choices and chunk.choices[0].delta
                    )
                else:
                    content = response.choices[0].message.content or "" if response.choices else ""

                if content:
                    return UnifiedAIResponse(content)
                raise RuntimeError("OpenAI mengembalikan respons kosong.")
            except Exception as e_openai:
                last_error = e_openai

        # Tier 2: Google Gemini SDK Fallback
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            try:
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel(self.gemini_model)
                req_opts = {"timeout": self.timeout}
                if 'request_options' in kwargs:
                    req_opts.update(kwargs.pop('request_options'))
                resp = model.generate_content(prompt_str, request_options=req_opts, **kwargs)
                if resp and hasattr(resp, 'text') and resp.text:
                    return UnifiedAIResponse(resp.text)
                raise RuntimeError("Gemini mengembalikan respons kosong.")
            except Exception as e_gemini:
                last_error = e_gemini

        error_msg = (
            f"Semua penyedia AI gagal. Error terakhir: {last_error}"
            if last_error
            else "Tidak ada API key AI yang terkonfigurasi (OPENAI_API_KEY / GEMINI_API_KEY)."
        )
        raise RuntimeError(error_msg)

# Backward-compatibility aliases
SafeAIClient = UnifiedAIClient
SafeGenerativeModel = UnifiedAIClient
SafeAIResponse = UnifiedAIResponse
```

### Dual-Route Decorator Registration

When exposing backend API endpoints that frontend templates or external clients consume, naming conventions often diverge between snake_case and kebab-case (e.g., `/api/generate_kata_fokus` in JavaScript vs `/api/generate-kata-fokus` in API documentation/curl). Always register both route formats on the controller (`@app.route('/api/endpoint_name')` and `@app.route('/api/endpoint-name')`) to eliminate 404 routing regressions.
