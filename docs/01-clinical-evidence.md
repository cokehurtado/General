# 01 — Evidencia clínica

**Versión:** 0.1 · **Estado:** Ola 1 completa con lagunas marcadas · **Fecha:** 2026-09-12

## Alcance y método

Revisión dirigida a responder únicamente las preguntas que **cambian decisiones de producto**.
Fuentes priorizadas: guía de la European Stroke Organisation, revisiones Cochrane, meta-análisis de
datos individuales, ECAs y revisiones sistemáticas. Cuando no se pudo acceder al texto completo se
indica `[TEXTO COMPLETO PENDIENTE]`: la afirmación proviene del resumen del editor o de PubMed y debe
confirmarse antes de fundamentar una decisión irreversible.

**Limitación declarada:** varias fuentes primarias (PMC, Nature, repositorios institucionales) están
bloqueadas por la política de red de este entorno. Las citas son verificables por DOI/PMID, pero la
lectura íntegra de 4 documentos queda pendiente. Está señalado dónde.

## Clasificación de evidencia

| Nivel | Significado |
|---|---|
| **SUPPORTED** | Respaldo de revisión sistemática, meta-análisis o guía clínica |
| **PROMISING** | Estudios positivos consistentes, pero con diseño o tamaño limitado |
| **EXPERIMENTAL** | Prueba de concepto, preprints, sin validación clínica |
| **INSUFFICIENT** | Evidencia ausente, contradictoria o explícitamente negativa |

---

## Resumen ejecutivo: las cinco conclusiones que gobiernan el producto

**E1. La terapia del lenguaje funciona, y mejora comunicación funcional.** `SUPPORTED`
La revisión Cochrane encuentra beneficio de la terapia fonoaudiológica frente a no recibir terapia en
comunicación funcional, lectura, escritura y lenguaje expresivo.
> Brady MC, Kelly H, Godwin J, Enderby P, Campbell P. *Speech and language therapy for aphasia following stroke.* Cochrane Database Syst Rev. 2016;(6):CD000425. doi:10.1002/14651858.CD000425.pub4

**E2. La terapia computarizada autogestionada mejora las palabras entrenadas, pero NO la conversación.** `SUPPORTED` / `INSUFFICIENT` respectivamente.
Big CACTUS (n=240, afasia crónica >4 meses post-ACV, 6 meses de intervención) mostró mejora clínicamente
significativa en la recuperación de palabras personalmente relevantes, **y ausencia de mejora en conversación**.
> Palmer R, et al. *Self-managed, computerised speech and language therapy for patients with chronic aphasia post-stroke compared with usual care or attention control (Big CACTUS): a multicentre, single-blinded, randomised controlled trial.* Lancet Neurol. 2019;18(9):821-833. PMID:31397288

**Esta es la conclusión más importante de todo el documento.** Es exactamente el producto que estábamos
tentados de construir, probado a escala, con el resultado a medias. Todo el diseño de la parte
rehabilitadora debe partir de aceptar este hallazgo, no de esperar ser la excepción.

**E3. El entrenamiento del interlocutor sí mejora la comunicación funcional.** `SUPPORTED`
56 estudios entre la revisión original y su actualización reportan resultados positivos, en distintos
grados de severidad y distintos tipos de interlocutor; mejora la comunicación funcional y la
participación de la persona con afasia, y el bienestar del interlocutor familiar.
> Simmons-Mackie N, Raymer A, Armstrong E, Holland A, Cherney LR. *Communication partner training in aphasia: a systematic review.* Arch Phys Med Rehabil. 2010.
> Simmons-Mackie N, Raymer A, Cherney LR. *Communication partner training in aphasia: an updated systematic review.* Arch Phys Med Rehabil. 2016.

**Implicación incómoda:** la intervención con mejor evidencia para el objetivo que declaramos como North
Star (comunicación funcional) **no es una app para el paciente**: es formación para su familia. §42 del
master prompt la trata como función secundaria. Debería subir de rango.

