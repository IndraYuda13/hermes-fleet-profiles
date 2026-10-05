---
name: fast-decision-engines
description: Deploy fast System 1 decision engines on CPU VPS.
---

# Fast System 1 Decision Engines

Use this skill when deploying, sizing, or integrating non-autoregressive and direct-logit decision models (such as Laya, SemIf/OpenJev, TypeSafe Jev) on CPU-only VPS hardware for high-throughput classification, routing, and guardrails.

## Architectural Trade-off: Four Paradigms

| Dimension | Dedicated Encoder (e.g. Laya) | Direct Logit Decoder (e.g. SemIf / OpenJev) | TypeSafe Jev (Cloud API) | Generative LLM (e.g. Qwen / Claude) | Heavy Multimodal Classifier (e.g. Jev-Omni) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Model Type** | Non-autoregressive encoder (ModernBERT, mmBERT) | Decoder-only LLM (Qwen3 0.6B-4B, MiniCPM5) | System One Cloud Decision Engine (Jev) | Autoregressive decoder-only | Multimodal decoder + decision head (Gemma 4 12B) |
| **Inference Mode** | Single forward classification pass | Single forward pass reading option logits | Remote forward decision pass | Autoregressive token generation loop | Multimodal forward hook + decision head |
| **Output Tokens** | **0 tokens** (calibrated probabilities) | **0 tokens** (typed option logits) | **0 tokens** (calibrated probabilities) | Multi-token text / JSON stream | **0 tokens** (option probabilities) |
| **Latency** | **40 - 150 ms** (on 4 vCPU) | **150 - 500 ms** (via llama.cpp GGUF) | **350 - 500 ms** (via Cloud API) | 1,500 - 10,000+ ms | Infeasible on CPU (timeout / severe bottleneck) |
| **Memory / Footprint** | ~1.5 - 2.0 GB RAM | ~1.0 - 3.5 GB RAM (Q4_K_M GGUF) | **0 MB local RAM** | 4 - 20+ GB RAM | 50 - 70+ GB (FP32/BF16 weights) |
| **Hardware Fit** | **Excellent on CPU ($0 cost)** | **Excellent on CPU via llama.cpp** | **Zero host footprint** (needs Internet) | Moderate (chat only, high CPU load) | **Incompatible (requires CUDA GPU)** |
| **Best Use Cases** | Bot triage, proxy checks, fast routing | Semantic `if`, shared state criteria branching | Real-time webhooks, low-latency cloud scoring | Open-ended reasoning, long-form drafting | Video/audio multimodal decision triage (on GPU) |

### CPU Parameter Sizing Trade-offs for Direct-Logit Decoders
When running SemIf or direct-logit decision models on CPU VPS (e.g. 4 vCPUs):
- **0.5B Models (`semif-qwen-0.5b`, ~490M):** ~1.5–2.0s per question cold, ~6s for 3-question evaluation. Ultra-lightweight footprint (~400MB RAM), best for real-time streaming webhook gates and low-latency bot triage where criteria are straightforward.
- **1.5B Models (`semif-qwen-1.5b`, ~1.5B):** ~3s per question, ~9s for 3-question evaluation with prefix caching. **The recommended sweet spot on CPU VPS**: delivers sharp semantic nuance and high-confidence classification comparable to 4B while maintaining sub-10s multi-question budgets.
- **4.0B Models (`semif-qwen-4b`, ~4.0B):** ~13s per question without caching, ~19s for 3 questions with prefix caching. High memory footprint (~2.5GB RAM) and heavy CPU load; reserve for deep semantic evaluations or background auditing tasks where latency is not user-facing.

### Laya vs SemIf (OpenJev) vs TypeSafe Jev
- **Laya (Local Encoder):** Best for fixed-taxonomy classification (2-15 labels) with lowest latency (~40-60 ms) and smallest footprint (~420M).
- **SemIf / OpenJev (Direct Logit Readout):** Best for dynamic, runtime-defined criteria and binary/multi-choice semantic `if` statements. Reuses decoder LLM weights without text generation. Features a native `llama.cpp` CPU backend and shared-state prefix caching (prefills state once, then scores 20+ criteria in parallel).
- **TypeSafe Jev (Cloud API):** High-speed System One cloud decision API (~350–500ms p50 latency). Zero local CPU load or memory footprint. Ideal for production webhooks and acting as a ground-truth baseline to benchmark local CPU models.
- **Jev-Omni (Research Multimodal):** Open multimodal classifier requiring high-end NVIDIA GPU (CUDA required, ~71 GB weights). Not viable on CPU VPS.

