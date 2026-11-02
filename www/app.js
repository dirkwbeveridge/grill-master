/* ═════════════════════════════════════════════════════════════════
   GRILL MASTER — Foundation build
   Pitmaster's notebook. Charred mood, Editorial grammar, Ember accent.
   Single-screen setup, Butcher Chart icons, The Log (history).
   ═════════════════════════════════════════════════════════════════ */

/* ─── BUTCHER CHART ICONS ───────────────────────────────────────────
   Solid-fill SVG silhouettes, viewBox 38×28, currentColor fill.
   Beef redrawn as a single unified silhouette per design decision —
   legs are part of the main body shape, not separate rectangles.
   ───────────────────────────────────────────────────────────────── */
const ICONS = {
  beef: `
    <svg width="38" height="28" viewBox="0 0 38 28" fill="currentColor" aria-hidden="true">
      <!-- Single unified silhouette: cow loaf with head on left.
           Matches the chunky-blob aesthetic of pork/lamb/fish. -->
      <path d="M 9 14
               C 9 12, 11 10, 14 10
               C 19 8, 26 8, 31 9
               C 34 10, 35 11, 35 14
               L 35 18
               C 35 21, 33 22, 30 22
               L 14 22
               C 11 22, 9 21, 9 19
               L 3 19
               C 1.5 19, 1 18, 1 16.5
               C 1 15, 1.5 14, 3 14
               Z"/>
      <!-- Ear (small triangle peeking above head) -->
      <path d="M 5 11 L 6 8 L 7.5 12 Z"/>
      <!-- Tail (small triangle off right end) -->
      <path d="M 35 11 L 38 8 L 36.5 13 Z"/>
      <!-- Eye (cutout dot in head) -->
      <circle cx="3.6" cy="16.5" r="0.7" fill="var(--bg)"/>
      <!-- Spots (subtle ellipses for cow markings) -->
      <ellipse cx="17" cy="13" rx="3" ry="1.5" fill="var(--bg)"/>
      <ellipse cx="27" cy="17" rx="2.4" ry="1.4" fill="var(--bg)"/>
    </svg>`,
  pork: `
    <svg width="38" height="28" viewBox="0 0 38 28" fill="currentColor" aria-hidden="true">
      <path d="M14 4 L 22 4 L 24 6 L 24 9 L 28 9 C 32 9, 35 12, 35 16 C 35 21, 31 25, 25 26 L 12 26 C 7 26, 4 22, 4 17 C 4 12, 7 8, 12 7 Z"/>
      <ellipse cx="20" cy="6" rx="4" ry="2.5" fill="var(--bg)"/>
    </svg>`,
  poultry: `
    <svg width="38" height="28" viewBox="0 0 38 28" fill="currentColor" aria-hidden="true">
      <ellipse cx="14" cy="14" rx="10" ry="9"/>
      <rect x="22" y="12" width="12" height="4" rx="2"/>
      <circle cx="33" cy="11" r="2.5"/>
      <circle cx="33" cy="17" r="2.5"/>
    </svg>`,
  lamb: `
    <svg width="38" height="28" viewBox="0 0 38 28" fill="currentColor" aria-hidden="true">
      <path d="M10 12 C 8 8, 12 4, 18 4 C 26 4, 32 10, 32 16 C 32 22, 27 26, 20 26 C 14 26, 10 22, 10 17 Z"/>
      <rect x="2" y="13" width="9" height="3" rx="1.5"/>
      <circle cx="2.5" cy="14.5" r="2"/>
    </svg>`,
  fish: `
    <svg width="38" height="28" viewBox="0 0 38 28" fill="currentColor" aria-hidden="true">
      <path d="M4 14 C 5 7, 12 4, 19 4 C 26 4, 30 8, 31 14 C 30 20, 26 24, 19 24 C 12 24, 5 21, 4 14 Z"/>
      <path d="M31 14 L 36 6 L 35 14 L 36 22 Z"/>
      <circle cx="10" cy="11" r="1.4" fill="var(--bg)"/>
      <path d="M14 6 Q 12.5 14, 14 22" fill="none" stroke="var(--bg)" stroke-width="1"/>
    </svg>`,
  burger: `
    <svg width="38" height="28" viewBox="0 0 38 28" fill="currentColor" aria-hidden="true">
      <path d="M3 13 C 3 7, 10 3, 19 3 C 28 3, 35 7, 35 13 Z"/>
      <path d="M2 14 L 36 14 L 36 18 C 33 19, 30 18, 27 19 C 24 18, 21 19, 18 18 C 15 19, 12 18, 9 19 C 6 18, 4 19, 2 18 Z"/>
      <path d="M3 19 L 35 19 C 35 23, 28 26, 19 26 C 10 26, 3 23, 3 19 Z"/>
      <ellipse cx="12" cy="7" rx="0.7" ry="0.5" fill="var(--bg)"/>
      <ellipse cx="19" cy="5.5" rx="0.7" ry="0.5" fill="var(--bg)"/>
      <ellipse cx="26" cy="7" rx="0.7" ry="0.5" fill="var(--bg)"/>
    </svg>`,
  sausage: `
    <svg width="38" height="28" viewBox="0 0 38 28" fill="currentColor" aria-hidden="true">
      <path d="M5 14 C 5 9, 9 7, 14 7 L 28 9 C 33 9.5, 35 13, 35 16 C 35 19, 32 21, 28 21 L 13 19 C 8 18.5, 5 18, 5 14 Z"/>
      <path d="M8 11 Q 5 14, 8 17" fill="none" stroke="var(--bg)" stroke-width="1"/>
      <path d="M19 9 Q 17 14, 19 20" fill="none" stroke="var(--bg)" stroke-width="0.8"/>
    </svg>`,
  veggie: `
    <svg width="38" height="28" viewBox="0 0 38 28" fill="currentColor" aria-hidden="true">
      <path d="M13 6 L 17 1 L 18 8 Z"/>
      <path d="M21 8 L 25 1 L 26 7 Z"/>
      <ellipse cx="19" cy="17" rx="9" ry="9"/>
      <circle cx="15" cy="13" r="0.8" fill="var(--bg)"/>
      <circle cx="19" cy="12" r="0.8" fill="var(--bg)"/>
      <circle cx="23" cy="13" r="0.8" fill="var(--bg)"/>
      <circle cx="14" cy="17" r="0.8" fill="var(--bg)"/>
      <circle cx="19" cy="17" r="0.8" fill="var(--bg)"/>
      <circle cx="24" cy="17" r="0.8" fill="var(--bg)"/>
      <circle cx="15" cy="21" r="0.8" fill="var(--bg)"/>
      <circle cx="19" cy="22" r="0.8" fill="var(--bg)"/>
      <circle cx="23" cy="21" r="0.8" fill="var(--bg)"/>
    </svg>`,
};

