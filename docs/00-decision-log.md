# 00 — Registro de decisiones

Formato obligatorio (§61): HIPÓTESIS · EVIDENCIA · DECISIÓN · MEDICIÓN · RIESGO · VALIDACIÓN REQUERIDA.
Etiqueta obligatoria: `EVIDENCE-BASED` / `PRODUCT HYPOTHESIS` / `ENGINEERING DECISION`.

---

## D-001 · Cambio del test de aceptación primario `PRODUCT HYPOTHESIS`
**Fecha:** 2026-09-12 · **Estado:** APROBADA

**Hipótesis.** El caso de uso estrella del master prompt (§58: reparación conversacional en vivo, en un
almuerzo, "en segundos") no es alcanzable con la tecnología actual, y validar el MVP contra él lo condena.

**Evidencia.** Una conversación adulta tiene ventanas de turno de ~1–2 s. El flujo real
(ASR sobre habla disfluente → LLM → 2 rondas de aclaración → confirmación) mide decenas de segundos.
La tasa de error de palabra en ASR sobre habla afásica ronda el 37% (`01-clinical-evidence`, E5), lo que
añade rondas en lugar de quitarlas. La literatura de AAC documenta además reticencia a usar el sistema en
público con interlocutores no familiares (`01-clinical-evidence`, sección AAC).

**Decisión.** El test de aceptación primario pasa a ser: *pre-composición antes de una conversación o
llamada, respuesta a mensajería asíncrona, y preparación de lo que quiere decir.* La reparación en vivo
se mantiene como **visión a v3**, no como criterio de aceptación del MVP.

**Medición.** Mediana de tiempo hasta mensaje confirmado; proporción de usos en contexto asíncrono vs. en vivo.

**Riesgo.** Perder la escena emocionalmente más potente del producto y con ella parte de la motivación.

**Validación requerida.** Cronometrar el flujo completo en Wizard-of-Oz antes de construir nada.

---

## D-002 · Reformulación del North Star `PRODUCT HYPOTHESIS`
**Fecha:** 2026-09-12 · **Estado:** APROBADA

**Hipótesis.** "La app debe volverse progresivamente menos necesaria" (§59) mezcla dos objetivos
distintos —prótesis comunicativa y rehabilitación— y crea un incentivo perverso: un AAC excelente y
permanente se mediría como fracaso.

**Evidencia.** Big CACTUS muestra ganancias concentradas en los ítems entrenados sin transferencia
automática a conversación (`01-clinical-evidence`, E2). La evidencia de dosis (≥20 h totales,
≥4 días/semana; ESO 2025 y RELEASE 2022) implica que el uso frecuente y sostenido **es el vehículo** del
beneficio. Un KPI que premie el descenso de uso contradice la evidencia de dosis.

**Decisión.** North Star reformulado:
> **La asistencia requerida por acto comunicativo disminuye, mientras el volumen y la complejidad de las
> ideas comunicadas aumentan.**

Menos ayuda *dentro* de la app, no menos app. El producto puede legítimamente ser permanente.

**Medición.** Nivel mínimo de andamiaje requerido por mensaje exitoso · nº de ideas comunicadas/semana ·
proporción de ideas novedosas · tasa de reparación exitosa · comunicación funcional medida con
instrumento externo a la app.

**Riesgo.** Perder la disciplina que imponía la formulación paradójica original: que el sistema no se
conforme con ser un AAC sofisticado. Se mitiga manteniendo "asistencia por acto" como métrica de primer
nivel, no como métrica secundaria.

**Validación requerida.** Que el andamiaje mínimo requerido descienda de forma medible a lo largo de semanas.

---

## D-003 · Incorporación del fonoaudiólogo/a antes de la investigación detallada `ENGINEERING DECISION`
**Fecha:** 2026-09-12 · **Estado:** APROBADA EN PRINCIPIO — factibilidad por confirmar

**Decisión.** Se incorpora al clínico tratante como co-diseñador antes del MVP, no en la fase de portal
clínico. Mientras no se confirme:
- Todo lo que dependa de configuración clínica queda **fuera de alcance**.
- El producto opera únicamente como asistente de comunicación, sin componente terapéutico configurable.
- Las preguntas del bloque crítico de `03-user-model` permanecen `[BLOQUEADO]`.

**Riesgo si no se concreta.** La pregunta 1 (fiabilidad del sí/no) queda sin responder por vía clínica.
Plan B: administrar un protocolo propio de elección forzada con significados conocidos durante la
Fase 1 Wizard-of-Oz, aceptando que es menos riguroso y documentándolo como tal.

---

## D-004 · No construir catálogo genérico de ejercicios `EVIDENCE-BASED`
**Fecha:** 2026-09-12 · **Estado:** PROPUESTA — pendiente de aprobación del comité

**Evidencia.** SFA mejora los ítems entrenados en ~82% de participantes con generalización limitada a
ítems no entrenados y habla conectada; Big CACTUS mejora las palabras entrenadas sin mejorar la
conversación (`01-clinical-evidence`).

**Decisión propuesta.** Eliminar del roadmap la biblioteca genérica de rehabilitación (§31), no
postergarla. El único material que justifica su coste es **el que él mismo falló en decir**. El primer
módulo terapéutico a construir, tras el MVP, es **script training**, que muestra la mejor señal de
generalización a conversación.

**Validación requerida.** Evidencia sobre predictores de generalización (pendiente, Ola 2).

---

## D-005 · Sin puntuación automática del habla en V1 `EVIDENCE-BASED`
**Fecha:** 2026-09-12 · **Estado:** PROPUESTA

**Evidencia.** Tasa de error de palabra ~37% en ASR sobre habla afásica natural, con amplia variación
intra-sujeto según severidad.

**Decisión propuesta.** V1 no emite juicio automático de corrección sobre su habla. Solo autoinforme
("lo dije bien") y éxito comunicativo. El ASR se usa como **fuente de hipótesis**, nunca como juez.

**Riesgo.** Perder señal cuantitativa de progreso lingüístico. Aceptado: la alternativa es una señal
falsa que además puede humillar.