### Architectural Constraints & Benchmark References for Encoder Models (Laya)
- **Scale Disparity:** 322M–421M parameters (ModernBERT/mmBERT) vs 1.5B–12B (SemIf / Jev). Sub-500M encoders lack deep world knowledge and fine-grained semantic nuance, leading to uncalibrated confidence or incorrect classification on complex, idiomatic, or non-English text.
- **Head Token Bottleneck (`head_max_len`):** Default option candidate budget is strictly bounded (192 tokens for English, 256 for multilingual). When evaluating >15–20 options or detailed criteria descriptions, text is truncated mid-stream, degrading accuracy (e.g. Banking77: Jev achieves 0.870 across 72 labels vs Laya 0.425 across 77 labels).
- **Weak Ordinal Scoring (`score`):** The `score` head lacks joint ranking calibration (~0.372 accuracy on SST-5). For multi-level rubrics, direct-logit decoders (SemIf) or cloud Jev provide substantially more reliable distributions.
- **Reference Benchmarks & Repos:**
  - Official Model Hub: `https://huggingface.co/convaiinnovations/laya`
  - Upstream Accuracy & ECE Report: `https://github.com/NandhaKishorM/laya/blob/main/BENCHMARKS.md`
  - Community System One Benchmarks: `https://github.com/AbdelStark/jev-benchmarks` and `https://github.com/nibzard/decision-model-benchmark`

## SemIf (OpenJev) CPU Deployment Workflow

SemIf provides open baselines for runtime-defined semantic decisions without generating text.

### 1. Installation on CPU VPS
```bash
# In an isolated virtual environment on expansive storage
python3 -m venv /mnt/semif-env
source /mnt/semif-env/bin/activate

# Install SemIf with llama.cpp CPU backend
pip install -e '.[test,llamacpp]'
```

### 2. Model Fetching (GGUF Format)
Store quantized models on spacious partitions (`/mnt`) to preserve root partition headroom:
```bash
huggingface-cli download bartowski/Qwen_Qwen3.5-4B-GGUF \
  Qwen_Qwen3.5-4B-Q4_K_M.gguf \
  --local-dir /mnt/models
```

### 3. CPU Scoring & Thread Allocation
Use `--backend llamacpp` and cap CPU threads with `--llama-threads`:
```bash
semif-score \
  --backend llamacpp \
  --gguf /mnt/models/Qwen_Qwen3.5-4B-Q4_K_M.gguf \
  --llama-threads 4 \
  --mode direct \
  --input examples/decisions.jsonl \
  --output results.jsonl
```

### 4. Shared State Prefix Caching Pattern
When multiple independent criteria evaluate the exact same underlying state or document:
- **CLI Mode (`--mode shared`):** `llama.cpp` prefills the shared sequence once into sequence slot 0 and branches across criteria suffixes via state save/restore, delivering up to 8–10x throughput gains over repeated direct evaluations.
- **Programmatic Python Pattern (`llama-cpp-python`):**
  Pre-tokenize and evaluate the shared evidence once, snapshot the KV cache state, and restore it before evaluating each criteria suffix:
  ```python
  # 1. Format and prefill shared evidence
  prefix_text = f"<<EVIDENCE>>\n{evidence_state}\n<<END_EVIDENCE>>\n\n"
  prefix_tokens = llm.tokenize(prefix_text.encode("utf-8"), add_bos=True)
  llm.reset()
  llm.eval(prefix_tokens)
  
  # 2. Snapshot KV cache state
  state_snapshot = llm.save_state()
  
  # 3. Branch across questions without re-evaluating evidence
  for q_id, q_spec in questions.items():
      llm.load_state(state_snapshot)
      suffix_text = format_criteria_suffix(q_spec)
      suffix_tokens = llm.tokenize(suffix_text.encode("utf-8"), add_bos=False)
      llm.eval(suffix_tokens)
      
      # Read candidate token logits at position t = -1
      # ... compute softmax over option logits ...
  ```

