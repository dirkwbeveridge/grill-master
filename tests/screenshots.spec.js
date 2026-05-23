import { test } from '@playwright/test';

/* ─────────────────────────────────────────────────────────────────
   Visual regression screenshots — generates portfolio-quality
   stills of each major screen on iPhone 15 Pro viewport.
   ───────────────────────────────────────────────────────────────── */

test.describe('Screenshots', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
    await page.reload();
  });

  test('01 setup empty', async ({ page }) => {
    await page.goto('/');
    await page.screenshot({ path: 'screenshots/01-setup-empty.png', fullPage: true });
  });

  test('02 setup with protein selected', async ({ page }) => {
    await page.goto('/');
    await page.locator('.protein[data-protein="beef"]').click();
    await page.locator('#thickness-input').fill('1.5');
    await page.locator('[data-heat="high"]').click();
    await page.locator('#doneness-pills .pill').filter({ hasText: 'Med-Rare' }).click();
    await page.waitForTimeout(200);
    await page.screenshot({ path: 'screenshots/02-setup-ready.png', fullPage: true });
  });

  test('03 setup charcoal toggled', async ({ page }) => {
    await page.goto('/');
    await page.locator('[data-grill="charcoal"]').click();
    await page.locator('.protein[data-protein="beef"]').click();
    await page.locator('#thickness-input').fill('1.5');
    await page.locator('[data-heat="high"]').click();
    await page.locator('#doneness-pills .pill').filter({ hasText: 'Med-Rare' }).click();
    await page.waitForTimeout(200);
    await page.screenshot({ path: 'screenshots/03-setup-charcoal.png', fullPage: true });
  });

  test('04 active timer', async ({ page }) => {
    await page.goto('/');
    await page.locator('.protein[data-protein="beef"]').click();
    await page.locator('#thickness-input').fill('1.5');
    await page.locator('[data-heat="high"]').click();
    await page.locator('#doneness-pills .pill').filter({ hasText: 'Med-Rare' }).click();
    await page.locator('#btn-start-cook').click();
    await page.waitForTimeout(400);
    await page.screenshot({ path: 'screenshots/04-active-timer.png', fullPage: true });
  });

  test('05 log empty', async ({ page }) => {
    await page.goto('/');
    await page.locator('#tab-log').click();
    await page.waitForTimeout(150);
    await page.screenshot({ path: 'screenshots/05-log-empty.png', fullPage: true });
  });

  test('06 temp guide', async ({ page }) => {
    await page.goto('/');
    await page.locator('#tab-temp').click();
    await page.waitForTimeout(150);
    await page.screenshot({ path: 'screenshots/06-temp-guide.png', fullPage: true });
  });

  test('07 queue empty', async ({ page }) => {
    await page.goto('/');
    await page.locator('#tab-queue').click();
    await page.waitForTimeout(150);
    await page.screenshot({ path: 'screenshots/07-queue-empty.png', fullPage: true });
  });

});