/* ─── MEAT DATABASE ─────────────────────────────────────────────── */
const MEAT_DB = {
  beef: {
    label: 'Beef',
    cuts: [
      { name: 'Ribeye', factor: 1.10 },
      { name: 'Filet Mignon', factor: 0.90 },
      { name: 'NY Strip', factor: 1.00 },
      { name: 'Sirloin', factor: 0.85 },
      { name: 'T-Bone', factor: 1.20 },
      { name: 'Porterhouse', factor: 1.25 },
      { name: 'Hanger', factor: 0.95 },
      { name: 'Flank', factor: 0.80 },
    ],
    doneness: [
      { label: 'Rare', temp: 125, factor: 0.75 },
      { label: 'Med-Rare', temp: 135, factor: 1.00 },
      { label: 'Medium', temp: 145, factor: 1.25 },
      { label: 'Well', temp: 160, factor: 1.60 },
    ],
  },
  pork: {
    label: 'Pork',
    cuts: [
      { name: 'Pork Chop', factor: 1.15 },
      { name: 'Tenderloin', factor: 1.00 },
      { name: 'Bacon Steak', factor: 0.70 },
      { name: 'Spare Ribs', factor: 1.40 },
    ],
    doneness: [
      { label: 'Medium', temp: 145, factor: 1.20 },
      { label: 'Well Done', temp: 160, factor: 1.60 },
    ],
  },
  poultry: {
    label: 'Poultry',
    cuts: [
      { name: 'Chicken Breast', factor: 1.20 },
      { name: 'Chicken Thigh', factor: 1.10 },
      { name: 'Turkey Breast', factor: 1.30 },
    ],
    doneness: [
      { label: 'Safe (165°F)', temp: 165, factor: 1.80 },
    ],
  },
  lamb: {
    label: 'Lamb',
    cuts: [
      { name: 'Lamb Chops', factor: 0.80 },
      { name: 'Lamb Loin', factor: 0.90 },
      { name: 'Lamb Leg', factor: 1.10 },
    ],
    doneness: [
      { label: 'Med-Rare', temp: 135, factor: 1.00 },
      { label: 'Medium', temp: 145, factor: 1.30 },
    ],
  },
  fish: {
    label: 'Fish',
    cuts: [
      { name: 'Salmon Fillet', factor: 0.85 },
      { name: 'Tuna Steak', factor: 0.70 },
      { name: 'Swordfish', factor: 1.00 },
      { name: 'Halibut', factor: 0.90 },
    ],
    doneness: [
      { label: 'Medium', temp: 135, factor: 0.80 },
      { label: 'Well Done', temp: 145, factor: 1.10 },
    ],
  },
  burger: {
    label: 'Burger',
    cuts: [
      { name: 'Beef Patty', factor: 1.00 },
      { name: 'Turkey Burger', factor: 0.90 },
      { name: 'Veggie Burger', factor: 0.75 },
      { name: 'Lamb Burger', factor: 1.05 },
    ],
    doneness: [
      { label: 'Medium', temp: 160, factor: 1.20 },
      { label: 'Well Done', temp: 165, factor: 1.50 },
    ],
  },
  sausage: {
    label: 'Sausage',
    cuts: [
      { name: 'Bratwurst', factor: 1.10 },
      { name: 'Italian Sausage', factor: 1.05 },
      { name: 'Hot Dog', factor: 0.60 },
      { name: 'Chorizo', factor: 1.00 },
      { name: 'Kielbasa', factor: 1.15 },
    ],
    doneness: [
      { label: 'Safe (160°F)', temp: 160, factor: 1.40 },
    ],
  },
  veggie: {
    label: 'Veggie',
    cuts: [
      { name: 'Corn on Cob', factor: 1.20 },
      { name: 'Asparagus', factor: 0.50 },
      { name: 'Bell Pepper', factor: 0.80 },
      { name: 'Portobello', factor: 0.90 },
      { name: 'Zucchini', factor: 0.70 },
      { name: 'Eggplant', factor: 0.85 },
    ],
    doneness: [
      { label: 'Tender', temp: 180, factor: 1.00 },
      { label: 'Charred', temp: 190, factor: 1.30 },
    ],
  },
};

const PROTEIN_ORDER = ['beef', 'pork', 'poultry', 'lamb', 'fish', 'burger', 'sausage', 'veggie'];
const NO_THICKNESS = new Set(['Hot Dog', 'Bratwurst', 'Italian Sausage', 'Chorizo', 'Kielbasa', 'Corn on Cob', 'Asparagus']);

/* ─── STATE ─────────────────────────────────────────────────────── */
const state = {
  grill: 'gas',
  grillFactor: 1.0,
  protein: null,
  cut: null,
  cutFactor: 1.0,
  thickness: 1.0,
  heat: null,
  heatFactor: 1.0,
  doneness: null,
  doneTemp: null,
  doneFactor: 1.0,
  winter: false,
  altitude: false,
};

const times = { sideA: 0, sideB: 0, finish: 0, rest: 0 };

const cook = {
  running: false,
  paused: false,
  stage: 0,
  total: 0,
  remaining: 0,
  startTime: 0,
  deadline: 0,
  active: false,
  completed: false,
  config: null,
  tickInterval: null,
  pendingStage: undefined,
  notificationIds: [],
};

let log = [];           // cook history (formerly favorites)
let nextLogId = 1;
let audioCtx = null;
let alarmNode = null;

/* ─── QUEUE (multi-lane parallel cooks) ─────────────────────────── */
const queue = {};       // map laneId → lane object
let nextLaneId = 1;
const MAX_LANES = 4;

/* ─── PERSISTENCE (Capacitor Preferences if available, else localStorage) ── */
const RUNTIME_KEY = 'gm-runtime-v1';
let storageWrites = Promise.resolve();
let pendingConfirmations = [];
let runtimeWarningShown = false;

async function readStored(key) {
  const preferences = window.Capacitor?.Plugins?.Preferences;
  return preferences ? (await preferences.get({ key })).value : localStorage.getItem(key);
}
function writeStored(key, value) {
  // Capture each snapshot at the call site; serialize native writes so an older
  // snapshot can never finish after a newer one.
  const preferences = window.Capacitor?.Plugins?.Preferences;
  if (!preferences) {
    try { localStorage.setItem(key, value); return Promise.resolve(true); }
    catch { return Promise.resolve(false); }
  }
  const result = storageWrites.then(() => preferences.set({ key, value })).then(() => true, () => false);
  storageWrites = result.then(() => undefined);
  return result;
}
async function persistLoad() {
  try {
    const raw = await readStored('gm-log');
    if (raw) {
      const data = JSON.parse(raw);
      log = Array.isArray(data.log) ? data.log : [];
      nextLogId = Math.max(data.nextLogId || 1, ...log.map(entry => Number(entry.id) + 1));
    }
  } catch { showToast('Cook history could not be loaded. Try reopening the app.'); }
}
function persistSave() {
  return writeStored('gm-log', JSON.stringify({ log, nextLogId }));
}
function serialTimer(timer) {
  const { tickInterval, interval, notificationTask, ...saved } = timer;
  return saved;
}
function persistRuntime() {
  const saved = {
    version: 1, state: { ...state }, times: { ...times },
    cook: serialTimer(cook), queue: Object.values(queue).map(serialTimer),
    nextLaneId, pendingConfirmations,
  };
  return writeStored(RUNTIME_KEY, JSON.stringify(saved)).then(ok => {
    if (!ok && !runtimeWarningShown) {
      runtimeWarningShown = true;
      showToast('Timer could not be saved. Keep the app open; retry after freeing storage.');
    }
    if (ok) runtimeWarningShown = false;
    return ok;
  });
}
function validTimer(timer) {
  return timer && Number.isInteger(timer.stage) && timer.stage >= -1 && timer.stage <= 4 &&
    Number.isFinite(timer.remaining) && timer.remaining >= 0 && Number.isFinite(timer.total) &&
    timer.times && STAGES.every(stage => Number.isFinite(timer.times[stage]) && timer.times[stage] >= 0) &&
    (timer.paused || !timer.running || Number.isFinite(timer.deadline));
}
async function restoreRuntime() {
  try {
    const raw = await readStored(RUNTIME_KEY);
    if (!raw) return;
    const saved = JSON.parse(raw);
    if (saved.version !== 1) return;
    if (saved.state?.protein && MEAT_DB[saved.state.protein]) {
      const selection = saved.state;
      selectProtein(selection.protein);
      Object.assign(state, selection);
      syncSetupUI();
      calculate();
    }
    if (saved.cook?.active && validTimer(saved.cook)) {
      Object.assign(cook, saved.cook, { tickInterval: null });
      Object.assign(times, cook.times);
      renderActiveCook();
      if (cook.completed) renderCookFinished();
      else {
        updateStageUI(cook.stage);
        $('timer-display').textContent = fmtDisplay(cook.remaining);
        $('btn-pause').textContent = cook.paused ? 'Resume' : 'Pause';
      }
    }
    for (const lane of (Array.isArray(saved.queue) ? saved.queue : []).slice(0, MAX_LANES)) {
      if (Number.isInteger(lane.id) && lane.id > 0 && validTimer(lane)) {
        queue[lane.id] = { ...lane, interval: null };
      }
    }
    nextLaneId = Math.max(saved.nextLaneId || 1, ...Object.keys(queue).map(id => Number(id) + 1));
    pendingConfirmations = (saved.pendingConfirmations || []).filter(item =>
      item.kind === 'main' ? cook.active && cook.pendingStage !== undefined : queue[item.id]?.pendingStage !== undefined);
    // Recover pending acknowledgements even if an interrupted older write omitted the list.
    if (cook.active && cook.pendingStage !== undefined) enqueueConfirmation('main', null, false);
    Object.values(queue).forEach(lane => {
      if (lane.pendingStage !== undefined) enqueueConfirmation('lane', lane.id, false);
    });
    reconcileTimers();
    renderQueue();
  } catch { showToast('Saved timers could not be restored. Check food with a thermometer.'); }
}

