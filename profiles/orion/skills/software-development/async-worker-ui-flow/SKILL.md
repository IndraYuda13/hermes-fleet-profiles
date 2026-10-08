---
name: async-worker-ui-flow
description: Use when building UI that polls async background workers.
version: 1.0.0
author: Orion
license: MIT
metadata:
  hermes:
    tags: [software-development, frontend, async, worker, polling, ui-ux]
---

# Async Worker UI Flow

## Overview

Use when designing and implementing web user interfaces that trigger asynchronous background processing (such as AI generation, media rendering, or queue-based tasks) and poll for completion.

## Core Architecture

### 1. Unified State Synchronization on Completion
When background workers process jobs asynchronously via a database queue (SKIP LOCKED, Celery, pg-boss):
- The polling endpoint (e.g. `/api/generations/:id`) tracks lifecycle: `PENDING` -> `PROCESSING` -> `COMPLETED` | `FAILED`.
- **Pitfall:** Do not merely set `isGenerating = false` when polling detects `COMPLETED`. Flipping local loading state without explicitly re-fetching the updated parent entity leaves newly created child records (such as new segments, choice nodes, or results) invisible until an unprompted page refresh.
- **Rule:** On terminal status `COMPLETED`, immediately trigger parent state re-fetch (e.g. `loadStory()`, `revalidate()`), then scroll the fresh content into viewport view.

### 2. Single Source of Truth for Progress Indicators
- Place generation and progress banners in a single authoritative container.
- **Pitfall:** Decoupling loading state between a top header banner and a bottom stream wrapper creates duplicate, conflicting progress cards during active worker polling.
- Bind the progress spinner/card to the active stream tail only, suppressing redundant sticky or header banners during in-progress execution.

### 3. Guarding Zero-Item States Against Phantom Spinners
- When a new document, narrative, or job container starts with 0 items (e.g. 0 chapters or segments):
  - **Pitfall:** Defaulting the progress indicator to an active running/spinning state (e.g. `stage={generationStage || 'preparing'}`) when no `jobId` exists or polling loop is active causes the UI to spin forever. If the initial start request was rejected (e.g. 429 quota exhausted, 403 entitlement, network drop), the user is stranded in a perpetual fake loading screen with no action available.
  - **Rule:** Never show an active progress spinner or multi-stage execution tracker unless actively tied to a running `jobId` or verified background poll.
  - **Rule:** If item count is 0 and no job is running, display an explicit idle state with a clear primary CTA (e.g. *"Mulai Rangkai Bab Pertama"*) or an explicit error banner with a retry trigger.
  - **Rule (URL Job ID Handoff):** When transitioning from a creation wizard (e.g. `/baru`) to an item room (e.g. `/cerita/:id`), pass the accepted job ID as a query param (e.g. `?jobId=<uuid>`). The receiving page must check `urlJobId` on mount and kick off polling immediately to prevent race conditions where parent entity hydration precedes worker reflection.

### 4. Clean End-User Facing UX Copy (No Infrastructure Leaks)
- **Pitfall:** Exposing backend routing mechanisms, model version tags, proxy providers, or internal gateway names (e.g. *"Diproses oleh model Gemini TTS via 9router"*, *"Worker task dispatched to Redis queue 4"*) in client-facing modals, audio players, or toasts.
- **Rule:** End-user client UI must show domain-level, customer-centric status only (e.g. *"Audio Siap Didengarkan"*, *"Menyusun Bab Pembuka"*).
- Internal model names, proxy routes, retry counts, and worker topologies belong strictly in server logs, admin observability consoles, and telemetry headers.
- **Rule (Sanitized Upstream Errors):** Never expose raw AI schema failures, JSON parser exceptions, model refusal tokens, or internal database constraints directly to end users. Map upstream errors through a domain sanitizer to calm, actionable guidance (e.g. *"AI sedang mengalami kendala sesaat saat menyusun alur cerita. Silakan tekan coba lagi."*).

### 5. Contextual Controls in Paginated / Segmented Views
- When a document or narrative is divided across multiple chapters or pages (e.g. 1 chapter per page with drawer navigation):
  - Actionable choice/decision controls belong strictly to the latest/head chapter.
  - If the user navigates back to inspect historical chapters (e.g. Chapter 1 while story is at Chapter 5), hide current choice controls and render an informational notice: *"You are viewing Chapter 1. Active continuation is at Chapter 5"* with a one-click quick jump to the latest chapter.
  - Store reader density preferences (e.g. chapters per page) in `localStorage` for consistent UX across sessions.

### 6. Resilient Draft Preservation & Non-Destructive Error Handling
- When users submit custom steering text, prompts, or choices that trigger background generation:
  - **Pitfall:** Storing drafts purely in React `useState` erases user input if validation, quota limits, or entitlement checks reject the request (e.g. 403 `FEATURE_UNAVAILABLE` or 429 `QUOTA_EXHAUSTED`), or if the user accidentally refreshes.
  - **Rule:** Synchronize custom inputs to `sessionStorage` on change (keyed by entity ID). Clear the draft storage key only upon verified HTTP 200 / successful queue acceptance.
  - **Rule:** On API rejection, set the error state without resetting the input field or draft state. Retain typed text so the user can edit or retry once the gate clears.
  - **Rule (Server Log Before Gating):** Always log freeform steering payloads to the application journal before running entitlement or quota gating, ensuring lost-draft forensics and support diagnostics are possible.
  - **Rule (No Native Browser Dialogs):** Never interrupt async operations or communicate quota/validation rejections using unstyled `window.alert()` or browser popups. Render contextual inline notices or non-blocking toasts that keep the user's form context intact.