### 5. Native Direct-Logit Extraction Engine Pattern (llama-cpp-python)
When integrating SemIf logic directly into a web API without external CLI subprocesses, read logits from a single forward pass:
```python
import numpy as np
from llama_cpp import Llama

llm = Llama(model_path="/mnt/models/qwen-0.5b.gguf", logits_all=True, n_threads=4, verbose=False)

def predict_choice(prompt: str, choices: list[str]) -> dict:
    # 1. Format prompt with A, B, C... labels ending with 'Answer: '
    labels = [chr(65 + i) for i in range(len(choices))]
    formatted_prompt = prompt.rstrip() + "\n" + "\n".join(f"{lbl}. {c}" for lbl, c in zip(labels, choices)) + "\nAnswer: "
    
    # 2. Forward pass with 1 token generation to capture output logits
    out = llm(formatted_prompt, max_tokens=1, logprobs=50)
    top_logprobs = out["choices"][0]["logprobs"]["top_logprobs"][0]
    
    # 3. Resolve candidate token logits (check both spaced ' A' and bare 'A')
    logits = []
    for lbl in labels:
        score = top_logprobs.get(lbl, top_logprobs.get(" " + lbl, -100.0))
        logits.append(score)
        
    # 4. Softmax over candidate option logits
    exp_l = np.exp(np.array(logits) - np.max(logits))
    probs = exp_l / np.sum(exp_l)
    winner_idx = int(np.argmax(probs))
    
    return {
        "predicted_label": choices[winner_idx],
        "confidence": float(probs[winner_idx]),
        "probabilities": {c: float(p) for c, p in zip(choices, probs)}
    }
```

### 6. Standard Decision Studio UI Contract Mapping (Laya Studio / Web Workbench)
When exposing direct-logit models to UI decision workbenches, match the expected answer schema exactly across question types:
- **`choice` questions:**
  ```json
  {"choice": "opt_id", "confidence": 0.95, "probabilities": {"opt1": 0.95, "opt2": 0.05}, "action": {"act_probability": 0.95}}
  ```
- **`noul` (Boolean True/False) questions:**
  The frontend evaluates gating via `answer.noul` (`float` probability of `true`). If omitted, client logic defaults to `Unavailable`.
  ```json
  {"choice": "true", "noul": 0.9976, "confidence": 0.9976, "probabilities": {"true": 0.9976, "false": 0.0024}, "action": {"act_probability": 0.9976}}
  ```
- **`score` (Rubric level) questions:**
  Must be **0-indexed** (`"0"`, `"1"`, `"2"`, ...) so the client maps `criteria[Number(level)]` correctly. Compute the expected scalar score via `sum(i * p_i)` and include a `"legend"` dictionary:
  ```json
  {"score": 1.7467, "choice": "2", "probabilities": {"0": 0.02, "1": 0.23, "2": 0.71, "3": 0.03}, "legend": {"0": "Poor", "1": "Fair", "2": "Good", "3": "Great"}, "confidence": 0.71}
  ```

## TypeSafe Jev Cloud Deployment & Adapter Workflow

TypeSafe Jev provides cloud-hosted System One decision models (`jev-latest`, `jev-preview`) with sub-500ms response times.

### 1. API Endpoint and Authentication
- **Endpoint:** `POST https://api.typesafe.ai/v1/systemone`
- **Headers:** `X-API-Key: <api_key>`, `Content-Type: application/json`
- **Request Payload:**
  ```json
  {
    "model": "jev-latest",
    "state": "Transaction succeeded but game coins not credited after 15m.",
    "questions": {
      "action": {
        "type": "choice",
        "instructions": "Recommended support action",
        "criteria": {
          "sync_ledger": "Re-sync ledger mutations",
          "block_user": "Block user account"
        }
      },
      "urgent": {
        "type": "noul",
        "instructions": "Does this impact user balance directly?"
      }
    }
  }
  ```

