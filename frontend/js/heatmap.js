/**
 * Muscle heatmap — SVG visual + canvas-based pixel-perfect hit detection.
 *
 * Visual:  SVG <image> elements render identically to the old PNG approach.
 * Hit test: muscle PNGs loaded into off-screen canvases; on mousemove the
 *           alpha channel is sampled to find which muscle is under the cursor.
 *
 * Images from MertenD/musclegroup-image-generator (MIT).
 */

const REPO = "https://raw.githubusercontent.com/MertenD/musclegroup-image-generator/main/resources/images";

// Resolution used for hit-test canvases — 1/5 of 1920 keeps memory ~14 MB total
const HIT_RES = 384;

// Heat scale: null = inactive (no overlay)
const SCALE = [
  { sets: 0,  color: null      },
  { sets: 1,  color: "#7c2d12" },
  { sets: 4,  color: "#9a3412" },
  { sets: 7,  color: "#c2410c" },
  { sets: 11, color: "#ea580c" },
  { sets: 16, color: "#f97316" },
  { sets: 22, color: "#fb923c" },
];

// Muscle slug → overlay PNG (1920×1920, transparent bg, opaque muscle shape)
const MUSCLE_PNG = {
  chest:        "chest.png",
  abs:          "abs.png",
  obliques:     "core_side.png",
  biceps:       "biceps.png",
  triceps:      "triceps.png",
  deltoids:     "shoulders.png",
  trapezius:    "back_upper.png",
  forearm:      "forearms.png",
  quadriceps:   "quadriceps.png",
  adductors:    "adductors.png",
  calves:       "calfs.png",
  "upper-back": "back_upper.png",
  "lower-back": "back_lower.png",
  gluteal:      "gluteus.png",
  hamstring:    "hamstring.png",
};

// ── Color helpers ──────────────────────────────────────────────────────
function interpolateColor(sets) {
  if (sets <= 0) return null;
  const active = SCALE.filter(s => s.color !== null);
  if (sets >= active[active.length - 1].sets) return active[active.length - 1].color;
  const i = active.findIndex((s, idx) => active[idx + 1] && sets < active[idx + 1].sets);
  if (i < 0) return active[0].color;
  const t = (sets - active[i].sets) / (active[i + 1].sets - active[i].sets);
  return lerpHex(active[i].color, active[i + 1].color, t);
}

function lerpHex(a, b, t) {
  const ah = parseInt(a.slice(1), 16), bh = parseInt(b.slice(1), 16);
  const r = Math.round(((ah >> 16) & 0xff) + (((bh >> 16) & 0xff) - ((ah >> 16) & 0xff)) * t);
  const g = Math.round(((ah >>  8) & 0xff) + (((bh >>  8) & 0xff) - ((ah >>  8) & 0xff)) * t);
  const bv= Math.round(( ah        & 0xff) + (( bh        & 0xff) - ( ah        & 0xff)) * t);
  return `#${r.toString(16).padStart(2,"0")}${g.toString(16).padStart(2,"0")}${bv.toString(16).padStart(2,"0")}`;
}

// ── Pixel-perfect hit detection via off-screen canvases ────────────────
const _hitCtx  = {};   // slug → CanvasRenderingContext2D
let   _hitsReady = false;

function _loadHitCanvases() {
  if (_hitsReady) return;

  // Deduplicate: multiple slugs share the same PNG (e.g. trapezius + upper-back)
  const fileToSlugs = {};
  for (const [slug, file] of Object.entries(MUSCLE_PNG)) {
    if (!fileToSlugs[file]) fileToSlugs[file] = [];
    fileToSlugs[file].push(slug);
  }

  let remaining = Object.keys(fileToSlugs).length;

  for (const [file, slugs] of Object.entries(fileToSlugs)) {
    const canvas = document.createElement("canvas");
    canvas.width  = HIT_RES;
    canvas.height = HIT_RES;
    const ctx = canvas.getContext("2d");
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      ctx.drawImage(img, 0, 0, HIT_RES, HIT_RES);
      for (const slug of slugs) _hitCtx[slug] = ctx;
      if (--remaining === 0) _hitsReady = true;
    };
    img.onerror = () => { if (--remaining === 0) _hitsReady = true; };
    img.src = `${REPO}/${file}`;
  }
}

