# Hermes Fleet Profiles

Declarative Configuration, Prompts, and Domain Skills for the Multi-Agent Autonomous Fleet on [Hermes Agent](https://hermes-agent.nousresearch.com).

## 🏛️ Fleet Architecture

The fleet is organized around domain-specialized roles governed by an orchestrator with strict zero-bypass quality verification:

| Profile | Domain & Responsibilities |
| :--- | :--- |
| **`orion`** | **Chief of Staff & Quality Governor** — Task classification, decomposition, A2A routing, release gates, final synthesis. |
| **`aurora`** | **Product & UX Design** — Information architecture, UI design DNA, interaction contracts, anti-homogenization. |
| **`frame`** | **Frontend Engineering** — Clean implementation, responsive web, browser runtime states. |
| **`lens`** | **Visual & Interaction QA** — Independent rendered QA, screenshot analysis, macro-diversity auditing. |
| **`forge`** | **Backend & Systems** — APIs, databases, queues, bot engines, background workers, integration code. |
| **`prism`** | **Functional QA & Correctness** — Algorithmic correctness, benchmarks, regression testing, reproducibility. |
| **`sentinel`** | **Security & Risk** — Threat modeling, vulnerability scanning, auth/secrets audit, defense hardening. |
| **`atlas`** | **Infrastructure & SRE** — Cloudflare tunnels, deployment, Docker, reliability, process supervision. |
| **`radar`** | **Technical Intelligence** — Emerging tech research, primary-source reconnaissance, market discovery. |
| **`quant`** | **Quantitative & Market Research** — Statistical models, time-series, regime analysis, financial signals. |
| **`nexus`** | **Operations & Docs** — SOPs, documentation, runbooks, release communications. |
| **`groupbot`** | **Bridge & Community Bot** — Public chat / group routing integration. |

---

## 📂 Repository Structure

```text
hermes-fleet-profiles/
├── .gitignore
├── README.md
├── bootstrap.sh                 # Validated, dry-run-first restore
├── governance/                  # Canonical kernel, roles and workflow packs
│   ├── gauntlets/               # End-to-end fleet acceptance fixtures
│   └── runtime-smoke.yaml       # Effective runtime and role-boundary probes
├── requirements-policy.txt
├── scripts/
│   ├── apply_role_policy.py     # Render role boundaries into configs
│   ├── deploy_role_policy.py    # Surgical, backed-up live policy overlay
│   ├── sanitize_config.py       # Remove committed runtime secrets
│   ├── sanitize_skill_examples.py # Remove credential-shaped doc samples
│   ├── runtime_smoke.py         # Live config, A2A, SoD and UI gauntlet
│   ├── validate_fleet.py        # Policy, A2A and evidence checks
│   └── sync.sh                  # Staged export from live Hermes
├── global/
│   └── skills/                  # Shared fleet skills across all profiles
└── profiles/                    # 12 directories: 11 A2A profiles + GROUPBOT
    ├── orion/
    ├── atlas/
    ├── aurora/
    ├── forge/
    ├── frame/
    ├── lens/
    └── ...
```

---

## 🚀 Quick Setup & Restore

On a fresh server with Hermes installed:

```bash
git clone git@github.com:IndraYuda13/hermes-fleet-profiles.git
cd hermes-fleet-profiles
chmod +x bootstrap.sh scripts/sync.sh
./bootstrap.sh                    # read-only plan
./bootstrap.sh --apply            # prompts/skills; preserves config and .env
# Only after runtime secrets exist in ~/.hermes/.env:
./bootstrap.sh --apply --replace-config
```

Before exporting live changes back into Git:

```bash
./scripts/sync.sh                 # staged validation + itemized dry-run
./scripts/sync.sh --apply         # requires a clean Git worktree
```

For an existing configured fleet, apply policy without replacing runtime-owned
credentials, providers, channel identifiers, plugins or skills:

```bash
python3 scripts/deploy_role_policy.py --hermes-home "$HOME/.hermes"          # dry-run
# Stop all fleet gateways after reviewing the plan.
python3 scripts/deploy_role_policy.py --hermes-home "$HOME/.hermes" --apply
```

## Policy gate

```bash
python3 -m pip install -r requirements-policy.txt
python3 scripts/sanitize_config.py --check profiles/*/config.yaml
python3 scripts/sanitize_skill_examples.py --check global/skills profiles
python3 scripts/validate_fleet.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

The gate enforces model allocation, exact A2A topology, role-specific tool
boundaries, disabled automatic MOA/delegation, GROUPBOT isolation, secret-free
configs and the AURORA → FRAME → LENS UI lifecycle.

## Staged runtime proof

Repository policy is necessary but not sufficient. After deploying to a
disposable staging fleet, validate the effective runtime in increasing order:

```bash
python3 scripts/runtime_smoke.py --mode discovery --hermes-home "$HOME/.hermes"
python3 scripts/runtime_smoke.py --mode boundaries --execute \
  --hermes-home "$HOME/.hermes" --workspace /srv/hermes-fleet-staging
python3 scripts/runtime_smoke.py --mode full --execute --timeout 600 \
  --hermes-home "$HOME/.hermes" --workspace /srv/hermes-fleet-staging
python3 scripts/runtime_smoke.py --mode ui-gauntlet --execute --timeout 3600 \
  --hermes-home "$HOME/.hermes" --workspace /srv/hermes-fleet-staging
```

The mutating modes refuse to run unless the workspace contains the explicit
`.hermes-fleet-staging` safety marker. See
[`docs/PHASE_2_3_RUNTIME_VALIDATION.md`](docs/PHASE_2_3_RUNTIME_VALIDATION.md)
for preparation, acceptance and failure handling.

See [SECURITY.md](SECURITY.md) before deploying this branch. Historical secrets
must be rotated by the owner even after they are removed from the current tree.
