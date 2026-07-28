/*
 * rss-parser.js — parser RSS 2.0 / RSS 1.0 (RDF) / Atom sin dependencias.
 *
 * No es un parser XML completo: extrae los campos que un feed de noticias
 * bien formado siempre trae (title, link, description, fecha, imagen).
 * Cualquier item al que le falte título o link se descarta.
 */
"use strict";

const NAMED_ENTITIES = {
  amp: "&",
  lt: "<",
  gt: ">",
  quot: '"',
  apos: "'",
  nbsp: " ",
  ndash: "–",
  mdash: "—",
  hellip: "…",
  rsquo: "’",
  lsquo: "‘",
  rdquo: "”",
  ldquo: "“",
  laquo: "«",
  raquo: "»",
  aacute: "á",
  eacute: "é",
  iacute: "í",
  oacute: "ó",
  uacute: "ú",
  ntilde: "ñ",
  Aacute: "Á",
  Eacute: "É",
  Iacute: "Í",
  Oacute: "Ó",
  Uacute: "Ú",
  Ntilde: "Ñ",
  uuml: "ü",
  Uuml: "Ü",
  iquest: "¿",
  iexcl: "¡"
};

function decodeEntities(text) {
  if (!text) return "";
  return text
    .replace(/&#x([0-9a-fA-F]+);/g, (_, hex) => String.fromCodePoint(parseInt(hex, 16)))
    .replace(/&#(\d+);/g, (_, dec) => String.fromCodePoint(parseInt(dec, 10)))
    .replace(/&([a-zA-Z]+);/g, (m, name) =>
      Object.prototype.hasOwnProperty.call(NAMED_ENTITIES, name) ? NAMED_ENTITIES[name] : m
    );
}

function stripCdata(text) {
  if (!text) return "";
  return text.replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1");
}

function stripTags(text) {
  if (!text) return "";
  return text
    .replace(/<[^>]*>/g, " ")
    .replace(/\s+/g, " ")
    .replace(/\s+([.,;:!?»)\]])/g, "$1")
    .trim();
}

/* Devuelve el contenido de la primera aparición de cualquiera de los tags. */
function tagContent(xml, tagNames) {
  for (const tag of tagNames) {
    const re = new RegExp(`<${tag}(?:\\s[^>]*)?>([\\s\\S]*?)<\\/${tag}>`, "i");
    const m = xml.match(re);
    if (m && m[1] != null) {
      const value = stripCdata(m[1]).trim();
      if (value) return value;
    }
  }
  return "";
}

/* Devuelve el valor de un atributo del primer tag (auto-cerrado o no). */
function tagAttr(xml, tagNames, attr) {
  for (const tag of tagNames) {
    const re = new RegExp(`<${tag}\\s[^>]*?${attr}=["']([^"']+)["'][^>]*>`, "i");
    const m = xml.match(re);
    if (m && m[1]) return m[1].trim();
  }
  return "";
}

function extractLink(itemXml, isAtom) {
  if (isAtom) {
    // Atom: preferir <link rel="alternate" href=...>, luego cualquier <link href=...>
    const alt = itemXml.match(
      /<link\b[^>]*rel=["']alternate["'][^>]*href=["']([^"']+)["'][^>]*\/?>/i
    );
    if (alt && alt[1]) return alt[1].trim();
    const noRel = itemXml.match(/<link\b(?![^>]*\brel=)[^>]*href=["']([^"']+)["'][^>]*\/?>/i);
    if (noRel && noRel[1]) return noRel[1].trim();
    const any = itemXml.match(/<link\b[^>]*href=["']([^"']+)["'][^>]*\/?>/i);
    return any && any[1] ? any[1].trim() : "";
  }
  const content = tagContent(itemXml, ["link"]);
  if (content) return decodeEntities(content);
  // Algunos feeds RSS usan <link href=...> igualmente.
  return tagAttr(itemXml, ["link"], "href");
}

function extractImage(itemXml) {
  const url =
    tagAttr(itemXml, ["enclosure"], "url") ||
    tagAttr(itemXml, ["media:content", "media\\:content"], "url") ||
    tagAttr(itemXml, ["media:thumbnail", "media\\:thumbnail"], "url");
  if (url && /^https?:\/\//i.test(url)) return decodeEntities(url);
  // Última opción: primera <img> dentro de la descripción/contenido HTML.
  const img = itemXml.match(/<img\b[^>]*src=["']([^"']+)["']/i);
  if (img && /^https?:\/\//i.test(img[1])) return decodeEntities(img[1]);
  return "";
}

function extractDate(itemXml) {
  const raw = tagContent(itemXml, [
    "pubDate",
    "dc:date",
    "published",
    "updated",
    "lastBuildDate"
  ]);
  if (!raw) return null;
  const ts = Date.parse(decodeEntities(raw));
  return Number.isNaN(ts) ? null : new Date(ts).toISOString();
}

function parseItem(itemXml, isAtom) {
  const title = stripTags(decodeEntities(tagContent(itemXml, ["title"])));
  const link = extractLink(itemXml, isAtom);
  if (!title || !link || !/^https?:\/\//i.test(link)) return null;

  const rawDescription = tagContent(itemXml, [
    "description",
    "summary",
    "content:encoded",
    "content"
  ]);
  let description = stripTags(decodeEntities(rawDescription));
  if (description.length > 320) description = description.slice(0, 317).trimEnd() + "…";

  return {
    title,
    link,
    description,
    date: extractDate(itemXml),
    image: extractImage(itemXml)
  };
}

/*
 * parseFeed(xml) -> { title, items: [{title, link, description, date, image}] }
 * Lanza Error si el texto no parece un feed RSS/Atom.
 */
function parseFeed(xml) {
  if (typeof xml !== "string" || !xml.trim()) {
    throw new Error("Feed vacío");
  }

  const isAtom = /<feed[\s>]/i.test(xml) && !/<rss[\s>]/i.test(xml) && !/<rdf:RDF[\s>]/i.test(xml);
  const itemRe = isAtom
    ? /<entry(?:\s[^>]*)?>([\s\S]*?)<\/entry>/gi
    : /<item(?:\s[^>]*)?>([\s\S]*?)<\/item>/gi;

  const items = [];
  let m;
  while ((m = itemRe.exec(xml)) !== null) {
    const item = parseItem(m[1], isAtom);
    if (item) items.push(item);
  }

  if (items.length === 0 && !/<(rss|feed|rdf:RDF)[\s>]/i.test(xml)) {
    throw new Error("El contenido no parece un feed RSS/Atom");
  }

  // Título del canal: buscar el primer <title> antes del primer item/entry.
  const firstItemIdx = xml.search(isAtom ? /<entry[\s>]/i : /<item[\s>]/i);
  const headXml = firstItemIdx >= 0 ? xml.slice(0, firstItemIdx) : xml;
  const feedTitle = stripTags(decodeEntities(tagContent(headXml, ["title"])));

  return { title: feedTitle, items };
}

module.exports = { parseFeed, decodeEntities, stripTags };