/* ─── HAPTICS (Capacitor optional) ──────────────────────────────── */
function haptic(style = 'medium') {
  try {
    const cap = window.Capacitor;
    if (cap?.Plugins?.Haptics) {
      const styleMap = { light: 'Light', medium: 'Medium', heavy: 'Heavy' };
      cap.Plugins.Haptics.impact({ style: styleMap[style] || 'Medium' });
    }
  } catch (e) { /* ignore */ }
}

/* ─── LOCAL NOTIFICATIONS (Capacitor optional) ──────────────────── */
let notificationTasks = Promise.resolve();
let notificationWarningShown = false;
function notificationWarning(message) {
  if (notificationWarningShown) return;
  notificationWarningShown = true;
  showToast(message);
}
function scheduleStageNotifications(stageIdx, secondsRemaining, owner = cook, laneId = null) {
  const LN = window.Capacitor?.Plugins?.LocalNotifications;
  if (!LN) return Promise.resolve();
  const deadline = owner.deadline;
  const id = laneId === null ? 1 : 1000 + laneId;
  owner.notificationIds = [id];
  persistRuntime();
  notificationTasks = notificationTasks.then(async () => {
    if (!owner.running || owner.paused || owner.deadline !== deadline) return;
    try {
      let perm = await LN.checkPermissions();
      if (perm.display === 'prompt' || perm.display === 'prompt-with-rationale') perm = await LN.requestPermissions();
      if (perm.display !== 'granted') {
        notificationWarning('Alerts are off. Enable notifications in Settings for background timer alerts.');
        return;
      }
      // Permission prompts may outlive a pause/cancel or the timer itself.
      if (!owner.running || owner.paused || owner.deadline !== deadline || deadline <= Date.now()) return;
      const config = owner.config || state;
      await LN.schedule({ notifications: [{ id,
        title: `${laneId === null ? config.cut : owner.label} · ${STAGE_LABELS[stageIdx]} complete`,
        body: stageIdx >= 2 ? temperatureGuidance(config) : STAGE_CONFIRM[stageIdx].sub,
        schedule: { at: new Date(deadline) },
      }] });
      notificationWarningShown = false;
    } catch { notificationWarning('Background alert could not be scheduled. Keep the app open and check notification settings.'); }
  });
  return notificationTasks;
}
function clearScheduledNotifications(owner = cook) {
  const ids = [...(owner.notificationIds || [])];
  owner.notificationIds = [];
  const LN = window.Capacitor?.Plugins?.LocalNotifications;
  if (!LN || !ids.length) return Promise.resolve();
  notificationTasks = notificationTasks.then(async () => {
    try { await LN.cancel({ notifications: ids.map(id => ({ id })) }); }
    catch { notificationWarning('An old alert could not be cleared. Check the timer in the app.'); }
  });
  return notificationTasks;
}
let nativeCookTasks = Promise.resolve();
function syncNativeCook() {
  const native = window.Capacitor?.Plugins?.GrillMasterNative;
  if (!native) return Promise.resolve();
  const config = cook.config || state;
  const active = cook.active && !cook.completed && !cook.paused;
  const snapshot = { cook: {
    id: cook.id || 'main', title: config.cut || 'Grill Master',
    phase: cook.pendingStage !== undefined ? 'Check food' : STAGE_LABELS[cook.stage],
    startedAt: cook.startedAt, endsAt: cook.deadline || Date.now(),
    targetTemperature: config.doneTemp, unit: 'F', active: true,
  } };
  // ActivityKit calls cross async native boundaries. Preserve invocation order
  // so an earlier start cannot resurrect an activity after pause or cancel.
  nativeCookTasks = nativeCookTasks.then(() => active ? native.syncCook(snapshot) : native.endCook()).catch(() => {});
  return nativeCookTasks;
}
function handleNativeRoute({ destination } = {}) {
  if (destination === 'temperatures') switchTab('temp');
  else if (destination === 'active') switchTab(cook.active ? 'timer' : laneCount() ? 'queue' : 'timer');
  else if (destination === 'configure') switchTab('timer');
}
function reconcileTimers() {
  if (cook.active && cook.running && !cook.paused && cook.pendingStage === undefined) {
    tick();
    if (cook.running) {
      clearInterval(cook.tickInterval);
      cook.tickInterval = setInterval(tick, 250);
      scheduleStageNotifications(cook.stage, cook.remaining);
    }
  }
  Object.values(queue).forEach(lane => {
    if (lane.running && !lane.paused && lane.pendingStage === undefined) {
      tickLane(lane.id);
      if (lane.running) {
        clearInterval(lane.interval);
        lane.interval = setInterval(() => tickLane(lane.id), 500);
        scheduleStageNotifications(lane.stage, lane.remaining, lane, lane.id);
      }
    }
  });
  showNextConfirmation();
  syncNativeCook();
}

/* ─── ELEMENT HELPERS ───────────────────────────────────────────── */
const $ = (id) => document.getElementById(id);
const show = (id) => $(id).classList.remove('hidden');
const hide = (id) => $(id).classList.add('hidden');

/* ─── TABS ──────────────────────────────────────────────────────── */
function switchTab(name) {
  ['timer', 'queue', 'log', 'temp'].forEach(t => {
    $('tab-' + t).classList.toggle('active', t === name);
    $('tab-' + t).setAttribute('aria-selected', t === name);
    $('tab-' + t).tabIndex = t === name ? 0 : -1;
    $('panel-' + t).classList.toggle('active', t === name);
  });
  if (name === 'log') renderLog();
  if (name === 'queue') renderQueue();
}

/* ─── PROTEIN PICKER ────────────────────────────────────────────── */
function buildProteinPicker() {
  const grid = $('protein-grid');
  grid.innerHTML = '';
  PROTEIN_ORDER.forEach(key => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'protein';
    btn.dataset.protein = key;
    btn.setAttribute('aria-pressed', 'false');
    btn.innerHTML = `${ICONS[key]}<span class="lbl">${MEAT_DB[key].label}</span>`;
    btn.addEventListener('click', () => selectProtein(key));
    grid.appendChild(btn);
  });
}

function selectProtein(key) {
  state.protein = key;
  state.cut = null;
  state.cutFactor = 1.0;

  document.querySelectorAll('.protein').forEach(b => {
    const active = b.dataset.protein === key;
    b.classList.toggle('active', active);
    b.setAttribute('aria-pressed', active);
  });
  $('ans-protein').textContent = MEAT_DB[key].label;

  buildCuts(key);
  buildDoneness(key);
  // Auto-select Medium heat so Start Cook is reachable without
  // requiring the user to manually pick heat
  if (!state.heat) {
    state.heat = 'medium';
    state.heatFactor = 1.0;
    document.querySelectorAll('#heat-pills .pill').forEach(b => {
      const active = b.dataset.heat === 'medium';
      b.classList.toggle('active', active);
      b.setAttribute('aria-pressed', active);
    });
    $('ans-heat').textContent = 'Medium';
  }
  show('sect-cut');
  show('sect-heat');
  show('sect-doneness');
  show('sect-env');
  haptic('light');
  calculate();
}