### 2. Output Adapter Normalization Pattern
Jev returns probabilities directly, but lacks workbench-specific metadata (such as `action.act_probability`, top-level `noul` floats, or computed rubric expectation scalars). Wrap the HTTP client with an adapter to ensure 100% compatibility with UI decision workbenches:
```python
def normalize_jev_response(data: dict) -> dict:
    answers = {}
    for q_id, ans in data.get("answers", {}).items():
        q_type = ans.get("type")
        choice = ans.get("choice")
        probs = ans.get("probabilities", {})
        conf = float(ans.get("confidence", 0.0))
        
        normalized = {
            "type": q_type,
            "choice": choice,
            "confidence": conf,
            "probabilities": probs,
            "action": {"act_probability": conf}
        }
        
        if q_type == "noul":
            normalized["noul"] = float(probs.get("true", conf))
        elif q_type == "score":
            try:
                exp_score = sum(int(k) * float(p) for k, p in probs.items() if str(k).isdigit())
                normalized["score"] = round(exp_score, 2)
            except Exception:
                normalized["score"] = float(choice) if choice and str(choice).isdigit() else 0.0
                
        answers[q_id] = normalized
        
    return {
        "model": data.get("model", "jev"),
        "answers": answers,
        "usage": data.get("usage", {}),
        "latency_ms": data.get("latency_ms", {}),
        "backend": "jev"
    }
```

## High-Impact Deployment Patterns

1. **Bot Webhook Pre-Router & Triage (WA / Telegram):**
   Place Laya or SemIf as the first ingress filter in `on_message`. Evaluate `intent` (`choice`), `needs_human_admin`, and `urgency`. Drop spam sub-50ms, answer stock/pricing via direct DB query, and only escalate complex sentiment to expensive LLMs.
2. **Scraper Anomaly & Proxy Auto-Rotation Gate:**
   Inspect the initial 500 characters of HTTP response bodies before triggering DOM parsers. Evaluate `block_type` (`clean_html`, `cf_turnstile`, `datadome`, `soft_ban`) and `rotate_proxy_immediately` in ~50ms to recycle dirty IP proxies instantly.
3. **Autonomous Agent Inner-Loop Reflex:**
   Evaluate stdout from terminal commands or test runs (`execution_status` -> `build_ok`, `syntax_error`, `port_conflict`, `fatal_crash`) to make instant retry/patch decisions in ~60ms without invoking 2–4s frontier LLM roundtrips.
4. **Multi-Criteria State Auditing:**
   Use SemIf `--mode shared` over large text logs or customer records to evaluate 10-30 compliance criteria concurrently on a single CPU core without repetitive prompt re-encoding.
5. **Hybrid Model Comparison & Verification Bench:**
   Configure local CPU models (Laya, SemIf Qwen) alongside cloud decision models (TypeSafe Jev) behind a unified workbench router. Use Jev as a high-fidelity reference to measure quantization drift and calibration quality on local models.

## Deployment Procedure for Encoders (Laya)

### 1. Storage & Partition Isolation
When root filesystem (`/`) is constrained (>80% full), never allow default caches:
```bash
# Isolate HuggingFace models & virtualenv to expansive storage
export HF_HOME="/mnt/decision-engine/hf_cache"
python3 -m venv /mnt/decision-engine/venv
```

### 2. Warm Singleton Service Pattern
Cold loading weights into memory takes 30-40s on CPU. Keep models loaded in a long-lived process (FastAPI / Uvicorn) using a singleton registry or SDK Router with multi-model capacity:
```python
AGENTS = {}

def get_agent(model_key: str):
    if model_key not in AGENTS:
        AGENTS[model_key] = Agent(model_id_or_path="...", device="cpu")
    return AGENTS[model_key]
```
- **Asynchronous Startup Warmup:** Trigger model loading in a background daemon thread during the ASGI `startup` event rather than synchronously blocking Uvicorn or waiting for the first client request.
- **In-Memory Residency:** When host RAM permits (>16 GB), configure `max_loaded >= total_models` (e.g. `LAYA_MAX_LOADED=2`) so candidate checkpoints stay co-resident in memory.

### 3. CPU Inference & Threading Optimization
- **Wrap Predictions in `torch.inference_mode()`:** Wrap all `agent.predict(...)` invocations with `with torch.inference_mode():`. This disables PyTorch autograd tracking and intermediate graph allocations, shaving 30–40% off latency.
- **Full vCPU Scaling vs Thread Contention Tuning:**
  - *Conservative/Stable default:* On virtualized multi-core VPS (e.g. 4 vCPU), clamping `torch.set_num_threads(logical_cpus // 2)` (e.g. 2 threads) gives consistent ~100–160 ms median latency without spikes.
  - *Full Core Allocation:* When running on all logical vCPUs (e.g. `threads=4`), export `KMP_BLOCKTIME=0`, `OMP_NUM_THREADS=4`, and `MKL_NUM_THREADS=4` in the systemd service or launch environment. `KMP_BLOCKTIME=0` stops Intel MKL/OpenMP worker threads from spin-waiting (default 200 ms) between tensor operations.

