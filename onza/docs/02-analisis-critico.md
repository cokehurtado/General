# 02 · Análisis crítico — desafiando la idea

> Rol: el socio de a16z/Sequoia/YC que tiene que decidir si firma el cheque. Nada de entusiasmo; solo lo que puede matar la empresa.

## Los mayores riesgos (en orden de letalidad)

### R1 — El mercado direccionable puede ser demasiado chico, demasiado pronto
Centroamérica + Caribe es rico en los extremos pero angosto en el medio. Si el GMV realista de lujo secundario transable en la región es <$300M/año, un take rate de 8% da un techo de ~$24M de revenue — un buen negocio, **no un unicornio**. El unicornio requiere México + Colombia + Brasil o la capa de datos/financiera.
**Mitigación:** diseñar para demanda regional/global desde el día 1 (el comprador de un Patek en Panamá puede estar en Miami o Bogotá); tratar Centroamérica como laboratorio de operaciones, no como TAM.

### R2 — El arbitraje como propuesta de valor se autodestruye
Si el motor de arbitraje funciona, los spreads se cierran; si publicamos las oportunidades, las regalamos. Un negocio cuyo pitch es "encuentra ineficiencias" tiene revenue decreciente por diseño.
**Reencuadre (decisión de fundador):** el arbitraje no es el producto para el usuario final — es (a) **nuestra herramienta interna de bootstrap de liquidez** (comprar barato en la región, vender al precio global, financiar la operación temprana y generar los primeros precios de cierre propios), y (b) un **feature premium para dealers** que les da razones para vivir dentro del terminal. El producto duradero es el precio de referencia y el rail de confianza, no el spread.

### R3 — Autenticación física: el cuello de botella que no escala con código
The RealReal quema dinero precisamente aquí. Cada categoría (relojes, carteras, joyas) requiere peritos distintos, equipos distintos, y un falso positivo de autenticidad puede destruir la marca con un solo tweet.
**Mitigación:** una sola sede de autenticación (Panamá) con throughput controlado; empezar con relojes (la categoría con mejor relación valor/esfuerzo pericial y datos más ricos); partnerships con peritos certificados en vez de nómina propia al inicio; seguro de autenticidad con deducible; la IA solo **prefiltra** (triage de riesgo), nunca certifica.

