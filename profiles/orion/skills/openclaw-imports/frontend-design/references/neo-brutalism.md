# Neo-Brutalist Frontend & Anti-AI-Slop Guidelines

## Anti-AI-Slop Directives

"AI Slop" in UI design is characterized by:
- Soft rounded pill/bubble cards (`rounded-2xl` / `rounded-3xl` everywhere).
- Cliché purple/cyan neon gradient meshes on sterile white or generic dark backgrounds.
- Weak typography contrast with default system fonts or overused Inter/Roboto.
- Timid spacing without deliberate informational density.
- Predictable copycat SaaS card grids with blurry backdrop filters (`backdrop-blur-md`).

## Minimalist Neo-Brutalist Architecture

When the user requests Neo-Brutalism or high-character tactile UI:

### 1. Geometry & Borders
- Hard, thick solid borders: `border-2` to `border-[3px] border-black dark:border-white` or ultra-crisp high contrast border tokens.
- Hard geometric corners: `rounded-none` or subtle retro `rounded-sm` / `rounded-md`. Eliminate pill shapes.
- Offset hard-drop box shadows:
  ```css
  box-shadow: 4px 4px 0px 0px #000000;
  /* Dark mode: */
  box-shadow: 4px 4px 0px 0px #FFFFFF;
  ```
- Physical keypress interactions:
  ```html
  <button class="border-2 border-black bg-[#D4FF00] shadow-[3px_3px_0px_0px_#000000] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none transition-all">
  ```

### 2. High-Contrast Tactical Color Palette
- Base: Chalk White / Off-white (`#F4F4F0`) for Light mode; Deep Pitch Charcoal/Black (`#0D0E12`, `#121316`) for Dark mode.
- Acid Accents:
  - Electric Lime / Acid Yellow: `#D4FF00` or `#E2F952` (Hero CTAs, Active badges)
  - Raw Coral / High-Contrast Orange: `#FF5C00` or `#FF4A4A` (Negative / Expense / Danger)
  - Cyber Mint / Vivid Emerald: `#00F0A8` or `#10B981` (Positive / Income / Success)
  - Deep Solid Ink: `#000000` / `#FFFFFF` for borders, dividers, and text.

### 3. Monospace & Tabular Data Density
- All monetary amounts, metrics, timestamps, and ledger rows MUST use heavy tabular monospace font styling (`font-mono font-bold tracking-tight`).
- High information density with crisp micro-labels in uppercase (`text-xs font-black uppercase tracking-wider`).
