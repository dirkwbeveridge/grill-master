import { test, expect } from '@playwright/test';

async function configure(page, protein = 'beef', cut) {
  await page.locator(`[data-protein="${protein}"]`).click();
  if (cut) await page.locator('#cut-pills button').filter({ hasText: cut }).click();
}
async function shortTimes(page, duration = 2) {
  await page.evaluate(seconds => Object.assign(window.gm.times, { sideA: seconds, sideB: seconds, finish: seconds, rest: seconds }), duration);
}
async function addLane(page) {
  await page.locator('#tab-queue').click();
  await page.locator('#btn-add-queue').click();
}
async function nativeMock(page, options = {}) {
  await page.addInitScript(settings => {
    window.nativeCalls = [];
    window.nativeRouteListener = null;
    window.Capacitor = { Plugins: {
      LocalNotifications: {
        checkPermissions: async () => ({ display: settings.permission || 'granted' }),
        requestPermissions: async () => ({ display: settings.permission || 'granted' }),
        schedule: async value => {
          if (settings.scheduleFailure) throw new Error('schedule failed');
          window.nativeCalls.push({ method: 'schedule', ...value });
        },
        cancel: async value => window.nativeCalls.push({ method: 'cancel', ...value }),
      },
      GrillMasterNative: {
        syncCook: async value => window.nativeCalls.push({ method: 'sync', ...value }),
        endCook: async () => window.nativeCalls.push({ method: 'end' }),
        addListener: async (name, listener) => { window.nativeRouteListener = listener; },
        consumeRoute: async () => ({ destination: settings.route || null }),
      },
    } };
  }, options);
  await page.reload();
}

test.beforeEach(async ({ page }) => {
  await page.goto('/');
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  await expect(page.locator('.protein')).toHaveCount(8);
  await page.clock.install({ time: new Date('2026-11-02T12:00:00Z') });
});

test('turkey burgers require 165°F in setup, pull and thermometer confirmation', async ({ page }) => {
  await configure(page, 'burger', 'Turkey Burger');
  await expect(page.locator('#doneness-pills button')).toHaveCount(1);
  await expect(page.locator('#results-target')).toContainText('165°F');
  await shortTimes(page);
  await page.locator('#btn-start-cook').click();
  await expect(page.locator('#timer-pull')).toHaveText('165°F');
  await page.clock.fastForward(2100);
  await page.locator('#btn-confirm-action').click();
  await page.clock.fastForward(2100);
  await page.locator('#btn-confirm-action').click();
  await page.clock.fastForward(2100);
  await expect(page.locator('#confirm-sub')).toContainText('at least 165°F before removing from heat');
  await expect(page.locator('#btn-confirm-action')).toContainText('Temperature checked');
});

test('whole-cut pull guidance respects USDA minimum and avoids promised carryover', async ({ page }) => {
  await configure(page, 'pork');
  await page.locator('#btn-start-cook').click();
  await expect(page.locator('#timer-pull')).toHaveText('145°F');
  await expect(page.locator('#timer-carryover')).toContainText('rest at least 3 minutes');
  await expect(page.locator('#timer-carryover')).not.toContainText('Climbs to');
});

test('reload reconciles absolute deadlines and retains active cook configuration', async ({ page }) => {
  await configure(page, 'burger', 'Turkey Burger');
  await shortTimes(page, 60);
  await page.locator('#btn-start-cook').click();
  const deadline = await page.evaluate(() => window.gm.cook.deadline);
  await page.clock.fastForward(12000);
  await page.reload();
  await expect(page.locator('#active-timer')).toBeVisible();
  expect(await page.evaluate(() => window.gm.cook.deadline)).toBe(deadline);
  expect(await page.evaluate(() => window.gm.cook.remaining)).toBeGreaterThan(45);
  expect(await page.evaluate(() => window.gm.cook.remaining)).toBeLessThan(49);
  await expect(page.locator('#timer-spec')).toContainText('TURKEY BURGER');
  await expect(page.locator('#timer-pull')).toHaveText('165°F');
});

