# 11 · Backlog ejecutable para Claude Code

> Cómo leer esto: cada **Epic** es una unidad de trabajo autocontenida y del tamaño de una sesión de Claude Code. Formato: objetivo, módulo del monorepo donde vive (ver doc 03), dependencias (qué epics deben existir antes), user stories con criterios de aceptación, y estimación de esfuerzo en **T-shirt size** (S ≈ 1-2 días, M ≈ 3-5 días, L ≈ 1-2 semanas, XL ≈ >2 semanas / dividir).
>
> Prioridad: **P0** (bloqueante del MVP), **P1** (MVP), **P2** (Fase 2), **P3** (Fase 3+).
> Regla de ejecución: nunca tomar un epic cuyas dependencias no estén cerradas. El orden sugerido está al final.

---

## Epic 0 · Fundaciones del monorepo `[P0] [S/M] · infra + packages`
**Objetivo:** esqueleto del monorepo listo para que todo lo demás se construya encima.
**Depende de:** nada.
**Módulo:** raíz, `packages/`, `infra/docker`, `infra/github`.

- **US-0.1** — Como dev, quiero un monorepo Turborepo+pnpm con `apps/`, `services/`, `packages/`, `data/`, `infra/`.
  *AC:* `pnpm install` y `turbo build` corren en verde; workspaces resueltos.
- **US-0.2** — Config compartida (`packages/config`): eslint, prettier, tsconfig base, ruff/black para Python.
  *AC:* lint pasa en un paquete de ejemplo TS y uno Py.
- **US-0.3** — `docker-compose` local: Postgres+TimescaleDB, Redis, Meilisearch, Temporal dev, mailhog. `make up` levanta todo.
  *AC:* healthchecks verdes; un script de smoke test conecta a cada servicio.
- **US-0.4** — CI base en GitHub Actions: lint + typecheck + test con path filters por paquete y Turbo remote cache.
  *AC:* PR de ejemplo dispara solo los jobs afectados.
- **US-0.5** — `packages/contracts`: setup de zod + generación de tipos; convención de esquemas de eventos.
  *AC:* un esquema de evento de ejemplo valida y exporta tipo.

---

## Epic 1 · Esquema de datos y catálogo canónico `[P0] [M] · packages/db + data/catalog`
**Objetivo:** el grafo de instrumentos — el corazón (doc 03).
**Depende de:** Epic 0.
**Módulo:** `packages/db` (Drizzle + migraciones), `data/catalog`.

- **US-1.1** — Esquema: `brands`, `families`, `instruments` (ticker canónico), atributos por categoría, imágenes de referencia.
  *AC:* migraciones aplican; seed de marcas de relojes prioritarias (Rolex, Patek, AP, Omega, Cartier, …) con familias y refs de ejemplo.
- **US-1.2** — Esquema: `listings`, `listing_versions` (SCD-2), `sales` (con fuente y calidad de dato), `market_snapshots` (Timescale, hypertable).
  *AC:* insertar un cambio de precio genera una nueva `listing_version` con `valid_from/valid_to`.
- **US-1.3** — Esquema: `bids`, `orders`, `escrow_accounts`, `ledger_entries` (doble entrada), `items`, `passports`.
  *AC:* un asiento de doble entrada balancea (suma cero) por constraint/test.
- **US-1.4** — Servicio de catálogo (`data/catalog`): CRUD de instrumentos + búsqueda por referencia, expuesto como lectura interna.
  *AC:* dado "126710BLRO" retorna el instrumento canónico; cobertura de tests.

---

## Epic 2 · Motor de ingesta y scraping `[P0] [L] · data/scraper-fleet + data/ingestion`
**Objetivo:** llenar el grafo con datos del mercado (doc 05).
**Depende de:** Epic 1.
**Módulo:** `data/scraper-fleet`, `data/ingestion`.

- **US-2.1** — Framework de scraping (Crawlee/Playwright): abstracción `Source` con scheduler adaptativo, dos pools (HTTP/browser), raw store inmutable.
  *AC:* un `Source` de ejemplo (fixture local o fuente de subasta pública) ingesta a raw store con snapshot.
