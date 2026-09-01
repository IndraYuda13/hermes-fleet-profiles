---
name: hackerai-repo-exploration
description: Explore and extract tools, prompts, and instructions from HackerAI.
version: 0.1.0
author: Hermes
metadata.hermes.tags:
  - Repository
  - Exploration
  - PromptEngineering
  - Cybersecurity
---

# HackerAI Repository Exploration

This skill encapsulates the process of exploring the HackerAI repository to extract useful patterns, agent behaviors, tools, and system prompts. It specifically focuses on identifying how the AI is orchestrated for penetration testing, how tools are structured, and how prompts are designed to guide the agent. It does not perform active hacking; instead, it extracts the *knowledge* of how to build an AI hacking assistant.

## When to Use

- "Analyze the HackerAI repository."
- "Extract the system prompts from HackerAI."
- "How does HackerAI structure its tools?"
- "What can I learn from HackerAI for reverse engineering or pentesting?"
- "Explore the hackerai-tech/hackerai project."

## Prerequisites

- Git installed and accessible via the `terminal` tool.
- Access to the target repository (e.g., via `git clone https://github.com/hackerai-tech/hackerai.git`).

## How to Run

Invoke the exploration process using the `terminal` tool to clone the repository and search for specific files like prompts, agent definitions, and tools. Use `search_files` or `read_file` to inspect the contents.

## Quick Reference

- **Clone Repo:** `git clone https://github.com/hackerai-tech/hackerai.git /tmp/hackerai`
- **Find Prompts:** `find /tmp/hackerai -name "*prompt*"`
- **Find Tools:** `ls /tmp/hackerai/lib/ai/tools`
- **Read System Prompt:** `read_file(path="/tmp/hackerai/lib/system-prompt.ts")`
- **Read Agent Instructions:** `read_file(path="/tmp/hackerai/AGENTS.md")`

## Procedure

1.  **Clone the Repository:**
    Use the `terminal` tool to clone the repository to a temporary directory.
    ```bash
    git clone https://github.com/hackerai-tech/hackerai.git /tmp/hackerai
    ```

2.  **Explore the Project Structure:**
    List the root directory and find key components like agents, tools, and prompts.
    ```bash
    ls -la /tmp/hackerai
    find /tmp/hackerai -type d -name "agent" -o -name "prompts" -o -name "tools" -o -name "core"
    ```

3.  **Analyze Tools:**
    The tools are located in `lib/ai/tools`. You can inspect them to see what capabilities the agent has. For example, search for the `tool` definition or the `execute` function.
    ```bash
    grep -rn "tool({" /tmp/hackerai/lib/ai/tools
    grep -rn "execute:" /tmp/hackerai/lib/ai/tools
    ```
    Tools include file manipulation, terminal execution, web search, and notes management.

4.  **Extract System Prompts:**
    Locate and read the system prompts used to configure the AI's behavior and personality.
    Use the `terminal` tool or `read_file` to inspect files like `lib/system-prompt.ts` and `lib/system-prompt/personality.ts`.
    ```bash
    cat /tmp/hackerai/lib/system-prompt.ts
    cat /tmp/hackerai/lib/system-prompt/personality.ts
    ```
    These files reveal how the AI is instructed to handle requests, including its personality (e.g., cynic, robot, listener, nerd) and general response guidelines.

5.  **Review Agent Instructions (AGENTS.md):**
    Read the `AGENTS.md` file to understand the workflow and constraints placed on the agent, such as PR review processes and thread coordination.
    ```bash
    cat /tmp/hackerai/AGENTS.md
    ```

6.  **Extract RE and Hacking Workflows:**
    While the repo itself is the *platform* for hacking, the actual "hacking" intelligence is primarily driven by the LLM, augmented by tools like `run-terminal-cmd` (for executing pentest tools in a sandbox) and `web-search`. The key takeaway for RE is the orchestration: combining terminal access, file reading/writing, and structured prompts within a secure sandbox (like E2B).

## Pitfalls

- The repository may be large, making manual inspection tedious. Use `grep` and `find` strategically.
- Some prompts or logic might be spread across multiple files or directories.
- The actual hacking logic might not be hardcoded but relies on the LLM's inherent knowledge combined with the provided tools (like terminal execution).
- The repository relies heavily on external services (OpenRouter, E2B, Convex) which are necessary for running it, but not strictly necessary for just analyzing its structure.

## Verification

Run a command to ensure the repository was cloned and key directories exist:
```bash
ls -d /tmp/hackerai/lib/ai/tools /tmp/hackerai/lib/system-prompt.ts
```