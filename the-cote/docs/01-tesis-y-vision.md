# 01 · Tesis y visión

## El problema, dicho sin romanticismo

El mercado secundario de lujo mueve **~$50B/año globalmente** (relojes ~$25B, carteras ~$8B, joyería ~$10B) y crece 2-3x más rápido que el mercado primario. En LatAm ese mercado existe — hay Rolex, Birkins y Cartier cambiando de manos todos los días — pero opera en la edad de piedra:

- **No hay precio de referencia.** El mismo Rolex GMT-Master II "Pepsi" ref. 126710BLRO puede estar a $9,500 en Chrono24, $8,200 con un dealer privado de la Zona Libre, $11,000 en una boutique de reventa en CDMX y "DM for price" en Instagram.
- **No hay confianza transaccional.** Las transacciones grandes se hacen por WhatsApp con transferencia bancaria y fe. El comprador asume 100% del riesgo de autenticidad; el vendedor asume 100% del riesgo de pago.
- **No hay liquidez visible.** Nadie sabe cuánto tarda en venderse una pieza, a qué precio real (no de lista) se cerró, ni cuántos compradores activos hay.
- **No hay datos LatAm.** WatchCharts y Chrono24 indexan el mercado US/EU. El spread LatAm vs global es invisible — y ahí vive el arbitraje.

## La hipótesis

**Los artículos de lujo son instrumentos financieros mal instrumentados.** Cada referencia de reloj, cada modelo de cartera, tiene oferta, demanda, volumen, spread, volatilidad, tendencia y profundidad de mercado. Lo único que falta es la infraestructura que los mida y los haga transables con la fricción de una acción, no la de un auto usado.

Corolarios:

1. **El precio es el producto.** Antes de que nadie compre o venda en tu marketplace, ya te consulta para saber cuánto vale lo que tiene. Zillow lo probó con el Zestimate: el dato crea el hábito, el hábito crea la audiencia, la audiencia crea la liquidez.
2. **La confianza es el take rate.** La gente paga 6-10% de comisión no por el matching (WhatsApp lo hace gratis) sino por eliminar el riesgo de fraude y falsificación. Escrow + autenticación física son el producto por el que se cobra.
3. **La custodia es el endgame.** Si el activo vive en un vault ya autenticado, venderlo es una escritura en una base de datos: settlement instantáneo, cero logística por transacción, posibilidad de préstamos colateralizados. Eso es lo que convierte un marketplace en un exchange.

## El producto (tres capas, en orden)

### Capa 1 — The Cote Terminal (el Bloomberg)
Terminal de datos del lujo: precio justo, histórico, liquidez, spread LatAm vs global, alertas, screener de oportunidades, índice The Cote. Single-player mode: **útil para una persona sola, sin necesidad de que exista el marketplace**. Resuelve el cold-start.

### Capa 2 — The Cote Market (el Chrono24 con escrow)
Marketplace transaccional con escrow, KYC/AML, autenticación física en Panamá y logística asegurada. Cada transacción alimenta la Capa 1 con el dato más valioso del mundo: **precio real de cierre**, que ningún scraper puede obtener.

### Capa 3 — The Cote Vault (el Nasdaq)
Custodia física en Panamá (idealmente en régimen de zona franca). El activo entra una vez, se autentica una vez, recibe un pasaporte digital, y luego se compra/vende N veces sin moverse. Habilita: trading instantáneo, ofertas bid/ask reales, préstamos con colateral, fracciones institucionales (fase tardía) y el order book genuino.

## Por qué ahora

- La generación que compra lujo en LatAm ya opera cripto y brokers digitales: entiende spreads, gráficos y órdenes.
- Los LLMs colapsaron el costo del problema técnico más difícil del negocio: **entity resolution** (saber que dos publicaciones con fotos y títulos distintos son el mismo modelo) y extracción de datos de fuentes no estructuradas (Instagram, WhatsApp, foros).
- Chrono24, StockX y The RealReal validaron el modelo en otros mercados, pero ninguno tiene operación física ni datos en LatAm — y su estructura de costos hace que la región no les sea prioritaria por años.
- El reloj y la cartera se consolidaron como *asset class* post-2020 (índices de WatchCharts, subastas récord, fondos de relojes).

## Por qué Panamá (el insight contraintuitivo)

Panamá **no** es el mercado — 4.5M de habitantes no sostienen un marketplace de lujo. Panamá es el **hub**:

| Ventaja | Implicación para The Cote |
|---|---|
| Economía 100% dolarizada | Sin riesgo cambiario en el libro; precios regionales en USD, el idioma natural del lujo |
| Zona Libre de Colón + regímenes de zona franca | Inventario en custodia con impuestos diferidos hasta que sale del país → el Vault puede recibir, autenticar y re-vender piezas de toda la región sin nacionalizarlas |
| Hub de Copa Airlines (80+ destinos directos en las Américas) | Logística de ida y vuelta a todo LatAm en <24h para autenticación |
| Centro bancario regional | Cuentas escrow/fiduciarias, adquirencia, y (con trabajo) financiamiento colateralizado |
| Turismo de compras ya existente | Los compradores de la región ya viajan a Panamá a comprar lujo; The Cote formaliza ese flujo |
| Sin impuesto sobre ventas a bienes reexportados; jurisdicción pro-comercio | Márgenes y estructura holding limpia para VC |

**El mercado es LatAm desde el día 1; Panamá es donde vive el vault, el equipo de autenticación y la entidad de escrow.** La demanda llega online; el activo pasa físicamente por Panamá solo cuando la transacción lo requiere (Capa 2) o una sola vez en su vida (Capa 3).

## Principios de diseño (los no-negociables)

1. **Cada dato tiene barra de error.** Un fair value sin intervalo de confianza es una mentira. Con 4 ventas comparables no se reporta "vale $9,340", se reporta "$8,900–$9,800, confianza media". La honestidad estadística es marca.
2. **El instrumento, no el listing.** El grafo de datos se organiza alrededor del **modelo canónico** (ref. 126710BLRO) como un ticker; los listings son cotizaciones de ese ticker en distintos venues.
3. **Precio de cierre > precio de lista.** Todo el diseño de producto empuja a capturar precios reales de transacción (los nuestros, los de subastas, los reportados por dealers a cambio de acceso al terminal).
4. **Compliance como feature, no como fricción.** Panamá carga estigma AML; The Cote lo invierte: KYC serio, trazabilidad de origen y pasaporte digital por pieza hacen que comprar en The Cote sea la forma *defendible* de comprar lujo en la región.
5. **Todo modular, todo generable.** Cada servicio del monorepo es una unidad que Claude Code puede construir, testear y desplegar de forma aislada (ver backlog).
