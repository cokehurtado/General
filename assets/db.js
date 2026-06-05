/*
 * db.js — tiny IndexedDB wrapper for Album Studio.
 *
 * Stores image blobs so albums survive page reloads without bumping into the
 * ~5MB localStorage quota. Exposes a small Promise-based API on `window.AlbumDB`.
 *
 * Object stores:
 *   - albums: { id, name, createdAt, order }
 *   - photos: { id, albumId, name, type, size, blob, addedAt }   index: by_album
 */
(function () {
  "use strict";

  const DB_NAME = "album-studio";
  const DB_VERSION = 1;
  const STORE_ALBUMS = "albums";
  const STORE_PHOTOS = "photos";

  let dbPromise = null;

  function openDB() {
    if (dbPromise) return dbPromise;
    dbPromise = new Promise(function (resolve, reject) {
      if (!("indexedDB" in window)) {
        reject(new Error("IndexedDB is not supported in this browser."));
        return;
      }
      const req = indexedDB.open(DB_NAME, DB_VERSION);
      req.onupgradeneeded = function (event) {
        const db = req.result;
        if (!db.objectStoreNames.contains(STORE_ALBUMS)) {
          db.createObjectStore(STORE_ALBUMS, { keyPath: "id" });
        }
        if (!db.objectStoreNames.contains(STORE_PHOTOS)) {
          const photos = db.createObjectStore(STORE_PHOTOS, { keyPath: "id" });
          photos.createIndex("by_album", "albumId", { unique: false });
        }
        void event;
      };
      req.onsuccess = function () { resolve(req.result); };
      req.onerror = function () { reject(req.error); };
    });
    return dbPromise;
  }

  function tx(storeNames, mode) {
    return openDB().then(function (db) {
      const transaction = db.transaction(storeNames, mode);
      return transaction;
    });
  }

  function reqToPromise(request) {
    return new Promise(function (resolve, reject) {
      request.onsuccess = function () { resolve(request.result); };
      request.onerror = function () { reject(request.error); };
    });
  }

  function txDone(transaction) {
    return new Promise(function (resolve, reject) {
      transaction.oncomplete = function () { resolve(); };
      transaction.onabort = function () { reject(transaction.error); };
      transaction.onerror = function () { reject(transaction.error); };
    });
  }

  // ---- Albums ----

  function getAlbums() {
    return tx(STORE_ALBUMS, "readonly").then(function (t) {
      return reqToPromise(t.objectStore(STORE_ALBUMS).getAll());
    }).then(function (albums) {
      return albums.sort(function (a, b) {
        return (a.order ?? 0) - (b.order ?? 0) || a.createdAt - b.createdAt;
      });
    });
  }

  function putAlbum(album) {
    return tx(STORE_ALBUMS, "readwrite").then(function (t) {
      t.objectStore(STORE_ALBUMS).put(album);
      return txDone(t).then(function () { return album; });
    });
  }

  function deleteAlbum(albumId) {
    return tx([STORE_ALBUMS, STORE_PHOTOS], "readwrite").then(function (t) {
      t.objectStore(STORE_ALBUMS).delete(albumId);
      const index = t.objectStore(STORE_PHOTOS).index("by_album");
      return new Promise(function (resolve, reject) {
        const cursorReq = index.openCursor(IDBKeyRange.only(albumId));
        cursorReq.onsuccess = function () {
          const cursor = cursorReq.result;
          if (cursor) {
            cursor.delete();
            cursor.continue();
          } else {
            resolve();
          }
        };
        cursorReq.onerror = function () { reject(cursorReq.error); };
      }).then(function () { return txDone(t); });
    });
  }

  // ---- Photos ----

  function getPhotos(albumId) {
    return tx(STORE_PHOTOS, "readonly").then(function (t) {
      const index = t.objectStore(STORE_PHOTOS).index("by_album");
      return reqToPromise(index.getAll(IDBKeyRange.only(albumId)));
    }).then(function (photos) {
      return photos.sort(function (a, b) { return a.addedAt - b.addedAt; });
    });
  }

  function putPhoto(photo) {
    return tx(STORE_PHOTOS, "readwrite").then(function (t) {
      t.objectStore(STORE_PHOTOS).put(photo);
      return txDone(t).then(function () { return photo; });
    });
  }

  function deletePhoto(photoId) {
    return tx(STORE_PHOTOS, "readwrite").then(function (t) {
      t.objectStore(STORE_PHOTOS).delete(photoId);
      return txDone(t);
    });
  }

  function countPhotos(albumId) {
    return tx(STORE_PHOTOS, "readonly").then(function (t) {
      const index = t.objectStore(STORE_PHOTOS).index("by_album");
      return reqToPromise(index.count(IDBKeyRange.only(albumId)));
    });
  }

  window.AlbumDB = {
    getAlbums: getAlbums,
    putAlbum: putAlbum,
    deleteAlbum: deleteAlbum,
    getPhotos: getPhotos,
    putPhoto: putPhoto,
    deletePhoto: deletePhoto,
    countPhotos: countPhotos
  };
})();
