#!/usr/bin/env node
/*
 * server.js — minimal zero-dependency static file server for Album Studio.
 * Usage: node server.js [port]   (default port 8080)
 */
"use strict";

const http = require("http");
const fs = require("fs");
const path = require("path");

const PORT = Number(process.argv[2]) || process.env.PORT || 8080;
const ROOT = __dirname;

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".gif": "image/gif",
  ".webp": "image/webp",
  ".txt": "text/plain; charset=utf-8",
  ".map": "application/json; charset=utf-8"
};

const server = http.createServer((req, res) => {
  try {
    const urlPath = decodeURIComponent(req.url.split("?")[0]);
    let filePath = path.normalize(path.join(ROOT, urlPath));

    // Prevent path traversal outside the project root.
    if (!filePath.startsWith(ROOT)) {
      res.writeHead(403).end("Forbidden");
      return;
    }
    if (urlPath === "/" || urlPath.endsWith("/")) {
      filePath = path.join(filePath, "index.html");
    }

    fs.stat(filePath, (err, stat) => {
      if (err || !stat.isFile()) {
        res.writeHead(404, { "Content-Type": "text/plain" }).end("404 Not Found");
        return;
      }
      const ext = path.extname(filePath).toLowerCase();
      res.writeHead(200, { "Content-Type": MIME[ext] || "application/octet-stream" });
      fs.createReadStream(filePath).pipe(res);
    });
  } catch (e) {
    res.writeHead(500, { "Content-Type": "text/plain" }).end("500 Server Error");
  }
});

server.listen(PORT, () => {
  console.log(`Album Studio running at http://localhost:${PORT}`);
});
