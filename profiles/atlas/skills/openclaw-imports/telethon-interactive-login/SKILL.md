---
name: telethon-interactive-login
description: Interactive Telethon login with PTY and process submit.
---

# Telethon Interactive Login Workflow

Guide for running interactive Telethon authentication (e.g. `login.py`) under Hermes Agent.

## Environment & Execution Requirements

- **Background + PTY execution**: Standard `terminal` execution of interactive Python scripts (`input('Please enter code: ')`) fails with `EOFError: EOF when reading a line` unless run in pseudo-terminal background mode (`background=True, pty=True`).
- **Interactive Input Delivery**: Use `process(action='submit', session_id=..., data='<OTP_OR_PASS>')` to pass user inputs directly to the waiting interactive process.

## Step-by-Step Procedure

1. **Start Interactive Script**:
   Execute `terminal(command="python3 login.py +628xxxxxxxxxx", workdir="/path/to/reseller", background=True, pty=True)`.
2. **Check Output Prompt**:
   Call `process(action='log', session_id=proc_id)` to verify script status.
   Look for `"Please enter the code you received:"` or 2FA password prompt.
3. **Ask User for Input**:
   Inform the user that the request has been dispatched and ask for OTP or 2FA password.
4. **Submit Input**:
   Call `process(action='submit', session_id=proc_id, data='12345')`.
5. **Verify Completion**:
   Check `process(action='log', session_id=proc_id)` to ensure user authentication succeeded.