**E4. La dosis importa, y el umbral útil es alto.** `SUPPORTED` (evidencia de baja calidad)
La guía ESO recomienda dosis total de terapia ≥20 horas y sugiere mayor intensidad y frecuencia,
con ≥4 días por semana; sugiere además terapia individualizada y modelos de entrega digitales y grupales.
El meta-análisis de datos individuales RELEASE (959 participantes, 25 ECAs) asocia las mayores ganancias
en lenguaje global y comprensión a dosis de >20 a 50 horas.
> Brady MC, Mills C, Øra HP, et al. *European Stroke Organisation (ESO) guideline on aphasia rehabilitation.* Eur Stroke J. 2025. doi:10.1177/23969873241311025 · PMID:40401776 `[TEXTO COMPLETO PENDIENTE]`
> RELEASE Collaboration. *Dosage, Intensity, and Frequency of Language Therapy for Aphasia: A Systematic Review–Based, Individual Participant Data Network Meta-Analysis.* Stroke. 2022. doi:10.1161/STROKEAHA.121.035216

**E5. El ASR no es fuente de verdad sobre habla afásica.** `SUPPORTED`
Sobre habla afásica natural se reporta una tasa de error de palabra en torno al **37%**, con variación
amplia según severidad. Modelos afinados reducen el error de forma significativa, pero el punto de partida
comercial es inservible como juez de corrección.
> *Automatic recognition and detection of aphasic natural speech.* arXiv:2408.14082
> *AS-ASR: A Lightweight Framework for Aphasia-Specific Automatic Speech Recognition.* arXiv:2506.06566
> *Evaluating ASR for aphasia: a framework for clinically relevant transcription performance.* Aphasiology. 2026. doi:10.1080/02687038.2026.2621235
> *Addressing Pitfalls in Auditing Practices of Automatic Speech Recognition Technologies: A Case Study of People with Aphasia.* arXiv:2506.08846

---

## Hallazgos por mecanismo

### Análisis de Rasgos Semánticos (SFA)
`SUPPORTED` para ítems entrenados · `INSUFFICIENT` para generalización.
Mejora la denominación por confrontación de los ítems entrenados en ~82% de los participantes revisados.
La generalización a ítems no entrenados y a habla conectada es limitada en muchos de los estudios
incluidos, especialmente para palabras semánticamente no relacionadas con los objetivos. Mayor
efectividad en afasia fluente que no fluente.
> Efstratiadou EA, Papathanasiou I, Holland R, Archonti A, Hilari K. *A Systematic Review of Semantic Feature Analysis Therapy Studies for Aphasia.* J Speech Lang Hear Res. 2018. PMID:29710193

**Implicación de producto:** si la generalización es débil, **el único material que justifica el coste de
construir ejercicios es el que el usuario realmente falló en decir**. El catálogo genérico de vocabulario
no se construye.

### Script training (guiones)
`PROMISING`, con la mejor señal de generalización de todos los mecanismos revisados.
Mejora exactitud, productividad gramatical, velocidad del habla y fluidez articulatoria, tanto en la
producción del guion como en tareas conversacionales más funcionales; varios estudios documentan
generalización a intercambios conversacionales no entrenados.
> Youmans G, Youmans SR, Hancock AB. *Script training and generalization for people with aphasia.* Am J Speech Lang Pathol. 2012. PMID:22442283

**Implicación de producto:** es el candidato con mejor relación evidencia/encaje. Un guion es,
funcionalmente, "practicar esto" sobre un mensaje real que el usuario quiso decir. Es el primer módulo
de rehabilitación a construir — **después** del MVP comunicador, no antes.

### Jerarquías de claves: errorless vs. errorful
`INSUFFICIENT` para afirmar superioridad de ninguna.
El aprendizaje sin error produce ganancias globalmente similares o menores que la terapia con error, con
resultados equivalentes post-terapia y en seguimiento. Las jerarquías de claves descendentes son
aprendizaje sin error; las ascendentes, con error. El perfil de respuesta varía entre personas según
memoria de reconocimiento y función ejecutiva.
> *Errorless, Errorful, and Retrieval Practice for Naming Treatment in Aphasia: A Scoping Review of Learning Mechanisms and Treatment Ingredients.* PMC10023178 `[TEXTO COMPLETO PENDIENTE]`

**Implicación de producto:** la escalera de 8 niveles de andamiaje (§29) **no tiene respaldo empírico de
superioridad sobre una escalera más corta**. Es una decisión de ingeniería disfrazada de decisión clínica.
Se recomienda empezar con 3 niveles (libre → concepto/palabra clave → modelo completo) e instrumentar qué
nivel usa realmente antes de añadir granularidad.

