# 10 · Roadmap a 3 años

> Regla que gobierna todo el roadmap: **no se construye la siguiente capa hasta que la actual pega su KPI.** La secuencia datos → confianza → liquidez es un candado, no una sugerencia. Cada fase tiene un "gate" cuantitativo para pasar a la siguiente.

## Vista general

| Fase | Meses | Objetivo | Capa dominante | Gate para avanzar |
|---|---|---|---|---|
| **1 — MVP** | 0–6 | El Terminal + marketplace curado en Panamá (relojes) | Capa 1 + semilla de Capa 2 | KPIs de datos + primeras transacciones con escrow |
| **2 — Product-Market Fit** | 6–18 | Marketplace self-serve, dealers, expansión a 1er anillo | Capa 2 madura | Liquidez sana + contribución positiva + retención |
| **3 — Escalamiento** | 18–30 | Vault, financiamiento, datos como producto, +categorías | Capa 3 | Rotación de vault + revenue diversificado |
| **4 — Internacionalización** | 30–36+ | México/Colombia, índice como estándar | Todas | Operación regional replicable |

## Fase 1 — MVP (meses 0–6)

**Objetivo:** ser útil para una sola persona (terminal single-player) y cerrar las primeras transacciones seguras, todo en relojes, todo con Panamá como base.

Entregables:
- Catálogo canónico de relojes (marcas prioritarias) + motor de matching v1.
- Motor de ingesta: subastas + 2-3 fuentes B + feeds de dealers cautivos.
- Motor de pricing v1 con intervalos de confianza y tiers de liquidez.
- Terminal web: ficha de instrumento (fair value, histórico, comparables), screener básico, watchlists + alertas.
- Marketplace **curado** (no self-serve): listings de 20-30 dealers, ofertas on-platform.
- Escrow v1 (transferencia a cuenta fiduciaria + ledger de doble entrada) + workflow de autenticación física (Temporal) + KYC (Sumsub).
- Antifraude v1 (reglas + scoring básico), compliance/AML operativo.
- Índice ONZA Watches v1 (aunque sea con datos limitados y etiquetado como beta).

**KPIs / Gate:**
- Cobertura: ≥60% del catálogo prioritario con ≥3 comparables; matching ≥95% precision.
- Fair value backtest tier A MAPE < 10%.
- ≥30 transacciones cerradas con escrow, 0 incidentes de fraude/autenticación materiales.
- Cohorte inicial de MAU del terminal con retención semana-4 medible.

## Fase 2 — Product-Market Fit (meses 6–18)

**Objetivo:** que el marketplace se sostenga solo (self-serve), que los dealers paguen, y probar el playbook de expansión en el primer anillo.

Entregables:
- Marketplace **self-serve** con onboarding de vendedor, listings propios, negociación asistida (agente #6).
- **Dealer SaaS** (líneas 6 de revenue): terminal + inventario + demanda + arbitraje premium.
- **Terminal Pro** (freemium) para consumidor.
- Carteras y joyería añadidas (playbook probado en relojes → nuevas categorías).
- App móvil (alertas + portfolio + compra).
- Seguros y logística como líneas propias.
- Expansión Ola 1 (Costa Rica, Rep. Dominicana) vía hub-and-spoke.
- Agentes de inversión (#7) y autenticación IA (#4) en producción con sus harness de evaluación.
- Data/price intelligence v1 (reportes, API beta).

**KPIs / Gate:**
- Tiempo mediano a venta bajando trimestre a trimestre (liquidez).
- Contribución por transacción positiva y estable.
- % de GMV recurrente vía dealers ≥ umbral (predecibilidad).
- Retención de dealers y de Terminal Pro sanas; CAC payback de dealers < 6 meses.
- GMV creciendo con al menos un segundo país aportando material.

## Fase 3 — Escalamiento (meses 18–30)

**Objetivo:** activar la Capa 3 (custodia) y las líneas de mayor margen; diversificar revenue más allá del take rate.

Entregables:
- **ONZA Vault:** custodia física en Panamá, pasaporte digital por pieza, transferencia de propiedad in-vault (settlement rápido), statements de portafolio.
- **Financiamiento colateralizado** (línea 10): préstamos sobre colección en vault. Piloto con partner financiero.
- **Market-maker interno** (agente #8) con capital acotado para profundizar liquidez y realizar arbitraje propio.
- **Data como producto** maduro: índice ONZA citado en prensa, API monetizada, feeds para aseguradoras/bancos/casas de empeño.
- Bids reales pre-autorizados → primer "book" genuino en instrumentos tier A.
- Ola 2 de expansión (Triángulo Norte).

**KPIs / Gate:**
- Piezas en vault y **rotación** (ventas por pieza) creciendo → validación del multiplicador de márgenes.
- Revenue diversificado: take rate < X% del total (el resto: SaaS + datos + financiamiento).
- Índice ONZA con citas externas (señal de moat de estándar).

## Fase 4 — Internacionalización (meses 30–36+)

**Objetivo:** llevar el playbook probado a los grandes mercados y consolidar el estándar de datos.

Entregables:
- Entrada a **México y Colombia** con operación local (segundo hub logístico probable en México).
- Índice ONZA como referencia regional del mercado del lujo.
- Expansión de categorías oportunista (arte, autos, coleccionables) donde el modelo de datos aplique.
- Infraestructura B2B / white-label para boutiques y relojerías.

**KPIs:**
- Operación regional replicable (un país nuevo se abre con costo marginal decreciente).
- Métricas de escala que soporten la ronda de crecimiento (Serie B/C).

## Hitos de financiamiento (referencial)

| Momento | Ronda | Para qué |
|---|---|---|
| Pre-Fase 1 | Pre-seed / Seed | Construir Capa 1 + semilla de Capa 2, equipo fundador, compliance base |
| Gate Fase 1→2 | Seed / Serie A | Self-serve, dealers, primera expansión, categorías nuevas |
| Gate Fase 2→3 | Serie A / B | Vault, financiamiento, capital de market-making/inventario, datos |
| Gate Fase 3→4 | Serie B/C | México/Colombia, escala regional |

El capital de inventario (market-making) y el de financiamiento colateralizado idealmente se fondean con **debt/vehículos separados**, no con equity de venture — un quant no diluye para comprar inventario rotable.
