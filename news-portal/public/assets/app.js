/*
 * app.js — lógica del Portal de Noticias personal.
 * Consume /api/news y maneja filtros, búsqueda, guardados y tema.
 */
"use strict";

(() => {
  const AUTO_REFRESH_MS = 10 * 60 * 1000;
  // Orden preferido de las pestañas; categorías no listadas van al final, alfabéticamente.
  const CATEGORY_ORDER = ["Chile", "Mundo", "Economía", "Política", "Tecnología", "Emprendimiento", "IA"];
  const SAVED_KEY = "news-portal:saved";
  const THEME_KEY = "news-portal:theme";
  const SOURCES_OFF_KEY = "news-portal:sources-off";
  const SAVED_TAB = "__saved__";

  const $ = (sel) => document.querySelector(sel);
  const els = {
    todayLine: $("#todayLine"),
    updatedAt: $("#updatedAt"),
    refreshBtn: $("#refreshBtn"),
    themeToggle: $("#themeToggle"),
    tabs: $("#categoryTabs"),
    todayOnly: $("#todayOnly"),
    search: $("#searchInput"),
    chips: $("#sourceChips"),
    sourceErrors: $("#sourceErrors"),
    loading: $("#loading"),
    empty: $("#emptyState"),
    errorState: $("#errorState"),
    errorText: $("#errorText"),
    retryBtn: $("#retryBtn"),
    list: $("#newsList"),
    cardTpl: $("#newsCardTemplate")
  };

  const state = {
    data: null,
    category: "Todas",
    query: "",
    todayOnly: false,
    sourcesOff: new Set(JSON.parse(localStorage.getItem(SOURCES_OFF_KEY) || "[]")),
    saved: new Map(JSON.parse(localStorage.getItem(SAVED_KEY) || "[]"))
  };

  /* ---------------- tema ---------------- */

  function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    els.themeToggle.querySelector(".theme-icon").textContent = theme === "dark" ? "☀️" : "🌙";
  }

  function initTheme() {
    const stored = localStorage.getItem(THEME_KEY);
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    applyTheme(stored || (prefersDark ? "dark" : "light"));
    els.themeToggle.addEventListener("click", () => {
      const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
      localStorage.setItem(THEME_KEY, next);
      applyTheme(next);
    });
  }

  /* ---------------- utilidades de fecha ---------------- */

  const dayFmt = new Intl.DateTimeFormat("es-CL", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric"
  });
  const timeFmt = new Intl.DateTimeFormat("es-CL", { hour: "2-digit", minute: "2-digit" });

  function capitalize(str) {
    return str ? str.charAt(0).toUpperCase() + str.slice(1) : str;
  }

  function sameDay(a, b) {
    return (
      a.getFullYear() === b.getFullYear() &&
      a.getMonth() === b.getMonth() &&
      a.getDate() === b.getDate()
    );
  }

  function relativeTime(iso) {
    if (!iso) return "";
    const then = new Date(iso);
    const mins = Math.round((Date.now() - then.getTime()) / 60000);
    if (mins < 1) return "ahora";
    if (mins < 60) return `hace ${mins} min`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `hace ${hours} h`;
    const days = Math.floor(hours / 24);
    if (days === 1) return "ayer";
    if (days < 7) return `hace ${days} días`;
    return capitalize(dayFmt.format(then));
  }

  function dayLabel(iso) {
    const d = new Date(iso);
    const today = new Date();
    const yesterday = new Date(today.getTime() - 86400000);
    if (sameDay(d, today)) return "Hoy";
    if (sameDay(d, yesterday)) return "Ayer";
    return capitalize(dayFmt.format(d));
  }

  /* ---------------- persistencia ---------------- */

  function persistSaved() {
    localStorage.setItem(SAVED_KEY, JSON.stringify([...state.saved.entries()]));
  }
  function persistSourcesOff() {
    localStorage.setItem(SOURCES_OFF_KEY, JSON.stringify([...state.sourcesOff]));
  }

  /* ---------------- carga de datos ---------------- */

  async function loadNews(forceRefresh = false) {
    els.refreshBtn.classList.add("is-loading");
    els.refreshBtn.disabled = true;
    if (!state.data) {
      els.loading.hidden = false;
      els.errorState.hidden = true;
    }
    try {
      const res = await fetch(`/api/news${forceRefresh ? "?refresh=1" : ""}`);
      if (!res.ok) throw new Error(`El servidor respondió HTTP ${res.status}`);
      state.data = await res.json();
      els.errorState.hidden = true;
      renderAll();
    } catch (err) {
      if (!state.data) {
        els.loading.hidden = true;
        els.errorState.hidden = false;
        els.errorText.textContent = String(err.message || err);
      }
    } finally {
      els.refreshBtn.classList.remove("is-loading");
      els.refreshBtn.disabled = false;
    }
  }

  /* ---------------- filtrado ---------------- */

  function visibleItems() {
    if (!state.data) return [];
    if (state.category === SAVED_TAB) {
      return [...state.saved.values()].sort((a, b) =>
        (b.date || "").localeCompare(a.date || "")
      );
    }
    const q = state.query.trim().toLowerCase();
    const today = new Date();
    return state.data.items.filter((item) => {
      if (state.category !== "Todas" && item.category !== state.category) return false;
      if (state.sourcesOff.has(item.sourceId)) return false;
      if (state.todayOnly && (!item.date || !sameDay(new Date(item.date), today))) return false;
      if (q && !(item.title + " " + item.description + " " + item.source).toLowerCase().includes(q)) return false;
      return true;
    });
  }

  /* ---------------- render ---------------- */

  function renderTabs() {
    const counts = new Map();
    for (const item of state.data.items) {
      counts.set(item.category, (counts.get(item.category) || 0) + 1);
    }
    const sorted = [...counts.keys()].sort((a, b) => {
      const ia = CATEGORY_ORDER.indexOf(a);
      const ib = CATEGORY_ORDER.indexOf(b);
      if (ia !== -1 && ib !== -1) return ia - ib;
      if (ia !== -1) return -1;
      if (ib !== -1) return 1;
      return a.localeCompare(b, "es");
    });
    const categories = ["Todas", ...sorted];

    els.tabs.innerHTML = "";
    for (const cat of categories) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "tab" + (state.category === cat ? " is-active" : "");
      btn.setAttribute("role", "tab");
      btn.setAttribute("aria-selected", String(state.category === cat));
      const count = cat === "Todas" ? state.data.items.length : counts.get(cat);
      btn.innerHTML = `${cat}<span class="tab__count">${count}</span>`;
      btn.addEventListener("click", () => {
        state.category = cat;
        renderAll();
      });
      els.tabs.appendChild(btn);
    }

    const savedBtn = document.createElement("button");
    savedBtn.type = "button";
    savedBtn.className = "tab" + (state.category === SAVED_TAB ? " is-active" : "");
    savedBtn.setAttribute("role", "tab");
    savedBtn.setAttribute("aria-selected", String(state.category === SAVED_TAB));
    savedBtn.innerHTML = `⭐ Guardadas<span class="tab__count">${state.saved.size}</span>`;
    savedBtn.addEventListener("click", () => {
      state.category = SAVED_TAB;
      renderAll();
    });
    els.tabs.appendChild(savedBtn);
  }

  function renderChips() {
    els.chips.innerHTML = "";
    const failed = [];
    for (const src of state.data.sources) {
      const chip = document.createElement("button");
      chip.type = "button";
      const on = !state.sourcesOff.has(src.id);
      chip.className = "chip" + (on ? " is-on" : "") + (src.ok ? "" : " is-err");
      chip.textContent = src.name;
      chip.title = src.ok
        ? `${src.count} noticias · clic para ${on ? "ocultar" : "mostrar"}`
        : `No disponible: ${src.error}`;
      chip.setAttribute("aria-pressed", String(on));
      chip.addEventListener("click", () => {
        if (state.sourcesOff.has(src.id)) state.sourcesOff.delete(src.id);
        else state.sourcesOff.add(src.id);
        persistSourcesOff();
        renderAll();
      });
      els.chips.appendChild(chip);
      if (!src.ok) failed.push(src.name);
    }

    if (failed.length) {
      els.sourceErrors.hidden = false;
      els.sourceErrors.textContent =
        `⚠️ Fuentes no disponibles en este momento: ${failed.join(", ")}. ` +
        "Puedes reemplazarlas en feeds.json.";
    } else {
      els.sourceErrors.hidden = true;
    }
  }

  function renderCard(item) {
    const node = els.cardTpl.content.firstElementChild.cloneNode(true);
    const imgLink = node.querySelector(".news-card__imglink");
    const img = node.querySelector(".news-card__img");
    if (item.image) {
      imgLink.hidden = false;
      imgLink.href = item.link;
      img.src = item.image;
      img.addEventListener("error", () => { imgLink.hidden = true; });
    }
    node.querySelector(".news-card__source").textContent = item.source;
    node.querySelector(".news-card__category").textContent = item.category;
    const time = node.querySelector(".news-card__time");
    time.textContent = relativeTime(item.date);
    if (item.date) {
      time.dateTime = item.date;
      time.title = `${dayFmt.format(new Date(item.date))}, ${timeFmt.format(new Date(item.date))}`;
    }
    const link = node.querySelector(".news-card__link");
    link.href = item.link;
    link.textContent = item.title;
    node.querySelector(".news-card__desc").textContent = item.description;

    const saveBtn = node.querySelector(".news-card__save");
    const paintSave = () => {
      const saved = state.saved.has(item.id);
      saveBtn.textContent = saved ? "★" : "☆";
      saveBtn.classList.toggle("is-saved", saved);
      saveBtn.setAttribute(
        "aria-label",
        saved ? "Quitar de guardadas" : "Guardar para leer después"
      );
    };
    paintSave();
    saveBtn.addEventListener("click", () => {
      if (state.saved.has(item.id)) state.saved.delete(item.id);
      else state.saved.set(item.id, item);
      persistSaved();
      if (state.category === SAVED_TAB) renderAll();
      else {
        paintSave();
        renderTabs();
      }
    });
    return node;
  }

  function renderList() {
    const items = visibleItems();
    els.list.innerHTML = "";
    els.empty.hidden = items.length > 0;

    let lastDay = null;
    for (const item of items) {
      const label = item.date ? dayLabel(item.date) : "Sin fecha";
      if (label !== lastDay) {
        lastDay = label;
        const divider = document.createElement("li");
        divider.className = "day-divider";
        divider.textContent = label;
        els.list.appendChild(divider);
      }
      els.list.appendChild(renderCard(item));
    }
  }

  function renderAll() {
    if (!state.data) return;
    els.loading.hidden = true;
    els.updatedAt.textContent = `Actualizado ${relativeTime(state.data.generatedAt)}`;
    renderTabs();
    renderChips();
    renderList();
  }

  /* ---------------- init ---------------- */

  function init() {
    initTheme();
    els.todayLine.textContent = capitalize(dayFmt.format(new Date()));

    els.refreshBtn.addEventListener("click", () => loadNews(true));
    els.retryBtn.addEventListener("click", () => loadNews(true));
    els.todayOnly.addEventListener("change", () => {
      state.todayOnly = els.todayOnly.checked;
      renderList();
    });

    let searchTimer;
    els.search.addEventListener("input", () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {
        state.query = els.search.value;
        renderList();
      }, 200);
    });

    loadNews();
    setInterval(() => loadNews(), AUTO_REFRESH_MS);
    setInterval(() => {
      if (state.data) els.updatedAt.textContent = `Actualizado ${relativeTime(state.data.generatedAt)}`;
    }, 60000);
  }

  init();
})();