test('elapsed stage restores pending acknowledgement without auto-advancing', async ({ page }) => {
  await configure(page);
  await shortTimes(page);
  await page.locator('#btn-start-cook').click();
  // Move wall time with no interval callbacks, as if the process was suspended.
  await page.clock.setSystemTime(new Date('2026-11-02T12:01:00Z'));
  await page.reload();
  await expect(page.locator('#confirm-overlay')).toHaveClass(/open/);
  expect(await page.evaluate(() => window.gm.cook.stage)).toBe(0);
  expect(await page.evaluate(() => window.gm.cook.pendingStage)).toBe(1);
  await page.locator('#btn-confirm-action').click();
  expect(await page.evaluate(() => window.gm.cook.stage)).toBe(1);
});

test('paused cook stays paused through reload and resumes from saved remainder', async ({ page }) => {
  await configure(page);
  await shortTimes(page, 60);
  await page.locator('#btn-start-cook').click();
  await page.clock.fastForward(10000);
  await page.locator('#btn-pause').click();
  const remaining = await page.evaluate(() => window.gm.cook.remaining);
  await page.clock.fastForward(90000);
  await page.reload();
  await expect(page.locator('#btn-pause')).toHaveText('Resume');
  expect(await page.evaluate(() => window.gm.cook.remaining)).toBe(remaining);
  await page.locator('#btn-pause').click();
  await page.clock.fastForward(1000);
  expect(await page.evaluate(() => window.gm.cook.remaining)).toBeLessThan(remaining);
});

test('queue snooze restarts the expired lane and leaves main cook untouched', async ({ page }) => {
  await configure(page);
  await shortTimes(page);
  await addLane(page);
  await page.locator('.lane-btn[data-act="start"]').click();
  await page.clock.fastForward(2100);
  await page.locator('#btn-confirm-snooze').click();
  expect(await page.evaluate(() => window.gm.cook.running)).toBe(false);
  expect(await page.evaluate(() => window.gm.queue[1].running)).toBe(true);
  expect(await page.evaluate(() => window.gm.queue[1].remaining)).toBe(30);
  await page.clock.fastForward(31000);
  await expect(page.locator('#confirm-overlay')).toHaveClass(/open/);
  await page.locator('#btn-confirm-action').click();
  expect(await page.evaluate(() => window.gm.queue[1].stage)).toBe(1);
});

test('simultaneous lane and main expiries retain every acknowledgement through reload', async ({ page }) => {
  await configure(page);
  await shortTimes(page);
  await addLane(page);
  await addLane(page);
  await page.locator('.lane-btn[data-act="start"]').first().click();
  await page.locator('.lane-btn[data-act="start"]').click();
  await page.locator('#tab-timer').click();
  await page.locator('#btn-start-cook').click();
  await page.clock.fastForward(2100);
  await page.reload();
  expect(await page.evaluate(() => Object.values(window.gm.queue).filter(lane => lane.pendingStage === 1).length)).toBe(2);
  for (let index = 0; index < 3; index++) {
    await expect(page.locator('#confirm-overlay')).toHaveClass(/open/);
    await page.locator('#btn-confirm-action').click();
  }
  await expect(page.locator('#confirm-overlay')).not.toHaveClass(/open/);
  expect(await page.evaluate(() => [window.gm.cook.stage, ...Object.values(window.gm.queue).map(lane => lane.stage)])).toEqual([1, 1, 1]);
});

test('queue waiting and paused lanes survive reload', async ({ page }) => {
  await configure(page);
  await shortTimes(page, 60);
  await addLane(page);
  await addLane(page);
  await page.locator('.lane-btn[data-act="start"]').first().click();
  await page.clock.fastForward(10000);
  await page.locator('.lane-btn[data-act="pause"]').click();
  const remaining = await page.evaluate(() => window.gm.queue[1].remaining);
  await page.clock.fastForward(100000);
  await page.reload();
  await page.locator('#tab-queue').click();
  await expect(page.locator('.lane-card')).toHaveCount(2);
  expect(await page.evaluate(() => window.gm.queue[1].remaining)).toBe(remaining);
  expect(await page.evaluate(() => window.gm.queue[1].paused)).toBe(true);
  expect(await page.evaluate(() => window.gm.queue[2].stage)).toBe(-1);
  await page.locator('.lane-btn[data-act="pause"]').click();
  await page.clock.fastForward(51000);
  await expect(page.locator('#confirm-overlay')).toHaveClass(/open/);
});

