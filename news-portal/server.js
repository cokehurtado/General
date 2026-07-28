#!/usr/bin/env node
/*
 * server.js — Portal de Noticias personal.
 *
 * Servidor sin dependencias que:
 *   - Sirve el front end estático desde public/
 *   - Expone GET /api/news : agrega todos los feeds de feeds.json,
 *     los parsea y devuelve un JSON unificado, ordenado por fecha.
 *
 * Uso: node server.js [puerto]          (por defecto 8090)
 * Opciones vía variables de entorno:
 *   FEEDS_FILE=/ruta/feeds.json   usar otra lista de fuentes
 *   CACHE_TTL_MIN=10              minutos de caché del agregado
 */
"use strict";

const http = require("http");
const fs = require("fs");
const path = require("path");
const { parseFeed } = require("./lib/rss-parser");

const PORT = Number(process.argv[2]) || Number(process.env.PORT) || 8090;
const ROOT = path.join(__dirname, "public");
const FEEDS_FILE = process.env.FEEDS_FILE || path.join(__dirname, "feeds.json");
const CACHE_TTL_MS = (Number(process.env.CACHE_TTL_MIN) || 10) * 60 * 1000;
const FETCH_TIMEOUT_MS = 12000;
const MAX_ITEMS_PER_FEED = 40;
const MAX_ITEMS_TOTAL = 400;

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon",
  ".png": "image/png",
  ".webp": "image/webp",
  ".txt": "text/plain; charset=utf-8"
};

/* ---------------------------------------------------------------- feeds */

function loadFeeds() {
  const raw = fs.readFileSync(FEEDS_FILE, "utf8");
  const parsed = JSON.parse(raw);
  const feeds = Array.isArray(parsed) ? parsed : parsed.feeds;
  if (!Array.isArray(feeds) || feeds.length === 0) {
    throw new Error(`No hay feeds definidos en ${FEEDS_FILE}`);
  }
  return feeds.filter((f) => f && f.id && f.name && f.url);
}

async function fetchFeed(feed) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
  try {
    const res = await fetch(feed.url, {
      signal: controller.signal,
      redirect: "follow",
      headers: {
        "User-Agent": "PortalNoticiasPersonal/1.0 (+lector RSS personal)",
        Accept: "application/rss+xml, application/atom+xml, application/xml, text/xml, */*"
      }
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const xml = await decodeBody(res);
    const parsed = parseFeed(xml);
    const items = parsed.items.slice(0, MAX_ITEMS_PER_FEED).map((item, i) => ({
      id: `${feed.id}:${hashCode(item.link)}`,
      sourceId: feed.id,
      source: feed.name,
      category: feed.category || "General",
      title: item.title,
      link: item.link,
      description: item.description,
      date: item.date,
      image: item.image,
      order: i
    }));
    return { feed, ok: true, items };
  } catch (err) {
    const message = err && err.name === "AbortError" ? "Tiempo de espera agotado" : String((err && err.message) || err);
    return { feed, ok: false, error: message, items: [] };
  } finally {
    clearTimeout(timer);
  }
}

/*
 * fetch().text() siempre decodifica como UTF-8, pero varios medios chilenos
 * (p. ej. Emol) sirven sus RSS en ISO-8859-1. Detectamos el charset en el
 * header Content-Type o en la declaración XML y decodificamos acorde.
 */
async function decodeBody(res) {
  const buf = Buffer.from(await res.arrayBuffer());
  const ctype = res.headers.get("content-type") || "";
  let charset = (ctype.match(/charset=([\w-]+)/i) || [])[1];
  if (!charset) {
    const head = buf.slice(0, 200).toString("latin1");
    charset = (head.match(/<\?xml[^>]*encoding=["']([\w-]+)["']/i) || [])[1];
  }
  charset = (charset || "utf-8").toLowerCase();
  try {
    return new TextDecoder(charset).decode(buf);
  } catch {
    return buf.toString("utf8");
  }
}

function hashCode(str) {
  let h = 0;
  for (let i = 0; i < str.length; i++) {
    h = (Math.imul(h, 31) + str.charCodeAt(i)) | 0;
  }
  return (h >>> 0).toString(36);
}

async function aggregateNews() {
  const feeds = loadFeeds();
  const results = await Promise.all(feeds.map(fetchFeed));

  const seenLinks = new Set();
  const items = [];
  for (const r of results) {
    for (const item of r.items) {
      if (seenLinks.has(item.link)) continue;
      seenLinks.add(item.link);
      items.push(item);
    }
  }

  // Más recientes primero; items sin fecha van al final conservando su orden en el feed.
  items.sort((a, b) => {
    if (a.date && b.date) return b.date.localeCompare(a.date);
    if (a.date) return -1;
    if (b.date) return 1;
    return a.order - b.order;
  });

  return {
    generatedAt: new Date().toISOString(),
    sources: results.map((r) => ({
      id: r.feed.id,
      name: r.feed.name,
      category: r.feed.category || "General",
      homepage: r.feed.homepage || "",
      ok: r.ok,
      error: r.ok ? null : r.error,
      count: r.items.length
    })),
    items: items.slice(0, MAX_ITEMS_TOTAL).map(({ order, ...item }) => item)
  };
}

/* ---------------------------------------------------------------- caché */

let cache = { data: null, at: 0 };
let inflight = null;

async function getNews(forceRefresh) {
  const fresh = cache.data && Date.now() - cache.at < CACHE_TTL_MS;
  if (fresh && !forceRefresh) return cache.data;
  if (!inflight) {
    inflight = aggregateNews()
      .then((data) => {
        cache = { data, at: Date.now() };
        return data;
      })
      .finally(() => {
        inflight = null;
      });
  }
  return inflight;
}

/* --------------------------------------------------------------- server */

function sendJson(res, status, obj) {
  const body = JSON.stringify(obj);
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store"
  });
  res.end(body);
}

const server = http.createServer(async (req, res) => {
  try {
    const url = new URL(req.url, `http://localhost:${PORT}`);

    if (url.pathname === "/api/news") {
      try {
        const data = await getNews(url.searchParams.get("refresh") === "1");
        sendJson(res, 200, data);
      } catch (err) {
        sendJson(res, 500, { error: String((err && err.message) || err) });
      }
      return;
    }

    if (url.pathname === "/api/health") {
      sendJson(res, 200, { ok: true, cachedAt: cache.at ? new Date(cache.at).toISOString() : null });
      return;
    }

    // Estáticos
    let filePath = path.normalize(path.join(ROOT, decodeURIComponent(url.pathname)));
    if (!filePath.startsWith(ROOT)) {
      res.writeHead(403).end("Forbidden");
      return;
    }
    if (url.pathname === "/" || url.pathname.endsWith("/")) {
      filePath = path.join(filePath, "index.html");
    }
    fs.stat(filePath, (err, stat) => {
      if (err || !stat.isFile()) {
        res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" }).end("404 Not Found");
        return;
      }
      const ext = path.extname(filePath).toLowerCase();
      res.writeHead(200, { "Content-Type": MIME[ext] || "application/octet-stream" });
      fs.createReadStream(filePath).pipe(res);
    });
  } catch (e) {
    res.writeHead(500, { "Content-Type": "text/plain; charset=utf-8" }).end("500 Server Error");
  }
});

server.listen(PORT, () => {
  console.log(`Portal de Noticias corriendo en http://localhost:${PORT}`);
  console.log(`Fuentes: ${FEEDS_FILE}`);
});
