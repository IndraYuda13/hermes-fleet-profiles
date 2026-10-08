---
name: interactive-fiction-craft
description: "Use when building AI stories or narrative prompt engines."
metadata:
  category: creative
  tags: [narrative, storytelling, interactive-fiction, anti-ai-slop, indonesian-prose, creative-writing]
---

# Interactive Fiction & AI Narrative Craftsmanship Standard

A comprehensive engineering guide for architecting, prompting, and evaluating AI-generated interactive fiction and branching narratives, with a primary focus on rich, natural Indonesian literary prose and robust continuity.

## 1. Anti-AI-Slop Narrative Invariants (Eliminating Machine Clichés)
- **Blacklist Stock Metaphors:**
  Never allow common AI stock phrases in generated segments:
  - *"Udara dingin menusuk tulang"*
  - *"Senyuman tipis tersungging di bibirnya"*
  - *"Matanya membulat tak percaya"*
  - *"Waktu seakan membeku / terhenti"*
  - *"Seolah alam semesta berkonspirasi"*
  - Meta-commentary narator: *"Perjalanan baru saja dimulai...", "Sedikit yang ia tahu bahwa..."*
- **The Somatic Show-Don't-Tell Rule:**
  Never state emotional states abstractly (*"Indra merasa sangat cemas dan takut"*). Convey emotional reality through physical visceral reactions and concrete object interactions (telapak tangan basah yang menggesek kain celana jins, helaan napas pendek yang tertahan di tenggorokan, gemeretak gigi).
- **Physical Sensory Anchors:**
  Require at least two distinct non-visual sensory details per scene (bau karat lembap pada engsel pintu, denging serangga malam di sudut plafon, rasa getir empedu di lidah, gesekan lantai semen kasar di telapak kaki tanpa alas).

## 2. Indonesian Literary Prose & Dialogue Realism
- **Natural Cadence vs Translationese:**
  Avoid stiff literal translations of English tropes (*"Well, kurasa kita tidak punya pilihan"* atau dialog berstruktur pasif kaku). Use idiomatic, living Indonesian speech with natural particles (*kan, kok, lha, ya sudah, toh*) appropriate to the character's background.
- **Dialogue Subtext Over Exposition Dumps:**
  Characters must not narrate their backstories or motivations aloud in neat paragraphs. Real conversation relies on evasion, hesitation, deflection, awkward pauses, and tactical silence.
- **Action Beats Over Speech Tags:**
  Minimize dialogue tags like *"ujarnya dengan nada sedih"*. Anchor dialogue lines with concrete physical actions (memadamkan puntung rokok, merapikan kerah kemeja yang kusut, memalingkan pandangan ke luar jendela bus).

## 3. Dynamic Scene Pacing & Sentence Rhythm
- **Tension-Modulated Syntax:**
  - **Action & Danger:** Use clipped, short sentences (3–8 words), active verbs, and rapid staccato paragraphs. Strip long ambient descriptions to reflect adrenaline tunnel vision.
  - **Mystery & Exploration:** Use layered, evocative compound sentences that trace spatial volume, atmosphere, shadows, and subtle ambient sounds.
  - **Emotional Climax:** Balance internal monologue with sudden, irreversible external physical shocks.

## 4. High-Stakes Consequential Branching (Choice Anatomy)
- **The Anti-Cosmetic Choice Invariant:**
  Never provide choices that are purely cosmetic variations (*"Belok kiri"* vs *"Belok kanan"* without context or consequence). Every decision point must present distinct trade-offs:
  - **Pragmatism vs Ethics:** Gaining an immediate tactical advantage by compromising a moral principle or breaking a promise.
  - **Direct Confrontation vs Stealth/Intel:** Risking physical trauma for speed, versus spending critical time to observe while danger escalates elsewhere.
  - **Sacrifice vs Retention:** Protecting a vulnerable ally at the expense of rare supplies, secrets, or personal safety.
- **Choice Label Craft:**
  Choice labels must communicate intent and tactical attitude clearly (e.g., `[Rebut pistol dari meja sebelum ia sempat menarik pelatuk]` bukan sekadar `[Serang]`).
- **Non-Terminal Segments Require Actionable Choices (`arc_end` vs `story_end`):**
  Distinguish strictly between terminal conclusion (`story_end`, where choices must be empty `[]`) and arc conclusion (`arc_end`, where an adventure arc closes but the narrative continues). Engine prompts and schema validators must mandate 2–4 forward-looking choices on `arc_end`. Never allow `choices: []` on non-terminal segments—an empty choice set strands interactive readers in a headless decision UI with no clickable paths.
- **Frontend Fallback for Missing Choices:**
  If a model or legacy segment produces a zero-choice non-terminal state, the reader UI must not render an empty decision shell; it must display an explicit arc-transition banner and automatically open custom prompt input for reader steering.

## 5. Continuity Engine & State Management
- **Established Facts Immutability:**
  Once a fact is introduced and locked into the continuity record (e.g., character injury, time of day, locked door, discovered artifact), subsequent generations must treat it as immutable ground truth. No silent healing or teleportation.
- **Open Threads Ledger:**
  Active unresolved conflicts and questions must be tracked explicitly in the continuity state. When a scene resolves a thread, it must transition from `open_threads` to `closed_threads` with immediate narrative consequences.
- **Character State Tracking:**
  Track character emotional state, physical inventory, injuries, and relational trust scores across segments to maintain coherent psychological arcs.

## 6. Prompt Engineering Architecture for Story Engines
- **Structured JSON Output Discipline:**
  Separate the artistic narrative body from narrative metadata using strict JSON schema contracts (e.g. `segment.title`, `segment.body`, `segment.ending_type`, `segment.choices`, `continuity.established_facts`, `continuity.open_threads`).