test('rest completion requires acknowledgement and completed cook remains reviewable after reload', async ({ page }) => {
  await configure(page);
  await shortTimes(page);
  await page.locator('#btn-start-cook').click();
  for (let stage = 0; stage < 4; stage++) {
    await page.clock.fastForward(2100);
    await expect(page.locator('#confirm-overlay')).toHaveClass(/open/);
    if (stage === 3) {
      expect(await page.evaluate(() => window.gm.cook.completed)).toBe(false);
      await page.reload();
    }
    await page.locator('#btn-confirm-action').click();
  }
  await expect(page.locator('#howd-prompt')).toBeVisible();
  await page.reload();
  await expect(page.locator('#timer-stage-small')).toHaveText('Done');
  await expect(page.locator('#howd-prompt')).toBeVisible();
});

test('native notification identities and cancellation are independent for main and lanes', async ({ page }) => {
  await nativeMock(page);
  await configure(page);
  await shortTimes(page, 60);
  await addLane(page);
  await addLane(page);
  await page.locator('.lane-btn[data-act="start"]').first().click();
  await page.locator('.lane-btn[data-act="start"]').click();
  await page.locator('#tab-timer').click();
  await page.locator('#btn-start-cook').click();
  await expect.poll(() => page.evaluate(() => window.nativeCalls.filter(call => call.method === 'schedule').length)).toBe(3);
  const ids = await page.evaluate(() => window.nativeCalls.filter(call => call.method === 'schedule').flatMap(call => call.notifications.map(note => note.id)));
  expect(new Set(ids).size).toBe(3);
  await page.locator('#tab-queue').click();
  await page.locator('[data-act="pause"][data-id="1"]').click();
  const laneId = await page.evaluate(() => JSON.parse(localStorage.getItem('gm-runtime-v1')).queue.find(lane => lane.id === 2).notificationIds[0]);
  await expect.poll(() => page.evaluate(() => window.nativeCalls.filter(call => call.method === 'cancel').length)).toBe(1);
  const cancelled = await page.evaluate(() => window.nativeCalls.filter(call => call.method === 'cancel').flatMap(call => call.notifications.map(note => note.id)));
  expect(cancelled).not.toContain(laneId);
  expect(cancelled).not.toContain(1);
  await page.locator('[data-act="pause"][data-id="1"]').click();
  await expect.poll(() => page.evaluate(() => window.nativeCalls.filter(call => call.method === 'schedule').length)).toBe(4);
});

test('denied notification permission reports recovery without stopping timer', async ({ page }) => {
  await nativeMock(page, { permission: 'denied' });
  await configure(page);
  await page.locator('#btn-start-cook').click();
  await expect(page.locator('#toast')).toContainText('Enable notifications in Settings');
  expect(await page.evaluate(() => window.gm.cook.running)).toBe(true);
});

test('failed notification scheduling reports that background alerts are unavailable', async ({ page }) => {
  await nativeMock(page, { scheduleFailure: true });
  await configure(page);
  await page.locator('#btn-start-cook').click();
  await expect(page.locator('#toast')).toContainText('could not be scheduled');
});

test('native surfaces sync with start/resume/restore and end on pause/cancel; routes never start timers', async ({ page }) => {
  await nativeMock(page, { route: 'temperatures' });
  await expect(page.locator('#panel-temp')).toBeVisible();
  expect(await page.evaluate(() => window.gm.cook.active)).toBe(false);
  await page.evaluate(() => window.nativeRouteListener({ destination: 'configure' }));
  await configure(page);
  await page.locator('#btn-start-cook').click();
  await expect.poll(() => page.evaluate(() => window.nativeCalls.some(call => call.method === 'sync' && call.cook.phase === 'Side A' && call.cook.endsAt > call.cook.startedAt))).toBe(true);
  await page.locator('#btn-pause').click();
  await expect.poll(() => page.evaluate(() => window.nativeCalls.filter(call => ['sync', 'end'].includes(call.method)).at(-1).method)).toBe('end');
  await page.locator('#btn-pause').click();
  await expect.poll(() => page.evaluate(() => window.nativeCalls.filter(call => ['sync', 'end'].includes(call.method)).at(-1).method)).toBe('sync');
  await page.reload();
  await expect.poll(() => page.evaluate(() => window.nativeCalls.some(call => call.method === 'sync'))).toBe(true);
  await page.evaluate(() => window.nativeRouteListener({ destination: 'active' }));
  await expect(page.locator('#active-timer')).toBeVisible();
  await page.locator('#btn-cancel').click();
  await expect.poll(() => page.evaluate(() => window.nativeCalls.filter(call => ['sync', 'end'].includes(call.method)).at(-1).method)).toBe('end');
  await page.reload();
  await page.evaluate(() => window.nativeRouteListener({ destination: 'configure' }));
  await expect(page.locator('#setup-form')).toBeVisible();
});

