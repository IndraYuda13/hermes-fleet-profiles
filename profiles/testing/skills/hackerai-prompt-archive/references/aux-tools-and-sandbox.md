# HackerAI auxiliary prompts: tool schemas + sandbox manager + stream helpers

Byte-exact extracts (machine-copied) from HackerAI @ 6cf55ed545a59b1a61740a857b505cf18b8fad2b.


## From `raw/aux/ai_tools_schemas.ts.extract.md`

# Extracts from ai/tools/schemas.ts


===== commandCompositionGuidance (254 chars) =====
1. Prefer one static command per tool call so a safe argv prefix can be approved and reused:
   - Do not chain commands or use shell operators such as \`&&\`, \`|\`, \`;\`, redirects, or substitutions
   - Use separate tool calls for multi-step workflows

===== <?> (315 chars) =====
1. Use command chaining and pipes for efficiency:
   - Chain commands with \`&&\` to execute multiple commands together and handle errors cleanly (e.g., \`cd /app && npm install && npm start\`)
   - Use pipes \`|\` to pass outputs between commands and simplify workflows (e.g., \`cat log.txt | grep error | wc -l\`)

===== largeOutputGuidance (355 chars) =====
7. Handle large outputs and save scan results to files:
  - For complex and long-running scans (e.g., nmap, dirb, gobuster), use the tool's native output-file flags (e.g., \`-oN\` for nmap)
  - Keep each command static and use separate tool calls to inspect or extract relevant results
  - Never let full verbose output return to context (causes overflow)

===== full (659 chars) =====
7. Handle large outputs and save scan results to files:
  - For complex and long-running scans (e.g., nmap, dirb, gobuster), save results to files using appropriate output flags (e.g., -oN for nmap) if the tool supports it, otherwise use redirect with > operator.
  - For large outputs (>10KB expected: sqlmap --dump, nmap -A, nikto full scan):
    - Pipe to file: \`sqlmap ... 2>&1 | tee sqlmap_output.txt\`
    - Extract relevant information: \`grep -E "password|hash|Database:" sqlmap_output.txt\`
    - Anti-pattern: Never let full verbose output return to context (causes overflow)
  - Always redirect excessive output to files to avoid context overflow.

===== full (3695 chars) =====
Execute a command on behalf of the user.
If you have this tool, note that you DO have the ability to run commands directly in the sandbox environment.
Commands run in the selected sandbox environment.${approvalGated ? " The platform will pause execution after you call this tool and ask the user to approve it; do not ask in chat instead of calling the tool when a command is needed." : ""}
${approvalGated ? "For every approval-gated command, provide a concise, user-facing justification describing the intended outcome; HackerAI displays it in the approval prompt, so do not merely repeat the command. prefix_rule is optional: provide it only for a narrow, useful category of similar commands the user can safely approve for this conversation. It must be an exact argv prefix represented as separate array elements. Prefer a stable safe prefix over copying the complete command, and omit it when no reusable scope is appropriate. Never provide prefix_rule for destructive commands, shell wrappers, compound commands, redirects, substitutions, environment assignments, wildcards, or other dynamic shell syntax." : ""}
In using these tools, adhere to the following guidelines:
${commandCompositionGuidance}
2. NEVER run code directly via interpreter inline commands (like \`python3 -c "..."\` or \`node -e "..."\`). ALWAYS save code to a file first, then execute the file. If the file tool reports a transport failure, reconnect the Desktop app before retrying. Never substitute a terminal write to bypass a rejected file operation or project-root boundary. A timeout or lost response may hide a completed write: inspect the file before retrying, especially before append.
3. For ANY commands that would require user interaction, ASSUME THE USER IS NOT AVAILABLE TO INTERACT and PASS THE NON-INTERACTIVE FLAGS (e.g. --yes for npx).
${pagerGuidance}
5. For long-running commands whose output or completion you need to monitor, keep \`is_background\` false. If the result says \`Process running with session ID X\`, continue it with \`interact_terminal_session\` using that exact session ID. Use \`is_background\` true only for detached jobs whose output and completion you do not need to poll; a detached PID is not a reusable terminal session.
6. Dont include any newlines in the command.
${largeOutputGuidance}
8. Install missing tools when needed: Use \`apt install tool\` or \`pip install package\` (no sudo needed in container).
9. After creating files that the user needs (reports, scan results, generated documents), use the get_terminal_files tool to share them as downloadable attachments.
10. Choose scope and execution intensity from the user's objective, target behavior, and available resources. Adapt when errors, throttling, or diminishing returns appear. Preserve useful progress and inspect existing sessions, execution records, and artifacts before repeating work. A wait expiring is not a process failure: continue the returned session. Finish when the requested outcome is supported by evidence, and state any remaining uncertainty.
11. When users make vague requests (e.g., "do recon", "scan this", "check security"), start with fast, lightweight tools and quick scans to provide initial results quickly. Use comprehensive/deep scans only when explicitly requested or after initial findings warrant deeper investigation.
12. When searching for text in files, prefer using \`rg\` (ripgrep) because it is much faster than alternatives like \`grep\`. When searching for files by name, prefer \`rg --files\` or \`find\`. If the \`rg\` command is not found, fall back to \`grep\` or \`find\`.
   - To read files, prefer the file tool over \`cat\`/\`head\`/\`tail\` when practical.

===== <?> (552 chars) =====
Time in seconds to wait for command output before returning; reaching this limit does not terminate the process. A foreground command that is still running returns a reusable opaque session ID for interact_terminal_session; copy it exactly and never derive one from a PID. Captured output is retained in a bounded execution record when available. Explicit cancellation and infrastructure resource limits can still stop execution. Capped at ${RUN_TERMINAL_MAX_TIMEOUT_SECONDS} seconds. Defaults to ${RUN_TERMINAL_DEFAULT_STREAM_TIMEOUT_SECONDS} seconds.

===== createInteractTerminalSessionToolSchema (3204 chars) =====
Interact with persistent shell sessions in the sandbox environment.

<supported_actions>
- \`view\`: View the content of a shell session
- \`wait\`: Wait for the running process in a shell session to return
- \`send\`: Send input to the active process (stdin) in a shell session
- \`kill\`: Terminate the running process in a shell session
</supported_actions>

<instructions>
- Use the exact \`session\` returned by \`run_terminal_cmd\`, including a session preserved in conversation context; never invent an ID
- Across turns, \`view\` or \`wait\` can retrieve a historical execution record when the live session has closed. Check its status, saved output, and artifacts before repeating work. A historical record cannot accept input or be killed; a last-recorded running state does not prove the process is still alive.
- A PID is not a session ID. Never derive a session from a PID (for example, never turn PID 1689 into \`cmd-1689\`)
- Input-capable sessions are created with \`interactive=true\`; timed-out foreground commands may return non-interactive sessions that support wait/view/kill but not send
- When using \`view\` action, ensure command has completed execution before using its output
- Set a short \`timeout\` (such as 5s) on \`wait\` for processes that don't return promptly to avoid meaningless waiting time
- The output wait does not kill processes; explicit cancellation, response cleanup, and infrastructure resource limits can close live sessions. Saved records remain available while the original sandbox and retention allow.
- Use \`wait\` action when a process needs additional time to complete and return
- Only use \`wait\` after \`send\`, or after \`run_terminal_cmd\` returned without finishing and included an explicit \`session\` field; decide whether to wait based on the prior output
- DO NOT use \`wait\` for long-running daemon processes
- \`send\` writes input and captures only the immediate response chunk; if the process needs more time before it replies, follow up with \`action=wait\`
- \`input\` is sent verbatim. Without a trailing \\n (or \`Enter\`), the line is typed but NOT submitted - a follow-up \`send\` will append to the same line. ALWAYS include \\n unless you specifically want to type without pressing Enter (e.g. building up a key sequence)
- For special keys, use official tmux key names: C-c (Ctrl+C), C-d (Ctrl+D), C-z (Ctrl+Z), Up, Down, Left, Right, Home, End, Escape, Tab, Enter, Space, F1-F12, PageUp, PageDown
- For modifier combinations: M-key (Alt), C-S-key (Ctrl+Shift)
- Note: Use official tmux names (BSpace not Backspace, DC not Delete, Escape not Esc)
- For non-key strings in \`input\`, DO NOT perform any escaping; send the raw string directly
</instructions>

<recommended_usage>
- Use \`view\` to check shell session history and latest status
- Use \`wait\` to wait for the completion of long-running commands
- Use \`send\` to interact with processes that require user input (e.g., responding to prompts)
- Use \`send\` with special keys like C-c to interrupt, C-d to send EOF
- Use \`kill\` to stop background processes that are no longer needed
- Use \`kill\` to clean up dead or unresponsive processes
</recommended_usage>

===== <?> (199 chars) =====
Timeout in seconds to wait for output. Only used for \`wait\` action. Defaults to ${INTERACT_TERMINAL_DEFAULT_WAIT_TIMEOUT_SECONDS} seconds. Max ${INTERACT_TERMINAL_MAX_WAIT_TIMEOUT_SECONDS} seconds.

===== createGetTerminalFilesToolSchema (995 chars) =====
Share files from the terminal sandbox with the user as downloadable attachments.

Usage:
- Use this tool when the user requests files or needs to download results from the sandbox
- Provide full file paths (e.g., /home/user/output.txt, /home/user/scan-results.xml)
- Files are automatically uploaded and made available for download
- Paths belong to the selected Cloud, Desktop, or remote computer; Cloud files are not already on the user's computer
- Before sharing a runnable package, verify the exact archive from a fresh extraction when the required environment is available; otherwise report the verification blocker
- deliveryReceipts confirm storage, not that a package runs or satisfies the requested behavior
- Files larger than 250 MB cannot be shared; reduce, split, or exclude bulky generated/dependency directories before sharing
- Use this after generating reports, saving scan results, or creating any files the user needs to access
- Multiple files can be shared in a single call

===== instructionsDescription (309 chars) =====
Perform operations on files in the sandbox file system.
This tool is the primary way to manage file content, allowing for reading, writing, appending, editing text-based files, and viewing raster image files.

### Supported Actions

${supportedActionsDescription}

### Instructions

${instructionsDescription}

===== todoWriteTool (4877 chars) =====
Use this tool to create and manage a structured task list for your penetration testing session. This helps track progress, organize complex security assessments, and ensure thorough coverage.

Note: Other than when first creating todos, don't tell the user you're updating todos, just do it.

### When to Use This Tool

Use proactively for:
1. Complex multi-step security assessments (3+ distinct steps)
2. Non-trivial vulnerability testing requiring systematic approach
3. User explicitly requests todo list
4. User provides multiple targets or attack vectors (numbered/comma-separated)
5. After receiving new instructions - use merge=true to add or patch requirements while retaining unfinished work. Use merge=false only for an intentional complete replan.
6. After completing tasks - mark complete with merge=true and add follow-ups
7. When starting new tasks - mark as in_progress (ideally only one at a time)

### When NOT to Use

Skip for:
1. Single, straightforward checks
2. Quick reconnaissance queries
3. Tasks completable in < 3 trivial steps
4. Purely informational requests about security concepts

NEVER INCLUDE THESE IN TODOS: basic enumeration steps; reading tool output; routine scanning operations.

### Examples

<example>
  User: Test the authentication system for vulnerabilities
  Assistant:
    - *Creates todo list:*
      1. Test login endpoint for SQL injection [in_progress]
      2. Check for authentication bypass vectors
      3. Analyze session management weaknesses
      4. Test password reset flow for flaws
    - [Immediately begins working on todo 1 in the same tool call batch]
<reasoning>
  Multi-step security assessment with multiple attack surfaces.
</reasoning>
</example>

<example>
  User: Perform a full security assessment of the /api endpoints
  Assistant: *Enumerates endpoints, identifies 12 routes across 5 controllers*
  *Creates todo list with specific items for each endpoint category*

<reasoning>
  Complex assessment requiring systematic tracking across multiple attack surfaces.
</reasoning>
</example>

<example>
  User: Check for IDOR, XSS, SSRF, and privilege escalation vulnerabilities
  Assistant: *Creates todo list breaking down each vulnerability class into specific tests*

<reasoning>
  Multiple vulnerability categories provided requiring organized testing approach.
</reasoning>
</example>

<example>
  User: The admin panel seems insecure - find all the issues
  Assistant: *Analyzes admin functionality, identifies attack vectors*
  *Creates todo list: 1) Test access controls, 2) Check for privilege escalation, 3) Analyze file upload functionality, 4) Test for CSRF, 5) Check sensitive data exposure*

<reasoning>
  Comprehensive security assessment requires multiple testing phases.
</reasoning>
</example>

### Examples of When NOT to Use the Todo List

<example>
  User: What is SQL injection?
  Assistant: SQL injection is a code injection technique...

<reasoning>
  Informational request with no testing task to complete.
</reasoning>
</example>

<example>
  User: Run a quick port scan on the target
  Assistant: *Executes port scan* Results show ports 22, 80, 443 open...

<reasoning>
  Single straightforward scan with immediate results.
</reasoning>
</example>

<example>
  User: Check if this URL is vulnerable to path traversal
  Assistant: *Tests for path traversal* The endpoint appears to sanitize input...

<reasoning>
  Single targeted test on one endpoint.
</reasoning>
</example>

### Task States and Management

1. **Task States:**
  - pending: Not yet started
  - in_progress: Currently testing
  - completed: Finished successfully
  - cancelled: No longer relevant

2. **Task Management:**
  - Update status in real-time
  - Mark complete IMMEDIATELY after finishing
  - Only ONE task in_progress at a time
  - Complete current tasks before starting new ones
  - Keep unfinished work pending or in_progress across turns, pauses, limits, and summarization. Never cancel work just to finish a turn or because its context is missing.
  - Cancel only when a user scope change or confirmed obsolescence makes the task irrelevant; explain the reason to the user. Mark completed only after verifying the work.
  - If IDs or the plan are unclear, read the current list with merge=true and todos=[] before updating. Never guess IDs.

3. **Task Breakdown:**
  - Create specific, actionable security tests
  - Break complex assessments into targeted checks
  - Use clear, descriptive names (e.g., "Test /api/users for IDOR")

4. **Parallel Todo Writes:**
  - Prefer creating the first todo as in_progress
  - Start working on todos by using tool calls in the same tool call batch as the todo write
  - Batch todo updates with other tool calls for efficiency

When in doubt, use this tool. Systematic task management ensures comprehensive security coverage and prevents missed vulnerabilities.

===== createWebSearchToolSchema (1242 chars) =====
Search for information across various sources.

<instructions>
- MUST use this tool to access up-to-date or external information when needed; DO NOT rely solely on internal knowledge
- Each search MUST contain exactly 1 to 3 \`queries\` (NEVER more than 3). Queries MUST be variants of the same intent (i.e., query expansions), NOT different goals
- For non-English queries, MUST include at least one English query as the final variant to expand coverage
- For complex searches, MUST break down into step-by-step searches instead of using a single complex query
- Access multiple URLs from search results for comprehensive information or cross-validation
- CAN use Google dork syntax (site:, filetype:, inurl:, intitle:, etc.) for targeted reconnaissance and pentest enumeration
- Only use \`time\` parameter when explicitly required by task, otherwise leave time range unrestricted
- Prioritize cybersecurity-relevant information: CVEs, CVSS scores, exploits, PoCs, security tools, and pentest methodologies
- Include specific versions, configurations, and technical details; cite reliable sources (NIST, OWASP, CVE databases)
- For commands/installations, prioritize Kali Linux compatibility using apt or pre-installed tools
</instructions>

===== createOpenUrlToolSchema (459 chars) =====
Retrieve the full contents of a specific webpage by URL.

<instructions>
- Use to fetch and read a specific webpage, usually obtained from a prior search
- URLs must be valid and publicly accessible
- Prioritize cybersecurity-relevant information: CVEs, CVSS scores, exploits, PoCs, security tools, and pentest methodologies
- Include specific versions, configurations, and technical details; cite reliable sources (NIST, OWASP, CVE databases)
</instructions>

===== createNoteTool (3014 chars) =====
Create a new personal note to record observations, findings, or research during security assessments. Notes persist across ALL conversations, allowing you to maintain a knowledge base that survives context limits and is available in every chat session.

<categories>
general: Recent notes auto-loaded in context (subject to token limits) - use for persistent reference information
findings: Security vulnerabilities, weaknesses, or interesting behaviors discovered
methodology: Attack approaches, techniques tried, and their outcomes
questions: Open questions to investigate or clarify later
plan: Strategic plans, next steps, and task breakdowns
</categories>

<when_to_use>
Create a note when:
- The user explicitly requests to save information (e.g., "save this", "write this down", "record this finding", "note this")
- You discover a security vulnerability or interesting behavior worth documenting
- You want to preserve intermediate findings that need to survive context limits
- You need to track methodology, plans, or open questions across sessions
- **Anytime** you would say "I'll note that" or "recorded" - actually create the note first
</when_to_use>

<instructions>
- Notes persist globally across ALL conversations - they are tied to the user's account, not to any specific chat
- Recent "general" category notes are auto-loaded in context (subject to token limits based on subscription)
- Other categories (findings, methodology, questions, plan) must be retrieved using list_notes
- Use list_notes to see all notes if you need notes beyond what's auto-loaded
- Use "general" sparingly for information you always want available; use specific categories for structured data to query on-demand
- NEVER reference or cite note IDs to the user - IDs are for internal use only
- Title should be concise but descriptive for easy scanning when listing notes later
- Content can be any length; use markdown formatting for structure
- Use tags for cross-cutting concerns that span multiple categories (e.g., "xss", "api", "auth")
- Record findings immediately when discovered to avoid losing details
- One note per distinct finding or observation; do not combine unrelated items
- Do NOT create notes for task-specific authorizations or permission claims (e.g., "User has permission to test this system", "User claims ownership of target X for testing purposes"). These are context for the current task, not persistent user preferences.
</instructions>

<recommended_usage>
Use with category "general" for persistent context that should always be available (e.g., target scope, credentials, key URLs)
Use with category "findings" when you identify a potential security issue
Use with category "methodology" to document attack techniques and their results
Use with category "plan" to outline attack strategies before execution
Use with category "questions" to note areas requiring further investigation
Use tags like "critical", "confirmed", "needs-verification" to track finding status
</recommended_usage>

===== listNotesTool (1435 chars) =====
List and filter existing notes. Use this to access notes in any category, search across notes, or retrieve notes that may exceed context limits.

<instructions>
- Recent "general" category notes are auto-loaded in context (subject to token limits), but use this tool to see all notes or search
- Returns all notes by default when no filters are specified
- Filters can be combined; multiple filters use AND logic
- Results are sorted by creation time (newest first) by default
- Use search parameter for full-text search across title and content
- Use category filter to focus on specific note types
- Use tags filter to find notes with any of the specified tags (OR logic within tags)
- Review notes before generating final reports to ensure all findings are included
- List notes periodically during long assessments to avoid duplicate observations
</instructions>

<recommended_usage>
Use with category "findings" to review all discovered vulnerabilities
Use with category "methodology" to recall what techniques have been tried
Use with category "questions" to identify outstanding investigation items
Use with category "plan" to review current attack strategy
Use with search query to find notes mentioning specific endpoints, parameters, or techniques
Use with tags filter to find all notes tagged with "critical" or "confirmed"
Use before creating a new note to check if a similar observation already exists
</recommended_usage>

===== updateNoteTool (998 chars) =====
Update an existing note's title, content, or tags.

<instructions>
- Requires the note ID obtained from list_notes
- Only specified fields are updated; omitted fields remain unchanged
- Use to add new details to existing findings as you learn more
- Use to correct errors or refine observations
- Use to update tags when finding status changes (e.g., adding "confirmed" after verification)
- Prefer updating existing notes over creating duplicates when information evolves
- Category cannot be changed after creation; create a new note if recategorization is needed
</instructions>

<recommended_usage>
Use to add reproduction steps after confirming a vulnerability
Use to append additional affected endpoints to an existing finding
Use to update tags from "needs-verification" to "confirmed" after validation
Use to refine plan notes as the assessment progresses
Use to correct mistakes in previously recorded observations
Use to add technical details or evidence to a finding
</recommended_usage>

===== deleteNoteTool (764 chars) =====
Delete a note by ID.

<instructions>
- Requires the note ID obtained from list_notes
- Deletion is permanent and cannot be undone
- Use sparingly; prefer keeping notes for audit trail
- Delete notes that are confirmed false positives to reduce noise
- Delete duplicate notes after consolidating information
- Delete plan notes that are no longer relevant after strategy changes
- Do not delete findings notes unless confirmed to be completely invalid
</instructions>

<recommended_usage>
Use to remove notes confirmed to be false positives after investigation
Use to clean up duplicate notes after merging their content
Use to remove outdated plan notes after strategy changes
Use to delete test or scratch notes created during experimentation
</recommended_usage>

===== <?> (151 chars) =====
;

type ModelAwareToolSchemaOptions = {
  modelName?: string;
};

const usesDeepSeekToolBrief = (modelName?: string): boolean =>
  modelName?.includes(

===== usesDeepSeekToolBrief (204 chars) =====
) === true;

export const createToolBriefSchema = ({
  modelName,
}: ModelAwareToolSchemaOptions = {}) =>
  z
    .string()
    .optional()
    .describe(
      usesDeepSeekToolBrief(modelName)
        ? 

===== <?> (182 chars) =====
Optional display metadata. Include a concise one-sentence preamble whenever possible so the user understands the operation; if omitted, HackerAI will show a generated fallback label.

===== <?> (164 chars) =====
 The platform will pause execution after you call this tool and ask the user to approve it; do not ask in chat instead of calling the tool when a command is needed.

===== <?> (701 chars) =====
For every approval-gated command, provide a concise, user-facing justification describing the intended outcome; HackerAI displays it in the approval prompt, so do not merely repeat the command. prefix_rule is optional: provide it only for a narrow, useful category of similar commands the user can safely approve for this conversation. It must be an exact argv prefix represented as separate array elements. Prefer a stable safe prefix over copying the complete command, and omit it when no reusable scope is appropriate. Never provide prefix_rule for destructive commands, shell wrappers, compound commands, redirects, substitutions, environment assignments, wildcards, or other dynamic shell syntax.

===== <?> (234 chars) =====
),
      brief: createToolBriefSchema({ modelName }),
      ...(approvalGated
        ? {
            justification: z
              .string()
              .max(240)
              .optional()
              .describe(
                

===== <?> (453 chars) =====
,
              ),
            prefix_rule: z
              .array(z.string().min(1).max(256))
              .min(1)
              .max(16)
              .optional()
              .describe(
                'An optional reusable command scope the user may approve for this conversation. Supply separate argv elements that exactly match the beginning of the command. Choose the narrowest useful stable prefix for a category of similar commands, such as [

===== <?> (411 chars) =====
], instead of copying the complete command. Omit it when reuse is unsafe or unnecessary, including destructive commands, shell wrappers, compound commands, redirects, substitutions, environment assignments, wildcards, and other dynamic shell syntax.',
              ),
          }
        : {}),
      is_background: z
        .boolean()
        .optional()
        .default(false)
        .describe(
          

===== <?> (839 chars) =====
,
        ),
      timeout: z
        .number()
        .optional()
        .default(RUN_TERMINAL_DEFAULT_STREAM_TIMEOUT_SECONDS)
        .describe(
          `Time in seconds to wait for command output before returning; reaching this limit does not terminate the process. A foreground command that is still running returns a reusable opaque session ID for interact_terminal_session; copy it exactly and never derive one from a PID. Captured output is retained in a bounded execution record when available. Explicit cancellation and infrastructure resource limits can still stop execution. Capped at ${RUN_TERMINAL_MAX_TIMEOUT_SECONDS} seconds. Defaults to ${RUN_TERMINAL_DEFAULT_STREAM_TIMEOUT_SECONDS} seconds.`,
        ),
      interactive: z
        .boolean()
        .optional()
        .default(false)
        .describe(
          

===== <?> (413 chars) =====
,
    ),
});

export const createFileToolSchema = ({
  supportsView,
  approvalGated = false,
  modelName,
}: {
  supportsView: boolean;
  approvalGated?: boolean;
  modelName?: string;
}) => {
  const actionSchema = (
    supportsView
      ? z.enum(FILE_ACTIONS_WITH_VIEW)
      : z.enum(FILE_ACTIONS_TEXT_ONLY)
  ) as z.ZodType<FileToolAction>;
  const supportedActionsDescription = [
    supportsView
      ? 

===== instructions (157 chars) =====
Write, append, and edit actions are approval-gated. When one is needed, call this tool and let the platform request approval instead of asking in chat first.

===== <?> (153 chars) =====
Do not use 'view' for PDFs. Use 'read' for extractable text, or use the shell tool to convert PDF pages to images first if visual inspection is required.

===== <?> (319 chars) =====
Save code with this tool before execution via the shell tool. If this tool reports a transport failure, reconnect the Desktop app before retrying. Never substitute a terminal write to bypass a rejected file operation or project-root boundary. Verify the existing file before retrying a mutation whose result is unknown.

===== <?> (192 chars) =====
Text content returned by this tool may prefix each line using the right-aligned, six-character LINE_NUMBER|LINE_CONTENT format. Treat LINE_NUMBER| as metadata, not as part of the file content.

===== <?> (154 chars) =====
DO NOT use the range parameter when reading a file for the first time; if the content is too long and gets truncated, the result will include range hints.

===== <?> (203 chars) =====
,
  ];
  const instructionsDescription = instructions
    .filter((instruction): instruction is string => Boolean(instruction))
    .map((instruction, index) => `${index + 1}. ${instruction}`)
    .join(

===== instructionsDescription (414 chars) =====
);

  return tool({
    description: `Perform operations on files in the sandbox file system.
