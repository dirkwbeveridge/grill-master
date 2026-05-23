import { test } from '@playwright/test';
import path from 'path';

test('generate 1024x1024 app icon PNG', async ({ browser }) => {
  const context = await browser.newContext({
    viewport: { width: 1024, height: 1024 },
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();
  await page.goto('file://' + path.resolve('icon-source.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(500);
  await page.locator('.icon').screenshot({ path: 'icon-1024.png', omitBackground: false });
  await context.close();
});

test('generate 2732x2732 splash PNG', async ({ browser }) => {
  const context = await browser.newContext({
    viewport: { width: 2732, height: 2732 },
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();
  await page.goto('file://' + path.resolve('splash-source.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(500);
  await page.locator('.splash').screenshot({ path: 'splash-2732.png', omitBackground: false });
  await context.close();
});