/* ─── CUTS ──────────────────────────────────────────────────────── */
function buildCuts(key) {
  const row = $('cut-pills');
  row.innerHTML = '';
  MEAT_DB[key].cuts.forEach((cut, i) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'pill' + (i === 0 ? ' active' : '');
    btn.dataset.cut = cut.name;
    btn.dataset.factor = cut.factor;
    btn.setAttribute('aria-pressed', i === 0);
    btn.textContent = cut.name;
    btn.addEventListener('click', () => selectCut(cut.name, cut.factor, btn));
    row.appendChild(btn);
  });
  // auto-select first cut
  const first = MEAT_DB[key].cuts[0];
  state.cut = first.name;
  state.cutFactor = first.factor;
  $('ans-cut').textContent = first.name;
  applyThicknessVisibility(first.name);
}

function selectCut(name, factor, btnEl) {
  state.cut = name;
  state.cutFactor = factor;
  document.querySelectorAll('#cut-pills .pill').forEach(b => {
    b.classList.remove('active');
    b.setAttribute('aria-pressed', 'false');
  });
  btnEl.classList.add('active');
  btnEl.setAttribute('aria-pressed', 'true');
  $('ans-cut').textContent = name;
  applyThicknessVisibility(name);
  buildDoneness(state.protein);
  haptic('light');
  calculate();
}

function applyThicknessVisibility(cutName) {
  if (NO_THICKNESS.has(cutName)) {
    hide('sect-thickness');
    state.thickness = 1.0;
  } else {
    show('sect-thickness');
  }
}

/* ─── THICKNESS SLIDER ──────────────────────────────────────────── */
function setupThicknessSlider() {
  const input = $('thickness-input');
  const updateSliderUI = () => {
    const val = parseFloat(input.value);
    state.thickness = val;
    $('thickness-val').textContent = val.toFixed(2).replace('.00', '.0') + '″';
    $('ans-thickness').textContent = val.toFixed(2).replace('.00', '.0') + '″';
    const pct = ((val - 0.5) / (2.5 - 0.5)) * 100;
    $('slider-fill').style.width = pct + '%';
    $('slider-thumb').style.left = pct + '%';
  };
  input.addEventListener('input', () => { updateSliderUI(); calculate(); });
  updateSliderUI();
}

/* ─── HEAT ──────────────────────────────────────────────────────── */
function setupHeatPills() {
  document.querySelectorAll('#heat-pills .pill').forEach(btn => {
    btn.addEventListener('click', () => {
      const key = btn.dataset.heat;
      const factor = parseFloat(btn.dataset.factor);
      state.heat = key;
      state.heatFactor = factor;
      document.querySelectorAll('#heat-pills .pill').forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-pressed', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-pressed', 'true');
      $('ans-heat').textContent = key === 'high' ? 'High' : 'Medium';
      haptic('light');
      calculate();
    });
  });
}

/* ─── DONENESS ──────────────────────────────────────────────────── */
function donenessOptions(config) {
  if (config.protein === 'burger' && config.cut === 'Turkey Burger') {
    return [{ label: 'Safe (165°F)', temp: 165, factor: 1.50 }];
  }
  if (config.protein === 'burger' && config.cut === 'Veggie Burger') {
    return [{ label: 'Package directions', temp: 165, factor: 1.20 }];
  }
  return MEAT_DB[config.protein].doneness;
}
function normalizeTemperature(config) {
  const option = donenessOptions(config).find(opt => opt.label === config.doneness) || donenessOptions(config)[0];
  config.doneness = option.label;
  config.doneTemp = option.temp;
  config.doneFactor = option.factor;
}
function temperatureGuidance(config) {
  if (config.protein === 'poultry' || config.cut === 'Turkey Burger') return 'Check the thickest part with a thermometer: at least 165°F before removing from heat. Time alone cannot confirm safety.';
  if (config.protein === 'burger' && config.cut !== 'Veggie Burger' || config.protein === 'sausage') return 'Confirm at least 160°F internally with a thermometer before removing from heat. Poultry sausage needs 165°F; follow package directions.';
  if (config.protein === 'pork') return 'Confirm at least 145°F internally with a thermometer, then rest at least 3 minutes. Carryover varies.';
  if (config.protein === 'fish') return 'USDA guidance: confirm 145°F internally with a thermometer. Lower doneness choices carry greater foodborne illness risk.';
  if (config.protein === 'beef' || config.protein === 'lamb') return 'USDA guidance for whole cuts: confirm 145°F internally, then rest at least 3 minutes. Lower doneness choices carry greater foodborne illness risk.';
  return 'Follow package cooking directions and check with a thermometer when required. Time is an estimate.';
}
function buildDoneness(key, preserve = false) {
  const row = $('doneness-pills');
  row.innerHTML = '';
  const options = donenessOptions(state);
  const chosen = preserve ? options.find(opt => opt.label === state.doneness) || options[0] : options[0];
  options.forEach((opt, i) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'pill' + (opt === chosen ? ' active' : '');
    btn.setAttribute('aria-pressed', opt === chosen);
    btn.textContent = opt.label;
    btn.addEventListener('click', () => {
      state.doneness = opt.label;
      state.doneTemp = opt.temp;
      state.doneFactor = opt.factor;
      row.querySelectorAll('.pill').forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-pressed', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-pressed', 'true');
      $('ans-doneness').textContent = opt.label;
      haptic('light');
      calculate();
    });
    row.appendChild(btn);
  });
  // auto-select first
  const first = chosen;
  state.doneness = first.label;
  state.doneTemp = first.temp;
  state.doneFactor = first.factor;
  $('ans-doneness').textContent = first.label;
}

/* ─── GRILL TYPE (Gas / Charcoal) ───────────────────────────────── */
function setupGrillPills() {
  document.querySelectorAll('#grill-pills .pill').forEach(btn => {
    btn.addEventListener('click', () => {
      const grill = btn.dataset.grill;
      state.grill = grill;
      // Charcoal differs substantially from gas: harder to dial heat,
      // benefits from two-zone setup, longer indirect/rest portions.
      // Reflect that with a noticeable multiplier and adjusted stage split.
      state.grillFactor = grill === 'charcoal' ? 1.15 : 1.0;
      document.querySelectorAll('#grill-pills .pill').forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-pressed', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-pressed', 'true');
      $('ans-grill').textContent = grill === 'charcoal' ? 'Charcoal' : 'Gas';
      $('charcoal-cue').classList.toggle('hidden', grill !== 'charcoal');
      haptic('light');
      calculate();
    });
  });
}

/* ─── ENV TOGGLES ───────────────────────────────────────────────── */
function setupEnvToggles() {
  $('toggle-winter').addEventListener('click', () => {
    state.winter = !state.winter;
    $('toggle-winter').classList.toggle('on', state.winter);
    $('toggle-winter').setAttribute('aria-pressed', state.winter);
    haptic('light');
    calculate();
  });
  $('toggle-altitude').addEventListener('click', () => {
    state.altitude = !state.altitude;
    $('toggle-altitude').classList.toggle('on', state.altitude);
    $('toggle-altitude').setAttribute('aria-pressed', state.altitude);
    haptic('light');
    calculate();
  });
}

