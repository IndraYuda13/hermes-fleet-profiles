# Local LLM Sizing (CPU-only VPS)

Decision tables for sizing Ollama/llama.cpp on CPU-only hosts. The always-on rules (BitNet limits, RAM vs cores, capability probes) live in SKILL.md.

## Sizing matrix (4 vCPU baseline)

| Class | Example models | RAM | Throughput | Best use |
|---|---|---|---|---|
| 1B–3B | Llama-3.2 3B, BitNet 2B | <3 GB | 20–50+ tok/s | edge tasks, fast tool calling |
| 7B–8B | Llama-3.1 8B, Qwen2.5 7B | ~5.5 GB | 10–18 tok/s | interactive chat, light coding |
| 14B–26B | Qwen2.5 14B, Gemma 26B | ~9–17 GB | 6–12 tok/s | reasoning depth at acceptable speed |
| 32B | Qwen2.5 32B, DeepSeek-R1 32B | ~20 GB | ~1.2–1.4 tok/s | offline batch/cron only; 8+ vCPU recommended |

RAM decides whether a model fits; core count decides generation speed. A high-RAM 4 vCPU host can load a 32B model but generation bottlenecks near 1.2–1.4 tok/s.

## Model format & behavior

- BitNet (`bitnet.cpp`) requires models natively pre-trained from scratch with 1.58-bit ternary weights ({-1, 0, 1}). Standard architectures (Gemma, Llama, Qwen) cannot be post-training quantized to BitNet without destroying output quality — use llama.cpp/Ollama standard quantization (`Q4_K_M`, `Q5_K_M`, `Q8_0`) instead.
- Instruct models (`qwen2.5:32b`, `llama3.1:8b`) answer immediately; reasoning models (`deepseek-r1:32b`) emit `<think>` chains before the answer — budget tokens and parse accordingly.

## CPU capability & storage

- Probe vector-extension support before deploying: `lscpu | grep -E "Model name|Flags|Architecture"` — AVX2/AVX-512 is required for viable throughput.
- A failed `ollama pull` leaves orphan partial blobs (`sha256-*-partial`) in the models dir. Recover: delete unused models (`ollama rm <model>`), purge `*partial*` blobs, check `df -h`, retry the pull.
