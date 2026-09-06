# Media & Video Streaming Architecture for Digital Catalogs

Key architectural rules when embedding media playback or streaming within digital catalogs and web applications:

## 1. Operating System MediaSession API
Sync media metadata with the host OS (`navigator.mediaSession`) to ensure lock screens, Android/iOS control centers, and bluetooth hardware controls function correctly:
```javascript
if ('mediaSession' in navigator) {
  navigator.mediaSession.metadata = new MediaMetadata({
    title: item.title,
    artist: 'Animestr',
    artwork: [{ src: item.cover, sizes: '512x512', type: 'image/jpeg' }]
  });
  navigator.mediaSession.setActionHandler('play', () => video.play());
  navigator.mediaSession.setActionHandler('pause', () => video.pause());
}
```

## 2. Picture-in-Picture (PiP) & Background Multitasking
- Check `document.pictureInPictureEnabled`.
- Provide a dedicated PiP button and hotkey (`P`) for multitasking viewers.

## 3. Subtitle / Multi-Track Memory Leak Prevention
- In dynamic SPAs where video sources change without a page reload, call `track.mode = 'disabled'` on existing `video.textTracks` before removing `<track>` elements to prevent memory leaks and cue collisions.

## 4. API & Stream Proxy Security
- **CORS Configuration**: Avoid pairing `allow_origins=["*"]` with `allow_credentials=True` (violates W3C spec; rejected by modern browsers).
- **Rate Limiting**: Throttling is critical on transcode/remux endpoints (`/api/stream/`) to prevent process exhaustion.
- **FFmpeg Lifecycle**: When terminating client streams, send `SIGTERM` first with a short timeout before `SIGKILL`.