### R4 — Riesgo AML/reputacional: lujo + Panamá + segunda mano = radar regulatorio
El lujo usado es un vehículo clásico de lavado, y Panamá viene saliendo de listas grises. Un solo caso de lavado procesado por la plataforma puede cerrar cuentas bancarias y matar la empresa.
**Mitigación:** compliance sobredimensionado desde el MVP (KYC con proveedor tier-1, umbrales de reporte, trazabilidad de origen de fondos en tickets altos, oficial de cumplimiento antes del empleado #10). Convertirlo en moat: "la única plataforma de la región donde un banco acepta el origen de tu compra".

### R5 — Dependencia de scraping: legalmente gris, técnicamente frágil
Chrono24/eBay pueden bloquear, cambiar ToS o demandar. Un "Bloomberg del lujo" construido solo sobre datos ajenos es una casa en terreno alquilado.
**Mitigación:** el scraping es el *arranque en frío* del dataset, no su estado final. La estrategia de datos madura hacia: (1) precios de cierre propios, (2) datos aportados por dealers a cambio del terminal (modelo "give-to-get", como Glassdoor), (3) resultados públicos de subastas (legalmente limpios), (4) acuerdos de datos. Priorizar fuentes públicas y APIs donde existan; presupuestar el riesgo legal.

### R6 — Cold start bilateral clásico
Sin compradores no vienen vendedores y viceversa; los grupos de WhatsApp ya tienen la confianza social que un marketplace nuevo no tiene.
**Mitigación:** la secuencia de tres capas existe exactamente para esto. La Capa 1 (terminal) es single-player. La Capa 2 arranca con **oferta cautiva**: 20-30 dealers de Panamá/ZLC con inventario real, onboarding manual, fotos hechas por nosotros. Los primeros 6 meses el marketplace es *curado*, no abierto.

### R7 — "Fair value" con datos escasos es estadísticamente indefendible
Un Rolex Submariner tiene liquidez; un Vacheron de producción limitada vende 3 unidades/año en toda la región. Publicar precios puntuales con n=3 destruye credibilidad ante el usuario sofisticado (que es exactamente nuestro usuario).
**Mitigación:** metodología pública (como Case-Shiller/Zestimate): intervalos de confianza siempre visibles, tiers de liquidez (A/B/C/D), y comparables jerárquicos (misma ref → misma familia → misma marca → categoría) con pesos decrecientes explícitos.

## Debilidades del modelo tal como fue planteado

1. **"Bloomberg + Nasdaq + Farfetch + Chrono24" es un pitch de 4 empresas.** Cada una es una década de trabajo. La debilidad es de foco, no de visión. La respuesta es la secuencia estricta: no se construye la Capa N+1 hasta que la Capa N tiene su KPI (ver roadmap).
2. **El order book prometido no existirá por años.** Con la frecuencia transaccional del lujo, un "book de órdenes" real es teatro al inicio. Honestidad de producto: mostrar *ofertas de compra registradas* (bids reales con tarjeta pre-autorizada) y *asks* (listings), no simular profundidad.
3. **Indicadores técnicos sobre activos ilíquidos son astrología.** RSI de una cartera Chanel con 8 datapoints es ruido. Sí a: tendencia, drawdown, volatilidad anualizada por tier de liquidez, spread regional. No a: MACD de un Birkin. La restricción es de credibilidad.
4. **El agente de negociación puede canibalizar el take rate** si enseña a los usuarios a cerrar por fuera. Diseño: el agente solo opera dentro de ofertas on-platform con escrow.

## Barreras de entrada (que nos afectan a nosotros)

- **Confianza de marca**: años. Un incumbente de retail de lujo local (o un family office de la ZLC) tiene ventaja de partida en oferta.
- **Adquirencia y banca**: conseguir procesamiento de pagos para bienes usados de alto ticket en Panamá es un proyecto en sí mismo (los adquirentes lo clasifican como alto riesgo).
- **Capital de inventario** si hacemos market-making propio: el arbitraje de bootstrap requiere balance sheet.

## La competencia real (no la aspiracional)

| Competidor | Amenaza real | Debilidad explotable |
|---|---|---|
| **Grupos de WhatsApp / Instagram dealers** | ALTÍSIMA — es el incumbente real, con confianza personal y cero comisión | Cero protección, cero datos, cero alcance fuera del círculo; los dealers *quieren* más demanda |
| **Chrono24** | Alta en relojes: envía a LatAm, tiene escrow | Sin presencia física, sin soporte español-local real, aduanas/impuestos son pesadilla del comprador, no cubre carteras/joyas, sin datos LatAm |
| **Mercado Libre** | Media: tráfico masivo | Cero autenticación de lujo, marca asociada a masivo, fraude rampante en tickets altos |
| **The RealReal / Vestiaire / Rebag** | Baja hoy en LatAm | No operan la región; su economics no aguanta expandirse pronto |
| **WatchCharts / Subdial / EveryWatch** | Alta en la capa de datos (relojes) | Solo relojes, solo datos US/EU, sin transacción, sin LatAm |
| **Casas de empeño premium / boutiques CPO locales** | Media: capturan la oferta de liquidez inmediata | Spreads abusivos (compran a 50-60% de mercado) — nuestro terminal los expone |

**Lectura estratégica:** el enemigo a vencer no es Chrono24; es la transacción informal por WhatsApp. El producto debe ser mejor que WhatsApp en lo que WhatsApp no puede hacer (precio de referencia, escrow, autenticación, alcance) y igual de fluido en lo que sí hace (chat, inmediatez, relación personal → por eso el dealer es cliente, no enemigo).

## Moats sostenibles (en orden de solidez)

1. **Datos transaccionales propietarios de LatAm** — cada cierre en ONZA es un datapoint que no existe en ningún otro dataset del mundo. Compuesto: más transacciones → mejor fair value → más consultas → más transacciones.
2. **La red física** — vault + laboratorio de autenticación + corredor logístico PTY. Capital y años; un competidor de software no lo copia con un fork.
3. **Rail de confianza regulado** — escrow bancario + KYC/AML + seguro. Las licencias y relaciones bancarias en la región son lentas de obtener: eso es exactamente lo que las hace moat.
4. **Red de dealers give-to-get** — el dealer aporta su inventario y precios de cierre a cambio del terminal y la demanda; su costo de cambiar de plataforma crece con su historial de reputación acumulado.
5. **El índice como estándar** — si el "índice ONZA" se cita en prensa financiera regional, somos el precio de referencia por default (el moat de Case-Shiller y CoinMarketCap).

## Cómo ser 10x mejor que un marketplace tradicional

| Marketplace tradicional | ONZA |
|---|---|
| Lista productos | Cotiza **instrumentos** con fair value, historial y liquidez |
| El comprador adivina el precio | Barra de error, comparables y spread vs global visibles en cada listing |
| Confianza = reviews | Confianza = escrow bancario + autenticación pericial + seguro + pasaporte digital |
| Cada venta mueve el objeto físico | En el Vault, la propiedad se transfiere sin mover el activo: settlement en segundos |
| El inventario es costo muerto | El inventario en custodia es **colateral**: préstamos sobre tu colección (la línea de revenue que ningún marketplace tiene) |
| Vende cuando alguien pregunta | Alertas estilo broker: "tu reloj subió 12% este trimestre; hay 3 bids activos a $X" |
| Comisión sobre transacción | Transacción + datos + suscripción + financiamiento + custodia + seguros |

**La frase para el pitch deck:** *un marketplace tradicional te ayuda a vender tu reloj; ONZA convierte tu colección en un portafolio.*

## Decisiones de cofundador (posiciones tomadas, no opciones)

1. **Relojes primero, solos, 12 meses.** Mejor densidad de datos (números de referencia = tickers naturales), pericia más sistematizable, ticket alto. Carteras y joyería entran en Fase 2 con el playbook probado. Diseñar el modelo de datos multi-categoría desde el día 1, operar mono-categoría.
2. **Terminal antes que marketplace.** 3-4 meses de ventaja construyendo el dataset y la audiencia antes de procesar la primera transacción.
3. **Market-making propio con presupuesto acotado** ($200-500k de inventario) para sembrar liquidez y comernos nuestro propio arbitraje — con disciplina de quant: límites de posición, stop-loss, rotación máxima 90 días.
4. **El dealer es el cliente enterprise.** El B2C llega por el dato; el GMV temprano lo trae el B2B2C.
5. **Compliance antes que growth.** Un unicornio en esta categoría y geografía muere más probablemente por un escándalo que por falta de usuarios.
