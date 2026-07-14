# 08 · Modelo de negocio

> El error a evitar: creer que todas estas líneas de ingreso existen desde el día 1. Existen **en secuencia**, cada una desbloqueada por la capa anterior. Un marketplace que intenta cobrar 12 cosas al lanzar no cobra ninguna.

## Las líneas de ingreso, mapeadas a las capas

| # | Línea | Capa que la habilita | Cuándo | Comentario |
|---|---|---|---|---|
| 1 | **Marketplace fee** (take rate 6–12%) | Capa 2 | Fase 1-2 | El pan. Cobrado al vendedor, o split. Escala con GMV |
| 2 | **Autenticación / inspección** | Capa 2 | Fase 1-2 | Fee fijo por peritaje (incluido en fee o à la carte para venta externa) |
| 3 | **Escrow fee** | Capa 2 | Fase 1-2 | % o fijo por custodia de fondos; puede estar dentro del take rate |
| 4 | **Seguros** (envío + almacenamiento) | Capa 2-3 | Fase 2 | Margen sobre prima; partner asegurador |
| 5 | **Logística** | Capa 2 | Fase 2 | Markup sobre envío asegurado puerta a puerta |
| 6 | **Dealer subscriptions** | Capa 1-2 | Fase 1 | SaaS mensual: terminal + herramientas de inventario + acceso a demanda + arbitraje. **El B2B es el revenue temprano confiable** |
| 7 | **Premium memberships (Terminal Pro)** | Capa 1 | Fase 1-2 | Consumidor: alertas avanzadas, fair value ilimitado, screener, portfolio analytics |
| 8 | **Price intelligence / Data** | Capa 1 | Fase 2 | Reportes, índice, series históricas para aseguradoras, casas de empeño, bancos, boutiques |
| 9 | **API** | Capa 1 | Fase 2-3 | Acceso programático a precios/índice — metered. Convierte el dato en infraestructura de terceros |
| 10 | **Financiamiento / colateral** | Capa 3 | Fase 3 | Préstamos con la colección en vault como garantía. **La línea de mayor margen y mayor moat** |
| 11 | **Custodia (Vault fee)** | Capa 3 | Fase 3 | Fee de almacenamiento por tiempo; habilita todo lo demás del vault |
| 12 | **Publicidad / destacados** | Capa 2 | Fase 2-3 | Listings promocionados de dealers. Bajo, pero margen puro |

Adicionales B2B (Fase 3): white-label de terminal para boutiques, feed de datos para aseguradoras (valuación de pólizas), integración con casas de empeño.

## Unit economics (marketplace core, ilustrativo)

Transacción típica de un reloj a **$12,000**, take rate **8%**:

```
GMV                         $12,000
Revenue (take 8%)           $   960
  − Autenticación (perito)  $  −120
  − Logística asegurada     $   −90
  − Pago/adquirencia (~2%)  $  −240   (alto en ticket alto; mover a transferencia lo reduce)
  − Fraude/chargeback prov. $   −60
Contribución bruta          $   450   (~47% del revenue, ~3.7% del GMV)
```
Palancas: bajar costo de pago moviendo ticket alto a transferencia bancaria a escrow (el mercado ya opera así); amortizar el peritaje si la pieza ya tiene pasaporte (Vault) → segunda venta de la misma pieza es casi todo margen.

**El insight de márgenes del Vault:** una pieza que se autentica una vez y se vende 3 veces reparte el costo de peritaje entre 3 transacciones. La custodia convierte un negocio de ~47% de margen de revenue en uno estructuralmente mejor con cada rotación.

## Estrategia de pricing

- **Take rate escalonado por ticket:** menor % en tickets altos (para no espantar el Patek de $80k a WhatsApp), mayor % en tickets bajos. Benchmark: Chrono24 ~6.5% comprador; StockX ~9–12%; casas de subasta 10–25% total. The Cote apunta a 6–10% *con* servicios incluidos que WhatsApp no da.
- **Dealer SaaS:** tiers (Starter / Pro / Enterprise) por # de listings, acceso a datos y arbitraje. Ancla de valor: "un solo buen arbitraje al mes paga la suscripción del año".
- **Terminal Pro (consumidor):** freemium. Gratis: fair value básico, 1 watchlist. Pro (~$20-40/mes): alertas, portfolio, histórico completo, sin límites.
- **Data/API:** metered + contratos enterprise (aseguradoras, bancos).

## Por qué esto puede ser venture-scale (y honestamente, dónde no)

**El caso alcista:** el revenue no depende solo del GMV de Centroamérica. Se apila: (marketplace de LatAm ampliado) + (SaaS de dealers de toda la región) + (datos vendidos a instituciones) + (financiamiento colateralizado, que es fintech con márgenes fintech). El TAM real es "infraestructura financiera del lujo en LatAm", no "reventa de relojes en Panamá".

**El caso bajista honesto (de la crítica, doc 02):** si el negocio se queda en marketplace transaccional de Centroamérica, es un buen negocio de $10-30M de revenue, no un unicornio. La tesis de unicornio **requiere** que al menos una de estas tres se materialice: (a) expansión a México/Colombia/Brasil, (b) la capa de datos se vuelve estándar de la industria, (c) el financiamiento colateralizado escala. El plan debe optimizar para llegar a poder intentar esas tres, no para maximizar el fee del mes 1.

## Métricas que importan (y le importan al VC)

| Métrica | Por qué |
|---|---|
| **GMV y take rate efectivo** | Tamaño y salud del core |
| **Contribución por transacción** | ¿Cada venta gana dinero después de operaciones? |
| **Liquidez: tiempo mediano a venta** | El mejor proxy de product-market fit de un marketplace |
| **% GMV recurrente (dealers)** | Predecibilidad del revenue |
| **Consultas de fair value / MAU del Terminal** | Salud de la Capa 1 (el moat de datos) |
| **Cobertura y precisión del dataset** | Salud del moat |
| **Tasa de disputa / fraude** | La confianza es el producto; esto la mide |
| **CAC por canal y payback** | Especialmente CAC de dealers (bajo, alto LTV) vs consumidor |
| **Piezas en Vault y rotación** (Fase 3) | El multiplicador de márgenes |