### Telerehabilitación
`PROMISING`. Existe meta-análisis previo y un ECA fase II de no inferioridad en curso (TERRA,
NCT04682223) en afasia crónica. Conclusión aún abierta.

### Estimulación cerebral no invasiva (tDCS)
`EXPERIMENTAL`. La guía ESO la restringe explícitamente al contexto de ensayos de alta calidad.
**Fuera de alcance de este producto.** No se menciona, no se sugiere, no se integra.

### IA generativa y LLMs en afasia
`EXPERIMENTAL`. Existe literatura 2025–2026 emergente y relevante, pero es de prueba de concepto:
reconstrucción de lenguaje afásico con IA generativa, agentes conversacionales para terapia, apoyo a la
expresión escrita, integración de LLM con herramientas AAC. Ninguna base para reclamar beneficio clínico.
> *Reconstructing impaired language using generative AI for people with aphasia.* Sci Rep. 2025. doi:10.1038/s41598-025-24725-x `[TEXTO COMPLETO PENDIENTE — fuente bloqueada por la red]`
> *Preclinical Dialogue Simulation: Evaluating Response Accessibility in Conversational Artificial Intelligence for Aphasia Therapy.* PMID:42340760
> *Integration of a large language model with an augmentative and alternative communication tool for oncological aphasia rehabilitation.* PMC10821375

**Implicación:** podemos construir sobre IA generativa como **decisión de producto**, nunca como
**afirmación clínica**. El material de usuario y de marketing no puede decir que la IA rehabilita.

### AAC en afasia
`SUPPORTED` como estrategia; `INSUFFICIENT` en adherencia.
Entre el **30% y el 50% de los usuarios de AAC abandonan o subutilizan** su sistema. Las personas
tienden a abandonar el sistema recomendado cuando no participaron en la decisión, y son reticentes a
usarlo en público con interlocutores no familiares.
> *Alternative and Augmentative Communication (AAC) for Individuals With Aphasia.* Arch Phys Med Rehabil. 2023.
> Lasker JP, Bedrosian JL. *Promoting acceptance of augmentative and alternative communication by adults with acquired communication disorders.* Augment Altern Commun. 2001;17(3):141-153.

**Implicación de producto:** la adherencia es un requisito de producto, no un extra (§59 acierta).
Y la reticencia al uso público refuerza la decisión aprobada de mover el caso de uso primario a
**pre-composición y asíncrono** en lugar de reparación en vivo frente a terceros.

### Fiabilidad del sí/no — el riesgo R1
`INSUFFICIENT` en la literatura general, pero existe instrumento específico.
Las baterías de afasia de uso general **no informan sobre la fiabilidad de las respuestas del paciente a
preguntas cerradas**. El *Yes/No Questionnaire* (YNQ) fue desarrollado precisamente para esa laguna: 10
preguntas cerradas que distinguen entre respondedores fiables y no fiables.
> Yes/No Questionnaire for Aphasic Patients (YNQ). NCT03257696

**Implicación de producto:** existe un procedimiento clínico al que anclar la pregunta más peligrosa del
diseño. Debe administrarse antes de construir el flujo de confirmación. Si Cristián resulta ser
"respondedor no fiable", **la confirmación binaria deja de ser un mecanismo de seguridad válido** y el
producto debe rediseñarse alrededor de elección forzada entre candidatos y verificación multicanal.

---

## Medición de comunicación funcional

Instrumentos candidatos, con la condición de que el outcome primario sea **externo a la app**:

- **ACOM** — autoinforme de funcionamiento comunicativo, desarrollado bajo teoría de respuesta al ítem,
  con evidencia de validez de contenido, estructura interna, estabilidad y sensibilidad al tratamiento.
  > Hula WD, et al. *The Aphasia Communication Outcome Measure (ACOM): Dimensionality, Item Bank Calibration, and Initial Validation.* J Speech Lang Hear Res. 2015. · y PMID:34261164 (2021)
- **CETI** — escala de efectividad comunicativa valorada por el informante/cuidador; consistente
  internamente, con fiabilidad test-retest e interevaluador aceptables.
  > Lomas J, et al. *The communicative effectiveness index.* J Speech Hear Disord. 1989. PMID:2464719
