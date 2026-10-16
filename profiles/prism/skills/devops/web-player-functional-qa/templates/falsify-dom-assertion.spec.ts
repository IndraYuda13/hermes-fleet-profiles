// Counterfactual harness: prove a DOM/layout assertion actually fails without the fix.
// Copy and modify. Run against a staging server; never against the shared production port.
//
//   node <repo>/node_modules/@playwright/test/cli.js test --config=<cfg> falsify-dom-assertion.spec.ts
//
// Neutralises the fix at runtime with an addStyleTag override (no repo file touched),
// so the check is safe to run while another agent owns the working tree.
import { test, expect, type Page } from "@playwright/test";
import { writeFile } from "node:fs/promises";

// --- configure -------------------------------------------------------------
const ART = process.env["PNL_PROBE_ART"] ?? "/root/fleet-evidence";
const ROUTE = "/<route>";                       // page that renders the fixed row
const TARGET = /<link label>/;                  // locator for the fixed element
const CELL = "<trailing-cell-class>";           // the cell that collapsed
const PRE_FIX_TEMPLATE = "auto minmax(0, 1fr) auto"; // the broken grid value
const FIXED_TEMPLATE = "minmax(0, 1fr) auto";        // the value the fix installs
// ---------------------------------------------------------------------------

/** Exactly the assertion under test, plus the mechanism for the report. */
const measure = (page: Page, target: RegExp, cell: string) =>
  page.getByRole("link", { name: target }).first().evaluate((el, cellSel) => {
    const node = el.querySelector(cellSel) as HTMLElement;
    const range = document.createRange();
    range.selectNodeContents(node);            // glyphs, not the span box
    const text = range.getBoundingClientRect();
    const row = el.getBoundingClientRect();
    return {
      textWidth: text.width,
      textRight: text.right,
      rowRight: row.right,
      cellWidth: node.getBoundingClientRect().width,
      gridTemplateColumns: getComputedStyle(el).gridTemplateColumns,
      docScrollWidth: document.documentElement.scrollWidth,
      innerWidth: window.innerWidth,
      overflowsRow: text.right > row.right + 0.5,
      specPasses: text.width > 0 && text.right <= row.right + 0.5,
    };
  }, cell);

// Hook this up to the repo's own auth/fixture helper before running.
async function reachFixedState(page: Page) {
  await page.goto(ROUTE);
  await page.setViewportSize({ width: 360, height: 800 }); // the viewport that revealed it
  await page.getByText("<expand control>", { exact: true }).click();
}

test("layout assertion fails when the fix is neutralised", async ({ page }) => {
  await reachFixedState(page);
  const obs: Record<string, unknown> = {};

  obs["with_fix"] = await measure(page, TARGET, CELL);
  await page.screenshot({ path: `${ART}/with-fix.png`, fullPage: true });

  // Step 2: neutralise. Overrides the fixed rule back to the pre-fix template.
  await page.addStyleTag({
    content: `.studio-row { grid-template-columns: ${PRE_FIX_TEMPLATE} !important; }`,
  });
  await page.waitForTimeout(150); // let the template change invalidate layout
  obs["fix_neutralised"] = await measure(page, TARGET, CELL);
  await page.screenshot({ path: `${ART}/fix-neutralised.png`, fullPage: true });

  // Step 3: restore. Guards against a probe that fails for an unrelated reason.
  await page.addStyleTag({
    content: `.studio-row:not(:has(.studio-row-icon)):not(:has(> :nth-child(3))) { grid-template-columns: ${FIXED_TEMPLATE} !important; }`,
  });
  await page.waitForTimeout(150);
  obs["with_fix_restored"] = await measure(page, TARGET, CELL);

  await writeFile(`${ART}/assertion-power.json`, JSON.stringify(obs, null, 2));
  console.log("ASSERTION-POWER OBS " + JSON.stringify(obs));

  expect((obs["with_fix"] as { specPasses: boolean }).specPasses).toBe(true);
  expect((obs["fix_neutralised"] as { specPasses: boolean }).specPasses).toBe(false);
  expect((obs["with_fix_restored"] as { specPasses: boolean }).specPasses).toBe(true);
});
