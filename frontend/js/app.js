import { api, userId, setUserId } from "./api.js";
import { renderHeatmap } from "./heatmap.js";

// ── Navigation ─────────────────────────────────────────────────────────
const pages = document.querySelectorAll(".page");
const navLinks = document.querySelectorAll(".sidebar nav a");

function navigate(id) {
  pages.forEach(p => p.classList.toggle("active", p.id === id));
  navLinks.forEach(a => a.classList.toggle("active", a.dataset.page === id));
  if (id === "dashboard") loadDashboard();
  if (id === "exercises") loadExercises();
  if (id === "history")   loadHistory();
  if (id === "analytics") loadAnalytics();
  if (id === "stats")     loadStats();
}

navLinks.forEach(a => a.addEventListener("click", e => {
  e.preventDefault();
  navigate(a.dataset.page);
}));

// ── Toast ──────────────────────────────────────────────────────────────
const toastEl = document.getElementById("toast");
let toastTimer;
function toast(msg) {
  toastEl.textContent = msg;
  toastEl.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toastEl.classList.remove("show"), 2800);
}

// ── User setup modal ───────────────────────────────────────────────────
const userModal = document.getElementById("user-modal");
const userForm  = document.getElementById("user-form");

async function ensureUser() {
  try {
    const users = await api.listUsers();
    if (users.length > 0) {
      setUserId(users[0].id);
      return;
    }
  } catch (_) {}
  userModal.classList.add("open");
}

userForm.addEventListener("submit", async e => {
  e.preventDefault();
  const fd = new FormData(userForm);
  const body = {
    name: fd.get("name"),
    age: parseInt(fd.get("age")),
    sex: fd.get("sex"),
    height_cm: parseFloat(fd.get("height_cm")),
    activity_level: parseFloat(fd.get("activity_level")),
    body_fat_pct: fd.get("body_fat_pct") ? parseFloat(fd.get("body_fat_pct")) : null,
  };
  try {
    const user = await api.createUser(body);
    setUserId(user.id);
    userModal.classList.remove("open");
    toast("Profile created!");
    loadDashboard();
  } catch (err) {
    toast("Error creating profile");
  }
});

// ── Dashboard ──────────────────────────────────────────────────────────
let sparklineChart = null;

async function loadDashboard() {
  const heatmapEl       = document.getElementById("heatmap");
  const recentEl        = document.getElementById("recent-workouts");
  const weightEl        = document.getElementById("current-weight");
  const weightUnitEl    = document.getElementById("weight-unit");
  const weightDeltaEl   = document.getElementById("weight-delta");
  const streakEl        = document.getElementById("streak");
  const streakSubEl     = document.getElementById("streak-sub");
  const weekSetsEl      = document.getElementById("week-sets");
  const weekSetsDeltaEl = document.getElementById("week-sets-delta");

  try {
    // ── This week's volume ─────────────────────────────────────────
    const { volume } = await api.muscleVolume(userId(), 7);
    renderHeatmap(heatmapEl, volume);
    const totalSets = Object.values(volume).reduce((a, b) => a + b, 0);
    weekSetsEl.textContent = totalSets;

    // ── Sets delta vs last week ────────────────────────────────────
    try {
      const { volume: vol14 } = await api.muscleVolume(userId(), 14);
      const sets14     = Object.values(vol14).reduce((a, b) => a + b, 0);
      const lastWeek   = sets14 - totalSets;
      if (lastWeek > 0 || totalSets > 0) {
        const delta = totalSets - lastWeek;
        weekSetsDeltaEl.textContent = `${delta >= 0 ? "↑" : "↓"} ${delta >= 0 ? "+" : ""}${delta} vs last week`;
        weekSetsDeltaEl.className   = `stat-card-delta ${delta >= 0 ? "delta-up" : "delta-down"}`;
      }
    } catch (_) { /* non-critical */ }

    // ── Workouts + streak ──────────────────────────────────────────
    const workouts = await api.listWorkouts(userId());
    recentEl.innerHTML = "";
    if (!workouts.length) {
      recentEl.innerHTML = '<div class="empty">No workouts yet. Log your first one!</div>';
    } else {
      workouts.slice(0, 5).forEach(w => {
        const item = document.createElement("div");
        item.className = "workout-item";
        item.innerHTML = `
          <div>
            <div class="workout-name">${w.name}</div>
            <div class="workout-date">${w.date}</div>
          </div>
          <div class="workout-meta">${w.sets.length} sets</div>`;
        recentEl.appendChild(item);
      });
    }
    const streak = calcStreak(workouts);
    streakEl.textContent = streak;
    const streakUnitEl = document.getElementById("streak-unit");
    if (streakUnitEl) streakUnitEl.textContent = streak === 1 ? "session" : "sessions";
    if (streakSubEl) streakSubEl.textContent = streakMessage(streak);

    // ── Body weight ────────────────────────────────────────────────
    const logs = await api.getWeightLog(userId());
    if (logs.length) {
      const latest = logs[logs.length - 1];
      weightEl.textContent = latest.weight_kg;
      if (weightUnitEl) weightUnitEl.style.display = "";

      // Weight trend vs ~4 weeks ago
      if (logs.length >= 2 && weightDeltaEl) {
        const cutoff = new Date(latest.date);
        cutoff.setDate(cutoff.getDate() - 28);
        const old = [...logs].reverse().find(l => new Date(l.date) <= cutoff) || logs[0];
        if (old !== latest) {
          const delta = Math.round((latest.weight_kg - old.weight_kg) * 10) / 10;
          const weeks = Math.max(1, Math.round(
            (new Date(latest.date) - new Date(old.date)) / (7 * 86400000)
          ));
          const isLoss = delta < 0;
          weightDeltaEl.textContent = `${isLoss ? "↓" : "↑"} ${delta > 0 ? "+" : ""}${delta} kg / ${weeks} wk${weeks !== 1 ? "s" : ""}`;
          weightDeltaEl.className   = `stat-card-delta ${isLoss ? "delta-up" : "delta-down"}`;
        }
      }

      drawWeightSparkline(logs);
    }

  } catch (err) {
    console.error(err);
  }
}

