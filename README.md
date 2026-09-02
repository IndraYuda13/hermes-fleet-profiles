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
├── requirements-policy.txt
├── scripts/
│   ├── apply_role_policy.py     # Render role boundaries into configs
│   ├── sanitize_config.py       # Remove committed runtime secrets
│   ├── sanitize_skill_examples.py # Remove credential-shaped doc samples
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

See [SECURITY.md](SECURITY.md) before deploying this branch. Historical secrets
must be rotated by the owner even after they are removed from the current tree.
