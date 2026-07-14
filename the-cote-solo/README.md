# The Cote Solo — terminal personal de arbitraje de relojes (v0)

> El arranque en chico de la visión The Cote: una herramienta **para beneficio propio** de compra/venta de relojes, bajo el mismo modelo de mercado financiero. No es el marketplace — es la Capa 1 (Terminal) + el motor de arbitraje del market-maker, operados por una sola persona con su propio capital.
>
> **Regla de oro:** mismo modelo de datos que el diseño grande (`the-cote/docs/03-arquitectura.md`), para que el día que quieras, esto *sea* la Capa 1 y no un prototipo desechable.

## Qué hace (y qué no)

**Hace:**
- Mantiene un universo curado de referencias líquidas (top marcas deportivas) como *tickers*.
- Estima **fair value** de cada pieza concreta, ajustado por **condición, caja y papeles**, con intervalo de confianza y tier de liquidez.
- Compara cada listing contra **dos referencias**: el fair value del secundario **y el precio retail (MSRP)**.
- Califica al **proveedor/procedencia** y **veta** compras de fuentes no confiables sin importar el spread.
- Calcula el **edge neto** restando costos reales de **internación y transporte a Panamá**, costo de capital y provisión de riesgo.
- Rankea oportunidades y mantiene un **libro personal** (P&L, días en inventario, precio objetivo de venta).

**No hace (fuera de alcance de v0):** marketplace, escrow, KYC, otros usuarios, móvil, vault, otras categorías. Todo eso es el diseño grande en `the-cote/`.

## Los cinco requisitos que definiste (y cómo se implementan)

| Requisito tuyo | Dónde vive | Cómo |
|---|---|---|
| Comprar bajo fair value **y** bajo retail | `pricing.py` | `fair_value` del secundario + `retail_usd` por referencia → señales `below_fair_value` y `below_retail` |
| Clasificación de calidad **altamente precisa** | `grading.py` | Taxonomía canónica de condición + normalizador de descripciones + multiplicadores. Punto de extensión para grading por visión (foto→grado) |
| Caja y papeles originales en el precio | `grading.py` | Ajustes explícitos: sin papeles y sin caja descuentan; *full set* es el baseline |
| Calificación de proveedores / procedencia segura | `provenance.py` | Score 0–100 por señales del vendedor + **veto duro** bajo umbral (`MIN_PROVENANCE`) |
| Costos de internación a Panamá | `costs.py` | Flete + seguro + arancel + ITBMS + broker + costo de capital, todo configurable |

## Metodología del fair value (condición-aware)

Cada referencia guarda un `base_fair_value_usd` que corresponde a una condición **canónica: EXCELLENT + full set (caja + papeles)**. El valor de una pieza concreta es:

```
fair_value_pieza = base_fair_value × mult_condición(grado) × ajuste(caja, papeles, pulido)
```

- `mult_condición`: NEW/UNWORN > MINT > EXCELLENT(1.0) > VERY_GOOD > GOOD > FAIR > POOR.
- Sin **papeles** descuenta más que sin **caja** (los papeles valen más en el mercado real).
- **Pulido** (polished) penaliza (afecta originalidad).

**Realizable ≠ fair value.** Tú no vendes al *mid*, vendes al *bid* y pagas por realizar. El motor usa `realizable = fair_value × (1 − haircut(tier))`, para que el edge sea honesto (misma filosofía de "edge neto" de `the-cote/docs/07-motor-financiero.md`). Todos los porcentajes son **calibrables** contra tus cierres reales — ese es el objetivo del libro personal.

## Factibilidad de venta y flujo de caja (`velocity.py`)

El spread absoluto no basta: un edge de 20% que tarda 180 días es peor para el flujo de caja que uno de 12% que rota en 30, porque el capital inmovilizado no se recicla. Por eso el motor decide por **retorno por unidad de tiempo**, no por spread absoluto:

- **Tiempo estimado de venta** (`expected_days_to_sell`): función de la liquidez del modelo (tier), la condición (full set/nuevo vende más rápido) y la demanda (premium sobre retail como proxy). Este mismo número alimenta el costo de capital, así todo es coherente.
- **Retorno anualizado** = `(1 + edge_neto)^(365/días) − 1`. La métrica de decisión real. Convierte "13% en 34 días" en ~272%/año.
- **Velocidad de capital** = `365/días` (vueltas/año): cuántas veces reciclas el mismo dinero. La traducción directa del flujo de caja.

**Gate nuevo — `SLOW_TURN`:** aunque el edge absoluto pase el piso, si el retorno **anualizado** cae bajo tu retorno requerido (`MIN_ANNUALIZED_EDGE`, default 30%/año) el motor lo marca como rotación lenta y no lo compra: te ahorra inmovilizar capital en un trade que se ve bueno en % pero es malo en flujo. El **ranking** es por retorno anualizado ponderado por confianza (de precio y de tiempo), riesgo de salida y procedencia.