function streakMessage(n) {
  if (n === 0) return "Start your streak!";
  if (n < 5)   return "Just getting started";
  if (n < 10)  return "Building momentum";
  if (n < 20)  return "Keep it going";
  return "You're on fire! 🔥";
}

function drawWeightSparkline(logs) {
  const canvas = document.getElementById("weight-sparkline");
  if (!canvas) return;
  if (sparklineChart) { sparklineChart.destroy(); sparklineChart = null; }
  const recent = logs.slice(-14);
  sparklineChart = new Chart(canvas, {
    type: "line",
    data: {
      labels: recent.map(l => l.date),
      datasets: [{
        data: recent.map(l => l.weight_kg),
        borderColor: "#60a5fa",
        borderWidth: 2,
        pointRadius: 0,
        fill: false,
        tension: 0.4,
      }]
    },
    options: {
      responsive: false,
      animation: false,
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
      scales: { x: { display: false }, y: { display: false } },
    },
  });
}

function calcStreak(workouts) {
  if (!workouts.length) return 0;
  const dates = [...new Set(workouts.map(w => w.date))].sort().reverse();
  let streak = 0, prev = null;
  for (const d of dates) {
    if (!prev) { streak = 1; prev = d; continue; }
    const diff = (new Date(prev) - new Date(d)) / 86400000;
    if (diff <= 2) { streak++; prev = d; } else break;
  }
  return streak;
}

// ── Exercises ──────────────────────────────────────────────────────────
let allExercises = [];
let currentCategory = "all";
let exercisesInitialized = false;

async function loadExercises() {
  const grid = document.getElementById("exercise-grid");
  grid.innerHTML = '<div class="empty">Loading…</div>';
  try {
    allExercises = await api.listExercises();

    // Wire up listeners only once (loadExercises is called on every nav)
    if (!exercisesInitialized) {
      exercisesInitialized = true;

      document.getElementById("ex-filter").addEventListener("input", applyExerciseFilters);

      document.querySelectorAll(".cat-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          document.querySelectorAll(".cat-btn").forEach(b => b.classList.remove("active"));
          btn.classList.add("active");
          currentCategory = btn.dataset.cat;
          applyExerciseFilters();
        });
      });
    }

    applyExerciseFilters();
  } catch (err) { grid.innerHTML = '<div class="empty">Failed to load exercises</div>'; }
}

