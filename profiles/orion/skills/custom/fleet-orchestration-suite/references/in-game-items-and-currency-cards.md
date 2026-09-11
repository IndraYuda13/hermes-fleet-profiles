# In-Game Items, Currency Cards & Pass Badges Pattern

## Overview
When designing and implementing fintech/gaming top-up interfaces, displaying generic text-only nominal cards causes cognitive friction and lowers user trust. Integrating authentic in-game currency icons (Diamonds, Crystals, CP, VP) and glowing pass badges (Weekly Diamond Pass, Welkin Moon, Starlight) elevates visual polish and conversion.

## 1. Asset & Currency Catalog Structure
Organize assets under a dedicated, traversal-safe directory structure (e.g. `assets/items/`) with dual-format WebP (95 quality) and PNG alpha:
- **Game Currencies (Tiered Assets):**
  - Small stack (e.g., 3-86 diamonds)
  - Medium cluster (e.g., 172-706 diamonds)
  - Big vault / treasury (e.g., 1000+ diamonds)
- **Subscription & Passes:**
  - Weekly Diamond Pass / FF Weekly Membership
  - Starlight Member / Twilight Pass
  - Blessing of the Welkin Moon / Express Supply Pass
- **Utilities & Telco:**
  - PLN kWh Token, Data GB Badge, Pulsa Coin, E-Wallet Balance.

## 2. Dynamic Asset Resolution Architecture
In the client-side store/app (`app.js`), use a resilient multi-tier resolver:
```javascript
function resolveItemAsset(product, brandKey) {
  const name = String(product.name || '').toLowerCase();
  const brand = String(brandKey || '').toLowerCase();

  // 1. Passes & Memberships
  if (name.includes('weekly diamond pass') || name.includes('wdp')) {
    return { icon: 'assets/items/mlbb_weekly_diamond_pass.webp', badge: 'WDP', glow: '#FFE500', isPass: true };
  }
  if (name.includes('welkin') || name.includes('blessing')) {
    return { icon: 'assets/items/genshin_blessing_of_the_welkin_moon.webp', badge: 'Welkin', glow: '#38BDF8', isPass: true };
  }
  if (name.includes('starlight')) {
    return { icon: 'assets/items/mlbb_starlight_member.webp', badge: 'Starlight', glow: '#F472B6', isPass: true };
  }

  // 2. Quantity-based Tiering
  const amountMatch = name.match(/(\d+[\.,]?\d*)\s*(diamond|dm|crystal|vp|cp)/i);
  if (amountMatch) {
    const qty = parseInt(amountMatch[1].replace(/\D/g, ''), 10);
    if (qty > 1000) return { icon: `assets/items/${brand}_diamonds_big.webp`, isPass: false };
    if (qty > 150) return { icon: `assets/items/${brand}_diamonds_medium.webp`, isPass: false };
    return { icon: `assets/items/${brand}_diamonds_small.webp`, isPass: false };
  }

  // 3. Fallback to Brand Logo
  return { icon: `assets/brands/logos/${brand}.webp`, isPass: false };
}
```

## 3. Tactile UI Card Layout & CSS Tokens
- **Item Thumbnail Box:** Fixed `44x44px` (`36x36px` on mobile), corner radius `8px`, background `var(--surface-overlay)`, 1px specular rim border.
- **Pass Badges:** Absolute positioning at top-right with radial glow matching pass identity (`#FFE500` for weekly passes, `#F472B6` for VIP starlight).
- **Tabular Pricing:** Always format prices with `font-variant-numeric: tabular-nums` to avoid layout jumping when toggling selections.
- **Zero CLS Image Fallback:** Use `<picture>` with `onError` event handling to switch seamlessly from WebP -> PNG -> Brand Logo Monogram without layout shift.