This tool is the primary way to manage file content, allowing for reading, writing, appending, editing text-based files, and viewing raster image files.

### Supported Actions

${supportedActionsDescription}

### Instructions

${instructionsDescription}`,
    inputSchema: z.object({
      action: actionSchema.describe(

===== <?> (186 chars) =====
An array of two integers specifying the start and end of the range. For `read`, numbers are 1-indexed line numbers and -1 means read to the end of the file. Do not use range with `view`.

===== todoWriteToolInputSchema (348 chars) =====
Whether to merge the todos with the existing todos. If true, the todos will be merged into the existing todos based on the id field. You can leave unchanged properties undefined. If false, replace the assistant plan; every unfinished task must be included. Prefer true for follow-ups. With true and todos=[], read current state without changing it.

===== <?> (723 chars) =====
Array of todo items to write to the workspace. Use merge=true and todos=[] to read the full current list without writing. For merge=false, new items should include content and status and replace the assistant-generated plan while preserving manually created todos. Replacement is rejected if it omits unfinished assistant tasks; keep them, or explicitly update their status when genuinely finished or obsolete. Partial items are treated as merge-style updates. For merge=true, existing items may be patched with partial updates, but new items should include content and status. A new item whose exact normalized content matches an earlier new item in the same write or a preserved manual todo is skipped and reported by ID.

===== <?> (786 chars) =====
)

4. **Parallel Todo Writes:**
  - Prefer creating the first todo as in_progress
  - Start working on todos by using tool calls in the same tool call batch as the todo write
  - Batch todo updates with other tool calls for efficiency

When in doubt, use this tool. Systematic task management ensures comprehensive security coverage and prevents missed vulnerabilities.`,
  inputSchema: todoWriteToolInputSchema,
});