/* ─── CALCULATE ─────────────────────────────────────────────────── */
function calculate() {
  if (!state.protein || !state.cut || !state.heat || !state.doneness) return;

  normalizeTemperature(state);
  const base = 7.5;
  let totalMins = base * state.thickness * state.doneFactor * state.cutFactor * state.heatFactor * state.grillFactor;
  if (state.winter) totalMins *= 1.15;
  if (state.altitude) totalMins *= 1.25;

  // Charcoal grills run hotter on the direct zone but rely more heavily
  // on indirect cooking. Bias more time to the finish stage when on charcoal.
  const directShare = state.grill === 'charcoal' ? 0.30 : 0.35;
  const sideA = Math.min(totalMins * directShare, 5) * 60;
  const sideB = sideA;
  const finish = Math.max(0, (totalMins * 60) - sideA - sideB);
  const rest = Math.max(3 * 60, state.thickness * 5 * 60);

  times.sideA = Math.round(sideA);
  times.sideB = Math.round(sideB);
  times.finish = Math.round(finish);
  times.rest = Math.round(rest);

  $('t-side-a').textContent = fmtShort(times.sideA);
  $('t-side-b').textContent = fmtShort(times.sideB);
  $('t-finish').textContent = times.finish > 0 ? fmtShort(times.finish) : '—';
  $('t-rest').textContent = fmtShort(times.rest);

  const parts = [
    `${state.cut} · ${state.thickness}″ · ${state.doneness}`,
    state.heat === 'high' ? 'high heat' : 'med heat',
    state.grill === 'charcoal' ? 'charcoal' : null,
    state.winter ? 'cold' : null,
    state.altitude ? 'altitude' : null,
  ].filter(Boolean);
  $('results-meta-line').textContent = parts.join(' · ');

  // Target temperature shown for proteins where it's meaningful
  if (['beef', 'pork', 'lamb', 'fish'].includes(state.protein)) {
    $('results-target').textContent = `${state.doneTemp}°F`;
  } else if (state.protein === 'veggie' || state.cut === 'Veggie Burger') {
    $('results-target').textContent = state.cut === 'Veggie Burger' ? 'Package directions' : 'Texture guide';
  } else {
    $('results-target').textContent = `${state.doneTemp}°F minimum`;
  }

  show('sect-results');
}

function fmtShort(s) {
  const m = Math.floor(s / 60), sec = Math.floor(s % 60);
  return sec === 0 ? `${m}m` : `${m}:${String(sec).padStart(2, '0')}`;
}
function fmtDisplay(s) {
  const m = Math.floor(s / 60), sec = Math.floor(s % 60);
  return `${m}:${String(sec).padStart(2, '0')}`;
}

/* ─── COOK FLOW ─────────────────────────────────────────────────── */
const STAGES = ['sideA', 'sideB', 'finish', 'rest'];
const STAGE_LABELS = ['Side A', 'Side B', 'Finish', 'Rest'];
const STAGE_INSTRUCTIONS_GAS = [
  "Place on hot grill. Don't move it.",
  "Flip once. Don't press down.",
  'Move to indirect heat. Lid closed.',
  'Off the grill. Tent loose with foil.',
];
const STAGE_INSTRUCTIONS_CHARCOAL = [
  'Direct zone. Lid open. Watch the smoke.',
  "Flip once. Don't press the meat.",
  'Indirect zone. Lid closed. Vents half.',
  'Off the coals. Tent loose with foil.',
];
function stageInstruction(idx) {
  const set = (cook.config || state).grill === 'charcoal' ? STAGE_INSTRUCTIONS_CHARCOAL : STAGE_INSTRUCTIONS_GAS;
  return set[idx] || '';
}

const STAGE_CONFIRM = [
  { eyebrow: 'Stage 1 complete', title: 'Flip.', sub: 'Flip once. Don\'t press down.', action: 'Flipped — start Side B' },
  { eyebrow: 'Stage 2 complete', title: 'Move it.', sub: 'Shift off direct heat. Close the lid.', action: 'Moved — start Finish' },
  { eyebrow: 'Stage 3 complete', title: 'Pull it.', sub: 'Off the heat. Tent loose. Walk away.', action: 'Pulled — start Rest' },
  { eyebrow: 'Cook complete', title: 'Done.', sub: 'Slice across the grain. Serve.', action: 'Eat' },
];

function renderActiveCook() {
  const config = cook.config || state;
  hide('setup-form');
  show('active-timer');
  $('timer-spec').textContent = `${config.cut} · ${config.thickness}″ · ${config.doneness}`.toUpperCase();
  const setTemperature = (id, text, target = false) => {
    const value = document.createElement('span');
    value.className = target ? 'v target' : 'v';
    value.textContent = text;
    $(id).replaceChildren(value);
  };
  setTemperature('timer-target', `${config.doneTemp}°F`, true);
  setTemperature('timer-pull', config.protein === 'veggie' || config.cut === 'Veggie Burger' ? 'See package' : `${Math.max(config.doneTemp, config.protein === 'fish' || ['beef', 'pork', 'lamb'].includes(config.protein) ? 145 : config.doneTemp)}°F`);
  $('timer-carryover').textContent = temperatureGuidance(config);
  show('timer-carryover');
  $('btn-pause').disabled = false;
  $('btn-pause').textContent = 'Pause';
  hide('howd-prompt');
}
function startCook() {
  if (!state.protein || !state.cut || !state.heat || !state.doneness) return;
  initAudio();
  normalizeTemperature(state);
  cook.config = { ...state };
  cook.times = { ...times };
  cook.id = `cook-${Date.now()}`;
  cook.startedAt = Date.now();
  cook.active = true;
  cook.completed = false;
  cook.logged = false;
  cook.pendingStage = undefined;
  renderActiveCook();
  runStage(0);
}
function runStage(idx, duration) {
  const stageTimes = cook.times || times;
  while (idx < STAGES.length && stageTimes[STAGES[idx]] <= 0) idx++;
  if (idx >= STAGES.length) { finishCook(); return; }
  clearScheduledNotifications();
  cook.stage = idx;
  cook.total = duration ?? stageTimes[STAGES[idx]];
  cook.remaining = cook.total;
  cook.paused = false;
  cook.running = true;
  cook.pendingStage = undefined;
  cook.startTime = Date.now();
  cook.deadline = Date.now() + cook.total * 1000;
  updateStageUI(idx);
  $('btn-pause').textContent = 'Pause';
  $('btn-pause').disabled = false;
  $('timer-carryover').textContent = temperatureGuidance(cook.config || state);
  show('timer-carryover');
  clearInterval(cook.tickInterval);
  cook.tickInterval = setInterval(tick, 250);
  persistRuntime();
  scheduleStageNotifications(idx, cook.total);
  syncNativeCook();
}
function tick() {
  if (cook.paused || !cook.running) return;
  cook.remaining = Math.max(0, (cook.deadline - Date.now()) / 1000);
  $('timer-display').textContent = fmtDisplay(cook.remaining);
  if (cook.remaining <= 0) {
    clearInterval(cook.tickInterval);
    cook.tickInterval = null;
    cook.running = false;
    cook.deadline = 0;
    clearScheduledNotifications();
    playAlarm(cook.stage);
    showConfirmOverlay(cook.stage + 1);
    syncNativeCook();
  }
}

function updateStageUI(idx) {
  $('timer-stage-small').textContent = STAGE_LABELS[idx];
  $('timer-instruction').textContent = stageInstruction(idx);
  $('timer-display').textContent = fmtDisplay(cook.total);
  $('timer-display').classList.remove('done');

  // Progress segments
  document.querySelectorAll('#timer-progress span').forEach((el, i) => {
    el.classList.remove('on', 'done');
    if (i < idx) el.classList.add('done');
    else if (i === idx) el.classList.add('on');
  });
  // Stages row
  document.querySelectorAll('#timer-stages-row span').forEach((el, i) => {
    el.classList.remove('now', 'done');
    if (i < idx) el.classList.add('done');
    else if (i === idx) el.classList.add('now');
  });
}

