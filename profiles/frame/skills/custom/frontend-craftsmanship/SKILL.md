---
name: frontend-craftsmanship
description: Build polished responsive UI and verify the rendered implementation.
version: 2.0.0
metadata:
  hermes:
    tags: [frontend, responsive, ui, engineering]
    category: custom
---

# Frontend Craftsmanship

## Procedure

1. Read AURORA's design intent when available; understand why before implementing what.
2. Build semantic, maintainable components with clear state ownership and accessible interactions.
3. Establish typography hierarchy, readable line lengths, numeric alignment, spacing rhythm, and density.
4. Implement coherent iconography and intentional interaction states.
5. Treat each responsive range as a composition rather than a scaled desktop.
6. Stress long labels, huge values, zero items, many items, validation, loading, errors, modals, dropdowns, sidebars, and theme changes.
7. Inspect hover, focus, keyboard, active, pressed, disabled, touch, and navigation states.
8. Render the actual interface; inspect visually and inspect browser console.
9. Fix visual issues even when code/test tools report no error.
10. After the final material change, rerun functional, build, and visual gates.

Do not reuse an older PASS after code changes.