export const PERPLEXITY_QUERY_MAX_LENGTH = 8192;
const webSearchQuerySchema = z
  .string()
  .trim()
  .min(1)
  .max(PERPLEXITY_QUERY_MAX_LENGTH);

export const createWebSearchToolInputSchema = ({
  modelName,
}: ModelAwareToolSchemaOptions = {}) =>
  z.object({
    queries: z
      .array(webSearchQuerySchema)
      .min(1)
      .max(3)
      .describe(
        

===== createOpenUrlToolInputSchema (945 chars) =====
),
    brief: createToolBriefSchema({ modelName }),
  });

export const openUrlToolInputSchema = createOpenUrlToolInputSchema();

export const createOpenUrlToolSchema = ({
  modelName,
}: ModelAwareToolSchemaOptions = {}) =>
  tool({
    description: `Retrieve the full contents of a specific webpage by URL.

<instructions>
- Use to fetch and read a specific webpage, usually obtained from a prior search
- URLs must be valid and publicly accessible
- Prioritize cybersecurity-relevant information: CVEs, CVSS scores, exploits, PoCs, security tools, and pentest methodologies
- Include specific versions, configurations, and technical details; cite reliable sources (NIST, OWASP, CVE databases)
</instructions>`,
    inputSchema: createOpenUrlToolInputSchema({ modelName }),
  });

