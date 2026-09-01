# Mobile-First Zero-Overflow Discipline & Viewport Defense

## Key Lessons from Production Mobile Refactoring

When building mobile web interfaces (especially forms, calculators, slips, and dashboards):

### 1. The Strict Zero-Overflow CSS Invariant
Always enforce strict box model sizing on all containers, form elements, and text:
```css
*, *::before, *::after {
  box-sizing: border-box !important;
  margin: 0;
  padding: 0;
  max-width: 100%;
}

html, body {
  width: 100%;
  max-width: 100vw;
  overflow-x: hidden !important;
}
```

### 2. Multi-Element Horizontal Button/Pill Traps
- **Pitfall**: Grouping action buttons (`btn-primary` + `btn-outline`) or preset chips horizontally (`flex-row` or 3+ column fixed widths) on mobile viewports (< 480px) causes the trailing buttons to be severely clipped outside the right edge.
- **Rule**:
  - Main hero CTA buttons: Default to `flex-direction: column; width: 100%;` on mobile (`< 480px`), and only switch to `flex-direction: row` on larger viewports.
  - Multi-option chips/presets: Use `display: grid; grid-template-columns: repeat(3, 1fr);` with small font (`font-size: 9px - 10px`) and `text-overflow: ellipsis; white-space: nowrap;`, or horizontal swipeable scroll with clear visual cues.

### 3. Typography & Text Truncation Defense
- Long headings and descriptive lead copy on mobile must use responsive clamp units and strict wrapping rules:
  ```css
  h1 {
    font-size: clamp(20px, 5.5vw, 42px);
    line-height: 1.08;
    word-break: break-word;
    overflow-wrap: break-word;
  }
  p {
    word-break: break-word;
    overflow-wrap: break-word;
  }
  ```

### 4. Input & Dropdown `<select>` Sizing
- `<select>` and `<input>` elements frequently breach container boundaries on WebKit/Blink if `box-sizing: border-box` or `width: 100%` is missing from the element rule itself.
- Always apply:
  ```css
  .input-control, .select-control {
    width: 100%;
    max-width: 100%;
    box-sizing: border-box;
    display: block;
  }
  ```