function applyExerciseFilters() {
  const q = document.getElementById("ex-filter").value.toLowerCase();
  const filtered = allExercises.filter(e => {
    const matchesCat  = currentCategory === "all" || e.category.toLowerCase() === currentCategory;
    const matchesText = !q ||
      e.name.toLowerCase().includes(q) ||
      e.primary_muscles.toLowerCase().includes(q) ||
      e.category.toLowerCase().includes(q);
    return matchesCat && matchesText;
  });
  renderExerciseGrid(filtered);
}

function renderExerciseGrid(exs) {
  const grid = document.getElementById("exercise-grid");
  grid.innerHTML = "";
  if (!exs.length) { grid.innerHTML = '<div class="empty">No exercises found</div>'; return; }
  exs.forEach(ex => {
    const card = document.createElement("div");
    card.className = "exercise-card";
    const pm = ex.primary_muscles.split(",").filter(Boolean).map(m =>
      `<span class="badge badge-primary">${m.trim()}</span>`).join("");
    const sm = ex.secondary_muscles.split(",").filter(Boolean).map(m =>
      `<span class="badge badge-secondary">${m.trim()}</span>`).join("");

    // Build media element programmatically — avoids HTML-attribute escaping bugs
    let mediaEl;
    if (ex.gif_url) {
      const img = document.createElement("img");
      img.className = "exercise-img";
      img.src = ex.gif_url;        // set directly so Chrome doesn't fire spurious error
      img.loading = "lazy";        // browser-native lazy loading — no custom observer needed
      img.decoding = "async";
      img.alt = ex.name;
      img.addEventListener("error", () => {
        const ph = document.createElement("div");
        ph.className = "exercise-img-placeholder";
        ph.textContent = "🏋️";
        img.replaceWith(ph);
      }, { once: true });
      mediaEl = img;
    } else {
      const ph = document.createElement("div");
      ph.className = "exercise-img-placeholder";
      ph.textContent = "🏋️";
      mediaEl = ph;
    }

    const body = document.createElement("div");
    body.className = "exercise-card-body";
    body.innerHTML = `
      <div class="exercise-name">${ex.name}</div>
      <div class="exercise-cat">${ex.category}</div>
      <div class="mt-8">${pm}${sm}</div>
      <div class="text-sm text-muted mt-8">${ex.description || ""}</div>`;

    card.appendChild(mediaEl);
    card.appendChild(body);
    card.addEventListener("click", () => openLoggerWith(ex));
    grid.appendChild(card);
  });

  // Native loading="lazy" handles deferred fetching — no custom observer needed
}

// ── Workout Logger ─────────────────────────────────────────────────────
let activeWorkout = null;

// Hardcoded quick-start templates — exercise names must match seed.py exactly
const TEMPLATES = {
  push: {
    name: "Push Day",
    exercises: ["Bench Press", "Incline Bench Press", "Overhead Press", "Lateral Raise", "Tricep Pushdown"],
  },
  pull: {
    name: "Pull Day",
    exercises: ["Deadlift", "Pull-up", "Barbell Row", "Bicep Curl", "Face Pull"],
  },
  legs: {
    name: "Leg Day",
    exercises: ["Barbell Back Squat", "Romanian Deadlift", "Leg Press", "Leg Curl", "Calf Raise"],
  },
};

function openLoggerWith(ex) {
  navigate("logger");
  addExerciseToLogger(ex);
}

async function initLogger() {
  document.getElementById("start-workout-btn").addEventListener("click", startWorkout);
  document.getElementById("finish-workout-btn").addEventListener("click", finishWorkout);
  document.getElementById("add-exercise-btn").addEventListener("click", showExPicker);
  document.getElementById("ex-picker-close").addEventListener("click", () =>
    document.getElementById("ex-picker-modal").classList.remove("open"));
  document.getElementById("ex-picker-search").addEventListener("input", e => {
    renderExPicker(e.target.value);
  });

  // Template card click handlers
  document.querySelectorAll(".template-card").forEach(card => {
    card.addEventListener("click", () => {
      const key = card.dataset.template;
      const tpl = TEMPLATES[key];
      if (tpl) startFromTemplate(tpl);
    });
  });
}

async function startFromTemplate(tpl) {
  // Ensure exercises are loaded
  if (!allExercises.length) {
    try { allExercises = await api.listExercises(); } catch (_) {}
  }
  // Set name and start
  document.getElementById("workout-name-input").value = tpl.name;
  startWorkout();
  // Add template exercises (match by name, case-insensitive)
  for (const name of tpl.exercises) {
    const ex = allExercises.find(e => e.name.toLowerCase() === name.toLowerCase());
    if (ex) addExerciseToLogger(ex);
  }
}

