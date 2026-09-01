# Telethon Interactive Login Reference

## PTY & Process Interaction

When executing interactive CLI scripts in Python (specifically Telethon's `TelegramClient.start()` which invokes standard `input()`), standard execution without PTY results in:

```text
Please enter the code you received: Traceback (most recent call last):
  File "login.py", line 9, in <module>
    client = TelegramClient(...).start()
  ...
  File "telethon/client/auth.py", line 102, in code_callback
    return input('Please enter the code you received: ')
EOFError: EOF when reading a line
```

### Solution Pattern

1. **Launch script with PTY enabled in background**:
   - Tool call: `terminal(command="python3 login.py +6281244495550", workdir="/root/cust/reseller", background=True, pty=True)`
   - Returns: `proc_id` (e.g. `proc_0902aad11a9a`)

2. **Poll output via `process` tool**:
   - Tool call: `process(action='log', session_id='proc_0902aad11a9a', limit=20)`
   - Output snippet: `Please enter the code you received:`

3. **Submit input via `process` tool**:
   - Tool call: `process(action='submit', session_id='proc_0902aad11a9a', data='<OTP_CODE>')`
