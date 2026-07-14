# 07 · Motor financiero (el "Bloomberg del lujo")

> Rol: el quant. Aquí es donde la mayoría de los "Bloomberg de X" fracasan — reportan números con falsa precisión sobre datos ilíquidos y pierden credibilidad ante el usuario sofisticado, que es justamente el que paga. La disciplina aquí no es opcional.

## Filosofía: honestidad estadística como marca

- **Todo número tiene barra de error.** Nunca un punto sin intervalo.
- **Todo instrumento tiene tier de liquidez** que gobierna qué métricas se muestran.
- **Precio de cierre > precio de lista.** El precio de lista es una *oferta*, no un *hecho*. Se ponderan distinto.
- **Metodología pública.** Como Case-Shiller y el Zestimate: publicar cómo se calcula construye confianza y es defensa reputacional.

## Tiers de liquidez

| Tier | Definición (aprox.) | Qué se muestra |
|---|---|---|
| **A — Líquido** | ≥ ~20 transacciones/comparables por trimestre (Submariner, Daytona, Nautilus) | Fair value con banda estrecha, índice, volatilidad, tendencias, spread, "book" |
| **B — Semi-líquido** | 5–20 / trimestre | Fair value con banda media, tendencias con cautela, sin indicadores técnicos finos |
| **C — Ilíquido** | 1–5 / trimestre | Solo rango amplio + "datos escasos"; comparables mostrados individualmente |
| **D — Único/raro** | <1 / trimestre (piezas de subasta) | Sin fair value automático; solo histórico de comparables y "consultar experto" |

El tier se recalcula continuamente y **degrada la confianza automáticamente**: nunca se muestra una banda estrecha sobre un tier C.

## Fair value: metodología

Estimador jerárquico con incertidumbre explícita.

**1. Selección de comparables (ponderados):**
```
peso(comp) = w_similitud × w_recencia × w_calidad_dato × w_condición
```
- `w_similitud`: misma ref (1.0) → misma familia (0.5) → misma marca+categoría (0.2).
- `w_recencia`: decaimiento exponencial (una venta de hace 30 días pesa más que una de hace 300).
- `w_calidad_dato`: cierre propio (1.0) > subasta (0.8) > lista-al-delist inferida (0.4) > lista activa (0.3).
- `w_condición`: ajuste por condición, box&papers, año.

**2. Estimador:**
- Tier A/B: modelo GBM (LightGBM) entrenado sobre features hedónicas + media ponderada de comparables como prior. Intervalo por cuantiles (predicción P10–P90).
- Tier C/D: media/mediana ponderada de comparables con intervalo por bootstrap; banda ancha por diseño.

**3. Salida estándar de cada instrumento:**
```json
{
  "instrument_id": "ROLEX-126710BLRO",
  "fair_value": 18900,
  "confidence_interval": [17800, 20200],
  "liquidity_tier": "A",
  "n_comparables": 34,
  "data_recency_days": 6,
  "confidence_index": 0.86,
  "methodology_version": "fv-2.1"
}
```

## Métricas estilo Bloomberg (definidas con rigor)

Para cada instrumento, con la advertencia de que las de mercado solo aplican a su tier:

| Métrica | Definición operativa |
|---|---|
| **Último precio** | Última transacción de calidad conocida (marca fuente y fecha) |
| **Precio promedio** | Media ponderada de comparables recientes (ventana por tier) |
| **Histórico** | Serie temporal de fair value diario (snapshot) + puntos de transacción reales |
| **Volumen** | # de transacciones/listings observados por período (con distinción lista vs cierre) |
| **Bid / Ask** | Bid = mejor oferta de compra registrada (pre-autorizada); Ask = menor precio de lista disponible |
| **Spread** | Ask − Bid, y por separado el **spread regional** (PTY/LatAm vs global) — la métrica estrella de arbitraje |
| **Liquidez** | Tier + tiempo mediano a venta + profundidad (# listings/bids activos) |
| **Tiempo promedio de venta** | Mediana de días entre `listing.observed` y `delisted/sold` |
| **Variación D/S/M** | Δ% del fair value (no del último precio ruidoso) en 1d/7d/30d |
| **Volatilidad** | Desviación estándar anualizada de retornos del fair value, **solo tier A/B**; en C/D se omite |
| **Índice de confianza** | Función de n_comparables, recencia, dispersión de comparables y calidad de fuente (0–1) |
| **Fair value** | Ver arriba, siempre con intervalo |
| **Book de órdenes** | Bids reales (compra pre-autorizada) vs asks (listings). **No se simula profundidad**; si hay poca, se muestra poca |

**Lo que NO se hace (por credibilidad):** MACD/RSI/Bollinger sobre instrumentos ilíquidos, "último precio" como si fuera un tick de bolsa, o fair value puntual en tier C/D. Ver doc 02.

## Motor de arbitraje (algoritmo)

```
Para cada listing nuevo o cambiado L del instrumento I:
  ref_price   = mid(fair_value(I))            # o precio en región/venue de salida
  gross_edge  = (ref_price − L.price) / L.price
  costs = fee_origen + logistica + aduana_estimada(region_L → region_salida)
        + costo_capital × tiempo_a_venta(I) + prob_defecto × valor
  net_edge    = (ref_price − L.price − costs) / L.price
  liq_salida  = liquidez(I, region_salida)     # ¿se puede realizar?
  score = net_edge × confianza(fair_value) × liq_salida
  Si net_edge > umbral Y liq_salida ≥ mínimo:
     emitir arbitrage.opportunity_found(L, score, net_edge, horizonte)
```

Ejemplo (el del brief, corregido a spread neto):
```
Chrono24:        USD 9,500  (precio de referencia/salida)
Dealer ZLC:      USD 8,200  (compra)
Spread bruto:    13.7%
Costos (fee 6% + logística $150 + aduana ~$0 reexport + capital 45d):  ~$650
Spread neto:     ~5.8%  →  oportunidad real, pero muy por debajo del bruto
```
La lección de producto: **publicar el spread bruto es engañar; el motor razona en neto.**

## Índice The Cote

**The Cote 50:** índice de precio del lujo, metodología **repeat-sales / hedónica** (como Case-Shiller, no media simple — evita el sesgo de composición cuando cambia qué se vende).
- Universo: canasta ponderada de instrumentos tier A/B por capitalización de mercado estimada (liquidez × precio).
- Sub-índices: The Cote Watches, The Cote Bags, The Cote Jewelry; y por marca (The Cote Rolex, The Cote Patek).
- Rebalanceo trimestral, reglas públicas, valor histórico reconstruible.
- **Objetivo estratégico:** que la prensa financiera regional cite "el índice The Cote" — ese es el moat de estándar (doc 02). Publicar un reporte trimestral del mercado del lujo LatAm es marketing y moat a la vez.

## Backtesting y validación (no negociable)

- **Backtest del fair value:** ¿cuánto se desvió la estimación del precio de cierre real observado después? Métrica: MAPE por tier. Objetivo tier A < 8%, B < 15%.
- **Backtest del arbitraje:** simular las oportunidades emitidas contra los cierres reales posteriores — ¿el edge neto se materializó? Esto valida (o mata) el motor antes de arriesgar capital propio.
- **Cobertura de incertidumbre:** ¿el precio real cae dentro del intervalo publicado el % de las veces que promete (p.ej. 80% dentro del P10–P90)? Si no, el intervalo miente y se recalibra.
- Todo versionado (`methodology_version`) para poder decir "así se calculaba en esa fecha".
