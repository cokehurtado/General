# 📰 Mi Portal de Noticias

Portal de noticias **personal** para informarte a diario de lo más importante
de **Chile** y el **mundo**, en un solo lugar. Sin dependencias, sin build, sin
cuentas: un servidor Node que agrega feeds RSS/Atom y un front end limpio en
español.

## Características

- **Agregador RSS/Atom propio** — el servidor consulta todas las fuentes en
  paralelo, las parsea (sin dependencias) y entrega un solo JSON unificado,
  ordenado de lo más reciente a lo más antiguo y sin duplicados.
- **Fuentes chilenas y mundiales preconfiguradas** — Cooperativa, Emol,
  El Mostrador, CIPER, The Clinic, BBC Mundo, DW, France 24, CNN en Español,
  Noticias ONU, y más. Todas editables en `feeds.json`.
- **Categorías** — pestañas automáticas según las categorías de tus fuentes
  (Chile, Mundo, Economía, Tecnología…), con contador de noticias.
- **Filtros útiles** — búsqueda por texto, filtro "Solo hoy", y chips para
  activar/desactivar fuentes individuales (se recuerda tu selección).
- **Guardadas** ⭐ — marca noticias para leer después; quedan en `localStorage`.
- **Agrupación por día** — separadores "Hoy", "Ayer" y fechas, con horas
  relativas ("hace 20 min").
- **Actualización automática** cada 10 minutos + botón "Actualizar" que fuerza
  una nueva consulta a las fuentes.
- **Tolerante a fallos** — si una fuente está caída, se muestra tachada con el
  motivo y el resto del portal sigue funcionando.
- **Codificación correcta** — decodifica feeds en UTF-8 e ISO-8859-1 (varios
  medios chilenos aún usan Latin-1), así los acentos y la ñ salen bien.
- **Tema claro y oscuro**, diseño responsivo y accesible.

## Cómo usarlo

```bash
node news-portal/server.js        # → http://localhost:8090
# o desde la raíz del repo:
npm run news
```

Abre <http://localhost:8090> y listo. Puerto alternativo:
`node news-portal/server.js 3000`.

## Personalizar las fuentes

Edita `news-portal/feeds.json`. Cada fuente tiene esta forma:

```json
{
  "id": "mi-fuente",
  "name": "Mi Fuente",
  "category": "Chile",
  "url": "https://ejemplo.cl/feed/",
  "homepage": "https://ejemplo.cl/"
}
```

- `category` es libre: las pestañas del portal se generan solas a partir de
  las categorías que uses (por ejemplo "Deportes" o "Ciencia").
- Casi cualquier sitio WordPress tiene feed en `/feed/`; muchos medios
  publican los suyos en `/rss`.
- Si una fuente aparece tachada en el portal, su feed cambió de URL o está
  caído: pasa el cursor sobre el chip para ver el error exacto.

Reinicia el servidor (o espera el próximo refresco con el botón
"Actualizar") para que tome los cambios.

## Configuración opcional

| Variable | Por defecto | Descripción |
|---|---|---|
| `PORT` (o 1er argumento) | `8090` | Puerto del servidor |
| `FEEDS_FILE` | `feeds.json` | Ruta a otra lista de fuentes |
| `CACHE_TTL_MIN` | `10` | Minutos de caché del agregado |

## Estructura

```
news-portal/
  server.js           # servidor estático + API /api/news (agregador con caché)
  feeds.json          # tus fuentes (edítalo a gusto)
  lib/rss-parser.js   # parser RSS 2.0 / RSS 1.0 / Atom sin dependencias
  public/
    index.html        # interfaz
    assets/styles.css # tema claro/oscuro, layout, tarjetas
    assets/app.js     # filtros, búsqueda, guardados, auto-refresco
```

## API

- `GET /api/news` — agregado de todas las fuentes (caché de 10 min).
- `GET /api/news?refresh=1` — fuerza una nueva consulta a las fuentes.
- `GET /api/health` — estado del servidor y hora del último caché.

## Licencia

MIT
