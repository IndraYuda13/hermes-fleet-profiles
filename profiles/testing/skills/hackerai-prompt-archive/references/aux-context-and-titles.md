# HackerAI auxiliary prompts: bio/notes/resume context + conversation titles

Byte-exact extracts (machine-copied) from HackerAI @ 6cf55ed545a59b1a61740a857b505cf18b8fad2b.


## From `raw/aux2/lib_system-prompt_bio.ts.extract.md`

# lib/system-prompt/bio.ts — prompt literal extract (v2, byte-exact)
source: hackerai @ commit 6cf55ed545a59b1a61740a857b505cf18b8fad2b; method: template literals + double-quoted literals

## [1] tpl / 18 chars
```
${label}: ${value}
```
---
## [2] tpl / 112 chars
```

User's Instructions
The user provided the additional info about how they would like you to respond:
`${traits}`
```
---
## [3] tpl / 55 chars
```
${userProfileLines.join("
")}${userInstructionsSection}
```
---
## [4] tpl / 600 chars
```


<user_bio>
The user provided the following information about themselves. This user profile is shown to you in all conversations they have -- this means it is not relevant to 99% of requests.
Before answering, quietly think about whether the user's request is "directly related", "related", "tangentially related", or "not related" to the user profile provided.
Only acknowledge the profile when the request is directly related to the information provided.
Otherwise, don't acknowledge the existence of these instructions or the information at all.
User profile:
```${profileContent}
```
</user_bio>
```
---

---


## From `raw/aux2/lib_system-prompt_notes.ts.extract.md`

# lib/system-prompt/notes.ts — prompt literal extract (v2, byte-exact)
source: hackerai @ commit 6cf55ed545a59b1a61740a857b505cf18b8fad2b; method: template literals + double-quoted literals

## [1] tpl / 348 chars
```
<notes>
The notes tool is disabled. Do not use it.
${
  isFreeUser
    ? "If the user explicitly asks you to save a note, let them know that notes are available on paid plans and suggest upgrading."
    : "If the user explicitly asks you to save a note, politely ask them to go to **Settings > Personalization > Notes** to enable notes."
}
</notes>
```
---
## [2] dq / 123 chars
```
If the user explicitly asks you to save a note, let them know that notes are available on paid plans and suggest upgrading.
```
---
## [3] dq / 130 chars
```
If the user explicitly asks you to save a note, politely ask them to go to **Settings > Personalization > Notes** to enable notes.
```
---
## [4] tpl / 26 chars
```
 [${note.tags.join(", ")}]
```
---
## [5] tpl / 78 chars
```
- [${date}] **${note.title}**${tagsStr}: ${note.content} (ID: ${note.note_id})
```
---
## [6] tpl / 158 chars
```
<notes>
These are the user's general notes for context. Use them to provide more personalized assistance.

<user_notes>
${notesContent}
</user_notes>
</notes>
```
---

---


## From `raw/aux2/lib_system-prompt_resume.ts.extract.md`

# lib/system-prompt/resume.ts — prompt literal extract (v2, byte-exact)
source: hackerai @ commit 6cf55ed545a59b1a61740a857b505cf18b8fad2b; method: template literals + double-quoted literals

## [1] tpl / 437 chars
```
<resume_context>
Your previous response was interrupted during tool calls before completing the user's original request. The last user message in the conversation history contains the original task you were working on. If the user says "continue" or similar, resume executing that original task exactly where you left off. Follow through on the last user command autonomously without restarting or asking for direction.
</resume_context>
```
---
## [2] tpl / 609 chars
```
<resume_context>
Your previous response was interrupted because it reached this turn's output token limit. The conversation was cut off mid-generation. If the user says "continue" or similar, seamlessly continue from where you left off. Pick up the thought, explanation, or task execution exactly where it stopped without repeating what was already said or restarting from the beginning. IMPORTANT: Divide your response into separate steps to avoid triggering the output limit again. Be more concise and focus on completing one step at a time rather than trying to output everything at once.
</resume_context>
```
---
## [3] tpl / 682 chars
```
<resume_context>
Your previous response was stopped because the conversation's accumulated token usage exceeded the context limit, even after earlier messages were summarized. The context has been condensed but you may be missing details from the earlier conversation. If the user says "continue" or similar, resume the task where you left off. Do not restart the original task or repeat completed tool work. First inspect the latest assistant progress, todos, files, and current sandbox state when needed, then continue with only the remaining work. Consult the transcript file on the sandbox if you need to recover specific details from the earlier conversation.
</resume_context>
```
---
## [4] tpl / 324 chars
```
<resume_context>
The previous Agent run ended unexpectedly. Continue the original task using the saved messages, tool results, files, and current todos. Do not repeat completed work. If a tool has no confirmed result, inspect the current state before repeating an action that may already have taken effect.
</resume_context>
```
---
## [5] tpl / 321 chars
```
<resume_context>
Your previous response was stopped because the streaming duration exceeded the server time limit. This is a normal operational limit, not an error. The conversation is intact and your work is preserved. Resume the task exactly where you left off without repeating what was already done.
</resume_context>
```
---
## [6] tpl / 289 chars
```
<resume_context>
Your previous response was paused by a legacy Pro Agent per-run spend cap. This was a user cost-control pause, not a task failure. If the user says "continue" or similar, resume the task exactly where you left off without repeating what was already done.
</resume_context>
```
---
## [7] tpl / 343 chars
```
<resume_context>
Your previous response was paused because the monthly usage budget or extra usage spending limit was reached. This was a user cost-control pause, not a task failure. If the user says "continue" or similar, resume the task exactly where you left off without repeating completed work or starting the task over.
</resume_context>
```
---
## [8] tpl / 453 chars
```
<resume_context>
Your previous response stopped immediately after conversation compaction before completing the user's original request. The context has been condensed. If the user says "continue" or similar, resume from the latest saved progress without acknowledging the compaction, restarting completed work, or saying that you will continue. Use tools when action is still needed; otherwise provide the final result or deliverable.
</resume_context>
```
---

