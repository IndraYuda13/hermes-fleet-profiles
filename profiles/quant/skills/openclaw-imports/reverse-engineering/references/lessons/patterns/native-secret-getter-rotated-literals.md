# Pattern: Native secret getters may still be static literal tables in newer builds

## When this pattern appears
- An older build exposes JNI secret getters that return human-readable final-form values directly.
- A newer build keeps the same getter family and naming pattern, but the app has a stronger loader / hidden-provider architecture.
- Analysts are tempted to assume the newer build now computes everything dynamically or that native extraction is blocked.

## Proven pattern
- The newer build may still return fixed literals directly from native `.rodata`.
- The change is often **semantic**, not **extractability**:
  - old build returns final-form URL / UUID / hex / pin values
  - new build returns rotated opaque or base64url-like literals from the same getter family
- This means the real blocker shifts from `cannot extract` to `must determine whether the extracted literal is used directly, decoded, or transformed upstream`.

## Practical signs
- Exported JNI getter family survives under the same conceptual namespace even if class names shift (`SecretKey` -> `Cardamom`, etc.).
- Getter functions are small and repetitive.
- Disassembly shows a simple pattern:
  1. allocate string buffer / object
  2. copy a fixed literal from `.rodata`
  3. return to Java via `NewStringUTF` or equivalent JNI call
- Grep may miss reuse across versions because the literal values rotate completely even while the boundary stays stable.

## Why this matters
- Do not stop at "new build is stripped" or "string not found".
- First ask whether the getter boundary itself still exists and whether the returned literal merely changed format.
- If so, use the older build to understand semantics and the newer build to recover current literals.

## Next best action after spotting this pattern
1. Prove the getter body shape directly in disassembly.
2. Extract the current literal set without persisting raw secrets into reusable notes.
3. Determine whether Java/native wrapper code consumes those literals as-is or decodes them.
4. Only after that escalate to loader, anti-hook, or dynamic tracing.