function startWorkout() {
  const name = document.getElementById("workout-name-input").value.trim() || "Workout";
  activeWorkout = { name, date: new Date().toISOString().slice(0,10), exercises: [] };
  document.getElementById("logger-start").style.display = "none";
  document.getElementById("logger-active").style.display = "block";
  document.getElementById("active-workout-title").textContent = name;
  document.getElementById("exercises-container").innerHTML = "";
}

function showExPicker() {
  if (!allExercises.length) api.listExercises().then(e => { allExercises = e; renderExPicker(""); });
  else renderExPicker("");
  document.getElementById("ex-picker-modal").classList.add("open");
}

function renderExPicker(q) {
  const list = document.getElementById("ex-picker-list");
  const filtered = allExercises.filter(e => e.name.toLowerCase().includes(q.toLowerCase()));
  list.innerHTML = "";
  filtered.forEach(ex => {
    const item = document.createElement("div");
    item.className = "workout-item";
    item.style.cursor = "pointer";
    item.innerHTML = `<div><div class="workout-name">${ex.name}</div>
      <div class="workout-meta">${ex.primary_muscles}</div></div>`;
    item.addEventListener("click", () => {
      addExerciseToLogger(ex);
      document.getElementById("ex-picker-modal").classList.remove("open");
    });
    list.appendChild(item);
  });
}

function addExerciseToLogger(ex) {
  if (!activeWorkout) startWorkout();
  const container = document.getElementById("exercises-container");
  const block = document.createElement("div");
  block.className = "card mt-16";
  block.dataset.exId = ex.id;
  block.innerHTML = `
    <div class="flex justify-between items-center mb-16">
      <div><div class="workout-name">${ex.name}</div>
        <div class="workout-meta">${ex.primary_muscles}</div></div>
      <button class="btn btn-ghost btn-sm add-set-btn">+ Set</button>
    </div>
    <div class="set-row" style="color:var(--muted);font-size:12px;font-weight:600;">
      <span>Set</span><span>Reps</span><span>kg</span><span>RPE</span><span></span>
    </div>
    <div class="sets-list"></div>`;
  block.querySelector(".add-set-btn").addEventListener("click", () => addSetRow(block, ex));
  container.appendChild(block);
  addSetRow(block, ex);
}

let setCounter = 0;
function addSetRow(block, ex) {
  setCounter++;
  const list = block.querySelector(".sets-list");
  const prevReps = list.querySelector(".set-reps:last-child")?.value || 8;
  const prevKg   = list.querySelector(".set-kg:last-child")?.value || 0;
  const setNum = list.querySelectorAll(".set-row").length + 1;
  const row = document.createElement("div");
  row.className = "set-row";
  row.innerHTML = `
    <span class="set-num">${setNum}</span>
    <input type="number" class="form-input set-reps" value="${prevReps}" min="1" max="100">
    <input type="number" class="form-input set-kg"   value="${prevKg}"   min="0" step="0.5">
    <input type="number" class="form-input set-rpe"  placeholder="—"    min="1" max="10" step="0.5">
    <button class="btn btn-danger btn-sm" title="Remove">×</button>`;
  row.querySelector(".btn-danger").addEventListener("click", () => row.remove());
  list.appendChild(row);
}

async function finishWorkout() {
  if (!activeWorkout) return;
  try {
    const workout = await api.createWorkout({
      user_id: userId(),
      date: activeWorkout.date,
      name: activeWorkout.name,
    });
    const blocks = document.querySelectorAll("#exercises-container .card");
    for (const block of blocks) {
      const exId = parseInt(block.dataset.exId);
      const rows = block.querySelectorAll(".sets-list .set-row");
      let setNum = 1;
      for (const row of rows) {
        const reps = parseInt(row.querySelector(".set-reps").value);
        const kg   = parseFloat(row.querySelector(".set-kg").value);
        const rpe  = parseFloat(row.querySelector(".set-rpe").value) || null;
        if (reps > 0) {
          await api.addSet(workout.id, { exercise_id: exId, set_number: setNum++, reps, weight_kg: kg, rpe });
        }
      }
    }
    toast("Workout saved!");
    activeWorkout = null;
    document.getElementById("logger-start").style.display = "block";
    document.getElementById("logger-active").style.display = "none";
    document.getElementById("workout-name-input").value = "";
  } catch (err) {
    toast("Error saving workout");
    console.error(err);
  }
}

