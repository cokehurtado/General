# ONZA Solo — terminal personal de arbitraje de relojes (v0)

> El arranque en chico de la visión ONZA: una herramienta **para beneficio propio** de compra/venta de relojes, bajo el mismo modelo de mercado financiero. No es el marketplace — es la Capa 1 (Terminal) + el motor de arbitraje del market-maker, operados por una sola persona con su propio capital.
>
> **Regla de oro:** mismo modelo de datos que el diseño grande (`onza/docs/03-arquitectura.md`), para que el día que quieras, esto *sea* la Capa 1 y no un prototipo desechable.

## Qué hace (y qué no)

**Hace:**
- Mantiene un universo curado de referencias líquidas (top marcas deportivas) como *tickers*.
- Estima **fair value** de cada pieza concreta, ajustado por **condición, caja y papeles**, con intervalo de confianza y tier de liquidez.
- Compara cada listing contra **dos referencias**: el fair value del secundario **y el precio retail (MSRP)**.
- Califica al **proveedor/procedencia** y **veta** compras de fuentes no confiables sin importar el spread.
- Calcula el **edge neto** restando costos reales de **internación y transporte a Panamá**, costo de capital y provisión de riesgo.
- Rankea oportunidades y mantiene un **libro personal** (P&L, días en inventario, precio objetivo de venta).

**No hace (fuera de alcance de v0):** marketplace, escrow, KYC, otros usuarios, móvil, vault, otras categorías. Todo eso es el diseño grande en `onza/`.

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

**Realizable ≠ fair value.** Tú no vendes al *mid*, vendes al *bid* y pagas por realizar. El motor usa `realizable = fair_value × (1 − haircut(tier))`, para que el edge sea honesto (misma filosofía de "edge neto" de `onza/docs/07-motor-financiero.md`). Todos los porcentajes son **calibrables** contra tus cierres reales — ese es el objetivo del libro personal.

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
onza-solo/
├── onza_solo/
│   ├── models.py       # dataclasses: Instrument, Listing, PricedPiece, Opportunity + enum Condition
│   ├── universe.py     # universo curado (seed) de refs con retail y base_fair_value
│   ├── grading.py      # taxonomía de condición + normalizador + ajustes caja/papeles/pulido
│   ├── provenance.py   # scoring de proveedor + veto
│   ├── costs.py        # modelo de costos de internación a Panamá (configurable)
│   ├── pricing.py      # fair value de la pieza + tier + CI + realizable + señales retail
│   ├── velocity.py     # tiempo estimado de venta + retorno anualizado + velocidad de capital
│   ├── arbitrage.py    # edge neto + retorno anualizado + gates + score + ranking
│   └── scan.py         # CLI: carga fixtures, evalúa, imprime reporte
├── fixtures/listings.json   # listings de ejemplo (buenos y malos) para demostrar los gates
└── tests/test_core.py       # tests con unittest (sin dependencias externas)
```

## Cómo correrlo (sin instalar nada)

Python 3.10+ de la stdlib, cero dependencias externas para v0:

```bash
cd onza-solo
python -m onza_solo.scan            # corre el scanner sobre los fixtures e imprime oportunidades
python -m unittest discover tests   # corre los tests
```

## Datos: de dónde vienen (y el paso siguiente)

- **Fuentes elegidas para v0:** Chrono24 + resultados de subastas + WatchCharts (benchmark). Las más limpias legal y estadísticamente.
- **Estado actual:** el núcleo corre con `fixtures/listings.json` (datos de ejemplo) y un universo *seed* con valores **ilustrativos** — el valor de v0 es el **método**, no los números semilla.
- **Paso siguiente (deliberado):** la ingesta en vivo (scraping/feeds) se construye aparte porque tiene aristas legales (ToS, rate limits) que conviene revisar con criterio antes de encenderla. El núcleo ya está listo para recibir listings reales sin cambios de arquitectura.

## Advertencia honesta

Esto es hoy un **negocio de trading**, no una empresa de tecnología: depende de ti en el loop y no escala solo. Es la **cuña**, no el destino. Y opera con tu propio dinero: el sistema **mide** —no elimina— el riesgo de capital inmovilizado, de comprar una falsificación, de no poder vender cuando quieras y de que el mercado baje. Cada compra/venta que registres calibra el modelo; ahí empieza a acumularse el dato propio que es el moat.
