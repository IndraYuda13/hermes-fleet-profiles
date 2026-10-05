---
name: relational-database-testing
description: Use when testing relational databases or concurrency limits.
version: 1.1.0
author: FORGE
license: MIT
metadata:
  hermes:
    tags: [database, postgresql, vitest, concurrency, drizzle, testing, verification]
    related_skills: [software-development-workflows]
---

# Relational Database Testing & Concurrency Hardening

## Overview

Use this skill when developing, testing, or hardening relational database operations, transactions, row-level locks, quota enforcement, versioned verification workflows, and integration test suites against shared databases.

## Concurrency & Quota Invariants

### 1. PostgreSQL Aggregate Locking Trap (`SELECT ... FOR UPDATE` with aggregates)
- In PostgreSQL, running `SELECT COUNT(*) ... FOR UPDATE` or `SELECT SUM(...) ... FOR UPDATE` fails immediately with `ERROR: FOR UPDATE is not allowed with aggregate functions`.
- **Atomic Quota Solution:** To serialize concurrent requests enforcing a strict threshold (e.g. max 20 items per owner):
  1. Transactionally lock the parent entity row using type-safe Drizzle `.for("update")`:
     ```typescript
     const [parent] = await tx
       .select({ id: parents.id })
       .from(parents)
       .where(eq(parents.id, parentId))
       .for("update");
     if (!parent) throw new NotFoundError("Parent not found");
     ```
  2. In the same transaction, lock the existing child rows matching the active condition:
     ```typescript
     const existingItems = await tx
       .select({ id: children.id })
       .from(children)
       .where(
         and(
           eq(children.parentId, parentId),
           eq(children.status, "ACTIVE")
         )
       )
       .for("update");
     ```
  3. Inspect the returned row count: if `existingItems.length >= quota_limit`, reject immediately with a domain quota error.
  4. Insert the new row and commit.
- **Why:** Locking the parent row guarantees total per-parent serialization across competing concurrent transactions, ensuring parallel requests (such as two simultaneous submissions at count 19) serialize cleanly so exactly one succeeds. Using Drizzle `.for("update")` preserves TypeScript type-safety while generating correct row-level locks.

### 2. Seed Idempotency & Baseline Concurrency (`ON CONFLICT DO NOTHING`)
- When baseline data (roles, system configurations, static anchors) is seeded or lazily initialized in tests or parallel worker processes:
  - Checking existence first with `select()` and conditionally inserting (`if (!existing) await insert()`) creates a time-of-check to time-of-use (TOCTOU) race condition. Two concurrent test workers will both observe no record, attempt simultaneous insertion, and fail with a duplicate key constraint violation (`code_unique` constraint).
- **Rule:** Never use conditional `SELECT` before `INSERT` for idempotent seeds. Always use atomic conflict avoidance on unique columns:
  ```typescript
  await db.insert(roles).values(role).onConflictDoNothing();
  await db.insert(campuses).values(campusConfig).onConflictDoNothing();
  ```
- **Why:** PostgreSQL executes `INSERT ... ON CONFLICT DO NOTHING` atomically at the engine level, eliminating race windows and ensuring concurrent test workers execute safely without duplicate key failures.

### 3. Vitest Shared Database Serialization, Pool Options & In-File Concurrency
- Vitest defaults to running test files in parallel across worker processes (`fileParallelism: true`) and running up to 5 concurrent tests per file (`maxConcurrency: 5`).
- **CLI Default Override Pitfall:** In Vitest, running `vitest run` without CLI worker flags can default `maxWorkers` to `os.cpus().length`, overriding `maxWorkers: 1` defined in `vitest.config.ts`. Always bake `--no-file-parallelism` directly into `package.json` scripts:
  ```json
  "scripts": {
    "test": "vitest run --no-file-parallelism"
  }
  ```