- **Context Window Economy:**
  Do not feed full book text on long stories. Inject:
  1. Core story premise and frozen character bible.
  2. World rules and stylistic tone directives.
  3. Cumulative summary recap (free of spoilers).
  4. Active established facts and open threads.
  5. The immediate previous 1–2 segments verbatim for stylistic continuity.
- **Dynamic Style Injectors:**
  Allow modular tone configurations (e.g. *Sastrawan Reflektif*, *Sinematik Cepat*, *Misteri Mencekam*, *Realistis Sehari-hari*) that append targeted stylistic guidelines to the system prompt per story or scene.

## 7. Interactive Engine State Persistence & Branching Pitfalls
- **PostgreSQL JSONB Serialization in Fork and Rewrite Copies:**
  When cloning segments during branch forking, story rewrites, or state snapshots, all JSONB metadata fields (e.g. `content_tags`, `narrative_state`, `continuity_state`, `narrative_config`) must be explicitly stringified (`JSON.stringify(val)`) before being passed as SQL query parameters in `node-postgres` (`pg`). Passing raw JavaScript arrays directly causes `pg` to format them as PostgreSQL native arrays (`{"tag1", "tag2"}` instead of `["tag1", "tag2"]`), triggering fatal database error `invalid input syntax for type json (DETAIL: Expected ":", but found ",")`.
- **Zero Quota Deductions for Branch/Draft Creation:**
  Branch forking, draft rewrites, and segment cloning must be zero-quota operations; only actual AI generation calls consume user quota.

## 8. Multimodal Chapter Audio & Neural TTS Synthesis (`gemini-3.8-flash-tts`)
- **Model Selection & Native Speech Modality:**
  Use Google's dedicated multimodal speech model `gemini-3.8-flash-tts` via `generateContent`. Pass `responseModalities: ["AUDIO"]` and configure voice persona under `speechConfig.voiceConfig.prebuiltVoiceConfig.voiceName`.
- **Prebuilt Voice Personas & Casting:**
  Select voices aligned with narrative genre and point of view:
  - `Aoede`: Warm, nuanced, literary narration with natural breathing and expressive dramatic pauses (ideal for third-person literary prose and character reflection).
  - `Fenrir`: Deep, resonant, authoritative delivery (ideal for dark fantasy, thriller, horror, or tense action beats).
  - `Kore`: Calm, crisp, modern storytelling tone (ideal for slice-of-life, sci-fi mystery, or investigative narration).
  - `Puck`: Energetic, dynamic pacing (ideal for youth adventure, comedic relief, or fast-paced dialogue).
- **Long-Form Chapter Narration Capacity:**
  `gemini-3.8-flash-tts` accepts full chapters in a single request (tested reliably up to 4,500+ characters / ~700 words, producing ~4m45s of continuous audio). Never truncate chapters unnecessarily into tiny sentence snippets, which causes disjointed emotional pacing and voice inflection resets.
- **On-Demand Generation Invariant (Zero-Waste Quota Guard):**
  Never generate speech automatically upon segment creation or completion. Provide an explicit trigger button in the chapter header/action bar so only the reader/author who consciously chooses to listen initiates generation, conserving API quotas and server compute.
- **Content-Hash Cache Invalidation & In-Place Rewrite Handling:**
  Never key cached audio solely by `segment_id` or story metadata. Always compute `content_hash = sha256(segment.title + '\n\n' + segment.body + voice)`. Store this hash in database metadata and filename (`storage/audio/{story_id}/{segment_id}_{hash}_{voice}.mp3`). When loading a chapter, compare current content hash against stored audio metadata: if different (due to text edits or rewrites), surface an explicit status ("Teks bab telah diperbarui. Buat ulang suara narasi"). On chapter forks with identical text, link existing files via matching content hash without hitting upstream APIs.
- **Decoupled Storage & HTTP 206 Streaming Standard:**
  Never store binary audio blobs in PostgreSQL tables (causes WAL bloating, slows backups, and thrashes connection pools). Store files in dedicated server disk storage, and serve via a dedicated streaming route supporting `Accept-Ranges: bytes` and HTTP 206 Partial Content. This enables instant timeline scrubbing/seeking on iOS Safari and mobile Chrome without loading the full file.
- **Raw Audio Output & Transcoding Invariant:**
  The API returns base64-encoded 24,000 Hz, 16-bit mono PCM in a WAV container (`mimeType: "audio/wav"`). Uncompressed WAV files for full chapters reach 12–15 MB, causing high network egress and slow browser buffer times. Always transcode server-side to MP3 using FFmpeg (`ffmpeg -i input.wav -c:a libmp3lame -q:a 2 output.mp3`), reducing payload by ~80% (to ~2.5 MB) for instant HTML5 `<audio>` streaming.
- **Quota Resilience & Multi-Key Round-Robin:**
  The free tier of Google AI Studio enforces strict rate limits (~3 Requests Per Minute on `gemini-3.8-flash-tts`). Maintain a pool of validated Google API keys in server environment/config (`GOOGLE_TTS_API_KEYS`). Rotate keys round-robin per generation and implement exponential backoff on HTTP 429 (`RESOURCE_EXHAUSTED`) before surfacing errors.
- **Feature Entitlement Gating for High-Cost Operations:**
  Gate TTS audio synthesis and open-ended steering (such as custom decisions) under explicit entitlement checks (`feature_key = 'chapter_tts'`). Decouple playback from generation: allow free readers to stream previously generated audio on published stories, but restrict generation triggers to VIP/entitled accounts to prevent abuse.