function _getMuscleAt(px, py) {
  // px, py are in 0–1920 space
  const sx = Math.round(px / 1920 * HIT_RES);
  const sy = Math.round(py / 1920 * HIT_RES);
  for (const [slug, ctx] of Object.entries(_hitCtx)) {
    try {
      if (ctx.getImageData(sx, sy, 1, 1).data[3] > 20) return slug;
    } catch (_) { /* tainted canvas or out of bounds */ }
  }
  return null;
}

// ── Tooltip ────────────────────────────────────────────────────────────
let _tip = null;
function showTooltip(text, e) {
  if (!_tip) {
    _tip = document.createElement("div");
    _tip.style.cssText =
      "position:fixed;background:#1a1a22;border:1px solid #2e2e3e;" +
      "padding:6px 10px;border-radius:6px;font-size:12px;color:#e8e8f0;" +
      "pointer-events:none;z-index:200;white-space:nowrap;";
    document.body.appendChild(_tip);
  }
  _tip.textContent = text;
  _tip.style.display = "block";
  _tip.style.left = (e.clientX + 12) + "px";
  _tip.style.top  = (e.clientY - 28) + "px";
}
function hideTooltip() { if (_tip) _tip.style.display = "none"; }

// ── Main render ────────────────────────────────────────────────────────
export function renderHeatmap(containerEl, volume = {}) {
  containerEl.innerHTML = "";

  // Kick off hit-canvas loading in the background
  _loadHitCanvases();

  const NS  = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(NS, "svg");
  svg.setAttribute("viewBox", "0 0 1920 1920");
  svg.setAttribute("xmlns",   NS);
  svg.style.cssText = "width:100%;height:auto;display:block;border-radius:12px;cursor:crosshair;max-width:460px;margin:0 auto;";

  const defs = document.createElementNS(NS, "defs");
  svg.appendChild(defs);

  // ── Base body silhouette image ──────────────────────────────────────
  const base = document.createElementNS(NS, "image");
  base.setAttribute("href",   `${REPO}/baseImage_transparent.png`);
  base.setAttribute("width",  "1920");
  base.setAttribute("height", "1920");
  base.setAttribute("pointer-events", "none");
  svg.appendChild(base);

  // ── Colored muscle overlays (active muscles only) ───────────────────
  for (const [slug, file] of Object.entries(MUSCLE_PNG)) {
    const color = interpolateColor(volume[slug] || 0);
    if (!color) continue;

    const maskId = `hm-${slug}`;
    const mask   = document.createElementNS(NS, "mask");
    mask.setAttribute("id", maskId);
    const mi = document.createElementNS(NS, "image");
    mi.setAttribute("href",   `${REPO}/${file}`);
    mi.setAttribute("width",  "1920");
    mi.setAttribute("height", "1920");
    mask.appendChild(mi);
    defs.appendChild(mask);

    const rect = document.createElementNS(NS, "rect");
    rect.setAttribute("width",   "1920");
    rect.setAttribute("height",  "1920");
    rect.setAttribute("fill",    color);
    rect.setAttribute("mask",    `url(#${maskId})`);
    rect.setAttribute("opacity", "0.85");
    rect.setAttribute("pointer-events", "none");
    svg.appendChild(rect);
  }

  // ── Transparent hit layer — captures all mouse events ───────────────
  const hitLayer = document.createElementNS(NS, "rect");
  hitLayer.setAttribute("width",  "1920");
  hitLayer.setAttribute("height", "1920");
  hitLayer.setAttribute("fill",   "none");
  hitLayer.setAttribute("pointer-events", "all");
  svg.appendChild(hitLayer);

  let _lastSlug = null;

  hitLayer.addEventListener("mousemove", e => {
    if (!_hitsReady) return;
    const r  = svg.getBoundingClientRect();
    const px = (e.clientX - r.left) / r.width  * 1920;
    const py = (e.clientY - r.top)  / r.height * 1920;
    const slug = _getMuscleAt(px, py);

    if (slug !== _lastSlug) {
      _lastSlug = slug;
      if (slug) {
        const sets = volume[slug] || 0;
        showTooltip(`${slug.replace(/-/g, " ")}: ${sets} sets`, e);
      } else {
        hideTooltip();
      }
    } else if (slug && _tip) {
      _tip.style.left = (e.clientX + 12) + "px";
      _tip.style.top  = (e.clientY - 28) + "px";
    }
  });

  hitLayer.addEventListener("mouseleave", () => { _lastSlug = null; hideTooltip(); });

  containerEl.appendChild(svg);
}