- **Avoid CLI `--pool=threads`:** Never pass `--pool=threads` on the CLI or in `vitest.config.ts` when testing against a real database. In Vitest, worker threads share memory/event loops and bypass file serialization flags, running test suites in parallel and causing immediate PostgreSQL deadlocks (`40P01`) and cross-test table truncation collisions. The default `forks` pool with `--no-file-parallelism` runs files sequentially in clean process isolation.
- **TypeScript `InlineConfig` Compatibility in `vitest.config.ts`:** Do not place unsupported `forks: { singleFork: true }` or `poolOptions: { forks: ... }` directly in `vitest.config.ts` — in Vitest 5 types, these properties do not exist on `InlineConfig` and break `tsc --noEmit` with `error TS2769: Object literal may only specify known properties`. The typecheck-safe, battle-tested configuration is:
  ```typescript
  export default defineConfig({
    test: {
      globals: true,
      environment: "node",
      include: ["tests/**/*.test.ts"],
      fileParallelism: false,
      maxWorkers: 1,
      maxConcurrency: 1,
      testTimeout: 30000,
      hookTimeout: 30000,
      sequence: {
        concurrent: false,
      },
    },
    resolve: {
      alias: {
        "@": path.resolve(import.meta.dirname, "./src"),
      },
    },
  });
  ```
- **Vitest Suite Filter Regex Trap (`-t`):** Vitest's `-t <pattern>` filters match both `it(...)` test titles AND `describe(...)` suite names. If a suite is named `describe("... (TC-48..55)", ...)` passing `-t "TC-48"` matches the suite name and executes all 8 tests rather than only TC-48. Always filter using a unique phrase inside the test title (e.g. `-t "Nominal price-only"`).
- **Vitest Suite Syntax Pitfall:** In Vitest, `describe.sequential` does not exist and throws `TypeError: describe.sequential is not a function`. To enforce sequential test runs, use standard `describe("suite", () => { ... })` paired with `sequence: { concurrent: false }` + `maxConcurrency: 1` in the configuration, or use `it.sequential("test", async () => { ... })` on individual test cases.

### 4. Database Teardown: In-Driver `TRUNCATE ... CASCADE` with Deadlock Retry
- As schemas scale across dozens of interconnected tables, maintaining manual reverse foreign-key `db.delete(table)` lists becomes brittle, failing with foreign key violation errors (`Key is still referenced from table ...`) when cyclical or cascading dependencies expand.
- In-driver multi-table truncation is the canonical approach, but rapid consecutive test execution can trigger PostgreSQL deadlock error `40P01` when background connection pool sessions briefly overlap with the `AccessExclusiveLock` required by `TRUNCATE`.
- **Rule:** Wrap `TRUNCATE TABLE ... CASCADE` in a bounded retry loop catching PostgreSQL error `40P01`:
  ```typescript
  export async function cleanTestDatabase(retries = 5) {
    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        await db.execute(sql`
          TRUNCATE TABLE
            audit_logs,
            reports,
            survey_evidence,
            survey_records,
            survey_requests,
            property_revisions,
            property_media,
            property_contacts,
            property_amenities,
            room_prices,
            room_types,
            favorites,
            preview_allocations,
            entitlement_grants,
            entitlement_projections,
            payment_events,
            provider_transactions,
            invoices,
            properties,
            verification_challenges,
            sessions,
            auth_identities,
            user_roles,
            users
          CASCADE;
        `);
        return;
      } catch (err: any) {
        if (err.code === "40P01" && attempt < retries) {
          await new Promise((resolve) => setTimeout(resolve, 100 * attempt));
          continue;
        }
        throw err;
      }
    }
  }
  ```
- **Terminal Shell Pitfall:** Never execute raw `TRUNCATE` commands via shell CLI tools (`terminal` / bash one-liners) in automated agent workflows. Terminal command safety heuristics detect `TRUNCATE` as a destructive action and pause for interactive confirmation, causing automated workflows to hang or time out. Keep database truncations strictly inside the application/test code executed by the test runner.

### 5. Hook Scope Hygiene in Integration Suites
- Ensure service instantiations, fake webhook providers, and database clients initialized per test are strictly scoped inside `beforeEach(async () => { ... })`.
- If closing braces `});` are placed prematurely before service assignments, those instances become file-scoped singletons executed only once at module load time. This causes transaction caches, idempotency maps, and connection contexts to bleed across tests.
- **Unique Usernames Per Test Case:** In suites where users are registered in test cases, always use distinct usernames per test (e.g. `owner_tc48`, `owner_tc49`) or suffix with entity UUID fragments rather than reusing static strings across tests. If a teardown fails or is delayed, static username collisions trigger `users_username_unique` violations.