function togglePause() {
  if (!cook.running && !cook.paused) return;
  if (!cook.paused) {
    tick();
    if (!cook.running) return;
    cook.paused = true;
    cook.running = false;
    cook.deadline = 0;
    clearInterval(cook.tickInterval);
    cook.tickInterval = null;
    $('btn-pause').textContent = 'Resume';
    clearScheduledNotifications();
  } else {
    cook.paused = false;
    cook.running = true;
    cook.deadline = Date.now() + cook.remaining * 1000;
    cook.tickInterval = setInterval(tick, 250);
    $('btn-pause').textContent = 'Pause';
    scheduleStageNotifications(cook.stage, cook.remaining);
  }
  persistRuntime();
  syncNativeCook();
  haptic('light');
}
function removeConfirmation(kind, id) {
  pendingConfirmations = pendingConfirmations.filter(item => !(item.kind === kind && item.id === id));
}
function cancelCook() {
  clearInterval(cook.tickInterval);
  cook.tickInterval = null;
  cook.running = false;
  cook.paused = false;
  cook.active = false;
  cook.completed = false;
  cook.deadline = 0;
  cook.pendingStage = undefined;
  removeConfirmation('main', null);
  clearScheduledNotifications();
  stopAlarm();
  hide('active-timer');
  show('setup-form');
  $('btn-pause').disabled = false;
  showNextConfirmation();
  persistRuntime();
  syncNativeCook();
}
function enqueueConfirmation(kind, id, render = true) {
  if (!pendingConfirmations.some(item => item.kind === kind && item.id === id)) pendingConfirmations.push({ kind, id });
  if (render) { showNextConfirmation(); persistRuntime(); }
}
function showConfirmOverlay(nextIdx) {
  const stageTimes = cook.times || times;
  while (nextIdx < STAGES.length && stageTimes[STAGES[nextIdx]] <= 0) nextIdx++;
  cook.pendingStage = nextIdx;
  $('btn-pause').disabled = true;
  enqueueConfirmation('main', null);
}
function showNextConfirmation() {
  const item = pendingConfirmations[0];
  if (!item) { $('confirm-overlay').classList.remove('open'); return; }
  const owner = item.kind === 'main' ? cook : queue[item.id];
  if (!owner || owner.pendingStage === undefined) {
    pendingConfirmations.shift();
    showNextConfirmation();
    return;
  }
  const c = STAGE_CONFIRM[owner.stage] || STAGE_CONFIRM[0];
  const config = owner.config || state;
  $('confirm-eyebrow').textContent = item.kind === 'lane' ? `${owner.label} · ${c.eyebrow}` : c.eyebrow;
  $('confirm-title').innerHTML = `<em>${owner.pendingStage === 3 ? 'Check it.' : c.title}</em>`;
  $('confirm-sub').textContent = owner.pendingStage >= 3 ? temperatureGuidance(config) : c.sub;
  $('btn-confirm-action').textContent = owner.pendingStage === 3 ? 'Temperature checked — start Rest' : owner.pendingStage >= 4 ? 'Checked — finish cook' : c.action;
  $('confirm-overlay').classList.add('open');
  haptic('heavy');
}
function confirmStageAdvance() {
  const item = pendingConfirmations.shift();
  if (!item) return;
  stopAlarm();
  const owner = item.kind === 'main' ? cook : queue[item.id];
  if (owner) {
    const next = owner.pendingStage;
    owner.pendingStage = undefined;
    if (item.kind === 'lane') {
      if (next >= STAGES.length) finishLane(item.id);
      else runLaneStage(item.id, next);
    } else if (next >= STAGES.length) finishCook();
    else runStage(next);
  }
  showNextConfirmation();
  persistRuntime();
}
function snoozeStage() {
  const item = pendingConfirmations.shift();
  if (!item) return;
  stopAlarm();
  const owner = item.kind === 'main' ? cook : queue[item.id];
  if (owner) {
    owner.pendingStage = undefined;
    if (item.kind === 'lane') runLaneStage(item.id, owner.stage, 30);
    else runStage(owner.stage, 30);
  }
  showNextConfirmation();
  persistRuntime();
  showToast('+ 30s');
}
function renderCookFinished() {
  $('timer-stage-small').textContent = 'Done';
  $('timer-display').textContent = '✓';
  $('timer-display').classList.add('done');
  $('timer-instruction').textContent = 'Confirm safe internal temperature before serving.';
  document.querySelectorAll('#timer-progress span').forEach(el => {
    el.classList.remove('on'); el.classList.add('done');
  });
  document.querySelectorAll('#timer-stages-row span').forEach(el => {
    el.classList.remove('now'); el.classList.add('done');
  });
  hide('timer-carryover');
  $('btn-pause').disabled = true;
  $('howd-prompt').classList.toggle('hidden', !!cook.logged);
}
function finishCook() {
  clearInterval(cook.tickInterval);
  cook.tickInterval = null;
  cook.running = false;
  cook.paused = false;
  cook.completed = true;
  cook.deadline = 0;
  cook.pendingStage = undefined;
  clearScheduledNotifications();
  renderCookFinished();
  persistRuntime();
  syncNativeCook();
  haptic('heavy');
}

/* ─── HOW'D IT LAND? ────────────────────────────────────────────── */
function setupHowdPrompt() {
  document.querySelectorAll('#howd-prompt button').forEach(btn => {
    btn.addEventListener('click', () => {
      const rating = btn.dataset.rating;
      btn.focus();
      // Prompt for name + save to log
      $('fav-name-input').value = `${(cook.config || state).cut} · ${new Date().toLocaleDateString()}`;
      $('save-modal').classList.add('open');
      $('save-modal').dataset.rating = rating;
    });
  });
}

/* ─── SAVE / LOG ────────────────────────────────────────────────── */
function setupSaveModal() {
  $('btn-cancel-save').addEventListener('click', () => {
    $('save-modal').classList.remove('open');
    if (cook.completed && !cook.logged) show('howd-prompt');
  });
  $('btn-confirm-save').addEventListener('click', confirmSave);
  $('fav-name-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') confirmSave();
  });
}

async function confirmSave() {
  const button = $('btn-confirm-save');
  if (button.disabled) return;
  button.disabled = true;
  const config = cook.config || state;
  const name = $('fav-name-input').value.trim() || `${config.cut} · ${new Date().toLocaleDateString()}`;
  const rating = $('save-modal').dataset.rating || null;
  log.unshift({
    id: nextLogId++,
    name,
    rating,
    date: Date.now(),
    protein: config.protein,
    cut: config.cut,
    cutFactor: config.cutFactor,
    thickness: config.thickness,
    heat: config.heat,
    heatFactor: config.heatFactor,
    doneness: config.doneness,
    doneTemp: config.doneTemp,
    doneFactor: config.doneFactor,
    grill: config.grill,
    times: { ...(cook.times || times) },
  });
  const saved = await persistSave();
  button.disabled = false;
  if (!saved) {
    log.shift();
    nextLogId--;
    showToast('Cook was not saved. Free storage and tap Log it again.');
    return;
  }
  cook.logged = true;
  hide('howd-prompt');
  persistRuntime();
  $('save-modal').classList.remove('open');
  showToast('Logged');
  haptic('medium');
  renderLog();
}

/* ─── RENDER LOG ────────────────────────────────────────────────── */
function renderLog() {
  const list = $('log-list');
  if (!log.length) {
    list.innerHTML = `<div class="log-empty">Nothing logged yet.<br>Cook something. Log it. Build the book.</div>`;
    return;
  }
  list.innerHTML = '';
  log.forEach(entry => {
    const div = document.createElement('div');
    div.className = 'log-entry';
    const date = new Date(entry.date);
    const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    const ratingLabel = entry.rating === 'right' ? 'Right' : entry.rating === 'under' ? 'Under' : entry.rating === 'over' ? 'Over' : '';
    div.innerHTML = `
      <div class="date">${dateStr.toUpperCase()} · № ${String(entry.id).padStart(3, '0')}</div>
      <div>
        <div class="name">${escapeHtml(entry.name)}</div>
        <div class="meta">${entry.cut} · ${entry.thickness}″ · ${entry.doneness} · ${entry.grill}</div>
      </div>
      <div class="actions">
        ${ratingLabel ? `<div class="rating">${ratingLabel}</div>` : ''}
        <button class="log-action" data-load="${entry.id}">Repeat</button>
      </div>`;
    list.appendChild(div);
  });
  list.querySelectorAll('[data-load]').forEach(btn => {
    btn.addEventListener('click', () => loadFromLog(parseInt(btn.dataset.load, 10)));
  });
}