## El cálculo de arbitraje (edge neto)

```
realizable   = bid(fair_value_pieza, tier)                       # lo que REALMENTE recuperas
landed_cost  = precio_compra
             + flete + seguro                                    # transporte a Panamá
             + arancel + ITBMS (sobre CIF)                       # internación
             + broker/handling
             + costo_capital (fair_value × días_hold/365 × tasa)
             + provisión_riesgo (f del score de procedencia)
net_edge     = (realizable − landed_cost) / landed_cost
```

**Gates (vetos) antes de recomendar comprar:**
1. `provenance_score < MIN_PROVENANCE` → **UNSAFE_SOURCE**, no comprar sin importar el edge.
2. Tier de liquidez C/D y edge no excepcional → **ILLIQUID**, difícil de salir.
3. `net_edge < MIN_NET_EDGE` → **PASS** (piso absoluto: no operar por márgenes triviales).
4. `annualized_edge < MIN_ANNUALIZED_EDGE` → **SLOW_TURN** (rota tan lento que mata el flujo de caja).
Si pasa los cuatro → **BUY**, con score = `retorno_anualizado × confianza × conf_tiempo × riesgo_salida × procedencia`.

## Estructura

```
the-cote-solo/
├── the_cote_solo/
│   ├── models.py       # dataclasses: Instrument, Listing, PricedPiece, Opportunity + enum Condition
│   ├── universe.py     # universo curado (seed) de refs con retail y base_fair_value
│   ├── grading.py      # taxonomía de condición + normalizador + ajustes caja/papeles/pulido
│   ├── provenance.py   # scoring de proveedor + veto
│   ├── costs.py        # modelo de costos de internación a Panamá (configurable)
│   ├── pricing.py      # fair value de la pieza + tier + CI + realizable + señales retail
│   ├── velocity.py     # tiempo estimado de venta + retorno anualizado + velocidad de capital
│   ├── arbitrage.py    # edge neto + retorno anualizado + gates + score + ranking
│   ├── comparables.py  # calibración del fair value con cierres reales (cierra el loop ingesta→pricing)
│   ├── portfolio.py    # libro personal: posiciones, P&L, señales de salida, calibración por venta
│   ├── server.py       # servidor local (stdlib): sirve el terminal + API del motor real
│   └── scan.py         # CLI: carga fixtures, evalúa, imprime reporte
├── fixtures/listings.json   # listings de ejemplo (buenos y malos) para demostrar los gates
├── tests/                   # tests con unittest (sin dependencias externas)
└── web/terminal.html        # mockup del terminal (UI): screener, analizador, libro — abre en el navegador
```

La UI vive en [`web/terminal.html`](web/terminal.html) — el terminal (acción-primero, banda de confianza, alertas, filas accionables) con la identidad **The Cote** (navy + crema, wordmark serif con el dispositivo `_`). Dos modos:
- **Estático:** ábrelo directo en el navegador → datos embebidos de demo.
- **Conectado al motor:** `python -m the_cote_solo.server` → abre `http://127.0.0.1:8000`; el screener, el analizador y el libro consumen el motor real (fair value calibrado con cierres).

## Cómo correrlo (sin instalar nada)

Python 3.10+ de la stdlib, cero dependencias externas para v0:

```bash
cd the-cote-solo
python -m the_cote_solo.scan             # scanner de arbitraje sobre los fixtures
python -m the_cote_solo.ingest.run       # ingesta + calibración del fair value con cierres reales
python -m the_cote_solo.portfolio        # libro personal: posiciones, P&L y señales de salida
python -m the_cote_solo.server           # terminal en http://127.0.0.1:8000, sobre el motor real
python -m unittest discover tests        # corre los 49 tests
```

## Calibración del fair value (`comparables.py`)

El fair value ya **no es semilla**: se calibra con cierres reales ingestados (subastas/eBay/ventas propias), siguiendo doc 07 — normaliza cada cierre a la condición baseline, pondera por recencia y calidad de fuente, y promedia. Si una referencia no tiene ≥2 cierres, cae al valor semilla. `python -m the_cote_solo.ingest.run` muestra el efecto (seed → calibrado, con Δ%). Cada **venta que registras en el libro** es un cierre propio de calidad máxima que recalibra el modelo: ese es el loop del moat.

## Libro personal (`portfolio.py`)

Registra compras/ventas (SQLite stdlib), calcula P&L no realizado contra el fair value actual, días en inventario y una **señal de salida** por velocidad: `SELL` (llegó al objetivo), `REVIEW` (rota más lento de lo esperado), `HOLD`. Las ventas cerradas alimentan la calibración (cierres propios) y la estimación de tiempo (días-a-venta realizados).

## Ingesta automatizada (`the_cote_solo/ingest/`)