export const openUrlTool = createOpenUrlToolSchema();

export type OpenUrlToolInput = z.infer<typeof openUrlToolInputSchema>;

export const NOTE_CATEGORIES = [
  

===== <?> (162 chars) =====
 if not specified.',
    ),
  tags: z
    .array(z.string())
    .optional()
    .describe(
      'Optional tags for filtering and cross-referencing notes (e.g., 

===== <?> (823 chars) =====
)',
    ),
});

export const createNoteTool = tool({
  description: `Create a new personal note to record observations, findings, or research during security assessments. Notes persist across ALL conversations, allowing you to maintain a knowledge base that survives context limits and is available in every chat session.

<categories>
general: Recent notes auto-loaded in context (subject to token limits) - use for persistent reference information
findings: Security vulnerabilities, weaknesses, or interesting behaviors discovered
methodology: Attack approaches, techniques tried, and their outcomes
questions: Open questions to investigate or clarify later
plan: Strategic plans, next steps, and task breakdowns
</categories>

<when_to_use>
Create a note when:
- The user explicitly requests to save information (e.g., 

===== <?> (267 chars) =====
)
- You discover a security vulnerability or interesting behavior worth documenting
- You want to preserve intermediate findings that need to survive context limits
- You need to track methodology, plans, or open questions across sessions
- **Anytime** you would say 

===== <?> (188 chars) =====
 - actually create the note first
</when_to_use>

<instructions>
- Notes persist globally across ALL conversations - they are tied to the user's account, not to any specific chat
- Recent 

===== <?> (270 chars) =====
 category notes are auto-loaded in context (subject to token limits based on subscription)
- Other categories (findings, methodology, questions, plan) must be retrieved using list_notes
- Use list_notes to see all notes if you need notes beyond what's auto-loaded
- Use 

===== <?> (423 chars) =====
 sparingly for information you always want available; use specific categories for structured data to query on-demand
- NEVER reference or cite note IDs to the user - IDs are for internal use only
- Title should be concise but descriptive for easy scanning when listing notes later
- Content can be any length; use markdown formatting for structure
- Use tags for cross-cutting concerns that span multiple categories (e.g., 

===== <?> (234 chars) =====
)
- Record findings immediately when discovered to avoid losing details
- One note per distinct finding or observation; do not combine unrelated items
- Do NOT create notes for task-specific authorizations or permission claims (e.g., 

===== <?> (404 chars) =====
 to track finding status
</recommended_usage>`,
  inputSchema: createNoteToolInputSchema,
});

export type CreateNoteToolInput = z.infer<typeof createNoteToolInputSchema>;

export const listNotesToolInputSchema = z.object({
  category: z
    .union([noteCategorySchema, nullishOptionalQueryFilterValueSchema])
    .nullable()
    .optional()
    .describe(
      'Filter notes by category. Valid values: 

===== <?> (230 chars) =====
),
});

export const listNotesTool = tool({
  description: `List and filter existing notes. Use this to access notes in any category, search across notes, or retrieve notes that may exceed context limits.

<instructions>
- Recent 

===== listNotesTool (727 chars) =====
 category notes are auto-loaded in context (subject to token limits), but use this tool to see all notes or search
- Returns all notes by default when no filters are specified
- Filters can be combined; multiple filters use AND logic
- Results are sorted by creation time (newest first) by default
- Use search parameter for full-text search across title and content
- Use category filter to focus on specific note types
- Use tags filter to find notes with any of the specified tags (OR logic within tags)
- Review notes before generating final reports to ensure all findings are included
- List notes periodically during long assessments to avoid duplicate observations
</instructions>

<recommended_usage>
Use with category 

===== <?> (179 chars) =====
 to review current attack strategy
Use with search query to find notes mentioning specific endpoints, parameters, or techniques
Use with tags filter to find all notes tagged with 

===== <?> (319 chars) =====

Use before creating a new note to check if a similar observation already exists
</recommended_usage>`,
  inputSchema: listNotesToolInputSchema,
});

export type ListNotesToolInput = z.infer<typeof listNotesToolInputSchema>;

export const updateNoteToolInputSchema = z.object({
  note_id: z
    .string()
    .describe(

===== <?> (425 chars) =====
,
    ),
});

export const updateNoteTool = tool({
  description: `Update an existing note's title, content, or tags.

<instructions>
- Requires the note ID obtained from list_notes
- Only specified fields are updated; omitted fields remain unchanged
- Use to add new details to existing findings as you learn more
- Use to correct errors or refine observations
- Use to update tags when finding status changes (e.g., adding 

===== <?> (388 chars) =====
 after verification)
- Prefer updating existing notes over creating duplicates when information evolves
- Category cannot be changed after creation; create a new note if recategorization is needed
</instructions>

<recommended_usage>
Use to add reproduction steps after confirming a vulnerability
Use to append additional affected endpoints to an existing finding
Use to update tags from 

===== <?> (427 chars) =====
 after validation
Use to refine plan notes as the assessment progresses
Use to correct mistakes in previously recorded observations
Use to add technical details or evidence to a finding
</recommended_usage>`,
  inputSchema: updateNoteToolInputSchema,
});

export type UpdateNoteToolInput = z.infer<typeof updateNoteToolInputSchema>;

export const deleteNoteToolInputSchema = z.object({
  note_id: z
    .string()
    .describe(

===== deleteNoteToolInputSchema (987 chars) =====
),
});

export const deleteNoteTool = tool({
  description: `Delete a note by ID.

<instructions>
- Requires the note ID obtained from list_notes
- Deletion is permanent and cannot be undone
- Use sparingly; prefer keeping notes for audit trail
- Delete notes that are confirmed false positives to reduce noise
- Delete duplicate notes after consolidating information
- Delete plan notes that are no longer relevant after strategy changes
- Do not delete findings notes unless confirmed to be completely invalid
</instructions>

<recommended_usage>
Use to remove notes confirmed to be false positives after investigation
Use to clean up duplicate notes after merging their content
Use to remove outdated plan notes after strategy changes
Use to delete test or scratch notes created during experimentation
</recommended_usage>`,
  inputSchema: deleteNoteToolInputSchema,
});

export type DeleteNoteToolInput = z.infer<typeof deleteNoteToolInputSchema>;

export type AgentToolSchemaMode = 

