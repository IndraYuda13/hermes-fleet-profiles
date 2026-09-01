# Mobile Responsive Remediation & Table Container Patterns

## Common Mobile Viewport Breakage Modes
1. **Fixed min-width on parent wrappers:** Setting `min-width: 800px` on a wrapper container causes `document.documentElement.scrollWidth > clientWidth`, breaking mobile viewport zooming, headers, and sidebars.
2. **Unconstrained flex child containers:** Flex items without `min-width: 0` inherit `min-width: auto`, preventing children from shrinking and causing overflow.
3. **Negative margins overlapping controls:** Negative margins on filter bars or button rows collapse hit targets and overlap adjacent element bounding boxes.

## Recommended Responsive Table Pattern
```css
/* Container must constrain width and allow touch scrolling */
.table-container {
  width: 100%;
  max-width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  min-width: 0;
}

/* Inner table maintains readable column widths without forcing viewport blowout */
table {
  width: 100%;
  min-width: 540px;
  border-collapse: collapse;
}
```

## Viewport Closure Assertion (Playwright / LENS)
```python
# Verify zero horizontal window overflow on mobile (390px / 360px)
scroll_width = page.evaluate("() => document.documentElement.scrollWidth")
client_width = page.evaluate("() => document.documentElement.clientWidth")
assert scroll_width <= client_width, f"Mobile overflow detected: {scroll_width} > {client_width}"
```