### 6. Paywall & Real-Time Entitlement Boundaries
- **Zero Query Quotas:** For active paid seeker subscriptions, never enforce hidden query counters, throttling, or view caps (verify across 50+ consecutive detail queries).
- **Real-Time Entitlement Expiry:** Validate user entitlement against `now` directly in queries. At exactly `end_at` (e.g. `now >= end_at`), reject access immediately with a domain error (e.g., `SubscriptionRequiredError`) without relying on cron jobs or delayed background status synchronization.
- **Zero Sensitive Data Leakage in Previews & Summaries:** Preview allocations and verification summaries accessible by free/unsubscribed seekers must serialize strictly into a whitelisted projection (`{ id, name, coverPhotoUrl, badge }` or `{ propertyId, badge, verificationStatus, surveyedAt, verifiedAt, disclaimer }`). Verify the returned objects contain zero pricing, contact phone numbers, exact addresses, coordinates, or room type breakdowns.

### 7. Dual-Version Tracking & Atomic Invalidation Engine
- When an entity carries an official verification badge (e.g. `VERIFIED`) based on a physical or onsite inspection, editing the entity must follow strict version governance:
  1. **Dual Version Counters:** Maintain two counters on the entity table:
     - `content_version` (integer): increments on EVERY substantive edit (including nominal pricing).
     - `verification_relevant_version` (integer): increments ONLY when sensitive, inspected fields change (address, amenities, photos, availability, room types, contacts). Nominal price adjustments keep this version unchanged.
  2. **Two-Step Edit Warning Workflow:**
     - **Step 1 (Preview):** Run pure domain diff classification (`classifyPropertyChange(oldState, newState)`). If sensitive fields change on a `VERIFIED` entity, set `willRevokeVerified: true` and issue a signed HMAC-SHA256 confirmation token encoding `{ entityId, expectedVersion, changesetHash, issuedAt }`.
     - **Step 2 (Commit):** Lock entity row `FOR UPDATE`. Verify `entity.content_version === confirmation.expectedVersion` (reject with 409 Conflict if stale). If `willRevokeVerified` is true, verify the confirmation token signature, matching entity ID, matching version, and matching changeset hash. Atomically revoke verification status (`UNVERIFIED`), record `revoked_at` and `revocation_reason`, increment versions, record audit log, and record entity revision snapshot.
     - **Whitespace / Identical Edits:** Normalization (e.g. trimming strings or reordering identical primitive arrays) must result in `changedFields: []`, preserving verified badges and versions without requiring confirmation tokens.
  3. **Survey Approval Version Race Protection:**
     - When approving an inspection/survey request, lock the entity `FOR UPDATE` in a transaction.
     - Verify `entity.verification_relevant_version === request.relevant_version`.
     - If the owner edited non-price fields while the inspection was pending, the entity's version will exceed the request's version: reject approval with 409 Conflict (`ConflictError`). An old inspection cannot verify uninspected new data.
  4. **Alternative Mutation Endpoints:** All alternative update paths (e.g. dedicated endpoints for uploading photos, deleting contacts, changing room availability) must execute the same verification invalidation logic if the entity is `VERIFIED`.

## Verification Checklist

- [ ] Row locks (`.for("update")`) are placed on concrete entity rows via type-safe queries, never on aggregate queries.
- [ ] Concurrent tests verify that parallel requests at boundary limit (e.g. limit - 1) allow only one success.
- [ ] Baseline seeds and reference data insertions use `.onConflictDoNothing()` to avoid TOCTOU duplicate key failures during concurrent test runs.
- [ ] Test cleanups use in-driver `TRUNCATE TABLE ... CASCADE` with retry on PostgreSQL `40P01` deadlocks, never shell one-liners.
- [ ] Vitest configuration specifies `fileParallelism: false`, default `forks` pool, `maxWorkers: 1`, and `maxConcurrency: 1` with `--no-file-parallelism` in npm test scripts. Avoid `--pool=threads` which ignores sequential execution.
- [ ] Test lifecycle hooks enclose all per-test service instantiations to prevent singleton state leakage across test cases.
- [ ] Paywall queries verify strict real-time entitlement boundaries without hidden quotas, and public preview serializers contain zero sensitive contact or pricing fields.
- [ ] Verification workflows enforce dual version tracking (`content_version` vs `verification_relevant_version`), two-step HMAC confirmation tokens for sensitive edits, and 409 Conflict rejection on concurrent version races during approval.