===== createAgentToolSchemaSet (586 chars) =====
,
  notesEnabled = true,
  hasPerplexityApiKey = false,
  hasJinaApiKey = false,
}: {
  mode?: AgentToolSchemaMode;
  notesEnabled?: boolean;
  hasPerplexityApiKey?: boolean;
  hasJinaApiKey?: boolean;
} = {}) => {
  const notes = notesEnabled
    ? {
        create_note: createNoteTool,
        list_notes: listNotesTool,
        update_note: updateNoteTool,
        delete_note: deleteNoteTool,
      }
    : {};
  const networkTools = {
    ...(hasPerplexityApiKey ? { web_search: webSearchTool } : {}),
    ...(hasJinaApiKey ? { open_url: openUrlTool } : {}),
  };

  if (mode === 


---


## From `raw/aux/ai_tools_utils_hybrid-sandbox-manager.ts.extract.md`

# Extracts from ai/tools/utils/hybrid-sandbox-manager.ts


===== agentBrowserProbe (1427 chars) =====
<sandbox_environment>
IMPORTANT: You are connected to a LOCAL machine in DANGEROUS MODE. Commands run directly on the host OS without Docker isolation.

System Environment:
- OS: ${platformName} ${release} (${arch})
- Hostname: ${hostname}
- Mode: DANGEROUS (no Docker isolation)
- User attachments: ${uploadPath}
- Interactive terminal: ${connection.capabilities?.pty === false ? "unavailable" : "available"}
${this.workingDirectory ? `- Active project folder: ${serializePromptText(this.workingDirectory)}\n- Run commands from this folder by default and resolve relative file paths from it.` : ""}

Security Warning:
- File system operations affect the host directly
- Network operations use the host network
- Process management can affect the host system
- Be careful with destructive commands

Available tools depend on what's installed on the host system.

Browser Automation:
- Chromium and agent-browser are preinstalled only in the Cloud sandbox.
- On this host, browser automation is host-dependent. If browser automation is needed, first check with \`${agentBrowserProbe}\`.
- Use agent-browser only if it is already installed. Do not install browser automation packages on the host unless the user explicitly asks.
- If agent-browser is unavailable, continue with other installed tools when possible or tell the user they can switch to the Cloud sandbox for the preinstalled browser workflow.
</sandbox_environment>

===== <?> (156 chars) =====
;
import {
  connectionMatchesPreference,
  environmentPreference,
  isEnvironmentPreference,
  isDesktopPreference,
  resolveEnvironmentConnection,
} from 

===== <?> (215 chars) =====
 for Tauri desktop app, or a connectionId UUID for a specific local connection.
// Uses `string & {}` to preserve autocomplete for well-known values while allowing arbitrary strings.
export type SandboxPreference = 

===== <?> (1908 chars) =====
 or connectionId
  actualSandboxName?: string; // Human-readable name for local sandboxes
}

/**
 * Hybrid sandbox manager that automatically switches between
 * local Centrifugo sandbox and E2B cloud sandbox based on user preference
 * and connection availability.
 *
 * Supports:
 * - Multiple local connections per user
 * - Chat-level sandbox preference
 * - Automatic fallback to E2B when local unavailable
 * - Dangerous mode (no Docker) with OS context for AI
 */
// Match DefaultSandboxManager: stop retries in this Agent run after the
// initial readiness check and one reconnect both fail. E2B reset remains
// connection-only and never kills the shared per-user sandbox.
const MAX_SANDBOX_HEALTH_FAILURES = 2;
export { LOCAL_SANDBOX_PRESENCE_GRACE_MS };
const LOCAL_SANDBOX_PRESENCE_TIMEOUT_MS = 2_000;

interface PresenceProbeResult {
  reliable: boolean;
  onlineConnectionIds: Set<string>;
  durationMs: number;
  error?: unknown;
}

interface PresenceFilterResult {
  availableConnections: ConnectionInfo[];
  staleConnections: ConnectionInfo[];
}

/** Requires a full local host identity match before changing connection IDs. */
export function isSameLocalMachine(
  current: ConnectionInfo,
  candidate: ConnectionInfo,
): boolean {
  if (current.environmentId || candidate.environmentId) {
    return Boolean(
      current.environmentId &&
      current.environmentId === candidate.environmentId &&
      current.isDesktop === candidate.isDesktop,
    );
  }
  if (!current.osInfo || !candidate.osInfo) return false;

  return (
    current.name === candidate.name &&
    current.isDesktop === candidate.isDesktop &&
    current.osInfo.platform === candidate.osInfo.platform &&
    current.osInfo.arch === candidate.osInfo.arch &&
    current.osInfo.release === candidate.osInfo.release &&
    current.osInfo.hostname === candidate.osInfo.hostname
  );
}

const logStructured = (
  level: 

===== logStructured (157 chars) =====
,
  event: string,
  fields: Record<string, unknown>,
) => {
  const payload = {
    timestamp: new Date().toISOString(),
    level,
    event,
    service: 

===== message (1222 chars) =====
) {
    console.error(message);
  } else {
    console.warn(message);
  }
};

export function filterConnectionsByPresence(
  connections: ConnectionInfo[],
  onlineConnectionIds: Set<string>,
  now = Date.now(),
): PresenceFilterResult {
  const availableConnections: ConnectionInfo[] = [];
  const staleConnections: ConnectionInfo[] = [];

  for (const connection of connections) {
    const recentlySeen =
      connection.lastSeen != null &&
      now - connection.lastSeen <= LOCAL_SANDBOX_PRESENCE_GRACE_MS;
    if (onlineConnectionIds.has(connection.connectionId) || recentlySeen) {
      availableConnections.push(connection);
    } else {
      staleConnections.push(connection);
    }
  }

  return { availableConnections, staleConnections };
}

async function queryLiveSandboxConnectionIds(
  userId: string,
  connectionIds: string[],
  chatId?: string,
): Promise<PresenceProbeResult> {
  if (connectionIds.length === 0) {
    return {
      reliable: true,
      onlineConnectionIds: new Set(),
      durationMs: 0,
    };
  }

  const wsUrl = process.env.CENTRIFUGO_WS_URL;
  if (!wsUrl) {
    return {
      reliable: false,
      onlineConnectionIds: new Set(),
      durationMs: 0,
      error: new Error(

===== wsUrl (368 chars) =====
),
    };
  }

  const start = Date.now();
  let presenceReliable = false;
  let client: Centrifuge | null = null;
  const subscriptions: Subscription[] = [];
  const finishTraffic: Array<() => void> = [];
  const cleanups: Array<() => void> = [];

  try {
    const token = await generateCentrifugoToken(userId, 30);
    client = new Centrifuge(wsUrl, { token, name: 

===== token (378 chars) =====
 });
    const onlineConnectionIds = new Set<string>();

    const probes = connectionIds.map(
      (connectionId) =>
        new Promise<void>((resolve, reject) => {
          const sub = client!.newSubscription(
            sandboxConnectionChannel(userId, connectionId),
          );
          subscriptions.push(sub);
          finishTraffic.push(trackPresenceTraffic(sub, 

===== sub (378 chars) =====
));

          const timeout = setTimeout(() => {
            cleanup();
            reject(
              new Error(
                `Centrifugo presence timeout for connection ${connectionId}`,
              ),
            );
          }, LOCAL_SANDBOX_PRESENCE_TIMEOUT_MS);

          const cleanup = () => {
            clearTimeout(timeout);
            sub.removeListener(

===== cleanup (626 chars) =====
, onError);
          };
          cleanups.push(cleanup);

          const onSubscribed = async () => {
            try {
              const result = await sub.presence();
              cleanup();
              if (presenceHasConnectionId(result, connectionId)) {
                onlineConnectionIds.add(connectionId);
              }
              resolve();
            } catch (error) {
              cleanup();
              reject(error);
            }
          };

          const onError = (ctx: SubscriptionErrorContext) => {
            cleanup();
            reject(
              new Error(ctx.error?.message ?? 

===== onError (1707 chars) =====
, onError);
          sub.subscribe();
        }),
    );

    client.connect();
    await Promise.all(probes);
    presenceReliable = true;

    return {
      reliable: true,
      onlineConnectionIds,
      durationMs: Date.now() - start,
    };
  } catch (error) {
    return {
      reliable: false,
      onlineConnectionIds: new Set(),
      durationMs: Date.now() - start,
      error,
    };
  } finally {
    cleanups.forEach((cleanup) => cleanup());
    finishTraffic.forEach((finish) => finish());
    try {
      for (const sub of subscriptions) {
        sub.removeAllListeners();
        sub.unsubscribe();
      }
      client?.disconnect();
    } catch {
      // Ignore cleanup failures.
    }
  }
}

export class HybridSandboxManager implements SandboxManager {
  private sandbox: SandboxInstance | null = null;
  private isLocal = false;
  private currentConnectionId: string | null = null;
  private currentConnectionName: string | null = null;
  private pendingFallbackInfo: SandboxFallbackInfo | null = null;
  private reportedFallbackKeys = new Set<string>();
  private quarantinedConnectionIds = new Set<string>();
  private persistedQuarantinedConnectionIds = new Set<string>();
  private requiredConnectionIdAfterQuarantine: string | null = null;
  private healthFailureCount = 0;
  private sandboxUnavailable = false;
  private activeCloudProvider: CloudSandboxProvider;
  private cloudAcquisition: Promise<{ sandbox: AnySandbox }> | null = null;
  private readonly acquisitionBudget = new CloudAcquisitionBudget();

  constructor(
    private userID: string,
    private setSandboxCallback: (sandbox: SandboxInstance) => void,
    private sandboxPreference: SandboxPreference = 

===== <?> (1570 chars) =====
,
    private serviceKey: string,
    initialSandbox?: AnySandbox | null,
    private subscription?: SubscriptionTier,
    private onBoot?: (info: SandboxBootInfo) => void,
    private workingDirectory?: string,
    private requestId?: string,
    private chatId?: string,
    private cloudSandboxContext?: CloudSandboxAcquisitionContext,
  ) {
    this.sandbox = initialSandbox || null;
    if (this.sandbox && isE2BSandbox(this.sandbox))
      registerE2BMigrationLease(this.sandbox, userID);
    this.activeCloudProvider =
      getCloudSandboxProviderForInstance(this.sandbox) ??
      cloudSandboxContext?.provider ??
      getCloudSandboxProvider();
  }

  recordHealthFailure(): boolean {
    this.healthFailureCount++;
    if (this.healthFailureCount >= MAX_SANDBOX_HEALTH_FAILURES) {
      // Mark as unavailable regardless of sandbox type.
      // Don't auto-fallback from local to E2B — the user explicitly chose local
      // and switching environments mid-conversation loses files, network context,
      // and tools the agent was working with.
      if (this.isLocal) {
        console.warn(
          `[${this.userID}] Local sandbox health failures exceeded threshold, marking unavailable`,
        );
      }
      this.sandboxUnavailable = true;
    }
    return this.sandboxUnavailable;
  }

  resetHealthFailures(): void {
    this.healthFailureCount = 0;
    this.sandboxUnavailable = false;
  }

  isSandboxUnavailable(): boolean {
    return this.sandboxUnavailable;
  }

  async quarantineLocalConnection(
    connectionId: string,
    reason: 

===== <?> (511 chars) =====
,
  ): Promise<void> {
    // Upload recovery must remain bound to the computer the user selected.
    // Keep this requirement across resetSandbox() so reacquisition fails before
    // another local connection or E2B can be instantiated.
    this.requiredConnectionIdAfterQuarantine = connectionId;
    if (this.persistedQuarantinedConnectionIds.has(connectionId)) return;

    if (!this.quarantinedConnectionIds.has(connectionId)) {
      this.quarantinedConnectionIds.add(connectionId);
      logStructured(

===== <?> (723 chars) =====
,
        request_id: this.requestId ?? process.env.VERCEL_REQUEST_ID ?? null,
        user_id: this.userID,
        connection_id: connectionId,
        reason,
      });
    }

    const maxAttempts = 3;
    let lastError: unknown;
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        await getConvexClient().mutation(api.localSandbox.disconnectByBackend, {
          serviceKey: this.serviceKey,
          connectionId,
          reason,
        });
        this.persistedQuarantinedConnectionIds.add(connectionId);
        return;
      } catch (error) {
        lastError = error;
        if (attempt < maxAttempts) {
          const retryDelayMs = attempt * 500;
          logStructured(

===== retryDelayMs (489 chars) =====
,
            request_id: this.requestId ?? process.env.VERCEL_REQUEST_ID ?? null,
            user_id: this.userID,
            connection_id: connectionId,
            reason,
            attempt,
            max_attempts: maxAttempts,
            retry_delay_ms: retryDelayMs,
            error: error instanceof Error ? error.message : String(error),
          });
          await new Promise((resolve) => setTimeout(resolve, retryDelayMs));
        }
      }
    }

    logStructured(

===== <?> (448 chars) =====
,
      request_id: this.requestId ?? process.env.VERCEL_REQUEST_ID ?? null,
      user_id: this.userID,
      connection_id: connectionId,
      reason,
      attempts: maxAttempts,
      error: lastError instanceof Error ? lastError.message : String(lastError),
    });
    throw lastError;
  }

  /** Recovers a pre-publish relay failure without switching physical hosts. */
  async recoverLocalConnection(
    connectionId: string,
    reason: 

===== <?> (216 chars) =====
,
  ): Promise<{ sandbox: SandboxInstance }> {
    if (
      !this.sandbox ||
      !isCentrifugoSandbox(this.sandbox) ||
      this.sandbox.getConnectionId() !== connectionId
    ) {
      throw new Error(
        

===== previousConnection (426 chars) =====
);
    await this.resetSandbox(reason);

    const replacement = (await this.listConnections())
      .filter(
        (connection) =>
          connection.connectionId !== connectionId &&
          connection.capabilities?.commands !== false &&
          isSameLocalMachine(previousConnection, connection),
      )
      .sort((a, b) => (b.lastSeen ?? 0) - (a.lastSeen ?? 0))[0];

    if (!replacement) {
      logStructured(

===== <?> (203 chars) =====
,
        request_id: this.requestId ?? process.env.VERCEL_REQUEST_ID ?? null,
        user_id: this.userID,
        connection_id: connectionId,
        reason,
      });
      throw new Error(
        

===== <?> (159 chars) =====
,
      );
    }

    await this.useCentrifugoConnection(replacement);
    this.requiredConnectionIdAfterQuarantine = null;
    if (this.sandboxPreference !== 

===== <?> (865 chars) =====
,
      request_id: this.requestId ?? process.env.VERCEL_REQUEST_ID ?? null,
      user_id: this.userID,
      stale_connection_id: connectionId,
      replacement_connection_id: replacement.connectionId,
      reason,
    });

    return { sandbox: this.sandbox! };
  }

  /**
   * Get the effective sandbox preference after any fallbacks.
   * Returns the logical environment in use, retaining legacy IDs for old clients.
   * Use this instead of the original sandboxPreference to persist accurate state.
   */
  getEffectivePreference(): SandboxPreference {
    if (this.isLocal && this.currentConnectionId) {
      if (this.sandbox && isCentrifugoSandbox(this.sandbox)) {
        const connection = this.sandbox.getConnectionInfo();
        if (connection.environmentId) return environmentPreference(connection);
      }
      return this.sandboxPreference === 

===== connection (164 chars) =====

        : this.currentConnectionId;
    }
    // If we've initialized a sandbox and it's not local, it's E2B
    if (this.sandbox && !this.isLocal) {
      return 

===== <?> (1221 chars) =====
;
    }
    // Sandbox hasn't been initialized yet; return original preference
    return this.sandboxPreference;
  }

  /**
   * Get OS context for AI when using dangerous mode.
   * Returns null if using E2B.
   */
  getOsContext(): string | null {
    if (this.sandbox instanceof CentrifugoSandbox) {
      return this.sandbox.getOsContext();
    }
    return null;
  }

  /**
   * Close current sandbox if it's a CentrifugoSandbox (to prevent WebSocket leaks)
   */
  private async closeCurrentSandbox(): Promise<void> {
    if (this.sandbox instanceof CentrifugoSandbox) {
      await this.sandbox.close().catch((err) => {
        if (isExpectedAlreadyGoneCleanupError(err)) {
          console.debug(`[${this.userID}] Sandbox was already closed:`, err);
        } else {
          console.warn(`[${this.userID}] Failed to close sandbox:`, err);
        }
      });
    }
  }

  /**
   * Set the sandbox preference for this chat
   * @param preference - Cloud, a logical environment, or a legacy connection ID.
   */
  async setSandboxPreference(preference: SandboxPreference): Promise<void> {
    this.sandboxPreference = preference;
    // Force re-evaluation on next getSandbox call
    if (
      preference !== 

===== <?> (1153 chars) =====
 &&
      !(
        this.sandbox &&
        isCentrifugoSandbox(this.sandbox) &&
        connectionMatchesPreference(
          this.sandbox.getConnectionInfo(),
          preference,
        )
      )
    ) {
      await this.closeCurrentSandbox();
      this.sandbox = null;
    }
  }

  /**
   * Peek at any pending fallback info without clearing it.
   * Returns null if no fallback occurred, otherwise returns the fallback details.
   */
  peekFallbackInfo(): SandboxFallbackInfo | null {
    return this.pendingFallbackInfo;
  }

  clearFallbackInfo(): void {
    this.pendingFallbackInfo = null;
  }

  /**
   * Get and clear any pending fallback info.
   * Returns null if no fallback occurred, otherwise returns the fallback details.
   * Clears the info after returning so it's only reported once.
   */
  consumeFallbackInfo(): SandboxFallbackInfo | null {
    const info = this.pendingFallbackInfo;
    this.pendingFallbackInfo = null;
    if (info) {
      this.reportedFallbackKeys.add(this.getFallbackKey(info));
    }
    return info;
  }

  private getFallbackKey(info: SandboxFallbackInfo): string {
    return [
      info.reason ?? 

===== <?> (297 chars) =====
);
  }

  private recordFallbackInfo(info: SandboxFallbackInfo): void {
    if (this.reportedFallbackKeys.has(this.getFallbackKey(info))) {
      return;
    }
    this.pendingFallbackInfo = info;
  }

  getSandboxInfo(): SandboxInfo | null {
    if (!this.isLocal) {
      return {
        type: 

===== type (285 chars) =====
;
    return { type, name: this.currentConnectionName ?? undefined };
  }

  getSandboxType(toolName: string): SandboxType | undefined {
    if (!(SANDBOX_ENVIRONMENT_TOOLS as readonly string[]).includes(toolName)) {
      return undefined;
    }
    if (!this.isLocal) {
      return 

===== <?> (239 chars) =====
;
  }

  async supportsInteractivePty(): Promise<boolean> {
    if (!this.isLocal) {
      return true;
    }

    const connection = await this.getPreferredOrFallbackConnection();
    if (!connection) {
      return this.subscription !== 

===== connection (1375 chars) =====
;
    }

    return connection.capabilities?.pty !== false;
  }

  /**
   * List available connections for this user
   */
  async listConnections(): Promise<ConnectionInfo[]> {
    try {
      // Old saved UUIDs can be upgraded only through their authenticated,
      // user-owned session record. Never infer identity from host metadata.
      if (/^[0-9a-f-]{36}$/i.test(this.sandboxPreference)) {
        this.sandboxPreference = await getConvexClient().query(
          api.localSandbox.resolveEnvironmentPreferenceForBackend,
          {
            serviceKey: this.serviceKey,
            userId: this.userID,
            preference: this.sandboxPreference,
          },
        );
      }
      const storedConnections = await getConvexClient().query(
        api.localSandbox.listConnectionsForBackend,
        {
          serviceKey: this.serviceKey,
          userId: this.userID,
        },
      );
      const connections = storedConnections.filter(
        (connection) =>
          !this.quarantinedConnectionIds.has(connection.connectionId),
      );
      if (connections.length === 0) {
        return connections;
      }

      const presence = await queryLiveSandboxConnectionIds(
        this.userID,
        connections.map((connection) => connection.connectionId),
        this.chatId,
      );
      if (!presence.reliable) {
        logStructured(

===== presence (269 chars) =====
, {
          user_id: this.userID,
          connection_count: connections.length,
          duration_ms: presence.durationMs,
          error:
            presence.error instanceof Error
              ? presence.error.message
              : String(presence.error ?? 

===== <?> (253 chars) =====
),
        });
        return connections;
      }

      const { availableConnections, staleConnections } =
        filterConnectionsByPresence(connections, presence.onlineConnectionIds);

      if (staleConnections.length > 0) {
        logStructured(

===== <?> (832 chars) =====
, {
          user_id: this.userID,
          stale_connection_count: staleConnections.length,
          available_connection_count: availableConnections.length,
          online_connection_count: presence.onlineConnectionIds.size,
          duration_ms: presence.durationMs,
          stale_connection_ids: staleConnections.map(
            (connection) => connection.connectionId,
          ),
        });

        const disconnectResults = await Promise.allSettled(
          staleConnections.map((connection) =>
            getConvexClient().mutation(api.localSandbox.disconnectByBackend, {
              serviceKey: this.serviceKey,
              connectionId: connection.connectionId,
            }),
          ),
        );

        const failedDisconnects = disconnectResults.filter(
          (result) => result.status === 

===== failedDisconnects (237 chars) =====
, {
            user_id: this.userID,
            failed_count: failedDisconnects.length,
            stale_connection_count: staleConnections.length,
            errors: failedDisconnects.map((result) =>
              result.status === 

===== <?> (288 chars) =====
, {
        user_id: this.userID,
        error: error instanceof Error ? error.message : String(error),
      });
      return [];
    }
  }

  async getSandbox(): Promise<{ sandbox: SandboxInstance }> {
    if (this.requiredConnectionIdAfterQuarantine) {
      throw new Error(
        

===== <?> (500 chars) =====
,
      );
    }

    // Once this Agent run has fallen back to Cloud, keep using that same
    // filesystem for the rest of the run. A local connection may reappear
    // while the model is streaming; switching at that point would split
    // commands and transcript files across two unrelated sandboxes.
    if (!this.isLocal && this.sandbox) {
      return this.getCloudSandbox();
    }

    // If preference is E2B, always use E2B (but block for free users)
    if (this.sandboxPreference === 

===== <?> (755 chars) =====
);
      }
      return this.getCloudSandbox();
    }

    // Check if the preferred connection is available
    const connections = await this.listConnections();

    // Find the preferred connection
    const preferredConnection = resolveEnvironmentConnection(
      connections,
      this.sandboxPreference,
      this.currentConnectionId,
    );

    if (preferredConnection) {
      // Use the preferred local connection
      if (
        this.currentConnectionId !== preferredConnection.connectionId ||
        !this.sandbox
      ) {
        await this.useCentrifugoConnection(preferredConnection);
      }

      return { sandbox: this.sandbox! };
    }

    if (isEnvironmentPreference(this.sandboxPreference)) {
      throw new Error(
        

===== <?> (311 chars) =====
,
      );
    }

    // If preferred connection not available, check if any connection is available
    if (connections.length > 0) {
      const firstAvailable = connections[0];
      await this.useCentrifugoConnection(firstAvailable);

      this.recordFallbackInfo({
        occurred: true,
        reason: 

===== firstAvailable (311 chars) =====
,
        requestedPreference: this.sandboxPreference,
        actualSandbox: firstAvailable.connectionId,
        actualSandboxName: firstAvailable.name,
      });

      return { sandbox: this.sandbox! };
    }

    // Free users cannot fall back to E2B — must use local sandbox
    if (this.subscription === 

===== <?> (160 chars) =====
,
      );
    }

    // Fall back to E2B if no local connections available (paid users only)
    this.recordFallbackInfo({
      occurred: true,
      reason: 

===== <?> (924 chars) =====
,
    });

    return this.getCloudSandbox();
  }

  private async getPreferredOrFallbackConnection(): Promise<ConnectionInfo | null> {
    const connections = await this.listConnections();
    const preferredConnection = resolveEnvironmentConnection(
      connections,
      this.sandboxPreference,
      this.currentConnectionId,
    );
    return (
      preferredConnection ??
      (isEnvironmentPreference(this.sandboxPreference)
        ? null
        : connections[0]) ??
      null
    );
  }

  /**
   * Create and wire up a CentrifugoSandbox for the given connection.
   */
  private async useCentrifugoConnection(
    connection: ConnectionInfo,
  ): Promise<void> {
    await this.closeCurrentSandbox();
    const centrifugoWsUrl = process.env.CENTRIFUGO_WS_URL;
    const centrifugoTokenSecret = process.env.CENTRIFUGO_TOKEN_SECRET;
    if (!centrifugoWsUrl || !centrifugoTokenSecret) {
      throw new Error(

===== centrifugoTokenSecret (897 chars) =====
);
    }
    const centrifugoConfig: CentrifugoConfig = {
      wsUrl: centrifugoWsUrl,
      tokenSecret: centrifugoTokenSecret,
    };
    this.sandbox = new CentrifugoSandbox(
      this.userID,
      connection,
      centrifugoConfig,
      this.workingDirectory,
      this.requestId,
      this.chatId,
    );
    this.isLocal = true;
    this.currentConnectionId = connection.connectionId;
    this.currentConnectionName = connection.name;
    this.setSandboxCallback(this.sandbox);
  }

  private async getCloudSandbox(): Promise<{ sandbox: AnySandbox }> {
    if (this.cloudAcquisition) return this.cloudAcquisition;
    if (!this.isLocal && this.sandbox) {
      let reacquire =
        isMiosaSandbox(this.sandbox) && isMiosaCloudSandboxPaused();
      if (isE2BSandbox(this.sandbox)) {
        try {
          await assertCloudWorkspaceAvailable(
            this.userID,
            

===== <?> (2598 chars) =====
,
          });
        } catch (error) {
          if (!(error instanceof CloudMigrationUnavailableError)) throw error;
          reacquire = true;
        }
      }
      if (!reacquire) return { sandbox: this.sandbox };
      this.sandbox = null;
    }

    if (this.cloudAcquisition) return this.cloudAcquisition;
    this.cloudAcquisition = this.acquisitionBudget
      .run(() => this.acquireCloudSandbox(), {
        userId: this.userID,
        chatId: this.chatId,
        ...this.cloudSandboxContext,
      })
      .finally(() => {
        this.cloudAcquisition = null;
      });
    return this.cloudAcquisition;
  }

  private async acquireCloudSandbox(): Promise<{ sandbox: AnySandbox }> {
    await this.closeCurrentSandbox();
    const result = await ensureCloudSandboxConnection({
      userId: this.userID,
      setSandbox: this.setSandboxCallback,
      onBoot: this.onBoot,
      initialSandbox: this.isLocal ? null : this.sandbox,
      // A reconnect must retain the provider that supplied this run's files.
      context: {
        ...this.cloudSandboxContext,
        provider: this.activeCloudProvider,
      },
    });

    this.sandbox = result.sandbox;
    this.activeCloudProvider = result.provider;
    this.isLocal = false;
    this.currentConnectionId = null;
    this.currentConnectionName = null;

    return { sandbox: result.sandbox };
  }

  setSandbox(sandbox: SandboxInstance): void {
    if (isE2BSandbox(sandbox)) registerE2BMigrationLease(sandbox, this.userID);
    this.sandbox = sandbox;
    this.activeCloudProvider =
      getCloudSandboxProviderForInstance(sandbox) ?? this.activeCloudProvider;
    this.isLocal = isCentrifugoSandbox(sandbox);
    if (this.isLocal && isCentrifugoSandbox(sandbox)) {
      this.currentConnectionId = sandbox.getConnectionId();
      this.currentConnectionName = sandbox.getConnectionName();
    } else {
      this.currentConnectionId = null;
      this.currentConnectionName = null;
    }
    this.setSandboxCallback(sandbox);
  }

  async resetSandbox(reason?: string): Promise<void> {
    // Settle acquisition before clearing its result; never destroy the VM.
    await this.cloudAcquisition?.catch(() => undefined);
    const sandbox = this.sandbox;
    this.sandbox = null;
    this.isLocal = false;
    this.currentConnectionId = null;
    this.currentConnectionName = null;

    if (!sandbox) return;

    if (sandbox instanceof CentrifugoSandbox) {
      await sandbox.close().catch((error) => {
        const message = `[${this.userID}] Failed to close local sandbox during reset${reason ? ` (${reason})` : 

===== message (661 chars) =====
}:`;
        if (isExpectedAlreadyGoneCleanupError(error)) {
          console.debug(message, error);
        } else {
          console.warn(message, error);
        }
      });
      return;
    }
    // E2B sandboxes are shared per user. Forget this worker's SDK connection
    // and let the next acquisition reconnect without terminating commands
    // owned by another Agent run.
  }

  /**
   * Get expected sandbox context for the system prompt based on preference
   * without initializing the sandbox. Returns null for E2B (uses default prompt).
   */
  async getSandboxContextForPrompt(): Promise<string | null> {
    if (this.sandboxPreference === 

===== <?> (577 chars) =====
) {
      return null;
    }

    const connections = await this.listConnections();
    const preferredConnection = resolveEnvironmentConnection(
      connections,
      this.sandboxPreference,
      this.currentConnectionId,
    );

    if (preferredConnection) {
      // Cache early so getSandboxType()/getSandboxInfo() work before getSandbox() is called
      this.currentConnectionName = preferredConnection.name;
      return this.buildSandboxContext(preferredConnection);
    }

    if (isEnvironmentPreference(this.sandboxPreference)) {
      throw new Error(
        

===== <?> (225 chars) =====
,
      );
    }

    if (connections.length > 0) {
      const firstAvailable = connections[0];
      this.currentConnectionName = firstAvailable.name;
      this.recordFallbackInfo({
        occurred: true,
        reason: 

===== firstAvailable (257 chars) =====
,
        requestedPreference: this.sandboxPreference,
        actualSandbox: firstAvailable.connectionId,
        actualSandboxName: firstAvailable.name,
      });
      return this.buildSandboxContext(firstAvailable);
    }

    if (this.subscription !== 

===== <?> (338 chars) =====
,
      });
    }

    return null;
  }

  private buildSandboxContext(connection: ConnectionInfo): string | null {
    const { osInfo } = connection;

    if (osInfo) {
      const { platform, arch, release, hostname } = osInfo;
      const platformName = getPlatformDisplayName(platform);

      const uploadPath =
        platform === 

===== agentBrowserProbe (398 chars) =====
;

      return `<sandbox_environment>
IMPORTANT: You are connected to a LOCAL machine in DANGEROUS MODE. Commands run directly on the host OS without Docker isolation.

System Environment:
- OS: ${platformName} ${release} (${arch})
- Hostname: ${hostname}
- Mode: DANGEROUS (no Docker isolation)
- User attachments: ${uploadPath}
- Interactive terminal: ${connection.capabilities?.pty === false ? 


---


## From `raw/aux2/lib_ai_tools_utils_cloud-sandbox-provider.ts.extract.md`

# lib/ai/tools/utils/cloud-sandbox-provider.ts — prompt literal extract (v2, byte-exact)
source: hackerai @ commit 6cf55ed545a59b1a61740a857b505cf18b8fad2b; method: template literals + double-quoted literals

## [1] dq / 31 chars
```
miosa_empty_workspace_migration
```
---
## [2] dq / 30 chars
```
miosa_file_workspace_migration
```
---
## [3] dq / 31 chars
```
miosa_configuration_unavailable
```
---
## [4] dq / 30 chars
```
miosa_cloud_sandbox_rollout_v1
```
---
## [5] tpl / 73 chars
```
Unsupported CLOUD_SANDBOX_PROVIDER: ${configured}. Expected miosa or e2b.
```
---
## [6] dq / 31 chars
```
miosa_configuration_unavailable
```
---

---


## From `raw/aux2/lib_api_chat-stream-helpers.ts.extract.md`

# lib/api/chat-stream-helpers.ts — prompt literal extract (byte-exact)
source: hackerai @ 6cf55ed545a59b1a61740a857b505cf18b8fad2b

## [1] dq / 42 chars
```
@/lib/chat/summarization/provider-pressure
```
---
## [2] dq / 108 chars
```
[Image attachment hidden — image attachments are a paid-plan feature and aren't available on the free plan.]
```
---
## [3] tpl / 21 chars
```
sendRateLimitWarnings
```
---
## [4] tpl / 13 chars
```
BudgetMonitor
```
---
## [5] dq / 43 chars
```
@/lib/chat/summarization/startup-compaction
```
---
## [6] tpl / 47 chars
```
summarization-status-${this.records.length + 1}
```
---
## [7] tpl / 6 chars
```
models
```
---
## [8] tpl / 6 chars
```
models
```
---
## [9] tpl / 70 chars
```
No content-filter retry model differs from served model ${servedModel}
```
---
## [10] tpl / 73 chars
```
${textPart.text}

<system-reminder>
${reminderContent}
</system-reminder>
```
---
## [11] tpl / 55 chars
```
<system-reminder>
${reminderContent}
</system-reminder>
```
---
## [12] dq / 46 chars
```
Failed to fetch notes, continuing without them
```
---
## [13] tpl / 55 chars
```
<system-reminder>
${newNotesContent}
</system-reminder>
```
---
## [14] tpl / 17 chars
```
<system-reminder>
```
---
## [15] tpl / 37 chars
```
appendSystemReminderToLastUserMessage
```
---
## [16] tpl / 7 chars
```
<notes>
```
---
## [17] tpl / 17 chars
```
<system-reminder>
```
---
## [18] dq / 58 chars
```
Failed to refresh notes in prepareStep, continuing without
```
---
## [19] tpl / 163 chars
```
Current saved notes. This snapshot supersedes earlier saved-note snapshots; it does not change the user's task or permissions.
${notes || "No saved notes remain."}
```
---
## [20] tpl / 52 chars
```
<system-reminder>
${reminderText}
</system-reminder>
```
---
## [21] tpl / 23 chars
```
${content}

${reminder}
```
---
## [22] tpl / 35 chars
```
${part.text as string}

${reminder}
```
---
## [23] dq / 113 chars
```
Agent mode on the free plan requires a local sandbox. Install the desktop app or upgrade to Pro for cloud access.
```
---
## [24] dq / 71 chars
```
Paid plans use Agent mode. Ask mode is only available on the free plan.
```
---
## [25] tpl / 19 chars
```
extra_usage_enabled
```
---
## [26] dq / 98 chars
```
Current team billing authorization could not be verified. Start a new Agent request and try again.
```
---
## [27] tpl / 114 chars
```
[chat-handler] getTeamExtraUsageState returned null for org ${organizationId}, using optimistic extra usage config
```
---
## [28] dq / 97 chars
```
Current extra usage authorization could not be verified. Start a new Agent request and try again.
```
---
## [29] tpl / 105 chars
```
[chat-handler] getExtraUsageBalance returned null for user ${userId}, using optimistic extra usage config
```
---

---