## Pitfalls & Operational Rules

1. **Hardware Incompatibility Screening (Hard CUDA Assertions)**: Do not attempt to run complex multimodal decision models (e.g. Jev-Omni) on CPU VPS without inspecting the reference loader. Many reference implementations hardcode assertions such as `if device != 'cuda' or not torch.cuda.is_available(): raise RuntimeError(...)` and rely on CUDA-only autocast operations.
2. **Multi-Shard Repository Disk Exhaustion**: Multimodal decision models can package 10-15+ safetensors shards totaling >70 GB, and their loaders often trigger automatic downstream downloads of base 12B+ models. Always check total repository sibling sizes and target partitions (`/mnt` vs `/`) before triggering snapshot downloads.
3. **Root Partition Overflow**: Model weights will exhaust constrained root disks if `HF_HOME` is not explicitly exported before runtime startup. Always pin model directories to storage partitions with >20 GB headroom.
4. **Autoregressive Fallback Waste**: Do not use heavy generative LLMs for simple classification or routing tickets when a System 1 non-autoregressive or direct-logit engine can resolve them in ~100ms at 10x lower CPU utilization.
5. **Cold Startup 502 on Reverse Proxies**: On CPU VPS, model weight instantiation takes 20–35s. Probing public domains or tunnel endpoints immediately after `systemctl restart` returns HTTP 502 Bad Gateway while Uvicorn waits on startup. Always wait for Uvicorn's startup log (`Application startup complete`) or poll the health endpoint with a retry loop.
6. **Autograd Computation Overhead during Inference**: Omitting `with torch.inference_mode():` during decision model prediction causes PyTorch to allocate autograd graph nodes, inflating CPU latency from ~100–160ms up to ~250–350ms for identical inputs.
7. **Thread Oversubscription & Spin-Wait on All vCPUs**: Setting OpenMP threads equal to total virtual CPU count without `KMP_BLOCKTIME=0` causes thread synchronization overhead and core thrashing. Set `KMP_BLOCKTIME=0` so worker threads immediately yield between parallel BLAS dispatches.
8. **Missing Semantic Criteria on Small Encoders**: Cross-attention encoders (~400M parameters) do not store open-domain trivia knowledge. Querying bare entities without context causes coin-toss probabilities (`~0.50`). Always provide explicit semantic criteria (`criteria: {"true": "...", "false": "..."}`) or descriptive context in `state`.
9. **High-Cardinality Label Collapse (>20 labels)**: Encoder decision heads are optimized for compact candidate token budgets (192–256 tokens). For >15–20 classes, implement a two-stage hierarchical classification flow (e.g. domain router -> leaf intent) or candidate shortlisting.
10. **Non-English `noul` Collapse via English Fallback Template**: When `criteria` is omitted on a `noul` question, the engine formats the decision prompt with the hardcoded English rubric `false: no, the statement does not hold` vs `true: yes, the statement holds`. Always supply localized criteria for non-English text.
11. **Quantization Logit Drift in Direct Scoring**: When evaluating direct option logits via quantized GGUF weights on `llama.cpp`, subtle numerical shifts occur compared to full-precision FP16/BF16 baselines. Compare final choices or use calibrated probability thresholds with tolerance rather than raw logits bit-for-bit.
12. **Tokenizer Leading-Whitespace Mismatch in Candidate Logits**: BPE/SentencePiece tokenizers (Qwen, Llama) assign completely different token IDs to `" A"` vs `"A"`. If the prompt ends with `"Answer: "` (trailing space), the candidate token is `"A"`, whereas if it ends with `"Answer:"` (no space), the candidate token is `" A"`. When reading candidate logits, inspect both token variants (`opt` and `" " + opt`) or strictly match the prompt trailing whitespace to tokenization behavior. Querying the wrong token ID yields uncalibrated, random probability splits.
13. **Single-Token Option Constraint in Direct-Logit Decoders**: Direct-logit readout inspects logits at position `t = -1` in a single forward pass. This requires options to be represented by single tokens (e.g. `A`, `B`, `C`, `1`, `2`, `3`). Never attempt multi-token option strings (e.g. `"high_priority"`) in a single pass without index mapping (`A: high_priority`, `B: low_priority`), because scoring multi-token targets requires auto-regressive prefix scoring which costs `N` forward passes.
14. **Missing `noul` Float Field in UI Gate Adapters**: Decision frontend interfaces (e.g. Laya Studio) evaluate Boolean question outcomes via `answer.noul` (the float probability of `true`). Omitting `answer.noul` from the top-level answer payload causes client gating (`!finite(answer.noul)`) to fall back to an "Unavailable" state even when `choice` and `probabilities` are populated. Always assign `answer["noul"] = probabilities["true"]`.
15. **1-Indexed vs 0-Indexed Level Offsets in Rubric `score` Answers**: Decision UI score components map probability distributions directly to criteria lists by numerical index (`criteria[Number(level)]`). If an adapter indexes score options starting at 1 (`"1"`, `"2"`...), the frontend criteria lookup is shifted by one position and the scalar expected score `sum(i * p_i)` becomes miscalibrated. Always zero-index score options (`"0"`, `"1"`, `"2"...`) and include an explicit `"legend"` map.
16. **Redundant KV Prefill on Multi-Question State Evaluations**: When evaluating multiple criteria or questions against the same underlying state (evidence) using `llama-cpp-python`, evaluating full prompts from scratch scales linearly (`O(N * L_state)`), causing 30–60s CPU stalls on 4B models. Tokenize and evaluate the shared state prefix once (`llm.eval(prefix_tokens)`), capture the KV snapshot via `state = llm.save_state()`, and call `llm.load_state(state)` before evaluating each criteria suffix. This drops multi-question latency by 2x–5x on CPU.
17. **Parameter Sizing Mismatch on Multi-Question CPU Workloads**: 4B models on 4 vCPUs require ~4–6s per forward pass, meaning 3+ questions can take 20–40s even with prefix caching. For real-time triage (<10s budget across 3–5 questions), deploy 1.5B (e.g. Qwen2.5/Qwen3.5 1.5B Q4_K_M) as the balanced baseline: it retains sharp semantic classification accuracy while cutting total CPU evaluation time to ~8–10s.
18. **TypeSafe Jev Cloud Response Normalization for Workbench Gating**: The TypeSafe Jev API (`POST /v1/systemone`) returns calibrated probability distributions directly, but omits UI workbench gating attributes like `action.act_probability`, top-level `answer.noul` float, and computed expected `score` scalars. Passing raw Jev payloads into client workbenches causes probability gauges and confidence badges to render as 'Unavailable'. Always normalize Jev API responses through an adapter that injects `action={"act_probability": confidence}`, assigns `answer["noul"] = probabilities["true"]`, and calculates `sum(int(k) * p)` for rubric scoring.
19. **Single Persistent Client for Remote Decision Cloud Invocations**: Creating a new HTTP client or TCP/TLS session per inference request to remote decision cloud APIs adds 150–300ms of TCP handshake and TLS negotiation overhead to every decision ticket. Use a long-lived async HTTP client (`httpx.AsyncClient(timeout=30.0)`) across the lifecycle of the decision service to maintain persistent HTTP keep-alive connections, keeping end-to-end cloud decision latency under 400ms.
20. **Label Dominance False-Negatives on Sub-500M Encoders (`noul` questions)**: Small cross-attention encoders often allow fixed option tokens (`false:` / `true:`) to dominate over the input state representation, causing confident "no" answers even for plainly positive text. When encoder `noul` outputs fail or stick to negative predictions, rephrase the question as a two-option `choice` with neutral alphabetical keys (`A`, `B`) and full natural-language descriptions in `criteria`.
21. **High-Cardinality Candidate Truncation in Encoder Heads**: When passing >15 options or long criteria descriptions to encoder decision models without tuning `head_max_len`, options exceeding 256 total tokens are silently truncated, resulting in degraded random predictions. For high-cardinality tasks (>20 classes), either raise `agent.cfg["head_max_len"] = 512+` or route to direct-logit decoders (SemIf) or cloud Jev which natively support 100+ un-truncated labels.
