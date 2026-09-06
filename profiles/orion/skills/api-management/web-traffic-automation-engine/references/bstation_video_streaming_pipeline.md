# Bstation Video Streaming & On-The-Fly Remuxing Pipeline

Playbook for extracting, remuxing, and serving protected Bstation video streams via web API gateways.

## 1. Stream Separation Architecture (DASH-like CDN)
Bstation does not serve pre-muxed single MP4 files with combined video and audio:
- **Video Streams:** Distinct format IDs (e.g. `format_id: 3..10`), resolutions from 144p to 1080p, codecs `avc1` (H.264) or `hev1` (HEVC/H.265), `acodec: none`.
- **Audio Streams:** Distinct format IDs (e.g. `format_id: 0..2`), codec `mp4a.40.2` or `mp4a.40.5` (AAC), `vcodec: none`.
- **Extraction:** Metadata extraction via `yt-dlp` requires valid regional proxies and Netscape session cookies (`bilibili.tv` headers).
- **Direct CDN Playback:** Once extracted, CDN video/audio URLs (e.g. `upos-sz-mirrorcosbstar1.bilivideo.com` or Akamai mirrors) can be fetched directly with standard headers (`Referer: https://www.bilibili.tv/`, `User-Agent: Mozilla/5.0...`) without continuing to route through residential/egress proxies.

## 2. On-The-Fly Remuxing with Zero Re-Encoding
To serve a playable MP4 stream to modern HTML5 `<video>` elements without high latency or CPU saturation, use FFmpeg with stream copy:
```bash
ffmpeg -y \
  -headers "Referer: https://www.bilibili.tv/\r\nUser-Agent: Mozilla/5.0\r\n" -i "<video_url>" \
  -headers "Referer: https://www.bilibili.tv/\r\nUser-Agent: Mozilla/5.0\r\n" -i "<audio_url>" \
  -c:v copy -c:a copy \
  -movflags frag_keyframe+empty_moov \
  -f mp4 pipe:1
```
- **Performance:** Takes ~1.0s to initiate streaming output; zero video re-encoding CPU load.
- **Delivery:** Stream directly via FastAPI / Starlette `StreamingResponse(media_type="video/mp4")`.

## 3. WebVTT Subtitle Conversion
Official multi-language subtitles (`.srt`) are fetched via `yt-dlp --write-subs --skip-download`:
- Native `<track>` tags in browser HTML5 `<video>` require `WEBVTT` format.
- Conversion rule: replace comma `,` milliseconds with dot `.`, e.g. `00:00:01,500` -> `00:00:01.500`, and prepend `WEBVTT\n\n`.
