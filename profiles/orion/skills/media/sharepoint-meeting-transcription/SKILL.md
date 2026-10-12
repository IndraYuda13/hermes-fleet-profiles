---
name: sharepoint-meeting-transcription
description: "Transcribe SharePoint/Teams recordings via HLS+Whisper."
version: 1.0.0
author: Hermes Agent Curator
license: MIT
metadata:
  hermes:
    tags:
    - sharepoint
    - teams
    - transcription
    - whisper
    - hls
---

# SharePoint/Teams Recording -> Transcript (CPU-only)

## When to Use

- User shares a `sharepoint.com/:v:/` recording link and asks to access, download, or transcribe it.
- You need captions/transcript text from an HLS (m3u8) video with AES-128-CBC encrypted segments, especially on a CPU-only host.

Proven end-to-end on a university SharePoint recording (113 min, no GPU).

## Pipeline

1. Open the share link in the browser; the page title reveals the recording name even before auth. Get the play/video manifest URL from the page context (network or `videomanifest` URL).
2. Fetch HLS init + media segments (audio track is enough and much smaller).
   - PITFALL: plain curl without browser context may get 401 even with cookies. Sending `Origin` + `Referer` headers of the SharePoint host made segments download with HTTP 200 WITHOUT cookies.
3. Segments are AES-128-CBC encrypted; key and IV come from the manifest properties (URL-encoded values; some segments need per-segment IV context).
4. Decrypt each segment; strip PKCS7 padding (padding byte varies 1-16 per segment; verify it looks uniform).
5. Concatenate: init (ftyp+moov) first, then all media segments (moof+mdat). Verify with ffprobe.
6. ffmpeg -> wav 16 kHz mono.
7. Transcribe with Whisper on CPU: small model is ~4x realtime; medium is slower but noticeably better punctuation for Indonesian. Chunk the audio (~10 min chunks) and checkpoint segments to JSONL after each chunk so a restart does not lose progress.
8. Output: `[hh:mm:ss]` timestamped txt, plain text, and .srt.

## Pitfalls

- Headless player shows "stalled"/never plays: NORMAL. The manifest and segments are still reachable.
- Segment count can be >1000; fetch in parallel from inside the browser page context if direct HTTP is blocked, then batch-extract.
- ffmpeg converting a long m4a to WhatsApp voice note can hit `spawnSync ffmpeg ETIMEDOUT`; fall back to sending the audio as a file attachment.
- Keep the raw m4a so the transcript can be redone with a better model later.
- Verify final text file line count against the total segment count before claiming completeness.
