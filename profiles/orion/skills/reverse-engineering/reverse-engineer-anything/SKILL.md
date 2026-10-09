---
name: reverse-engineer-anything
description: Use when reversing targets with REA CLI or MCP tools.
category: reverse-engineering
---

# Reverse Engineer Anything (REA)

REA is an autonomous reverse-engineering framework that provides a safe artifact graph provider, static/runtime analysis, and a deterministic Evidence Ledger across JavaScript/Electron, Android APK, PE/.NET, Mach-O, ELF, firmware, and EVM bytecode.

## Available Surfaces

- **CLI Binary:** `rea` installed globally at `/usr/local/bin/rea`.
- **MCP Server:** Registered as `rea` (command: `rea mcp`) on `orion` and `sentinel` profiles with 139 specialized tools.
- **Diagnostics:** Run `rea doctor` or `rea mcp doctor` to check installed providers and environment requirements.

## Core Capabilities by Target

### 1. Artifacts & Archives (Safe Artifact Graph)
- **Tool / Command:** `rea inspect-artifact <path> [--json]` or MCP `inspect_artifact`
- Generates root manifest, node and edge inventories, and deterministic SHA-256 hashes without executing untrusted binaries.
- Supports ZIP, TAR, ASAR, IPA, APK, DMG, and flat directories.

### 2. JavaScript & Electron Applications
- **CLI Commands:**
  - `rea analyze-javascript-application <path>` (reconstructs ASAR / JS package graphs)
  - `rea recover-javascript-sources <script.js>`
  - `rea export-web-scripts <target>`
- **MCP Tools:** `analyze_javascript_application`, `reconcile_javascript_runtime`, `trace_javascript_semantics`, `compare_javascript_export_shapes`, `recover_javascript_sources`.
- Traces data flow, direct calls, export shapes, and matches HistoricalSourceGraph against bundles.

### 3. Android APKs
- **CLI Command:** `rea inspect-android-package <app.apk>`
- **MCP Tools:** `inspect_android_package`, `search_android_classes`, `inspect_android_class`, `inspect_android_method`, `trace_android_references`, `project_android_application_graph`.
- Inspects package metadata, permissions, decompile classes/methods with smali fallback, and builds call/reference graphs.

### 4. Native Binaries & Memory Layout
- **CLI Command:** `rea inspect-binary-layout <binary>`
- **MCP Tools:** `inspect_binary_layout`, `binary_overview`, `analyze_function`, `batch_decompile`, `inspect_native_api`, `trace_feature`, `trace_call_path`.
- Note: Binary layout inspection via `pwntools-elf` requires `REA_PWNTOOLS_PYTHON` pointing to a Python environment with `pwntools 4.15.0`, `pyelftools 0.33`, and `Unicorn 2.1.2`.

### 5. Evidence Bundle Workflows (Provenance & Verification)
- **MCP Tools:** `export_evidence_bundle`, `import_evidence_bundle`, `get_evidence_bundle`, `record_unknown`, `update_unknown`, `verify_unknown_resolution`.
- Every observation receives an immutable `evidence_id` (e.g. `ev_...`), confidence level (`observed`), and authority (`shipped-artifact`).
- Export bundles to persist findings deterministically across sessions or fleet handoffs.

## Standard Workflow

1. **Verify Target & Health:** Run `rea doctor` if an external provider (pwntools, Hopper, Ghidra) is required.
2. **Safe Triage:** Always begin with `rea inspect-artifact <target>` or MCP `inspect_artifact` to establish artifact inventory and hashes before dynamic probing.
3. **Specialized Inspection:**
   - If JS/Electron: run `analyze_javascript_application` or `recover_javascript_sources`.
   - If APK: run `inspect_android_package` then search classes/methods.
   - If Native/ELF: run `binary_overview` and `analyze_function`.
4. **Anchor Evidence:** Collect evidence IDs and export the deterministic evidence bundle using `export_evidence_bundle` for SDLC or security review handoff.
