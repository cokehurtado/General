# 06 · Agentes de IA

> Principio rector: **el LLM hace lenguaje, visión y juicio en la cola difícil; la estadística hace los números.** Un agente que "calcula el precio justo" pidiéndoselo a un LLM es una alucinación con barra de progreso. Los agentes orquestan, extraen, clasifican y explican; los valores monetarios salen de modelos auditables.

Arquitectura común a todos: cada agente es un servicio con (1) entrada tipada, (2) política de decisión, (3) salida tipada **con score de confianza**, (4) umbral de auto-acción vs cola de revisión humana, (5) log de decisiones para auditoría y para reentrenar. Ninguno actúa sobre dinero o autenticidad sin humano por encima del umbral de riesgo.

---

## 1. Agente de Matching (entity resolution)
**Trabajo:** decidir que "Rolex GMT Pepsi 126710BLRO", "Rolex GMT Master 2 Pepsi jubilee 2023" y una foto sin texto son el **mismo instrumento canónico**.

**Cómo:** cascada de costo creciente —
1. Extracción de número de referencia (regex + diccionario por marca) → si hay ref válida, match casi seguro.
2. Reglas estructuradas (marca + familia + atributos: material, bisel, dial, tamaño).
3. Embeddings multimodales (texto del anuncio + imágenes) → vecino más cercano en `pgvector` sobre el catálogo.
4. LLM (Claude) solo para la cola ambigua: se le dan los 3 candidatos top y decide con justificación.

**Salida:** `instrument_id`, `confidence`, `method`. Bajo umbral → cola de revisión en el admin. Cada corrección humana es dato de entrenamiento.
**Por qué es el agente #1:** sin matching correcto, todo lo demás (pricing, arbitraje, índice) se construye sobre arena.

---

## 2. Agente de Pricing (fair value)
**Trabajo:** estimar el valor justo de un instrumento **con intervalo de confianza y tier de liquidez**.

**Cómo (no es un LLM):**
- Modelo hedónico / GBM (LightGBM) sobre features: referencia, condición, año, box&papers, completitud, estacionalidad, tendencia de la familia, región.
- Comparables jerárquicos con pesos decrecientes: misma ref (peso alto) → misma familia → misma marca → categoría.
- Salida: `fair_value`, `[low, high]` (intervalo), `liquidity_tier (A/B/C/D)`, `n_comparables`, `data_recency`.
- El LLM solo entra para **explicar** el número en lenguaje natural ("por qué vale esto") y para extraer features cualitativas de descripciones.

**Regla de oro:** si `n_comparables < k` para el tier, no se publica un punto — se publica un rango ancho con etiqueta "datos escasos". La honestidad estadística es el producto. Ver doc 07.

---

## 3. Agente de Arbitraje
**Trabajo:** detectar oportunidades de compra con **spread neto positivo** (después de fees, envío, aduanas, riesgo).

**Cómo:**
- Compara precio de un listing contra: fair value del instrumento, y precio del mismo instrumento en otras regiones/venues.
- Spread bruto → **spread neto** restando costos reales (comisión origen, logística, aduana estimada, tiempo-a-venta × costo de capital, prob. de defecto).
- Scoring: `expected_return`, `confidence`, `time_horizon`, `liquidity` del lado de salida.
- Filtra por liquidez de salida: un arbitraje que no se puede realizar (no hay comprador) no es arbitraje.

**Uso:** interno (bootstrap de inventario propio) y feature premium para dealers. **No se publica abiertamente al retail** (se autodestruiría). Ver doc 02, R2.

---

## 4. Agente de Autenticación (triage, no certificación)
**Trabajo:** dar un **score de riesgo de falsificación** a un listing/pieza para priorizar el peritaje humano. **Nunca certifica** — prefiltra.

