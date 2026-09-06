# Video Processing Worker Architecture (FFmpeg, yt-dlp & Subtitles)

Operational lessons, memory limits, and CPU scheduling rules when running automated video clipping and rendering pipelines on resource-constrained VPS hosts (e.g. 4 vCPU, RAM 54GB, CPU-only, 15GB root disk).

## 1. Scratchpad Storage & Disk Exhaustion Mitigations
- **Root Partition Guard (`ENOSPC`)**: Video encoding creates large uncompressed frame buffers, audio WAV tracks, and temporary MP4s. On systems where the root partition `/` has limited free space (e.g. <=15GB), rendering in `/tmp` or `$HOME` can instantly fill the disk and crash system services.
- **RAM Disk Scratchpad (`/dev/shm`)**:
  - Direct all download, audio slicing, ASS subtitle generation, and intermediate rendering to `/dev/shm/video_scratch/{job_id}`.
  - Check available tmpfs size (`df -h /dev/shm`).
  - **Crucial Swap Guardrail**: On hosts with `Swap = 0B`, files left uncleaned in `/dev/shm` consume physical RAM. Worker processes MUST wrap execution in strict `try ... finally: shutil.rmtree(job_dir, ignore_errors=True)`.
  - Transfer the final optimized MP4 to persistent storage (`/mnt` or object storage S3/R2) immediately upon completion.

## 2. Process Scheduling & Concurrency Budget
- **Worker Concurrency Limit**: On a 4 vCPU host with background services (AI gateways, Docker, databases), set video worker concurrency to **1**. Concurrent multi-render tasks cause extreme context switching and CPU starvation.
- **FFmpeg Thread Pinning & Priority De-escalation**:
  - Pin FFmpeg encoding threads: `-threads 2`.
  - Execute with low process and I/O scheduler priority:
    ```bash
    nice -n 15 ionice -c 2 -n 7 ffmpeg -hide_banner -y -i ...
    ```
  - This guarantees host daemons (like 9router or webhooks) do not experience request latency spikes or timeouts.
- **Asyncio Process Control over Preforking**:
  - Prefer asyncio task runners (like ARQ or Asyncio Worker) over Celery prefork for subprocess orchestration. If a job times out or aborts, ARQ cleanly terminates child subprocesses (`SIGTERM` -> `SIGKILL`), preventing detached "orphan" FFmpeg processes from consuming 100% CPU in the background.

## 3. FFmpeg & yt-dlp Reliability Quirks
- **Variable Frame Rate (VFR) Desync**: YouTube source streams are frequently encoded in VFR. Slicing and rendering directly leads to progressive audio-video desync. Always enforce Constant Frame Rate (CFR) and timestamp re-basing:
  ```bash
  -fps_mode cfr -r 30 -filter_complex "[0:v]setpts=PTS-STARTPTS...;[0:a]asetpts=PTS-STARTPTS..."
  ```
- **Selective Section Downloads (`--download-sections`)**:
  - Never download full 1-2 hour podcast videos just to clip a 45-second segment.
  - Use yt-dlp section cutting: `yt-dlp --download-sections "*02:15-03:00" -f "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best" <URL>`.
- **Bot Detection / HTTP 429 Prevention**:
  - Provide Netscape-formatted cookies: `--cookies /path/to/cookies.txt`.
  - Spoof player client args: `--extractor-args "youtube:player_client=android,web"`.
  - Implement randomized jitter delays (3–8s) between requests.
- **libass Subtitle Rendering Safety**:
  - Emojis and unmapped Unicode glyphs in `.ass` dialogue text can cause `libass` font-matching crashes or render unsightly empty boxes ("tofu").
  - Sanitize all transcribed dialogue text before generating `.ass` files (strip non-standard emojis, or overlay emojis via separate FFmpeg png image filters).