function loadFromLog(id) {
  if (cook.active && !cook.completed) { showToast('Finish or cancel the active cook before repeating a recipe.'); return; }
  const entry = log.find(e => e.id === id);
  if (!entry) return;
  // Restore state
  state.grill = entry.grill || 'gas';
  state.grillFactor = state.grill === 'charcoal' ? 1.15 : 1.0;
  state.protein = entry.protein;
  selectProtein(entry.protein);
  state.cut = entry.cut;
  state.cutFactor = entry.cutFactor;
  state.thickness = entry.thickness;
  state.heat = entry.heat;
  state.heatFactor = entry.heatFactor;
  state.doneness = entry.doneness;
  state.doneTemp = entry.doneTemp;
  state.doneFactor = entry.doneFactor;
  normalizeTemperature(state);
  buildDoneness(state.protein, true);

  syncSetupUI();

  switchTab('timer');
  calculate();
  showToast('Loaded');
}

function syncSetupUI() {
  const syncPills = (selector, matches) => document.querySelectorAll(selector).forEach(button => {
    const selected = matches(button);
    button.classList.toggle('active', selected);
    button.setAttribute('aria-pressed', String(selected));
  });
  syncPills('#grill-pills .pill', button => button.dataset.grill === state.grill);
  syncPills('#cut-pills .pill', button => button.dataset.cut === state.cut);
  syncPills('#heat-pills .pill', button => button.dataset.heat === state.heat);
  $('ans-grill').textContent = state.grill === 'charcoal' ? 'Charcoal' : 'Gas';
  $('charcoal-cue').classList.toggle('hidden', state.grill !== 'charcoal');
  $('ans-cut').textContent = state.cut;
  $('ans-heat').textContent = state.heat === 'high' ? 'High' : 'Medium';
  $('thickness-input').value = state.thickness;
  $('thickness-input').dispatchEvent(new Event('input'));
  applyThicknessVisibility(state.cut);
  buildDoneness(state.protein, true);
  ['winter', 'altitude'].forEach(key => {
    $('toggle-' + key).classList.toggle('on', state[key]);
    $('toggle-' + key).setAttribute('aria-pressed', String(state[key]));
  });
}

/* ─── QUEUE FUNCTIONS ───────────────────────────────────────────── */
function laneCount() { return Object.keys(queue).length; }

function addToQueue() {
  if (!state.protein || !state.cut || !state.heat || !state.doneness) {
    showToast('Configure a cook first');
    switchTab('timer');
    return;
  }
  if (laneCount() >= MAX_LANES) {
    showToast(`Max ${MAX_LANES} on the grill`);
    return;
  }
  const id = nextLaneId++;
  queue[id] = {
    id,
    label: state.cut,
    spec: `${state.thickness}″ · ${state.doneness}`,
    grill: state.grill,
    heat: state.heat,
    doneTemp: state.doneTemp,
    config: { ...state },
    times: { ...times },
    running: false,
    deadline: 0,
    notificationIds: [],
    stage: -1,            // -1 = not started
    total: 0,
    remaining: 0,
    startTime: 0,
    paused: false,
    interval: null,
  };
  renderQueue();
  switchTab('queue');
  persistRuntime();
  showToast('Added to queue');
  haptic('medium');
}

function renderQueue() {
  const list = $('queue-list');
  const ids = Object.keys(queue).map(Number).sort((a, b) => a - b);
  // Add button is always visible unless we've maxed out lanes
  $('btn-add-queue').classList.toggle('hidden', laneCount() >= MAX_LANES);
  if (!ids.length) {
    list.innerHTML = `<div class="log-empty">Nothing on the grill yet.<br>Configure a cook on Timer, then tap Add.</div>`;
    return;
  }
  list.innerHTML = '';
  ids.forEach(id => {
    const lane = queue[id];
    const row = document.createElement('div');
    row.className = 'lane-card';
    const stageLabel = lane.stage < 0
      ? 'WAITING'
      : lane.stage >= 4 ? 'DONE' : STAGE_LABELS[lane.stage].toUpperCase();
    const stageClass = lane.stage < 0 ? 'next' : lane.stage >= 4 ? 'done' : 'now';
    const timeText = lane.stage < 0
      ? fmtShort(lane.times.sideA)
      : lane.stage >= 4 ? '✓' : fmtDisplay(lane.remaining);
    row.innerHTML = `
      <div class="lane-head">
        <div class="lane-rule ${stageClass}"></div>
        <div class="lane-info">
          <div class="lane-name ${lane.stage >= 4 ? 'done' : ''}">${escapeHtml(lane.label)}</div>
          <div class="lane-spec">${escapeHtml(lane.spec)} · ${lane.grill}</div>
        </div>
        <div class="lane-right">
          <div class="lane-time ${stageClass}">${timeText}</div>
          <div class="lane-tag ${stageClass}">${stageLabel}</div>
        </div>
      </div>
      <div class="lane-actions">
        ${lane.stage < 0
          ? `<button class="lane-btn primary" data-act="start" data-id="${id}">Start</button>`
          : lane.stage >= 4
            ? `<button class="lane-btn" data-act="remove" data-id="${id}">Remove</button>`
            : `<button class="lane-btn" data-act="pause" data-id="${id}">${lane.pendingStage !== undefined ? 'Check food' : lane.paused ? 'Resume' : 'Pause'}</button>
               <button class="lane-btn" data-act="cancel" data-id="${id}">Cancel</button>`}
      </div>`;
    list.appendChild(row);
  });
  list.querySelectorAll('[data-act]').forEach(btn => {
    btn.addEventListener('click', () => handleLaneAction(btn.dataset.act, parseInt(btn.dataset.id, 10)));
  });
}

function handleLaneAction(act, id) {
  const lane = queue[id];
  if (!lane) return;
  if (act === 'start') startLane(id);
  else if (act === 'pause') toggleLanePause(id);
  else if (act === 'cancel') cancelLane(id);
  else if (act === 'remove') cancelLane(id);
}

function startLane(id) {
  const lane = queue[id];
  if (!lane) return;
  initAudio();
  runLaneStage(id, 0);
}

function runLaneStage(id, idx, duration) {
  const lane = queue[id];
  if (!lane) return;
  while (idx < STAGES.length && lane.times[STAGES[idx]] <= 0) idx++;
  if (idx >= STAGES.length) { finishLane(id); return; }
  clearScheduledNotifications(lane);
  lane.stage = idx;
  lane.total = duration ?? lane.times[STAGES[idx]];
  lane.remaining = lane.total;
  lane.paused = false;
  lane.running = true;
  lane.pendingStage = undefined;
  lane.startTime = Date.now();
  lane.deadline = Date.now() + lane.total * 1000;
  clearInterval(lane.interval);
  lane.interval = setInterval(() => tickLane(id), 500);
  renderQueue();
  persistRuntime();
  scheduleStageNotifications(idx, lane.remaining, lane, id);
}
function tickLane(id) {
  const lane = queue[id];
  if (!lane || lane.paused || !lane.running) return;
  lane.remaining = Math.max(0, (lane.deadline - Date.now()) / 1000);
  const card = document.querySelector(`[data-id="${id}"]`)?.closest('.lane-card');
  const display = card?.querySelector('.lane-time');
  if (display) display.textContent = fmtDisplay(lane.remaining);
  if (lane.remaining <= 0) {
    clearInterval(lane.interval);
    lane.interval = null;
    lane.running = false;
    lane.deadline = 0;
    clearScheduledNotifications(lane);
    playAlarm(lane.stage);
    showLaneConfirmOverlay(id, lane.stage + 1);
    renderQueue();
  }
}
function toggleLanePause(id) {
  const lane = queue[id];
  if (!lane || lane.stage < 0 || lane.stage >= 4) return;
  if (lane.pendingStage !== undefined) { showNextConfirmation(); return; }
  if (!lane.paused) {
    tickLane(id);
    if (!lane.running) return;
    lane.paused = true;
    lane.running = false;
    lane.deadline = 0;
    clearInterval(lane.interval);
    lane.interval = null;
    clearScheduledNotifications(lane);
  } else {
    lane.paused = false;
    lane.running = true;
    lane.deadline = Date.now() + lane.remaining * 1000;
    lane.interval = setInterval(() => tickLane(id), 500);
    scheduleStageNotifications(lane.stage, lane.remaining, lane, id);
  }
  renderQueue();
  persistRuntime();
  haptic('light');
}
function cancelLane(id) {
  const lane = queue[id];
  if (!lane) return;
  clearInterval(lane.interval);
  lane.running = false;
  lane.deadline = 0;
  clearScheduledNotifications(lane);
  removeConfirmation('lane', id);
  delete queue[id];
  renderQueue();
  showNextConfirmation();
  persistRuntime();
  haptic('medium');
}
function finishLane(id) {
  const lane = queue[id];
  if (!lane) return;
  clearInterval(lane.interval);
  lane.interval = null;
  lane.running = false;
  lane.paused = false;
  lane.deadline = 0;
  lane.pendingStage = undefined;
  lane.stage = 4;
  clearScheduledNotifications(lane);
  renderQueue();
  persistRuntime();
  haptic('heavy');
}
function showLaneConfirmOverlay(id, nextIdx) {
  const lane = queue[id];
  if (!lane) return;
  while (nextIdx < STAGES.length && lane.times[STAGES[nextIdx]] <= 0) nextIdx++;
  lane.pendingStage = nextIdx;
  enqueueConfirmation('lane', id);
}

