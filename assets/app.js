/*
 * app.js — Album Studio front end.
 *
 * Handles album management, drag & drop uploads with validation and per-file
 * progress, the gallery grid, search, a lightbox viewer, and theming.
 * Persists everything through window.AlbumDB (IndexedDB).
 */
(function () {
  "use strict";

  const ACCEPTED_TYPES = [
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/avif",
    "image/bmp",
    "image/svg+xml"
  ];
  const MAX_BYTES = 25 * 1024 * 1024; // 25 MB
  const THEME_KEY = "album-studio:theme";
  const ACTIVE_ALBUM_KEY = "album-studio:activeAlbum";

  // ---- App state ----
  const state = {
    albums: [],          // [{ id, name, createdAt, order, count }]
    activeAlbumId: null,
    photos: [],          // photos for the active album (with objectURL)
    filter: "",
    lightboxIndex: -1
  };

  // ---- DOM refs ----
  const el = {};

  function cacheDom() {
    const ids = [
      "newAlbumBtn", "themeToggle", "albumList", "albumCount",
      "activeAlbumName", "activeAlbumMeta", "searchInput",
      "renameAlbumBtn", "deleteAlbumBtn",
      "dropzone", "fileInput", "uploadQueue",
      "emptyState", "gallery",
      "lightbox", "lbClose", "lbPrev", "lbNext", "lbImage", "lbCaption",
      "toasts", "photoCardTemplate"
    ];
    ids.forEach(function (id) { el[id] = document.getElementById(id); });
  }

  // ---- Utilities ----

  function uid() {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    return "id-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 9);
  }

  function formatBytes(bytes) {
    if (bytes === 0) return "0 B";
    const units = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    const value = bytes / Math.pow(1024, i);
    return (i === 0 ? value : value.toFixed(value < 10 ? 1 : 0)) + " " + units[i];
  }

  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function pluralize(n, word) {
    return n + " " + word + (n === 1 ? "" : "s");
  }

  function toast(message, kind) {
    const node = document.createElement("div");
    node.className = "toast toast--" + (kind || "info");
    node.textContent = message;
    el.toasts.appendChild(node);
    requestAnimationFrame(function () { node.classList.add("toast--show"); });
    setTimeout(function () {
      node.classList.remove("toast--show");
      setTimeout(function () { node.remove(); }, 300);
    }, 3200);
  }

  function validateFile(file) {
    const typeOk = ACCEPTED_TYPES.indexOf(file.type) !== -1 ||
      (file.type === "" && /\.(jpe?g|png|gif|webp|avif|bmp|svg)$/i.test(file.name));
    if (!typeOk) return "Unsupported file type";
    if (file.size > MAX_BYTES) return "Larger than " + formatBytes(MAX_BYTES);
    if (file.size === 0) return "File is empty";
    return null;
  }

  // ---- Albums ----

  function defaultAlbum() {
    return {
      id: uid(),
      name: "My First Album",
      createdAt: Date.now(),
      order: 0
    };
  }

  function loadAlbums() {
    return AlbumDB.getAlbums().then(function (albums) {
      if (albums.length === 0) {
        const album = defaultAlbum();
        return AlbumDB.putAlbum(album).then(function () { return [album]; });
      }
      return albums;
    }).then(function (albums) {
      return Promise.all(albums.map(function (a) {
        return AlbumDB.countPhotos(a.id).then(function (count) {
          a.count = count;
          return a;
        });
      }));
    }).then(function (albums) {
      state.albums = albums;
      return albums;
    });
  }

  function renderAlbumList() {
    el.albumCount.textContent = String(state.albums.length);
    el.albumList.innerHTML = "";
    state.albums.forEach(function (album) {
      const li = document.createElement("li");
      li.className = "album-item" + (album.id === state.activeAlbumId ? " album-item--active" : "");
      li.setAttribute("role", "listitem");
      li.dataset.id = album.id;
      li.innerHTML =
        '<button class="album-item__btn" type="button">' +
          '<span class="album-item__name">' + escapeHtml(album.name) + "</span>" +
          '<span class="album-item__count">' + pluralize(album.count || 0, "photo") + "</span>" +
        "</button>";
      li.querySelector(".album-item__btn").addEventListener("click", function () {
        selectAlbum(album.id);
      });
      el.albumList.appendChild(li);
    });
  }

  function activeAlbum() {
    return state.albums.find(function (a) { return a.id === state.activeAlbumId; }) || null;
  }

  function selectAlbum(albumId) {
    state.activeAlbumId = albumId;
    state.filter = "";
    el.searchInput.value = "";
    try { localStorage.setItem(ACTIVE_ALBUM_KEY, albumId); } catch (e) { void e; }
    renderAlbumList();
    renderAlbumBar();
    return loadActivePhotos();
  }

  function renderAlbumBar() {
    const album = activeAlbum();
    if (!album) return;
    el.activeAlbumName.textContent = album.name;
    const created = new Date(album.createdAt);
    el.activeAlbumMeta.textContent =
      pluralize(album.count || 0, "photo") + " · created " +
      created.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
  }

  function createAlbum() {
    const name = window.prompt("Name your new album:", "Untitled album");
    if (name === null) return;
    const trimmed = name.trim() || "Untitled album";
    const album = {
      id: uid(),
      name: trimmed,
      createdAt: Date.now(),
      order: state.albums.length,
      count: 0
    };
    AlbumDB.putAlbum(album).then(function () {
      state.albums.push(album);
      selectAlbum(album.id);
      toast('Album "' + trimmed + '" created', "success");
    }).catch(function (err) { toast("Could not create album: " + err.message, "error"); });
  }

  function renameAlbum() {
    const album = activeAlbum();
    if (!album) return;
    const name = window.prompt("Rename album:", album.name);
    if (name === null) return;
    const trimmed = name.trim();
    if (!trimmed) { toast("Album name cannot be empty", "error"); return; }
    album.name = trimmed;
    AlbumDB.putAlbum({ id: album.id, name: trimmed, createdAt: album.createdAt, order: album.order })
      .then(function () {
        renderAlbumList();
        renderAlbumBar();
        toast("Album renamed", "success");
      }).catch(function (err) { toast("Rename failed: " + err.message, "error"); });
  }

  function deleteActiveAlbum() {
    const album = activeAlbum();
    if (!album) return;
    if (state.albums.length === 1) {
      toast("You need at least one album", "error");
      return;
    }
    const ok = window.confirm(
      'Delete "' + album.name + '" and its ' + pluralize(album.count || 0, "photo") + "? This cannot be undone."
    );
    if (!ok) return;
    AlbumDB.deleteAlbum(album.id).then(function () {
      state.albums = state.albums.filter(function (a) { return a.id !== album.id; });
      const next = state.albums[0];
      toast("Album deleted", "success");
      selectAlbum(next.id);
    }).catch(function (err) { toast("Delete failed: " + err.message, "error"); });
  }

  // ---- Photos ----

  function loadActivePhotos() {
    revokePhotoUrls();
    return AlbumDB.getPhotos(state.activeAlbumId).then(function (photos) {
      state.photos = photos.map(function (p) {
        p.objectURL = URL.createObjectURL(p.blob);
        return p;
      });
      renderGallery();
    }).catch(function (err) { toast("Could not load photos: " + err.message, "error"); });
  }

  function revokePhotoUrls() {
    state.photos.forEach(function (p) {
      if (p.objectURL) URL.revokeObjectURL(p.objectURL);
    });
  }

  function filteredPhotos() {
    if (!state.filter) return state.photos;
    const q = state.filter.toLowerCase();
    return state.photos.filter(function (p) {
      return p.name.toLowerCase().indexOf(q) !== -1;
    });
  }

  function renderGallery() {
    const photos = filteredPhotos();
    el.gallery.innerHTML = "";
    const album = activeAlbum();
    const hasAny = state.photos.length > 0;
    el.emptyState.hidden = hasAny;

    if (album) {
      album.count = state.photos.length;
    }
    renderAlbumBar();
    renderAlbumList();

    if (!hasAny) return;

    if (photos.length === 0) {
      const li = document.createElement("li");
      li.className = "gallery__no-match";
      li.textContent = 'No photos match "' + state.filter + '".';
      el.gallery.appendChild(li);
      return;
    }

    const frag = document.createDocumentFragment();
    photos.forEach(function (photo) {
      frag.appendChild(buildCard(photo));
    });
    el.gallery.appendChild(frag);
  }

  function buildCard(photo) {
    const node = el.photoCardTemplate.content.firstElementChild.cloneNode(true);
    node.dataset.id = photo.id;
    const img = node.querySelector(".photo-card__thumb");
    img.src = photo.objectURL;
    img.alt = photo.name;
    node.querySelector(".photo-card__name").textContent = photo.name;
    node.querySelector(".photo-card__size").textContent = formatBytes(photo.size);

    node.querySelector(".photo-card__thumb-btn").addEventListener("click", function () {
      openLightbox(photo.id);
    });
    node.querySelector(".photo-card__delete").addEventListener("click", function (event) {
      event.stopPropagation();
      removePhoto(photo.id);
    });
    return node;
  }

  function removePhoto(photoId) {
    const photo = state.photos.find(function (p) { return p.id === photoId; });
    if (!photo) return;
    if (!window.confirm('Delete "' + photo.name + '"?')) return;
    AlbumDB.deletePhoto(photoId).then(function () {
      if (photo.objectURL) URL.revokeObjectURL(photo.objectURL);
      state.photos = state.photos.filter(function (p) { return p.id !== photoId; });
      renderGallery();
      toast("Photo deleted", "success");
    }).catch(function (err) { toast("Delete failed: " + err.message, "error"); });
  }

  // ---- Upload flow ----

  function handleFiles(fileList) {
    const files = Array.prototype.slice.call(fileList || []);
    if (files.length === 0) return;

    const accepted = [];
    files.forEach(function (file) {
      const error = validateFile(file);
      if (error) {
        addQueueRow(file, "error", error);
      } else {
        accepted.push(file);
      }
    });

    if (accepted.length === 0) {
      toast("No valid images were added", "error");
      return;
    }

    el.uploadQueue.hidden = false;
    // Upload sequentially so progress reads naturally and we don't thrash IO.
    let chain = Promise.resolve();
    accepted.forEach(function (file) {
      chain = chain.then(function () { return uploadOne(file); });
    });
    chain.then(function () {
      toast(pluralize(accepted.length, "photo") + " added", "success");
      // Auto-clear the queue shortly after everything settles.
      setTimeout(clearFinishedQueueRows, 1500);
    });
  }

  function addQueueRow(file, status, message) {
    const row = document.createElement("div");
    row.className = "queue-row queue-row--" + status;
    row.innerHTML =
      '<div class="queue-row__name" title="' + escapeHtml(file.name) + '">' +
        escapeHtml(file.name) + "</div>" +
      '<div class="queue-row__bar"><span class="queue-row__fill"></span></div>' +
      '<div class="queue-row__status">' + escapeHtml(message || "") + "</div>";
    el.uploadQueue.hidden = false;
    el.uploadQueue.appendChild(row);
    return row;
  }

  function uploadOne(file) {
    const row = addQueueRow(file, "uploading", "0%");
    const fill = row.querySelector(".queue-row__fill");
    const statusEl = row.querySelector(".queue-row__status");

    return readWithProgress(file, function (pct) {
      fill.style.width = pct + "%";
      statusEl.textContent = pct + "%";
    }).then(function (blob) {
      const photo = {
        id: uid(),
        albumId: state.activeAlbumId,
        name: file.name,
        type: file.type || "image/*",
        size: file.size,
        blob: blob,
        addedAt: Date.now()
      };
      return AlbumDB.putPhoto(photo).then(function () {
        photo.objectURL = URL.createObjectURL(photo.blob);
        state.photos.push(photo);
        renderGallery();
        row.classList.remove("queue-row--uploading");
        row.classList.add("queue-row--done");
        fill.style.width = "100%";
        statusEl.textContent = "Done ✓";
      });
    }).catch(function (err) {
      row.classList.remove("queue-row--uploading");
      row.classList.add("queue-row--error");
      statusEl.textContent = "Failed";
      toast('Could not upload "' + file.name + '": ' + err.message, "error");
    });
  }

  // Reads a file into a Blob, reporting progress. FileReader gives us real
  // progress events; we keep the resulting Blob to store in IndexedDB.
  function readWithProgress(file, onProgress) {
    return new Promise(function (resolve, reject) {
      const reader = new FileReader();
      reader.onprogress = function (e) {
        if (e.lengthComputable) {
          onProgress(Math.min(99, Math.round((e.loaded / e.total) * 100)));
        }
      };
      reader.onload = function () {
        onProgress(100);
        resolve(new Blob([reader.result], { type: file.type || "application/octet-stream" }));
      };
      reader.onerror = function () { reject(reader.error || new Error("Read error")); };
      reader.readAsArrayBuffer(file);
    });
  }

  function clearFinishedQueueRows() {
    const rows = el.uploadQueue.querySelectorAll(".queue-row--done");
    rows.forEach(function (r) { r.remove(); });
    if (el.uploadQueue.children.length === 0) {
      el.uploadQueue.hidden = true;
    }
  }

  // ---- Lightbox ----

  function openLightbox(photoId) {
    const photos = filteredPhotos();
    const index = photos.findIndex(function (p) { return p.id === photoId; });
    if (index === -1) return;
    state.lightboxIndex = index;
    showLightboxPhoto();
    el.lightbox.hidden = false;
    document.body.classList.add("no-scroll");
    el.lbClose.focus();
  }

  function showLightboxPhoto() {
    const photos = filteredPhotos();
    const photo = photos[state.lightboxIndex];
    if (!photo) return;
    el.lbImage.src = photo.objectURL;
    el.lbImage.alt = photo.name;
    el.lbCaption.textContent =
      photo.name + "  ·  " + formatBytes(photo.size) +
      "  ·  " + (state.lightboxIndex + 1) + " / " + photos.length;
    const multiple = photos.length > 1;
    el.lbPrev.style.visibility = multiple ? "visible" : "hidden";
    el.lbNext.style.visibility = multiple ? "visible" : "hidden";
  }

  function moveLightbox(delta) {
    const photos = filteredPhotos();
    if (photos.length === 0) return;
    state.lightboxIndex = (state.lightboxIndex + delta + photos.length) % photos.length;
    showLightboxPhoto();
  }

  function closeLightbox() {
    el.lightbox.hidden = true;
    el.lbImage.src = "";
    state.lightboxIndex = -1;
    document.body.classList.remove("no-scroll");
  }

  // ---- Theme ----

  function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    const icon = el.themeToggle.querySelector(".theme-icon");
    if (icon) icon.textContent = theme === "dark" ? "☀️" : "🌙";
    try { localStorage.setItem(THEME_KEY, theme); } catch (e) { void e; }
  }

  function initTheme() {
    let theme;
    try { theme = localStorage.getItem(THEME_KEY); } catch (e) { theme = null; }
    if (!theme) {
      theme = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark" : "light";
    }
    applyTheme(theme);
  }

  function toggleTheme() {
    const current = document.documentElement.dataset.theme;
    applyTheme(current === "dark" ? "light" : "dark");
  }

  // ---- Drag & drop wiring ----

  function initDropzone() {
    const dz = el.dropzone;

    dz.addEventListener("click", function () { el.fileInput.click(); });
    dz.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        el.fileInput.click();
      }
    });

    el.fileInput.addEventListener("change", function () {
      handleFiles(el.fileInput.files);
      el.fileInput.value = ""; // allow re-selecting the same file
    });

    ["dragenter", "dragover"].forEach(function (type) {
      dz.addEventListener(type, function (e) {
        e.preventDefault();
        e.stopPropagation();
        dz.classList.add("dropzone--active");
      });
    });
    ["dragleave", "dragend"].forEach(function (type) {
      dz.addEventListener(type, function (e) {
        e.preventDefault();
        e.stopPropagation();
        if (e.target === dz) dz.classList.remove("dropzone--active");
      });
    });
    dz.addEventListener("drop", function (e) {
      e.preventDefault();
      e.stopPropagation();
      dz.classList.remove("dropzone--active");
      if (e.dataTransfer && e.dataTransfer.files) {
        handleFiles(e.dataTransfer.files);
      }
    });

    // Prevent the browser from navigating away if a file is dropped outside.
    window.addEventListener("dragover", function (e) { e.preventDefault(); });
    window.addEventListener("drop", function (e) { e.preventDefault(); });
  }

  // ---- Event wiring ----

  function initEvents() {
    el.newAlbumBtn.addEventListener("click", createAlbum);
    el.renameAlbumBtn.addEventListener("click", renameAlbum);
    el.deleteAlbumBtn.addEventListener("click", deleteActiveAlbum);
    el.themeToggle.addEventListener("click", toggleTheme);

    el.searchInput.addEventListener("input", function () {
      state.filter = el.searchInput.value.trim();
      renderGallery();
    });

    el.lbClose.addEventListener("click", closeLightbox);
    el.lbPrev.addEventListener("click", function () { moveLightbox(-1); });
    el.lbNext.addEventListener("click", function () { moveLightbox(1); });
    el.lightbox.addEventListener("click", function (e) {
      if (e.target === el.lightbox) closeLightbox();
    });

    document.addEventListener("keydown", function (e) {
      if (el.lightbox.hidden) return;
      if (e.key === "Escape") closeLightbox();
      else if (e.key === "ArrowLeft") moveLightbox(-1);
      else if (e.key === "ArrowRight") moveLightbox(1);
    });

    window.addEventListener("beforeunload", revokePhotoUrls);
  }

  // ---- Bootstrap ----

  function init() {
    cacheDom();
    initTheme();
    initEvents();
    initDropzone();

    loadAlbums().then(function (albums) {
      let activeId = null;
      try { activeId = localStorage.getItem(ACTIVE_ALBUM_KEY); } catch (e) { activeId = null; }
      const exists = albums.some(function (a) { return a.id === activeId; });
      selectAlbum(exists ? activeId : albums[0].id);
    }).catch(function (err) {
      toast("Failed to initialize: " + err.message, "error");
      el.activeAlbumName.textContent = "Storage unavailable";
      el.activeAlbumMeta.textContent = err.message;
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