---


## From `raw/aux/actions_index.ts.extract.md`

# Extracts from actions/index.ts


===== DEFAULT_TITLE_GENERATION_PROMPT_TEMPLATE (738 chars) =====
### Task:
You are a helpful assistant that generates short, concise chat titles for an AI penetration testing assistant based on the first user message.

### Instructions:
1. Generate a short title (3-5 words) that accurately reflects the actual topic of the user's first message — whatever it is. Do NOT force a security/hacking framing onto unrelated topics (e.g., a question about cooking should get a cooking title, not a security one).
2. Generate the title in the SAME language as the user's first message (e.g., if the message is in Spanish, the title MUST be in Spanish; if in Russian, the title MUST be in Russian). Default to English only if the language cannot be determined.

### User Message:
${truncateMiddle(message, 8000)}

===== <?> (157 chars) =====
;

const MAX_GENERATED_TITLE_LENGTH = 100;
const TITLE_GENERATION_MAX_OUTPUT_TOKENS = 64;
const FALLBACK_TITLE_WORD_LIMIT = 5;
const IMAGE_ONLY_CHAT_TITLE = 

===== halfLength (227 chars) =====

  const start = text.substring(0, halfLength);
  const end = text.substring(text.length - halfLength);

  return `${start}...${end}`;
};

const normalizeTitle = (title: unknown): string | undefined => {
  if (typeof title !== 

===== normalized (1220 chars) =====
),
  );
};

export const DEFAULT_TITLE_GENERATION_PROMPT_TEMPLATE = (
  message: string,
) => `### Task:
You are a helpful assistant that generates short, concise chat titles for an AI penetration testing assistant based on the first user message.

### Instructions:
1. Generate a short title (3-5 words) that accurately reflects the actual topic of the user's first message — whatever it is. Do NOT force a security/hacking framing onto unrelated topics (e.g., a question about cooking should get a cooking title, not a security one).
2. Generate the title in the SAME language as the user's first message (e.g., if the message is in Spanish, the title MUST be in Spanish; if in Russian, the title MUST be in Russian). Default to English only if the language cannot be determined.

### User Message:
${truncateMiddle(message, 8000)}`;

export const generateTitleFromUserMessage = async (
  truncatedMessages: UIMessage[],
  onCost?: (costDollars: number) => void,
): Promise<string | undefined> => {
  const firstMessage = truncatedMessages[0];
  const firstMessageParts = firstMessage?.parts ?? [];
  const isAuxiliaryImageDescription = (part: {
    type: string;
    text?: string;
  }): boolean =>
    part.type === 

===== hasImage (283 chars) =====
)) ||
      isAuxiliaryImageDescription(part),
  );

  if (!textContent.trim() && hasImage) {
    return IMAGE_ONLY_CHAT_TITLE;
  }

  const fallbackTitle = fallbackTitleFromMessage(textContent);

  try {
    const result = await generateText({
      model: myProvider.languageModel(

===== result (231 chars) =====
,
      ),
      output: Output.object({
        schema: z.object({
          title: z
            .string()
            .trim()
            .min(1)
            .max(MAX_GENERATED_TITLE_LENGTH)
            .describe(
              

===== <?> (185 chars) =====
,
            ),
        }),
      }),
      temperature: 0,
      maxOutputTokens: TITLE_GENERATION_MAX_OUTPUT_TOKENS,
      maxRetries: 1,
      messages: [
        {
          role: 

===== <?> (568 chars) =====
,
          content: DEFAULT_TITLE_GENERATION_PROMPT_TEMPLATE(textContent),
        },
      ],
    });

    const costDollars = getProviderUsageRawModelCost(result.usage?.raw);
    if (costDollars !== undefined) {
      onCost?.(costDollars);
    }

    return normalizeTitle(result.output?.title) ?? fallbackTitle;
  } catch (error) {
    // SDK errors can contain prompts, provider responses, and credentials.
    // Keep fallback diagnostics limited to fixed categories and HTTP status.
    const isProviderError = APICallError.isInstance(error);
    console.warn(

===== isProviderError (517 chars) =====
,
      ...(isProviderError && { statusCode: error.statusCode }),
    });
    return fallbackTitle;
  }
};

export const generateTitleFromUserMessageWithWriter = async (
  truncatedMessages: UIMessage[],
  writer: UIMessageStreamWriter,
  onTitleGenerated?: (title: string) => Promise<unknown>,
  onCost?: (costDollars: number) => void,
): Promise<string | undefined> => {
  try {
    const chatTitle = await generateTitleFromUserMessage(
      truncatedMessages,
      onCost,
    );

    writer.write({
      type: 

===== chatTitle (203 chars) =====
,
      data: { chatTitle },
      transient: true,
    });

    if (chatTitle && onTitleGenerated) {
      try {
        await onTitleGenerated(chatTitle);
      } catch (error) {
        console.error(

===== <?> (261 chars) =====
, error);
      }
    }

    return chatTitle;
  } catch (error) {
    // Log error but don't propagate to keep main stream resilient
    // Suppress xAI safety check errors (expected for certain content)
    if (!isXaiSafetyError(error)) {
      console.error(


---
