# Static editorial publishing mechanics

## 1. Inspect and freeze scope

Read the publishing function, imports, builder calls, upload steps, registry mutations, and search-engine submissions. Separate generation from deployment. Do not invoke an all-in-one publisher merely to obtain a preview: its downstream side effects may run before artifact checks.

Record editorial ownership, approval gates, allowed files, protected widgets, and final evidence. For artifact-only changes, isolate generation in scratch with side-effect paths excluded rather than modifying the shared engine. An inspected Python engine can be staged by parsing its AST, loading only reviewed function definitions, supplying a scratch BASE_DIR and explicit dependencies, and retaining only generation/listing/sitemap statements. Exclude deployment, registry mutation, search submission and side-effectful imports. Select boundaries semantically and re-inspect them when the engine changes; source line numbers are not a durable isolation interface. Exercise the extracted generator and validate its outputs before trusting it.

## 2. Establish rollback and drift evidence

Fetch the live article if it exists, listing pages, and sitemap. Save live bytes and local mirror bytes separately with SHA-256 hashes. If they differ, resolve the authoritative baseline before patching. Repeat the comparison immediately before deployment and stop on unexplained drift.

Read current CSS URLs from live pages; do not inherit a publisher's hard-coded cache version. Inspect existing sidebar DOM and preserve the approved widget policy in the staged article.

## 3. Prepare licensed photos

1. Open the original source page and verify author, specific license, original dimensions, and adaptation terms. A repository's general license or search excerpt does not establish rights to the individual photo.
2. Download the source bytes. For a failed media fetch, try a different HTTP client and the source's download URL; verify the resulting file decodes as an image rather than trusting the extension.
3. Convert proportionally to the required width without accidental cropping. A reusable Pillow recipe is:

   ```python
   image = Image.open(source).convert('RGB')
   height = round(image.height * target_width / image.width)
   image = image.resize((target_width, height), Image.Resampling.LANCZOS)
   image.save(destination, 'WEBP', quality=85, method=6)
   ```

4. Record output dimensions, SHA-256, author, linked source page, linked license, and modifications. Visually inspect each output for subject accuracy, corruption, watermark, and crop suitability.
5. Do not force portrait architectural photos into landscape `cover` crops: spires and subject context can disappear. Use an uncropped inline placement or choose a genuinely wider hero.
6. Include visible credit links and modification disclosure. Apply share-alike terms to the adapted image when required, without implying that all article text automatically carries that license.

## 4. Stage and review

Sanitize the generated article, not unrelated pages: exactly one H1; no invented view counts; no interface emoji or affiliate funnel when excluded by scope; approved widgets; current CSS; canonical and image metadata; parseable JSON-LD. Insert listing and sitemap membership surgically and verify exact occurrence counts rather than trusting string-marker insertion logs.

Before rendering, count editorial body words plus FAQ questions/answers separately from navigation and repeated chrome, and check the requested metadata length and numbered H2 structure. Inspect the generated DOM for promotion containers, not just outbound affiliate parameters: template advertisements can link to internal landing pages and evade URL-only filtering. Remove excluded promotion containers from the staged article only.

Render the staged artifact at required mobile and desktop widths. Scroll lazy-loaded photos into view, wait for complete && naturalWidth > 0, then return to the top for captures; an offscreen lazy image is not proven broken or loaded by an initial-page check. Check document overflow, heading wrapping, caption readability, touch targets, and sidebar composition. Save full-page and top-of-page screenshots, and visually inspect both viewport variants. Record console errors, photo decode status and artifact hash alongside measurements. Approval must bind to the staged revision being deployed; rerun evidence after a repair.

## 5. Deploy and verify

Upload only approved artifacts after the review gate. Fetch each exact live target again and compare SHA-256 with the staged bytes. Verify HTTP status for both photos, article canonical/JSON-LD, and index/blog/sitemap membership. Upload acknowledgments alone are insufficient evidence.

If Search Console work is authorized, bind requests to the literal approved property, such as a domain-property identifier. Verify sitemap submission with readback and report URL inspection separately: submission or inspection does not prove indexing. Never route ordinary editorial articles through the restricted Google Indexing API.

Keep the handoff short: revision/artifact path, changed targets, verified checks, pending gates, and concrete blockers. Do not claim final live evidence while publication is held.
