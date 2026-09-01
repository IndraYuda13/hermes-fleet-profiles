---
name: vps-llm-sizing
description: Use when sizing local LLMs for CPU-only VPS hardware.
---

# VPS LLM Sizing & Selection

Use this skill when evaluating hardware capacity for running local LLMs on CPU-only VPS host servers or selecting optimal models for CPU inference.

## Key Rules & Trade-offs

1. **BitNet vs Standard GGUF (llama.cpp / Ollama)**
   - **BitNet (`bitnet.cpp`)**: Requires models natively trained from scratch with 1.58-bit ternary weights ($\{-1, 0, 1\}$). Standard models (Gemma, Llama, Qwen) **cannot** be converted to BitNet via post-training quantization without destroying output quality.
   - **Standard GGUF**: Use `llama.cpp` or `Ollama` for full-precision or standard quantized models (Q4_K_M, Q5_K_M, Q8_0).

2. **RAM Capacity vs CPU Core Bottleneck**
   - RAM dictates **which model size can fit**.
   - CPU cores dictate **generation speed (tokens/sec)**.
   - Example: A 4 vCPU server with 54GB RAM can easily *fit* a 32B model (~20GB RAM), but throughput will be limited to ~3-6 tokens/sec due to core count.

3. **Recommended Model Sizing Matrix (CPU-only)**

| Model Scale | RAM Needed (Q4_K_M) | Target CPU Cores | Typical Speed (4 vCPU) | Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **1B - 3B** (e.g. BitNet 2B, Llama-3.2 3B) | < 3 GB | 2 - 4 vCPU | 20-50+ tok/s | Ultra-fast local tasks, edge devices, high-throughput APIs |
| **7B - 8B** (e.g. Llama-3.1 8B, Qwen2.5 7B) | ~5.5 GB | 4 - 8 vCPU | 10-18 tok/s | Good balance for light coding & general chat |
| **14B - 26B** (e.g. Qwen2.5 14B, Gemma4 26B) | ~9 - 17 GB | 4 - 8 vCPU | 6-12 tok/s | Best balance of high intelligence & reasonable speed |
| **32B** (e.g. Qwen2.5 32B, DeepSeek-R1 32B) | ~20 GB | 8+ vCPU recommended | ~1.2 - 1.4 tok/s | Maximum reasoning/coding intelligence; too slow for interactive chat on 4 vCPU, best for batch/cronjob |

## Model Capabilities: Instruct vs Reasoning (Thinking)

- **Instruct Models** (e.g. `qwen2.5:32b`, `llama3.1:8b`): Produce direct responses immediately.
- **Reasoning / Thinking Models** (e.g. `deepseek-r1:32b`, `deepseek-r1:14b`): Feature built-in Chain-of-Thought reasoning (`<think>` tags) before generating final answers. Built on top of base architectures (like Qwen) but fine-tuned for reasoning.

## Storage & Ollama Disk Management

- **Ollama Pull Disk Requirements**: Model downloads (`ollama pull`) download temporary layer blobs (often ~19GB+ for 32B models) into the Ollama storage directory (e.g. `/mnt/ollama-models/blobs`).
- **Insufficient Disk Space Error**: If disk space runs out during a pull, Ollama leaves partial blob files (`sha256-*-partial`).
- **Cleanup Step**:
  1. Remove unused/large existing models: `ollama rm <model_name>`
  2. Clean orphan partial files: `rm -f /mnt/ollama-models/blobs/*partial*`
  3. Verify available disk space: `df -h /mnt`
  4. Retry `ollama pull <model_name>`.

## Quick Diagnostics Commands

```bash
# Check available RAM and vCPU count
nproc
free -h

# Check CPU vector extension support (AVX2 / AVX-512 required for optimal speed)
lscpu | grep -E "Model name|Flags|Architecture"
```