/* ─── AUDIO ALARM ───────────────────────────────────────────────── */
function initAudio() {
  try {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === 'suspended') audioCtx.resume();
  } catch (e) { /* ignore */ }
}

function playAlarm(stageIdx) {
  const messages = [
    'Flip — Tap to confirm',
    'Move to indirect — Tap to confirm',
    'Pull it — Tap to confirm',
    'Rest complete — Tap to confirm',
  ];
  $('alarm-banner').textContent = messages[stageIdx] || 'Stage complete — Tap to confirm';
  $('alarm-banner').classList.add('visible');
  if (!audioCtx) return;
  try {
    const gain = audioCtx.createGain();
    gain.gain.setValueAtTime(0.22, audioCtx.currentTime);
    gain.connect(audioCtx.destination);
    alarmNode = audioCtx.createOscillator();
    alarmNode.type = 'sine';
    const notes = [523.25, 659.25, 783.99, 659.25, 523.25];
    const now = audioCtx.currentTime;
    notes.forEach((hz, i) => {
      alarmNode.frequency.setValueAtTime(hz, now + i * 0.15);
    });
    alarmNode.connect(gain);
    alarmNode.start(now);
    alarmNode.stop(now + notes.length * 0.15 + 0.2);
    alarmNode.onended = () => alarmNode = null;
  } catch (e) { alarmNode = null; }
  haptic('heavy');
}

function stopAlarm() {
  try { if (alarmNode) { alarmNode.stop(); alarmNode = null; } } catch (e) { /* ignore */ }
  $('alarm-banner').classList.remove('visible');
}

/* ─── TOAST ─────────────────────────────────────────────────────── */
let toastTimeout = null;
function showToast(msg) {
  $('toast').textContent = msg;
  $('toast').classList.add('visible');
  clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => $('toast').classList.remove('visible'), 2000);
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

/* Keep both sheets keyboard-accessible as their open state changes. A stage
   acknowledgement remains explicit; Escape may dismiss only the save sheet. */
function setupDialogs() {
  const dialogs = [$('confirm-overlay'), $('save-modal')];
  const previousFocus = new Map();
  const isOpen = dialog => dialog.classList.contains('open');
  const focusable = dialog => [...dialog.querySelectorAll('button, input, [tabindex="0"], a[href]')]
    .filter(element => !element.disabled && element.getClientRects().length);
  const update = dialog => {
    const current = dialogs.find(isOpen);
    // Release inert before restoring focus, or the browser rejects focus().
    [...document.body.children].forEach(element => {
      if (!['SCRIPT', 'STYLE'].includes(element.tagName)) {
        element.inert = !!current && element !== current && !element.contains(current) && element.id !== 'toast';
      }
    });
    const open = isOpen(dialog);
    if (open && !previousFocus.has(dialog)) {
      previousFocus.set(dialog, document.activeElement);
      (dialog.id === 'save-modal' ? $('fav-name-input') : $('btn-confirm-action')).focus();
    } else if (!open && previousFocus.has(dialog)) {
      const previous = previousFocus.get(dialog);
      previousFocus.delete(dialog);
      if (previous?.isConnected && previous !== document.body && previous.tabIndex >= 0 && !previous.disabled && previous.getClientRects().length) previous.focus();
      else (cook.active ? $('btn-cancel') : $('tab-timer')).focus();
    }
  };
  dialogs.forEach(dialog => {
    new MutationObserver(() => update(dialog)).observe(dialog, { attributes: true, attributeFilter: ['class'] });
    dialog.addEventListener('keydown', event => {
      if (event.key === 'Escape') {
        event.preventDefault();
        if (dialog.id === 'save-modal') $('btn-cancel-save').click();
      }
      if (event.key !== 'Tab') return;
      const controls = focusable(dialog);
      const first = controls[0], last = controls[controls.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
    });
  });
  document.addEventListener('focusin', event => {
    const dialog = dialogs.find(isOpen);
    if (dialog && !dialog.contains(event.target)) (focusable(dialog)[0] || dialog).focus();
  });
  document.querySelectorAll('.tab-btn').forEach(button => {
    button.addEventListener('keydown', event => {
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      const tabs = [...document.querySelectorAll('.tab-btn')];
      const index = tabs.indexOf(button);
      const next = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 :
        (index + (event.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
      tabs[next].click(); tabs[next].focus();
    });
  });
}

/* ─── BOOT ──────────────────────────────────────────────────────── */
async function boot() {
  buildProteinPicker();
  setupGrillPills();
  setupThicknessSlider();
  setupHeatPills();
  setupEnvToggles();
  setupHowdPrompt();
  setupSaveModal();
  setupDialogs();

  // Tabs
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab));
  });

  // Timer actions
  $('btn-start-cook').addEventListener('click', startCook);
  $('btn-add-queue').addEventListener('click', addToQueue);
  $('btn-pause').addEventListener('click', togglePause);
  $('btn-cancel').addEventListener('click', cancelCook);
  $('btn-confirm-action').addEventListener('click', confirmStageAdvance);
  $('btn-confirm-snooze').addEventListener('click', snoozeStage);
  $('alarm-banner').addEventListener('click', () => { stopAlarm(); showNextConfirmation(); });

  // Env disclosure (collapsible cold weather + altitude)
  $('env-toggle').addEventListener('click', () => {
    const isOpen = $('env-toggle').getAttribute('aria-expanded') === 'true';
    $('env-toggle').setAttribute('aria-expanded', !isOpen);
    $('env-content').classList.toggle('hidden', isOpen);
  });

  switchTab('timer');

  // Load persisted state
  await persistLoad();
  await restoreRuntime();
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') reconcileTimers();
    else persistRuntime();
  });
  window.addEventListener('pageshow', reconcileTimers);
  window.addEventListener('pagehide', persistRuntime);
  const native = window.Capacitor?.Plugins?.GrillMasterNative;
  if (native) {
    try {
      await native.addListener('route', handleNativeRoute);
      handleNativeRoute(await native.consumeRoute());
    } catch { /* App remains usable when native routing is unavailable. */ }
  }

  // Folio: count of entries
  $('folio').textContent = `№ ${String(log.length + 1).padStart(3, '0')}`;
}

// Boot when DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', boot);
} else {
  boot();
}

// Expose for tests
window.gm = { state, times, cook, get log() { return log; }, queue, MEAT_DB, ICONS, reconcileTimers };
