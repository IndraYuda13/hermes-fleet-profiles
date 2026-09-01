# Adversarial Verification Matrix for Cryptographic & CLI Deliverables

When performing independent verification (as PRISM or an independent QA certifier) on cryptographic validators, token engines, or security-sensitive CLI tools, follow this adversarial evaluation matrix.

## 1. Revision Lock & Integrity
- **Digest Verification:** Independently recompute source file SHA-256 (e.g. `hashlib.sha256(open(file, 'rb').read()).hexdigest()`) and compare against the claimed revision hash before running tests.
- **Self-Reported vs Actual:** Test CLI flags like `--revision` and `--health` to confirm they report matching hash digests and passing self-test diagnostics.
- **Zero In-Place Mutation:** Ensure the target source code is not modified or relaxed during QA.

## 2. Adversarial Test Dimensions

### A. Cryptographic Tamper Resistance (Exit Code 1)
- **Signature Bit-Flip:** Modify 1-2 bytes in the signature segment; confirm rejection with `TAMPERED` status.
- **Payload Privilege Escalation:** Decode payload, elevate claims (e.g. `role: admin`, `sub: root`), re-encode without updating signature; verify signature mismatch.
- **Algorithm Confusion Attacks:**
  - `alg: none` header injection.
  - Asymmetric vs symmetric confusion (e.g. setting `alg: RS256` on HMAC validator).
  - Verify rejection with `UNSUPPORTED_ALG` or `MALFORMED`.

### B. Temporal Boundaries & Leeway
- **Expiration Thresholds:** Test expired tokens (`now >= exp`) at exact second boundaries.
- **Clock Skew Leeway Tolerance:** Verify tokens within the configured leeway window (`now - leeway < exp`) evaluate to valid.
- **Strict Post-Leeway Boundary:** Verify that tokens past `exp + leeway` are strictly rejected.
- **Not Before (`nbf`):** Test future `nbf` timestamps for `NOT_YET_VALID` status and confirm leeway accommodates future boundaries.

### C. Secret Key Isolation & Resilience
- **Wrong Key Rejection:** Verify that validation with an incorrect key returns cryptographic failure (exit code 1, `TAMPERED`).
- **Empty / Null Secret:** Verify that an empty secret string triggers an operational error (exit code 2), not silent validation.
- **Secret File Support:** Verify whitespace, leading/trailing newline trimming when reading secret keys from disk.
- **Missing Secret File:** Ensure non-existent file path results in `FILE_NOT_FOUND` (exit code 2).
- **Multi-Byte Unicode:** Test secret keys containing UTF-8 multi-byte characters and symbols.

### D. Structural Fuzzing & Malformed Inputs
- **Segment Count:** Test 0 dots (plaintext), 1 dot, 3+ dots.
- **Malformed Base64:** Inject invalid base64 URL characters (`@`, `!`, `#`, `%`) in header, payload, and signature segments.
- **JSON Root Types:** Inject valid JSON arrays (e.g. `[1, 2, 3]`) or raw JSON primitives into header/payload; confirm rejection where a JSON dictionary/object is required.
- **Non-JSON Strings:** Test base64-encoded plain strings.

### E. Injection & Sanitization in Claims
- **Injection Vectors:** Test claims containing SQL injection payloads, XSS `<script>` tags, and shell metacharacters (`$(whoami)`, pipes).
- **Integrity:** Confirm JSON serialization safely preserves special characters without execution or corruption.

## 3. CLI Exit Code Contract Rigor
Ensure strict adherence to standard status semantics:
- **`0` (Success / Valid):** Successful generation or valid token verification.
- **`1` (Domain / Crypto Failure):** Cryptographically invalid, tampered, expired, or malformed input.
- **`2` (Usage / Syntax / IO Error):** Missing required arguments, bad JSON flags, missing files, or CLI parse errors.