test('runtime storage failure warns without pretending the cook is protected', async ({ page }) => {
  await configure(page);
  await page.evaluate(() => { Storage.prototype.setItem = () => { throw new Error('QuotaExceededError'); }; });
  await page.locator('#btn-start-cook').click();
  await expect(page.locator('#toast')).toContainText('Timer could not be saved');
  expect(await page.evaluate(() => window.gm.cook.running)).toBe(true);
});

test('failed log save retains the form and entry for retry without duplicate logs', async ({ page }) => {
  await configure(page);
  await shortTimes(page);
  await page.locator('#btn-start-cook').click();
  for (let stage = 0; stage < 4; stage++) {
    await page.clock.fastForward(2100);
    await page.locator('#btn-confirm-action').click();
  }
  await page.locator('#howd-prompt button').first().click();
  await page.locator('#fav-name-input').fill('Saturday turkey');
  await page.evaluate(() => {
    const set = Storage.prototype.setItem;
    window.restoreStorage = () => { Storage.prototype.setItem = set; };
    Storage.prototype.setItem = () => { throw new Error('QuotaExceededError'); };
  });
  await page.locator('#btn-confirm-save').click();
  await expect(page.locator('#save-modal')).toHaveClass(/open/);
  await expect(page.locator('#fav-name-input')).toHaveValue('Saturday turkey');
  await expect(page.locator('#toast')).toContainText('Cook was not saved');
  expect(await page.evaluate(() => window.gm.log.length)).toBe(0);
  await page.evaluate(() => window.restoreStorage());
  await page.locator('#btn-confirm-save').click();
  await expect(page.locator('#save-modal')).not.toHaveClass(/open/);
  expect(await page.evaluate(() => window.gm.log.length)).toBe(1);
  await page.reload();
  await page.locator('#tab-log').click();
  await expect(page.locator('.log-entry .name')).toHaveText('Saturday turkey');
});

test('stage dialog traps keyboard focus and Escape preserves its pending cook', async ({ page }) => {
  await configure(page);
  await shortTimes(page);
  await page.locator('#btn-start-cook').click();
  await page.clock.fastForward(2100);
  await expect(page.locator('#btn-confirm-action')).toBeFocused();
  await page.keyboard.press('Shift+Tab');
  await expect(page.locator('#btn-confirm-snooze')).toBeFocused();
  await page.keyboard.press('Tab');
  await expect(page.locator('#btn-confirm-action')).toBeFocused();
  await page.keyboard.press('Escape');
  await expect(page.locator('#confirm-overlay')).toHaveClass(/open/);
  expect(await page.evaluate(() => window.gm.cook.pendingStage)).toBe(1);
  await page.locator('#btn-confirm-action').click();
  await expect(page.locator('#btn-cancel')).toBeFocused();
});

test('log saves the completed cook snapshot after setup values change', async ({ page }) => {
  await configure(page, 'burger', 'Turkey Burger');
  await shortTimes(page);
  await page.locator('#btn-start-cook').click();
  for (let stage = 0; stage < 4; stage++) {
    await page.clock.fastForward(2100);
    await page.locator('#btn-confirm-action').click();
  }
  // Setup may be changed by a later recipe selection; the completed cook owns
  // its configuration, estimated stages and safety target independently.
  await page.evaluate(() => {
    Object.assign(window.gm.state, { cut: 'Ribeye', protein: 'beef', doneTemp: 125 });
    window.gm.times.sideA = 999;
  });
  await page.locator('#howd-prompt button').first().click();
  await expect(page.locator('#fav-name-input')).toHaveValue(/^Turkey Burger/);
  await page.locator('#btn-confirm-save').click();
  const entry = await page.evaluate(() => window.gm.log[0]);
  expect(entry.cut).toBe('Turkey Burger');
  expect(entry.doneTemp).toBe(165);
  expect(entry.times.sideA).toBe(2);
  await page.reload();
  await expect(page.locator('#howd-prompt')).toBeHidden();
});

