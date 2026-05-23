import { test, expect } from '@playwright/test';

/* ─────────────────────────────────────────────────────────────────
   GRILL MASTER — Foundation smoke tests
   Tests the core flows: setup, cook, charcoal toggle, log save/load.
   ───────────────────────────────────────────────────────────────── */

test.describe('Foundation', () => {

  test.beforeEach(async ({ page }) => {
    // Clear localStorage to ensure clean state
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
    await page.reload();
  });

  test('app shell renders with locked design tokens', async ({ page }) => {
    await page.goto('/');
    // Header brand visible
    await expect(page.locator('.brand')).toContainText('Grill');
    await expect(page.locator('.brand em')).toContainText('Master');
    // All 4 tabs visible
    await expect(page.locator('#tab-timer')).toBeVisible();
    await expect(page.locator('#tab-queue')).toBeVisible();
    await expect(page.locator('#tab-log')).toBeVisible();
    await expect(page.locator('#tab-temp')).toBeVisible();
    // Charred background applied
    const bg = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
    // #0f0a06 → rgb(15, 10, 6)
    expect(bg).toBe('rgb(15, 10, 6)');
  });

  test('Butcher Chart protein picker renders all 8 icons including redrawn Beef', async ({ page }) => {
    await page.goto('/');
    const proteins = await page.locator('.protein-grid .protein').count();
    expect(proteins).toBe(8);
    // Beef icon present and is a single unified SVG (one main path for body+legs)
    const beefSvg = page.locator('.protein[data-protein="beef"] svg');
    await expect(beefSvg).toBeVisible();
    // Verify Beef icon does NOT have 4 separate skinny leg rectangles (the bug we fixed)
    const beefRects = await page.locator('.protein[data-protein="beef"] svg rect').count();
    expect(beefRects).toBeLessThanOrEqual(0); // unified silhouette has no rect legs
  });

  test('single-screen setup: select protein reveals all setup blocks', async ({ page }) => {
    await page.goto('/');
    // Initially cut/heat/doneness hidden
    await expect(page.locator('#sect-cut')).toBeHidden();
    await expect(page.locator('#sect-heat')).toBeHidden();
    await expect(page.locator('#sect-doneness')).toBeHidden();
    // Click Beef
    await page.locator('.protein[data-protein="beef"]').click();
    // Now visible
    await expect(page.locator('#sect-cut')).toBeVisible();
    await expect(page.locator('#sect-heat')).toBeVisible();
    await expect(page.locator('#sect-doneness')).toBeVisible();
    // Answer chip shows "Beef"
    await expect(page.locator('#ans-protein')).toHaveText('Beef');
  });

  test('full setup flow: Beef → Ribeye → 1.5" → High → Med-Rare → start cook', async ({ page }) => {
    await page.goto('/');
    // Beef
    await page.locator('.protein[data-protein="beef"]').click();
    // Cut: Ribeye (already auto-selected — verify)
    await expect(page.locator('#ans-cut')).toHaveText('Ribeye');
    // Thickness: 1.5"
    await page.locator('#thickness-input').fill('1.5');
    await expect(page.locator('#ans-thickness')).toContainText('1.5');
    // Heat: High
    await page.locator('[data-heat="high"]').click();
    await expect(page.locator('#ans-heat')).toHaveText('High');
    // Doneness: Med-Rare
    await page.locator('#doneness-pills .pill').filter({ hasText: 'Med-Rare' }).click();
    await expect(page.locator('#ans-doneness')).toHaveText('Med-Rare');
    // Results visible
    await expect(page.locator('#sect-results')).toBeVisible();
    await expect(page.locator('#t-side-a')).not.toHaveText('—');
    await expect(page.locator('#results-target')).toContainText('135°F');
    // Start cook
    await page.locator('#btn-start-cook').click();
    // Timer visible, setup hidden
    await expect(page.locator('#active-timer')).toBeVisible();
    await expect(page.locator('#setup-form')).toBeHidden();
    // Timer numeral renders
    await expect(page.locator('#timer-display')).toBeVisible();
    // Stage label shows "Side A"
    await expect(page.locator('#timer-stage-small')).toHaveText('Side A');
  });

  test('charcoal toggle shows charcoal-specific cue and adjusts time', async ({ page }) => {
    await page.goto('/');
    // Initial: Gas is default, charcoal cue hidden
    await expect(page.locator('#charcoal-cue')).toBeHidden();
    // Select protein/cut/etc to get a calculation
    await page.locator('.protein[data-protein="beef"]').click();
    await page.locator('[data-heat="high"]').click();
    // Capture gas time
    const gasTime = await page.locator('#t-side-a').textContent();
    // Click Charcoal
    await page.locator('[data-grill="charcoal"]').click();
    await expect(page.locator('#ans-grill')).toHaveText('Charcoal');
    // Charcoal cue visible with the pitmaster's instruction
    await expect(page.locator('#charcoal-cue')).toBeVisible();
    await expect(page.locator('#charcoal-cue')).toContainText('Two-zone fire');
    // Time changed (charcoal factor is 1.08)
    const charcoalTime = await page.locator('#t-side-a').textContent();
    expect(charcoalTime).not.toBe(gasTime);
  });

  test('pause and resume during active cook', async ({ page }) => {
    await page.goto('/');
    await page.locator('.protein[data-protein="beef"]').click();
    await page.locator('[data-heat="high"]').click();
    await page.locator('#doneness-pills .pill').filter({ hasText: 'Med-Rare' }).click();
    await page.locator('#btn-start-cook').click();
    await expect(page.locator('#active-timer')).toBeVisible();
    // Pause
    await page.locator('#btn-pause').click();
    await expect(page.locator('#btn-pause')).toHaveText('Resume');
    // Resume
    await page.locator('#btn-pause').click();
    await expect(page.locator('#btn-pause')).toHaveText('Pause');
  });

  test('cancel cook returns to setup form', async ({ page }) => {
    await page.goto('/');
    await page.locator('.protein[data-protein="beef"]').click();
    await page.locator('[data-heat="high"]').click();
    await page.locator('#doneness-pills .pill').filter({ hasText: 'Med-Rare' }).click();
    await page.locator('#btn-start-cook').click();
    await page.locator('#btn-cancel').click();
    await expect(page.locator('#setup-form')).toBeVisible();
    await expect(page.locator('#active-timer')).toBeHidden();
  });

  test('tab navigation works across all 4 tabs', async ({ page }) => {
    await page.goto('/');
    await page.locator('#tab-queue').click();
    await expect(page.locator('#panel-queue')).toBeVisible();
    await expect(page.locator('#panel-queue .title')).toContainText('queue');

    await page.locator('#tab-log').click();
    await expect(page.locator('#panel-log')).toBeVisible();
    await expect(page.locator('#panel-log .title')).toContainText('cooks');

    await page.locator('#tab-temp').click();
    await expect(page.locator('#panel-temp')).toBeVisible();
    await expect(page.locator('#panel-temp .title')).toContainText('numbers');

    await page.locator('#tab-timer').click();
    await expect(page.locator('#panel-timer')).toBeVisible();
  });

  test('Temp tab shows expanded doneness reference + USDA + Pro Tips', async ({ page }) => {
    await page.goto('/');
    await page.locator('#tab-temp').click();
    // Intro paragraph
    await expect(page.locator('.temp-intro')).toContainText('Trust a probe, not a guess');
    // Doneness card: Rare 120-125°F with Celsius
    await expect(page.locator('.temp-card').filter({ hasText: 'Rare' }).first()).toBeVisible();
    await expect(page.locator('.temp-card').filter({ hasText: '49–52°C' })).toBeVisible();
    // Medium-Rare description
    await expect(page.locator('.temp-card').filter({ hasText: 'Medium-Rare' })).toContainText('Warm, pink-red center');
    // USDA card
    await expect(page.locator('.usda-card')).toBeVisible();
    await expect(page.locator('.usda-card')).toContainText('165°F');
    await expect(page.locator('.usda-card')).toContainText('All Poultry');
    // Pro Tips card
    await expect(page.locator('.tips-card')).toBeVisible();
    await expect(page.locator('.tips-card')).toContainText('Pull 5°F early');
    await expect(page.locator('.tips-card')).toContainText('Pat dry before grilling');
  });

  test('Heat pills show temperature ranges', async ({ page }) => {
    await page.goto('/');
    await page.locator('.protein[data-protein="beef"]').click();
    await expect(page.locator('[data-heat="medium"]')).toContainText('375–450°F');
    await expect(page.locator('[data-heat="high"]')).toContainText('450–550°F');
  });

  test('Medium heat auto-selects when protein is picked', async ({ page }) => {
    await page.goto('/');
    await page.locator('.protein[data-protein="beef"]').click();
    // Medium pill becomes active automatically — no manual click needed
    await expect(page.locator('[data-heat="medium"]')).toHaveClass(/active/);
    await expect(page.locator('#ans-heat')).toHaveText('Medium');
    // Results card visible (Start Cook is reachable)
    await expect(page.locator('#sect-results')).toBeVisible();
    await expect(page.locator('#btn-start-cook')).toBeVisible();
  });

  test('env toggles are collapsed by default and expand on click', async ({ page }) => {
    await page.goto('/');
    await page.locator('.protein[data-protein="beef"]').click();
    // Env content is hidden, toggle exists
    await expect(page.locator('#env-content')).toBeHidden();
    await expect(page.locator('#env-toggle')).toBeVisible();
    // Click to expand
    await page.locator('#env-toggle').click();
    await expect(page.locator('#env-content')).toBeVisible();
    await expect(page.locator('#toggle-winter')).toBeVisible();
    // Click to collapse
    await page.locator('#env-toggle').click();
    await expect(page.locator('#env-content')).toBeHidden();
  });

  test('add to queue button is visible on Queue tab and adds a lane', async ({ page }) => {
    await page.goto('/');
    // Configure a cook on Timer
    await page.locator('.protein[data-protein="beef"]').click();
    await page.locator('#doneness-pills .pill').filter({ hasText: 'Med-Rare' }).click();
    // Go to Queue tab
    await page.locator('#tab-queue').click();
    await expect(page.locator('#btn-add-queue')).toBeVisible();
    // Add to queue
    await page.locator('#btn-add-queue').click();
    // Lane card appears
    await expect(page.locator('.lane-card')).toHaveCount(1);
    await expect(page.locator('.lane-name').first()).toBeVisible();
    // Start button on lane
    await expect(page.locator('.lane-btn').filter({ hasText: 'Start' })).toBeVisible();
  });

  test('charcoal grill mode has noticeable time difference and stage cues', async ({ page }) => {
    await page.goto('/');
    await page.locator('.protein[data-protein="beef"]').click();
    // Capture gas indirect time
    const gasFinish = await page.locator('#t-finish').textContent();
    // Switch to charcoal
    await page.locator('[data-grill="charcoal"]').click();
    const charcoalFinish = await page.locator('#t-finish').textContent();
    // Finish stage should differ (charcoal bias is real)
    expect(charcoalFinish).not.toBe(gasFinish);
    // Charcoal-specific cue visible
    await expect(page.locator('#charcoal-cue')).toBeVisible();
    await expect(page.locator('#charcoal-cue')).toContainText('Two-zone');
  });

  test('Log tab empty state uses Pitmaster voice', async ({ page }) => {
    await page.goto('/');
    await page.locator('#tab-log').click();
    const logEmpty = page.locator('#panel-log .log-empty');
    await expect(logEmpty).toContainText('Nothing logged yet');
    await expect(logEmpty).toContainText('Build the book');
  });

  test('copy uses Pitmaster voice: imperatives, no exclamations', async ({ page }) => {
    await page.goto('/');
    // No "STEP 1 • PROTEIN" form-builder language
    const bodyText = await page.locator('body').textContent();
    expect(bodyText).not.toContain('STEP 1');
    expect(bodyText).not.toContain('STEP 2');
    expect(bodyText).not.toContain('Please');
    // No emoji
    expect(bodyText).not.toMatch(/[\u{1F300}-\u{1FAFF}]/u);
  });

  test('charcoal selection persists in calculated meta', async ({ page }) => {
    await page.goto('/');
    await page.locator('.protein[data-protein="beef"]').click();
    await page.locator('[data-heat="high"]').click();
    await page.locator('[data-grill="charcoal"]').click();
    await expect(page.locator('#results-meta-line')).toContainText('charcoal');
  });

  test('thickness slider auto-hides for cuts without thickness', async ({ page }) => {
    await page.goto('/');
    await page.locator('.protein[data-protein="sausage"]').click();
    // Hot Dog cut is in NO_THICKNESS — but we auto-select first cut (Bratwurst, also in NO_THICKNESS)
    await expect(page.locator('#sect-thickness')).toBeHidden();
  });

  test('all 8 proteins have icons that render', async ({ page }) => {
    await page.goto('/');
    const proteins = ['beef', 'pork', 'poultry', 'lamb', 'fish', 'burger', 'sausage', 'veggie'];
    for (const p of proteins) {
      const svg = page.locator(`.protein[data-protein="${p}"] svg`);
      await expect(svg).toBeVisible();
      // Each icon has at least one path or shape
      const shapeCount = await page.locator(`.protein[data-protein="${p}"] svg > *`).count();
      expect(shapeCount).toBeGreaterThan(0);
    }
  });

});