Capa de entrada de datos con dos vías, ambas corren sin red ni API key:

**1. Automática y legal** — fuentes limpias vía adapter, corren en el scheduler:
- `AuctionResultsSource`: resultados públicos de subastas (precios de **cierre** → calibran fair value). Incremental por fecha, idempotente.
- `EbaySource`: **API oficial de eBay (Browse)** — listings activos comprables (record_type `offer`). Vía legal y estable (no scraping). Online con `EBAY_CLIENT_ID`/`EBAY_CLIENT_SECRET`; sin credenciales, corre en **modo offline** con `fixtures/ebay_sample.json` para probar el parseo sin red. Extrae la referencia del título con el parser de reglas.
- Scheduler con **circuit breaker** por fuente: si una empieza a fallar, se abre y deja de golpearla hasta el cooldown.
- Raw store inmutable (SQLite stdlib): guarda el crudo, deduplica por `(source, external_id)`, detecta cambios de precio (SCD), y lleva el cursor incremental de cada fuente.

**2. Semi-automática sin riesgo** — el extractor **pega-el-texto**:
- Tú traes el deal (Instagram, WhatsApp, dealer, donde sea), lo pegas, y `RuleBasedExtractor` saca ref, precio, caja/papeles, año y marca → lo pasa por el motor de arbitraje. Automatiza el *análisis*, no la obtención. Cero scraping.
- `ClaudeExtractor` usa la **Claude API real** (SDK oficial, import perezoso → el núcleo sigue sin dependencias) para texto ambiguo/informal, con salida estructurada por JSON schema. Actívalo con `THE_COTE_LLM_EXTRACTOR=1` + `ANTHROPIC_API_KEY` (modelo por defecto `claude-opus-4-8`; `claude-haiku-4-5` es la opción de menor costo). `FallbackExtractor` cae al parser de reglas ante cualquier error, así que nunca se rompe.

**Sitios protegidos = gate legal.** `Chrono24Source` y `WatchChartsSource` existen como adapters **deshabilitados**: la arquitectura está lista, pero no corren hasta que haya una vía legítima (API/partner o feed licenciado). Ver §"Riesgos legales" abajo.

```bash
python -m the_cote_solo.ingest.run                          # tick del scheduler (subastas)
python -m the_cote_solo.ingest.run --paste "GMT 126710BLRO USD 16800 full set 2022"   # pega-el-texto
```

Distinción de diseño: `record_type='sale'` (cierres, calibran fair value) vs `record_type='offer'` (anuncios comprables, se escanean como arbitraje).

## Riesgos legales del scraping de sitios protegidos

Por qué Chrono24/WatchCharts van detrás de un gate y no como scraper (no es asesoría legal; validar con abogado en PA/UE/EE.UU.):
1. **Incumplimiento de contrato (ToS):** prohíben el acceso automatizado.
2. **Acceso no autorizado (CFAA/equivalentes):** raspar datos públicos suele ser tolerable, pero romper login o anti-bot cruza la línea.
3. **Derecho *sui generis* de bases de datos (UE) y copyright de fotos.**
4. **Competencia desleal / free-riding** (fuerte en Alemania — sede de Chrono24).
5. **Circunvención de CAPTCHA/anti-bot** (DMCA §1201 y equivalentes) — el filo más peligroso.
6. **GDPR:** los anuncios traen datos personales de residentes UE.

La vía defendible: APIs oficiales + subastas públicas + feeds licenciados + el dato propio (tus cierres) y give-to-get con dealers. Ese es el moat que nadie te demanda.

## Datos: de dónde vienen (y el paso siguiente)

- **Fuentes elegidas para v0:** Chrono24 + resultados de subastas + WatchCharts (benchmark). Las más limpias legal y estadísticamente.
- **Estado actual:** el núcleo corre con `fixtures/listings.json` (datos de ejemplo) y un universo *seed* con valores **ilustrativos** — el valor de v0 es el **método**, no los números semilla.
- **Ya construido:** la capa de ingesta (`the_cote_solo/ingest/`) con la vía híbrida (subastas + pega-el-texto) y los sitios protegidos tras el gate legal.
- **Paso siguiente:** (a) cablear los cierres ingestados al motor de pricing (que hoy usa `base_fair_value` estático del universo) para que el fair value se calibre con datos reales; (b) conectar la Claude API real en `ClaudeExtractor`; (c) sumar un adapter de API oficial (eBay Browse) para listings activos.

## Advertencia honesta

Esto es hoy un **negocio de trading**, no una empresa de tecnología: depende de ti en el loop y no escala solo. Es la **cuña**, no el destino. Y opera con tu propio dinero: el sistema **mide** —no elimina— el riesgo de capital inmovilizado, de comprar una falsificación, de no poder vender cuando quieras y de que el mercado baje. Cada compra/venta que registres calibra el modelo; ahí empieza a acumularse el dato propio que es el moat.