// ── History ────────────────────────────────────────────────────────────
async function loadHistory() {
  const list = document.getElementById("history-list");
  list.innerHTML = '<div class="empty">Loading…</div>';
  try {
    const workouts = await api.listWorkouts(userId());
    list.innerHTML = "";
    if (!workouts.length) { list.innerHTML = '<div class="empty">No workouts yet</div>'; return; }
    workouts.forEach(w => {
      const item = document.createElement("div");
      item.className = "card mt-8";
      const exNames = [...new Set(w.sets.map(s => s.exercise.name))].join(", ");
      item.innerHTML = `
        <div class="flex justify-between items-center">
          <div>
            <div class="workout-name">${w.name}</div>
            <div class="workout-date">${w.date}</div>
            <div class="text-sm text-muted mt-4">${exNames || "—"}</div>
          </div>
          <div class="flex gap-8 items-center">
            <span class="workout-meta">${w.sets.length} sets</span>
            <button class="btn btn-danger btn-sm del-btn" data-id="${w.id}">Delete</button>
          </div>
        </div>`;
      item.querySelector(".del-btn").addEventListener("click", async () => {
        await api.deleteWorkout(w.id);
        item.remove();
        toast("Workout deleted");
      });
      list.appendChild(item);
    });
  } catch (err) { list.innerHTML = '<div class="empty">Failed to load</div>'; }
}

// ── Analytics ──────────────────────────────────────────────────────────
let weightChart = null, volumeChart = null, ormChart = null;

async function loadAnalytics() {
  await renderWeightChart();
  await renderVolumeChart();
  await renderORMSection();
}

async function renderWeightChart() {
  const logs = await api.getWeightLog(userId());
  const ctx  = document.getElementById("weight-chart");
  if (!ctx) return;
  if (weightChart) weightChart.destroy();
  weightChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: logs.map(l => l.date),
      datasets: [{
        label: "Body Weight (kg)",
        data: logs.map(l => l.weight_kg),
        borderColor: "#f97316",
        backgroundColor: "#f9731620",
        borderWidth: 2,
        fill: true,
        tension: 0.4,
      }]
    },
    options: chartOpts("Body Weight"),
  });
}

async function renderVolumeChart() {
  const { volume } = await api.muscleVolume(userId(), 28);
  const slugs  = Object.keys(volume).sort((a, b) => volume[b] - volume[a]).slice(0, 10);
  const ctx    = document.getElementById("volume-chart");
  if (!ctx) return;
  if (volumeChart) volumeChart.destroy();
  volumeChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: slugs.map(s => s.replace(/-/g, " ")),
      datasets: [{
        label: "Sets (last 28 days)",
        data: slugs.map(s => volume[s]),
        backgroundColor: "#f97316",
        borderRadius: 6,
      }]
    },
    options: chartOpts("Volume by Muscle"),
  });
}

async function renderORMSection() {
  const sel = document.getElementById("orm-exercise-select");
  if (!sel) return;
  if (!allExercises.length) allExercises = await api.listExercises();
  sel.innerHTML = allExercises.map(e => `<option value="${e.id}">${e.name}</option>`).join("");
  sel.addEventListener("change", () => renderORMChart(parseInt(sel.value)));
  if (allExercises.length) renderORMChart(allExercises[0].id);
}

async function renderORMChart(exId) {
  const { history } = await api.oneRM(userId(), exId);
  const ctx = document.getElementById("orm-chart");
  if (!ctx) return;
  if (ormChart) ormChart.destroy();
  ormChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: history.map(h => h.date),
      datasets: [
        { label: "Epley",    data: history.map(h => h.epley),    borderColor: "#f97316", borderWidth: 2, tension: 0.4, fill: false },
        { label: "Brzycki",  data: history.map(h => h.brzycki),  borderColor: "#60a5fa", borderWidth: 2, tension: 0.4, fill: false },
        { label: "Average",  data: history.map(h => h.average),  borderColor: "#a3e635", borderWidth: 2, tension: 0.4, fill: false },
      ]
    },
    options: chartOpts("Estimated 1RM (kg)"),
  });
}

