---
name: bstation-ogv-catalog-architecture
description: Use when building or querying Bstation OGV anime catalogs.
---

# Bstation / Bilibili.tv OGV Catalog Architecture & Infinite Scroll Patterns

This skill encodes proven architecture, parameters, and pitfalls when harvesting, serving, and displaying the Bstation (`bilibili.tv`) OGV anime catalog.

## 1. Upstream Taxonomy Trap (Anime vs Donghua)
- **Official Bstation Taxonomy:** On official Bstation web (`bilibili.tv/id/category`), both Japanese anime and Chinese Donghua (2D & 3D) are unified under the single top-level category **`Anime`**.
- **User Mental Model:** Users opening Bstation's anime catalog expect to browse and scroll through the entire animation library (332+ to 360+ titles) as one flowing catalog.
- **Pitfall:** Do NOT partition the default catalog view into a narrow "Japanese Anime Only" slice (which only has 50–78 titles). If an "Anime" filter cuts off Donghua by default, users will complain that "the anime is only 50 titles" because they are used to seeing the combined catalog on Bstation.
- **Rule:**
  - Default view (`type=all`): Combine both Japanese anime and Donghua in a unified A-Z stream.
  - Sub-filters: Provide optional toggle pills (e.g. `Anime (78)` and `Donghua (282)`), but default to both active.

## 2. Platform Parameter Harvesting Expansion (`web` vs `android`)
Endpoint: `https://api.bilibili.tv/intl/gateway/web/v2/ogv/index/items_v2`

| Parameter | Platform | Result Count | Included Content |
| :--- | :--- | :--- | :--- |
| `season_type=1` | `platform='web'` | **50 titles** | Limited subset of Japanese Anime |
| `season_type=1` | `platform='android'` | **78 titles** | Unlocks major titles (*Demon Slayer*, *BLEACH* Movies 1-4, *Tonikaku Kawaii S2*, *Black Summoner*, *Spy Classroom*, etc.) |
| `season_type=4` | `platform='android'` | **282 titles** | Chinese Donghua & OGV animation |
- **Combined** | `platform='android'` | **360 titles** | Complete official Bstation OGV catalog |

**Harvesting Directive:**
Always pass `platform='android'` when querying `items_v2` to retrieve the expanded 360-title collection instead of the 332-title web-restricted list.

## 3. Unlisted Blockbuster Anime Discovery (Search API + Proxy Seed Harvester)
- **The OGV Hidden Library:** Bstation intentionally omits its most popular licensed blockbuster anime from the `ogv/index/items_v2` category index. These titles exist as valid, streamable OGV seasons (`season_type_enum=1`), but can only be accessed via direct search or specific `season_id` endpoints.
- **Top Blockbusters Recovered via Seed Discovery:**
  - *One Piece* (sid `37976` - 1200+ eps + movies `37130`, `37114`, `1017411`, `37120`, `37118`)
  - *Naruto* (`1005144`), *Naruto Shippuden* (`1005195` - 508 eps), *Boruto* (`1005426`)
  - *Jujutsu Kaisen* S1 (`37738`), S2 (`2084055`), *The Culling Game* (`2288197`)
  - *Attack on Titan* S1 (`35044`), S2 (`34521`), S3 P1/P2 (`34611`, `34539`), Final Season (`36297`, `1042594`)
  - *Demon Slayer / Kimetsu no Yaiba* S1 (`34580`), Mugen Train (`1023002`), Entertainment District (`1033760`), Swordsmith Village (`2079053`), Hashira Geiko (`2104174`)
  - *SPY x FAMILY* S1 (`1048837`), S2 (`2090049`)
  - *Frieren: Beyond Journey's End* (`2090295`), *Oshi no Ko* (`2080019`), *Solo Leveling* (`2097863`), *Chainsaw Man* (`2069687`), *Mushoku Tensei* (`36690`), *Hunter x Hunter 2011* (`37603`), *Haikyuu!!* S1-S4 (`34475`..`34634`), *BLEACH* (`35278` + TYBW `2069614`..`2414568`), *Tensura / Slime* (`34510`, `36689`), *KonoSuba* (`34558`..`2106744`), *Re:Zero* (`35753`..`2114391`), *One Punch Man* (`36279`, `36381`), *JoJo* (`34791`..`34796`), *Dr. Stone* (`34604`..`2123789`).
- **Discovery Mechanism:** Query `/intl/gateway/web/v2/search_v2?keyword=<title>&platform=tv&s_locale=id_ID` through Bstation proxy (`socks5://127.0.0.1:32012`), parse `modules` where `type` is `ogv` or `ogv_subject`, and store/seed in `backend/anime_seeds.json`.
- Combining `items_v2` (360) + seed harvester (180+) expands the library to **547+ titles (265+ Japanese anime)**.

## 5. The "Thousands of Anime" User Perception Pitfall & Upstream Reality
- **User Perception:** Users frequently believe Bstation has "thousands of anime" and suspect a 200–300 title catalog is incomplete.
- **Upstream Reality & Root Causes:**
  1. **Dracin Flooding (`season_type=5`):** Bstation's catalog API contains **1,448+ micro-dramas (Dracin / Short Drama Live-Action)** under `season_type=5` (*Cahaya Bulan CEO Fu*, *Kencan Manis*, *Rahasia Adikku*, etc.). When unpartitioned, these overwhelm the catalog and inflate title counts.
  2. **UGC Video Universe:** Bstation operates like YouTube; search queries return millions of UGC videos (fan clips, AMVs, re-uploads, reactions). UGC items have no `season_id`, no structured episode list, no official WebVTT subtitles, and cannot be ingested as structured OGV seasons.
  3. **Official Licensed Anime (OGV):** Bstation's active Southeast Asia (Indonesia) licensed anime catalog genuinely caps at **~250–350 active OGV titles**.
  4. **Ground Truth Proof on Web:** On `bilibili.tv/id/category`, scrolling to the absolute bottom yields only **332 titles** (combined Anime + Donghua). With mobile platform expansion and unlisted seed discovery, 547 titles (265 Anime + 282 Donghua) already exceeds Bstation's publicly browsable web catalog.
- **Handling Protocol:** When users report missing anime, verify specific titles against the search API rather than attempting to ingest UGC or dracin. If an anime was licensed by Bstation, find its unlisted `season_id` via targeted title search and add it to `anime_seeds.json`.

## 4. Seamless Infinite Scroll vs Manual Pagination
- Bstation web uses seamless infinite scrolling. Web frontends requiring manual button clicks ("Muat Lebih Banyak") break user expectation.
- **Recommended Implementation:**
  ```javascript
  // IntersectionObserver on pagination sentinel
  if ('IntersectionObserver' in window && DOM.sentinel) {
    const observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && !state.isLoading && state.hasMore) {
        state.page += 1;
        fetchAndRenderCatalog(false);
      }
    }, { rootMargin: '300px 0px 300px 0px' });
    observer.observe(DOM.sentinel);
  }
  ```
- **Deduplication:** Always deduplicate incoming cards by `season_id` before appending to state/DOM to avoid duplicate cards on rapid scroll triggers.
- Provide a smooth loading spinner during scroll fetch, and an end indicator ("Semua anime telah ditampilkan") when all items are exhausted.
