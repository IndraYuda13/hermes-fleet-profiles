# Bstation OGV Index & Catalog API Specification

Authoritative reference extracted from Bstation web client (`bstar-web-new`) and reverse engineered gateway endpoints.

## Endpoints

### 1. Catalog Items Index
- **URL**: `https://api.bilibili.tv/intl/gateway/web/v2/ogv/index/items_v2`
- **Method**: `GET`
- **Headers**:
  ```http
  User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)
  Referer: https://www.bilibili.tv/
  ```
- **Parameters**:
  - `season_type`: `1,4` (1 = Anime Jepang, 4 = Donghua / OGV Anime). Note: `5` is Dracin (Short Drama).
  - `pn`: Page number (starts at 1).
  - `ps`: Page size (default 20, **max 50**).
    - **CRITICAL**: `ps > 50` returns `code: -400` with `cards: null`. Always cap at 50.
  - `platform`: `web`
  - `s_locale`: `id_ID` (or `en_US`, `th_TH`, `vi_VN`)
  - `area_id`: `-1` (all), `1` (China), `2` (Japan)
  - `style_id`: Genre ID from filters (e.g. `20007` for Isekai, `-1` for all)
  - `index_year`: Filter by year range (e.g. `[2026,2027)`, `[2025,2026)`, `-1` for all)
  - `index_month`: Filter by season release (`1` = Winter, `4` = Spring, `7` = Summer, `10` = Fall, `-1` for all)
  - `order`: `0` (Hot), `2` (Terbaru)
- **Response Shape**:
  ```json
  {
    "code": 0,
    "message": "0",
    "ttl": 1,
    "data": {
      "cards": [
        {
          "type": "ogv",
          "card_type": "ogv_anime",
          "title": "Kage no Jitsuryokusha ni Naritakute! 2",
          "cover": "https://pic.bstarstatic.com/ogv/...",
          "view": "24.2M Putar",
          "styles": "",
          "style_list": ["Adaptasi novel", "Isekai"],
          "season_id": "2089246",
          "index_show": "Tamat",
          "corner_mark": { "text": "Bstation only" }
        }
      ],
      "total": 332,
      "size": 50,
      "num": 1,
      "has_next": true
    }
  }
  ```

### 2. Available Filters & Styles Taxonomy
- **URL**: `https://api.bilibili.tv/intl/gateway/web/v2/ogv/index/filters`
- **Method**: `GET`
- **Parameters**: `season_type=1,4&platform=web&s_locale=id_ID`
- **Yields**: Complete dictionary of `order`, `area_id`, `style_id` (genres), `index_year`, and `index_month`.

### 3. Categories Index
- **URL**: `https://api.bilibili.tv/intl/gateway/web/v2/ogv/index/categories`
- **Method**: `GET`
- **Returns**: Available category mappings:
  - `1,4`: Anime (Anime Jepang & Donghua)
  - `5`: Dracin (Short Drama)
  - `2,3`: Acara TV / Variety Shows

## Catalog Volume Breakdown (Bstation SEA id_ID)
- Anime (`season_type=1`): ~50 titles
- Donghua / OGV (`season_type=4`): ~282 titles
- **Total Official Anime**: Exactly 332 titles (requires 7 requests with `ps=50`).
- Dracin (`season_type=5`): 1,448 titles.