test('completed lane acknowledgement and status persist until removal', async ({ page }) => {
  await configure(page);
  await shortTimes(page);
  await addLane(page);
  await page.locator('[data-act="start"]').click();
  for (let stage = 0; stage < 4; stage++) {
    await page.clock.fastForward(2100);
    await page.locator('#btn-confirm-action').click();
  }
  await expect(page.locator('.lane-tag')).toHaveText('DONE');
  await page.reload();
  await page.locator('#tab-queue').click();
  await expect(page.locator('.lane-tag')).toHaveText('DONE');
  await page.locator('[data-act="remove"]').click();
  await page.reload();
  expect(await page.evaluate(() => Object.keys(window.gm.queue).length)).toBe(0);
});

test('native activity calls serialize so a delayed start cannot overtake cancellation', async ({ page }) => {
  await nativeMock(page);
  await page.evaluate(() => {
    const native = window.Capacitor.Plugins.GrillMasterNative;
    native.syncCook = async () => {
      window.nativeCalls.push({ method: 'sync-started' });
      await new Promise(resolve => { window.releaseNativeSync = resolve; });
      window.nativeCalls.push({ method: 'sync-finished' });
    };
  });
  await configure(page);
  await page.locator('#btn-start-cook').click();
  await expect.poll(() => page.evaluate(() => typeof window.releaseNativeSync)).toBe('function');
  await page.evaluate(() => { window.nativeCalls = []; });
  await page.locator('#btn-cancel').click();
  expect(await page.evaluate(() => window.nativeCalls.some(call => call.method === 'end'))).toBe(false);
  await page.evaluate(() => window.releaseNativeSync());
  await expect.poll(() => page.evaluate(() => window.nativeCalls.filter(call => ['sync-finished', 'end'].includes(call.method)).map(call => call.method))).toEqual(['sync-finished', 'end']);
});

test('native Preferences writes preserve the latest paused snapshot in invocation order', async ({ page }) => {
  await page.addInitScript(() => {
    window.preferenceWrites = [];
    window.releasePreferenceWrite = null;
    window.Capacitor = { Plugins: { Preferences: {
      get: async ({ key }) => ({ value: localStorage.getItem(key) }),
      set: async ({ key, value }) => {
        window.preferenceWrites.push(JSON.parse(value));
        await new Promise(resolve => { window.releasePreferenceWrite = resolve; });
        localStorage.setItem(key, value);
      },
    } } };
  });
  await page.reload();
  await configure(page);
  await shortTimes(page, 60);
  await page.locator('#btn-start-cook').click();
  await page.locator('#btn-pause').click();
  expect(await page.evaluate(() => window.preferenceWrites.length)).toBe(1);
  await page.evaluate(() => window.releasePreferenceWrite());
  await expect.poll(() => page.evaluate(() => window.preferenceWrites.length)).toBe(2);
  expect(await page.evaluate(() => window.preferenceWrites[0].cook.paused)).toBe(false);
  expect(await page.evaluate(() => window.preferenceWrites[1].cook.paused)).toBe(true);
  await page.evaluate(() => window.releasePreferenceWrite());
  await expect.poll(() => page.evaluate(() => JSON.parse(localStorage.getItem('gm-runtime-v1')).cook.paused)).toBe(true);
  await page.reload();
  await expect(page.locator('#btn-pause')).toHaveText('Resume');
});

test('save sheet supports keyboard dismissal and restores its rating controls', async ({ page }) => {
  await configure(page);
  await shortTimes(page);
  await page.locator('#btn-start-cook').click();
  for (let stage = 0; stage < 4; stage++) {
    await page.clock.fastForward(2100);
    await page.locator('#btn-confirm-action').click();
  }
  await page.locator('#howd-prompt button').first().click();
  await expect(page.locator('#fav-name-input')).toBeFocused();
  await page.keyboard.press('Shift+Tab');
  await expect(page.locator('#btn-confirm-save')).toBeFocused();
  await page.keyboard.press('Tab');
  await expect(page.locator('#fav-name-input')).toBeFocused();
  await page.keyboard.press('Escape');
  await expect(page.locator('#save-modal')).not.toHaveClass(/open/);
  await expect(page.locator('#howd-prompt')).toBeVisible();
  expect(await page.evaluate(() => document.activeElement.closest('#howd-prompt') !== null)).toBe(true);
});