**Cómo:**
- Visión (Claude / modelo de imagen): coherencia de logos, tipografías, grabados, alineación de dial, luminiscencia, acabados; comparación contra imágenes de referencia del catálogo.
- Señales de metadatos: precio anómalamente bajo vs fair value, vendedor nuevo, fotos genéricas/robadas (reverse image), descripción con red flags conocidos.
- Salida: `risk_score`, `flags[]` (razones), recomendación de nivel de peritaje.

**Frontera dura:** la certificación de autenticidad la firma un perito humano acreditado. La IA hace que el perito revise las 20 piezas correctas de 200, no las 200. Un falso "auténtico" de la IA jamás debe llegar al comprador sin humano.

---

## 5. Agente Antifraude
**Trabajo:** detectar vendedores/compradores/transacciones riesgosas (pago fraudulento, listing falso, colusión, lavado).

**Cómo:**
- Features de comportamiento: velocidad de cuenta, patrones de precio, device/IP, grafo de relaciones (¿el "comprador" y el "vendedor" comparten señales?), montos vs perfil KYC.
- Modelo de scoring + reglas duras (hard blocks) para señales AML (estructuración, origen de fondos incoherente en ticket alto).
- Salida: `fraud_score`, acción (permitir / step-up verification / bloquear / escalar a cumplimiento).

**Frontera:** integra con `trust` y con el workflow AML. Bloqueos de dinero siempre reversibles por humano; reportes regulatorios como workflow trazable.

---

## 6. Agente de Negociación
**Trabajo:** sugerir ofertas y contraofertas racionales dentro de la plataforma.

**Cómo:**
- Dado fair value, liquidez, tiempo del listing, urgencia declarada e histórico de aceptación, sugiere un rango de oferta con probabilidad de aceptación estimada.
- Opera **solo on-platform con escrow** — nunca facilita cerrar por fuera (protege el take rate; ver doc 02).
- Para el vendedor: sugiere precio de lista óptimo (trade-off precio vs tiempo-a-venta).

**Salida:** oferta sugerida, `p(accept)`, justificación en lenguaje natural.

---

## 7. Agente de Inversión (asesor de portafolio)
**Trabajo:** actuar como un roboadvisor del lujo: sugerir qué comprar/vender/mantener según objetivos del usuario.

**Cómo:**
- Sobre la colección del usuario (o watchlist): retorno esperado, riesgo (volatilidad por tier), concentración, correlación con el índice ONZA, liquidez.
- Sugerencias: "sobreexpuesto a Rolex deportivos; considera diversificar", "esta pieza superó su fair value +18%, ventana de venta", "instrumento X subvalorado con buena liquidez de salida".
- **Disclaimers claros:** no es asesoría financiera regulada; son señales de mercado. (Riesgo regulatorio real — revisar con legal antes de lanzar en cada país.)

**Salida:** recomendaciones rankeadas con retorno/riesgo esperado y razón.

---

## 8. Agente Market-Maker (interno, Fase 2-3)
**Trabajo:** gestionar el inventario propio de ONZA que siembra liquidez.

**Cómo:** con disciplina de quant — límites de posición por instrumento/marca, stop-loss, rotación máxima (p.ej. 90 días), tamaño de posición por Kelly fraccionado sobre el edge del arbitraje. Cotiza bids/asks para dar profundidad al book. Reporta P&L y exposición.

---

## Orquestación

- Los agentes se disparan por eventos (nuevo listing → matching → pricing → arbitraje/autenticación en paralelo) y por schedule (recalcular índice, revisar portafolios).
- **Guardrails universales:** todo output monetario o de riesgo lleva confianza; toda acción sobre dinero/identidad/autenticidad tiene humano en el loop por encima de umbral; todo prompt a LLM tiene evaluación (golden set + regresión) antes de deploy.
- **Evaluación continua:** golden datasets por agente (matching, pricing backtesting, autenticación con piezas conocidas). Un agente sin su harness de evaluación no va a producción.
- **Costos:** LLM solo donde aporta (cola difícil, extracción, explicación). El 90% del volumen lo resuelven reglas y modelos baratos; el LLM es el especialista caro que se llama cuando hace falta.