- **SAQOL-39** — calidad de vida en ACV y afasia a largo plazo.
  > Hilari K, et al.

**Laguna crítica `[PENDIENTE]`:** no se localizó documentación de versiones validadas en español
rioplatense/chileno de ACOM ni CETI. Para la evaluación basal sí existe adaptación española del Test de
Boston (BDAE), con traducciones y validación en España y México, sin confirmación de normalización
chilena. **Esto debe resolverlo el fonoaudiólogo/a; no lo decidimos nosotros.**

---

## Tabla de decisión sobre los módulos propuestos en §31 del master prompt

| Módulo (§31) | Evidencia | Decisión |
|---|---|---|
| Recuperación de palabras / acceso semántico (SFA) | `SUPPORTED` entrenados / `INSUFFICIENT` generalización | **Construir solo con ítems personales derivados de fallos comunicativos reales.** Sin catálogo genérico |
| Acceso fonológico | `PROMISING` | Postergar. Como jerarquía de claves dentro del anterior, no como módulo |
| Script training / conversación | `PROMISING`, mejor señal de generalización | **Primer módulo de rehabilitación tras el MVP** |
| Entrenamiento del interlocutor | `SUPPORTED` para comunicación funcional | **Subir de prioridad.** No es una función de la app del paciente: es contenido para la familia |
| Producción de oraciones / verbos | `PROMISING` | Postergar |
| Comprensión auditiva | `SUPPORTED` como objetivo de terapia | Fuera de alcance del producto: no es nuestro cuello de botella |
| Repetición | `SUPPORTED` como técnica | Solo como andamio dentro de "practicar esto" |
| Lectura | `SUPPORTED` | Postergar; **pero su evaluación es un gate de UI** (ver 03-user-model) |
| Escritura | `SUPPORTED` | Mantener como **modalidad de entrada** en V1, no como módulo terapéutico |
| Reparación de la comunicación | `PROMISING` (vía entrenamiento del interlocutor) | Núcleo del MVP |
| tDCS | `EXPERIMENTAL` | **No construir. No mencionar** |

---

## Lo que la evidencia dice sobre nuestro North Star

La decisión aprobada (ver `00-decision-log`, D-002) reformula el North Star como *asistencia por acto
comunicativo ↓ mientras el volumen y la complejidad de ideas comunicadas ↑*. La evidencia la respalda:

- Big CACTUS muestra que las ganancias se concentran en lo entrenado, sin transferencia automática a
  conversación. Prometer que la app se vuelve innecesaria **no tiene base empírica en afasia crónica**.
- La evidencia de dosis (≥20 h totales, ≥4 días/semana) implica que el uso frecuente y sostenido es el
  vehículo del beneficio. Un KPI que premie el descenso de uso **contradice la evidencia de dosis**.

Es decir: la paradoja del master prompt original era no solo un mal incentivo de producto, sino
clínicamente contraria a lo que sabemos. La reformulación aprobada corrige ambas cosas.

---

## Lagunas pendientes para la Ola 2

1. Texto completo de la guía ESO 2025 y extracción de recomendaciones literales con su nivel GRADE.
2. Texto completo de Sci Rep 2025 sobre reconstrucción de lenguaje con IA generativa: tasas de fidelidad
   y de error, que son nuestro R2.
3. Evidencia sobre **predictores de generalización** (relevancia personal del material, práctica variable,
   entrenamiento en contexto funcional). Es la pregunta que decide si nuestro enfoque es defendible.
4. Mantenimiento tras cese de la práctica.
5. Instrumentos de comunicación funcional validados en español de Chile.
6. Evidencia sobre fatiga en afasia y duración óptima de sesión (sustenta o refuta §38, micro-sesiones).

---

## Qué cambiaría este documento

- Un ECA que demuestre generalización de terapia computarizada a conversación revertiría E2 y
  reabriría la construcción de una biblioteca de ejercicios.
- Evidencia de que la relevancia personal del material predice generalización elevaría toda la mitad
  rehabilitadora del producto de `PROMISING` a fundamento.
- Un resultado de YNQ que muestre a Cristián como respondedor fiable estabiliza R1 y permite conservar
  la confirmación binaria como mecanismo de seguridad.
