---
name: break-tool-loops
description: Use when stuck in repetitive patch or test failure loops.
---

# Breaking Tool Loops and Stuck States

When executing complex tasks requiring multiple tool calls, agents can sometimes enter a "stuck state" where they repeat the exact same failing tool invocation or return empty conversational responses. This skill provides explicit strategies to detect and break these loops.

## Identifying the Loop

You are likely in a loop if:
1. You have executed the same `patch` or `terminal` command 3 or more times with identical failure results (e.g., "Could not find a match for old_string", "IndentationError").
2. The platform or system warns you about a "Tool loop warning" or "repeated_exact_failure_warning".
3. You are generating tool calls but returning empty conversational responses, prompting the user to ask "sudah?" or "You just executed tool calls...".

## Strategies to Break the Loop

### 1. Stop Repeating Identical Actions
Never retry a tool call with the exact same arguments if it just failed. The environment has not changed; the call will fail again.

### 2. For `patch` Failures:
- **"Could not find a match"**: The file content differs from your assumption. Widen the `old_string` context significantly, or run `read_file` to verify the current state of the file before trying again.
- **"Found multiple matches"**: Your `old_string` is too generic. Provide more surrounding context lines to make it unique, or use `replace_all=True` if you genuinely intend to change every occurrence.
- **Indentation Errors (Python)**: Ensure the replacement string maintains the exact indentation level of the original context.
- **Fallback**: If patching fails 2-3 times, abandon `patch` and use `write_file` to overwrite the entire file with the known correct content.

### 3. For `terminal` Test Failures:
- Read the test output carefully. If a test fails because of a missing module or syntax error, fix the underlying code before re-running the test.
- Do not blindly re-run a failing test suite without changing the code or environment first.

### 4. Preventing Empty Responses
- After executing a batch of tool calls, you **must** synthesize the results into a clear, concise conversational reply.
- Tell the user what succeeded, what failed, what the failure means, and what you are doing next.
- Do not rely on the user to prompt you to continue.

## Communication
When you detect a loop and pivot your strategy, state this explicitly in your response:
"Patching failed due to ambiguous context. I am reading the file to verify its state and will rewrite the function completely."