- **US-2.2** — Rotación de proxies + fingerprinting + throttling con jitter + circuit breaker por fuente.
  *AC:* config de proxies; el circuit breaker pausa una fuente al superar umbral de bloqueos (test con mock).
- **US-2.3** — Pipeline de normalización: moneda→USD, condición canónica, box&papers, extracción de referencia; funciones puras con fixtures.
  *AC:* set de fixtures de listings crudos → salida normalizada esperada; ≥90% de cobertura en el módulo.
- **US-2.4** — Deduplicación de listings (pHash de imágenes + serial + similitud de texto).
  *AC:* dos anuncios idénticos → un listing; dos venues distintos del mismo item → dos cotizaciones.
- **US-2.5** — Detección de cambios → emisión de eventos `listing.observed/price_changed/delisted` al bus.
  *AC:* cambio de precio emite evento con payload versionado.
- **US-2.6** — Conectores iniciales: resultados de subastas (tier A) + 1 marketplace (tier B) + formato de feed de dealer (CSV/API).
  *AC:* cada conector ingesta datos reales/sandbox a `listings`.

---

## Epic 3 · Agente de matching `[P0] [M] · data/matcher`
**Objetivo:** listing → instrumento canónico (doc 06 #1).
**Depende de:** Epics 1, 2.
**Módulo:** `data/matcher`.

- **US-3.1** — Cascada nivel 1-2: extracción de referencia + reglas estructuradas (marca/familia/atributos).
  *AC:* golden set de listings etiquetados; precisión medida y reportada.
- **US-3.2** — Nivel 3: embeddings multimodales (texto+imagen) en `pgvector`, vecino más cercano contra catálogo.
  *AC:* recall mejora sobre solo-reglas en el golden set.
- **US-3.3** — Nivel 4: fallback a LLM (Claude) para cola ambigua con top-K candidatos + justificación; salida con `confidence` y `method`.
  *AC:* casos ambiguos del golden set resueltos o enviados a cola bajo umbral.
- **US-3.4** — Cola de revisión en admin + feedback loop (correcciones → dataset de entrenamiento).
  *AC:* corregir un match en admin actualiza el instrumento y registra el ejemplo.

---

## Epic 4 · Motor de pricing y métricas de mercado `[P0] [L] · data/pricing`
**Objetivo:** fair value con incertidumbre + métricas Bloomberg (doc 07).
**Depende de:** Epics 1, 2, 3.
**Módulo:** `data/pricing`.

- **US-4.1** — Selección de comparables ponderados (similitud×recencia×calidad×condición) + tier de liquidez A/B/C/D.
  *AC:* dado un instrumento, retorna comparables con pesos y tier calculado.
- **US-4.2** — Estimador de fair value: media ponderada (tier C/D, bootstrap CI) + GBM (tier A/B, CI por cuantiles). Salida estándar (JSON del doc 07).
  *AC:* salida incluye `fair_value`, `confidence_interval`, `liquidity_tier`, `n_comparables`, `confidence_index`, `methodology_version`.
- **US-4.3** — Métricas de mercado: último precio, promedio, volumen, spread, spread regional, volatilidad (solo A/B), tiempo a venta, variaciones D/S/M.
  *AC:* snapshot diario por instrumento activo persistido en Timescale.
- **US-4.4** — Backtesting harness: MAPE por tier + cobertura de intervalos (calibración). Reporte reproducible.
  *AC:* corre sobre histórico y emite reporte; gate documentado (tier A MAPE < 10%).
- **US-4.5** — Recalcular on-event (instrumento afectado por nuevo dato) + batch nocturno.
  *AC:* evento `listing.price_changed` dispara recálculo del instrumento < 15 min.

---

## Epic 5 · Terminal web (Capa 1) `[P0] [L] · apps/web + services/gateway`
**Objetivo:** el Bloomberg del lujo, single-player, útil sin marketplace.
**Depende de:** Epics 1, 4.
**Módulo:** `apps/web`, `services/gateway`, `packages/ui`.

- **US-5.1** — Gateway/BFF con API tipada (lectura de instrumentos, series, comparables) + API pública de datos (base).
  *AC:* endpoints documentados (OpenAPI) y tipados consumidos por el front.
- **US-5.2** — Ficha de instrumento: fair value con banda, gráfico histórico (TradingView Lightweight Charts), comparables, métricas, tier de liquidez visible.
  *AC:* renderiza un instrumento tier A y uno tier C mostrando la incertidumbre correctamente (banda ancha en C).
- **US-5.3** — Screener/búsqueda (Meilisearch): filtros por marca/familia/precio/tier; typo-tolerance.
  *AC:* "submarnier" encuentra Submariner; facetas funcionan.
- **US-5.4** — Watchlists + alertas de precio (suscripción a instrumento, umbrales).
  *AC:* crear alerta → cambio de fair value dispara notificación (Epic 12).
- **US-5.5** — SEO: cada instrumento es una página SSR indexable (el growth loop de Zillow).
  *AC:* páginas con metadata, sitemap, render server-side.

---

## Epic 6 · Índice ONZA `[P1] [M] · data/index`
**Objetivo:** el índice del lujo (doc 07).
**Depende de:** Epics 4.
**Módulo:** `data/index`.

- **US-6.1** — Metodología repeat-sales/hedónica, universo tier A/B ponderado, reglas de rebalanceo público.
  *AC:* índice reconstruible sobre histórico; documento de metodología versionado.
- **US-6.2** — Sub-índices por categoría y marca; serie histórica persistida.
  *AC:* ONZA Watches + al menos un sub-índice de marca calculados.
- **US-6.3** — Widget de índice en el terminal + endpoint público.
  *AC:* gráfico del índice renderiza; endpoint retorna serie.

---

## Epic 7 · Identidad, KYC y antifraude v1 `[P0] [M] · services/core/identity + trust`
**Objetivo:** base de confianza y compliance (docs 02, 03, 06 #5).
**Depende de:** Epics 0, 1.
**Módulo:** `services/core` módulos `identity`, `trust`.

- **US-7.1** — Cuentas, roles (comprador/vendedor/dealer/perito/admin), sesiones (Clerk), estados KYC.
  *AC:* signup/login; rol y estado KYC en el token/sesión.
- **US-7.2** — Integración KYC (Sumsub): flujo de verificación, webhooks, almacenamiento seguro y aislado de documentos.
  *AC:* usuario completa KYC sandbox → estado `verified`; documentos en bucket auditado.
- **US-7.3** — Antifraude v1: reglas duras (AML: estructuración, origen de fondos en ticket alto) + scoring básico + colas de revisión.
  *AC:* transacción sobre umbral dispara step-up/escalación; audit log inmutable de decisiones.
- **US-7.4** — Compliance/AML: workflow de reporte (UAF), umbrales configurables.
  *AC:* caso simulado sobre umbral genera un caso de reporte trazable.

---

## Epic 8 · Marketplace curado + ofertas `[P1] [L] · services/core/marketplace`
**Objetivo:** semilla de Capa 2 con oferta cautiva (doc 10, Fase 1).
**Depende de:** Epics 1, 5, 7.
**Módulo:** `services/core` módulo `marketplace`.

- **US-8.1** — Listings propios (de dealers cautivos) ligados a instrumento canónico; back-office de carga en admin.
  *AC:* dealer/admin publica un listing → aparece en terminal ligado al instrumento con su fair value.
- **US-8.2** — Ofertas/contraofertas (bids) on-platform con estados; chat transaccional.
  *AC:* comprador oferta → vendedor acepta/contraoferta; estados persistidos.
- **US-8.3** — Órdenes: creación al aceptar oferta, ligada a escrow (Epic 9).
  *AC:* aceptar oferta crea orden en estado `awaiting_payment`.

---

## Epic 9 · Escrow, pagos y ledger `[P0] [L] · services/core/escrow + billing`
**Objetivo:** el rail de confianza — dinero con ledger propio (docs 03, 04).
**Depende de:** Epics 1, 7, 8.
**Módulo:** `services/core` módulos `escrow`, `billing`.

- **US-9.1** — Ledger de doble entrada como fuente de verdad; adaptadores de pago (transferencia a cuenta fiduciaria, Yappy, dLocal/tarjeta, Stripe para SaaS).
  *AC:* fondear una orden crea asientos balanceados; conciliación contra el proveedor.
- **US-9.2** — Máquina de estados de escrow (Temporal): `funded → in_transit → authenticating → delivered → released` con timeouts y compensaciones (refund si falla peritaje).
  *AC:* workflow durable sobrevive reinicio; ruta de fallo devuelve fondos.
- **US-9.3** — Payouts al vendedor (transferencia/Wise) netos de fee; recibos.
  *AC:* release genera payout y registra fee como revenue en el ledger.
- **US-9.4** — Suscripciones (Stripe): Dealer SaaS + Terminal Pro (billing base).
  *AC:* alta/baja de suscripción; estado refleja acceso.

---

## Epic 10 · Operaciones de autenticación y logística `[P1] [L] · services/core/authentication-ops + logistics`
**Objetivo:** la operación física en Panamá (docs 02, 03).
**Depende de:** Epics 8, 9.
**Módulo:** `services/core` módulos `authentication-ops`, `logistics`.

- **US-10.1** — Workflow de peritaje (Temporal): recepción en PTY → checklist pericial → certificado → pasaporte digital del `item`.
  *AC:* pieza recorre el flujo; certificado firmado + pasaporte creado; item ligado a la orden.
- **US-10.2** — Back-office de peritaje en admin: colas, checklist por categoría, adjuntar evidencia, decisión perito.
  *AC:* perito procesa una pieza end-to-end desde el admin.
- **US-10.3** — Logística: generación de etiquetas, tracking, seguro de envío, estados hacia el escrow.
  *AC:* etiqueta creada, tracking actualiza estado de la orden, seguro registrado.

---

## Epic 11 · Agentes de autenticación IA y arbitraje `[P1] [M] · data/arbitrage + servicio de visión`
**Objetivo:** triage de autenticidad + oportunidades (doc 06 #3, #4).
**Depende de:** Epics 4, 8.
**Módulo:** `data/arbitrage`, servicio de visión en `data/`.

- **US-11.1** — Agente de autenticación (triage): visión (Claude) + señales de metadatos → `risk_score` + `flags`. Prefiltra, no certifica.
  *AC:* golden set de piezas conocidas (auténticas/sospechosas); prioriza correctamente el peritaje; nunca autoaprueba.
- **US-11.2** — Motor de arbitraje: spread neto (fee+logística+aduana+capital+riesgo), filtro por liquidez de salida, scoring; evento `arbitrage.opportunity_found`.
  *AC:* backtest del arbitraje contra cierres posteriores (doc 07); umbral neto configurable; oportunidades solo internas/dealer, no retail abierto.

---

## Epic 12 · Notificaciones y alertas `[P1] [S/M] · services/core/notifications`
**Objetivo:** el sistema nervioso de alertas (docs 05, 06).
**Depende de:** Epics 5, 7.
**Módulo:** `services/core` módulo `notifications`.

- **US-12.1** — Fan-out de alertas por evento (precio, arbitraje, bids) a canales: push, email, WhatsApp Business API.
  *AC:* evento suscrito entrega por el canal preferido; preferencias por usuario.
- **US-12.2** — Alertas tipo broker: "tu reloj subió X% este trimestre; hay N bids activos".
  *AC:* generadas desde el estado del portafolio/watchlist del usuario.

---

## Epic 13 · Agentes de negociación e inversión `[P2] [M] · data/ + apps/web`
**Objetivo:** roboadvisor y negociación (doc 06 #6, #7).
**Depende de:** Epics 4, 8, 12.
**Módulo:** `data/`, `apps/web`.

- **US-13.1** — Agente de negociación: oferta sugerida + `p(accept)` + justificación; solo on-platform.
  *AC:* dada una situación de listing/oferta, sugiere rango con probabilidad estimada.
- **US-13.2** — Agente de inversión: retorno/riesgo/concentración/liquidez del portafolio + recomendaciones rankeadas con disclaimers.
  *AC:* sobre una colección de prueba, produce recomendaciones con razón; disclaimers legales presentes.

---

## Epic 14 · App móvil `[P2] [L] · apps/mobile`
**Objetivo:** alertas + portafolio + compra en el bolsillo.
**Depende de:** Epics 5, 8, 12.
**Módulo:** `apps/mobile` (Expo).

- **US-14.1** — Auth, watchlists, alertas push, ficha de instrumento y portafolio.
  *AC:* paridad de lectura con el terminal; push funciona.
- **US-14.2** — Flujo de compra/oferta con escrow desde móvil.
  *AC:* comprar/ofertar end-to-end desde la app.

---

## Epic 15 · Vault, financiamiento y datos como producto `[P3] [XL] · services/core/vault + billing + gateway`
**Objetivo:** la Capa 3 — custodia, colateral, monetización de datos (docs 07, 08, 10 Fase 3). **Dividir en sub-epics al llegar la fase.**
**Depende de:** Epics 9, 10, 6.
**Módulo:** `services/core` módulo `vault`, `billing`, `services/gateway`.

- **US-15.1** — Vault: posiciones, transferencia de propiedad in-vault (settlement sin mover el activo), statements de portafolio.
  *AC:* una pieza en vault cambia de dueño sin evento logístico; statement refleja la transferencia.
- **US-15.2** — Bids pre-autorizados → book real en instrumentos tier A.
  *AC:* bid con pago pre-autorizado aparece en el book; matching con ask ejecuta orden.
- **US-15.3** — Financiamiento colateralizado (piloto): originación de préstamo con pieza en vault como garantía; integración con partner.
  *AC:* flujo de solicitud→aprobación→desembolso→garantía registrada en el ledger.
- **US-15.4** — Data como producto: API monetizada (metered en `billing`) + reportes/índice para instituciones.
  *AC:* cliente API con cuota y facturación; reporte trimestral generado.

---

## Epic 16 · Observabilidad, seguridad y hardening `[P1 continuo] [M] · infra + transversal`
**Objetivo:** que nada de lo anterior falle en silencio con dinero de clientes.
**Depende de:** transversal (empezar con Epic 0, madurar continuo).
**Módulo:** `infra/`, transversal.

- **US-16.1** — OpenTelemetry (traces/logs/metrics) → Grafana Cloud; Sentry en front/back; dashboards de KPIs (docs 05, 08).
  *AC:* una transacción de escrow es trazable end-to-end; dashboard de liquidez y costos vivo.
- **US-16.2** — Seguridad: cifrado de PII a nivel columna, buckets KYC aislados, audit log inmutable de acciones sobre dinero/identidad, rate limiting + anti-scraping hacia nosotros.
  *AC:* pentest checklist básico; acciones sensibles auditadas.
- **US-16.3** — DR: PITR de Postgres (RPO 15 min), runbook de RTO 4h, backups probados.
  *AC:* restore de prueba documentado.

---

## Orden de ejecución sugerido (respetando dependencias)

```
Fase 1 (MVP):
  0 → 1 → 2 → 3 → 4 → 5        (camino crítico de la Capa 1: terminal funcionando)
  7 (identidad/KYC, en paralelo desde después de 1)
  8 → 9 → 10                    (semilla de Capa 2: transacción con escrow)
  6, 11, 12                     (índice, agentes IA, alertas — enriquecen el MVP)
  16                            (continuo desde el día 1)

Fase 2:
  13, 14  + endurecer 8/9/10 a self-serve + expansión (playbook doc 09)

Fase 3:
  15 (dividido) + market-maker + datos como producto
```

**Dependencias críticas a vigilar:**
- Nada de pricing (4) sin matching (3) sin datos (2) sin esquema (1). Es una cadena; no paralelizar en falso.
- Nada de marketplace real (8) sin identidad/KYC (7) — la confianza es prerrequisito, no feature tardío.
- Nada de escrow en producción (9) sin el ledger de doble entrada y sus tests (1.3) verdes.
- Cada agente IA entra a producción **con su harness de evaluación** (golden sets), nunca sin él.
