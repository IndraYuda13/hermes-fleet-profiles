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
├── bootstrap.sh                 # Restore configs to ~/.hermes/
├── scripts/
│   └── sync.sh                  # Export current VPS configs to repo
├── global/
│   └── skills/                  # Shared fleet skills across all profiles
└── profiles/                    # 13 profile definitions
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
./bootstrap.sh
```
