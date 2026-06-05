# 📷 Album Studio

A clean, responsive front end for **uploading and organizing pictures in photo albums**.
Built with vanilla HTML, CSS, and JavaScript — **zero dependencies**, no build step.

## Features

- **Drag & drop uploads** — drop image files onto the upload area, or click to browse.
- **Per-file progress bars** with real `FileReader` progress events.
- **Client-side validation** — type allow-list (JPG, PNG, GIF, WebP, AVIF, BMP, SVG) and a 25&nbsp;MB size cap, with clear inline errors.
- **Multiple albums** — create, rename, switch between, and delete albums.
- **Responsive gallery** with hover overlays showing name and file size.
- **Lightbox viewer** — click any photo for a full-screen view with keyboard navigation (←/→ to move, `Esc` to close).
- **Search** photos by file name within an album.
- **Persistent storage** — images are saved as blobs in **IndexedDB**, so albums survive page reloads (no localStorage quota issues).
- **Light & dark themes** — respects your system preference and remembers your choice.
- **Accessible** — keyboard operable dropzone, focus styles, ARIA labels, skip link, and reduced-motion support.
- **Toast notifications** for feedback on every action.

## Running it

It's a static site, so any of these work:

**Option A — included dev server (recommended):**

```bash
npm start
# → Album Studio running at http://localhost:8080
```

**Option B — open directly:**

Just open `index.html` in a modern browser. (IndexedDB works on `file://` in
most browsers.)

**Option C — any static server:**

```bash
python3 -m http.server 8080
```

## Project structure

```
index.html          # markup and templates
assets/
  styles.css        # theming + layout + components
  db.js             # tiny IndexedDB wrapper (albums + photo blobs)
  app.js            # UI logic: uploads, gallery, lightbox, albums, theme
server.js           # zero-dependency static file server
package.json        # npm start script
```

## How storage works

Albums and photos live entirely in the browser via IndexedDB:

- `albums` store — `{ id, name, createdAt, order }`
- `photos` store — `{ id, albumId, name, type, size, blob, addedAt }`, indexed by `albumId`

There is no backend; nothing is uploaded to a server. To wire this up to a real
API, replace the calls in `assets/db.js` (or swap `AlbumDB.putPhoto` for a
`fetch`/`XMLHttpRequest` upload) — the UI layer in `app.js` is decoupled from
the storage layer.

## License

MIT
