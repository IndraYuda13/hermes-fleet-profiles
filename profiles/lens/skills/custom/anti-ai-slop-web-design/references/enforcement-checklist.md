# Anti-Slop Enforcement Checklist & Implementation Guide

## Prohibited Tokens Checklist
- [ ] NO ambient purple/cyan glow or blur gradients (`from-purple-500 to-cyan-500`, radial blur blobs).
- [ ] NO default `rounded-2xl` / `rounded-3xl` everywhere. Enforce sharp 0px or 1px borders unless a specific rounded aesthetic is chosen.
- [ ] NO pervasive `backdrop-blur-md bg-white/5` glassmorphism.
- [ ] NO unconfigured fallback sans-serif (`Inter`, `Roboto`, `Arial`).
- [ ] NO centered hero layout with multi-color gradient text and generic 3-card feature grid.

## Fleet Role Directives
1. **AURORA**: Lock aesthetic archetype in `DESIGN_SPEC.md` before coding starts.
2. **FRAME**: Implement code strictly adhering to `DESIGN_SPEC.md` without adding AI slop embellishments.
3. **LENS**: Perform visual QA and browser mutation tests to explicitly flag and reject any prohibited tokens.
4. **SENTINEL**: Verify design tokens and assets during quality gate.