function chartOpts(title) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: "#8888a0", font: { size: 12 } } },
      title:  { display: false },
    },
    scales: {
      x: { ticks: { color: "#8888a0" }, grid: { color: "#2e2e3e" } },
      y: { ticks: { color: "#8888a0" }, grid: { color: "#2e2e3e" } },
    },
  };
}

// ── Stats / Calories ────────────────────────────────────────────────────
function loadStats() {
  const calcForm = document.getElementById("calc-form");
  const logWeightForm = document.getElementById("log-weight-form");

  calcForm.addEventListener("submit", async e => {
    e.preventDefault();
    const fd = new FormData(calcForm);
    const data = {
      weight_kg:    parseFloat(fd.get("weight_kg")),
      height_cm:    parseFloat(fd.get("height_cm")),
      age:          parseInt(fd.get("age")),
      sex:          fd.get("sex"),
      activity_level: parseFloat(fd.get("activity_level")),
      body_fat_pct: fd.get("body_fat_pct") ? parseFloat(fd.get("body_fat_pct")) : null,
    };
    try {
      const res = await api.calculateCalories(data);
      document.getElementById("calc-result").innerHTML = `
        <div class="grid-3 mt-16">
          <div class="card">
            <div class="card-title">Mifflin BMR</div>
            <div class="stat-value">${res.mifflin_bmr}</div>
            <div class="stat-label">kcal/day</div>
            <hr class="divider">
            <div class="card-title">TDEE</div>
            <div class="stat-value">${res.mifflin_tdee}</div>
          </div>
          <div class="card">
            <div class="card-title">Harris BMR</div>
            <div class="stat-value">${res.harris_bmr}</div>
            <div class="stat-label">kcal/day</div>
            <hr class="divider">
            <div class="card-title">TDEE</div>
            <div class="stat-value">${res.harris_tdee}</div>
          </div>
          ${res.katch_bmr ? `<div class="card">
            <div class="card-title">Katch-McArdle BMR</div>
            <div class="stat-value">${res.katch_bmr}</div>
            <div class="stat-label">kcal/day</div>
            <hr class="divider">
            <div class="card-title">TDEE</div>
            <div class="stat-value">${res.katch_tdee}</div>
          </div>` : ""}
        </div>`;

      const projForm = document.getElementById("proj-form");
      projForm.querySelector("[name=tdee]").value = res.mifflin_tdee;
      projForm.querySelector("[name=current_weight_kg]").value = data.weight_kg;
    } catch (err) { toast("Calculation failed"); }
  });

  document.getElementById("proj-form").addEventListener("submit", async e => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const data = {
      current_weight_kg: parseFloat(fd.get("current_weight_kg")),
      target_weight_kg:  parseFloat(fd.get("target_weight_kg")),
      weekly_change_kg:  parseFloat(fd.get("weekly_change_kg")),
      tdee:              parseFloat(fd.get("tdee")),
    };
    try {
      const res = await api.weightProjection(data);
      document.getElementById("proj-result").innerHTML = `
        <div class="grid-4 mt-16">
          <div class="card"><div class="card-title">Daily intake</div>
            <div class="stat-value">${res.daily_intake_goal}</div><div class="stat-label">kcal</div></div>
          <div class="card"><div class="card-title">Daily delta</div>
            <div class="stat-value">${res.daily_delta_kcal > 0 ? "+" : ""}${res.daily_delta_kcal}</div><div class="stat-label">kcal</div></div>
          <div class="card"><div class="card-title">Weeks to goal</div>
            <div class="stat-value">${res.weeks_to_target}</div></div>
          <div class="card"><div class="card-title">Target date</div>
            <div class="stat-value" style="font-size:18px">${res.target_date}</div></div>
        </div>`;
    } catch (err) { toast("Projection failed"); }
  });

  logWeightForm.addEventListener("submit", async e => {
    e.preventDefault();
    const fd = new FormData(logWeightForm);
    await api.logWeight({ user_id: userId(), date: fd.get("date"), weight_kg: parseFloat(fd.get("weight_kg")) });
    toast("Weight logged!");
    logWeightForm.reset();
  });
}

// ── Init ───────────────────────────────────────────────────────────────
(async () => {
  await ensureUser();
  await initLogger();
  navigate("dashboard");
})();
