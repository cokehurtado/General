# 20 — Registro de riesgos

**Estado a:** 2026-09-12 · Ordenados por riesgo. Cada uno con su prueba de falsación más barata.

| ID | Riesgo | Estado | Evidencia acumulada |
|---|---|---|---|
| R1 | La confirmación sí/no no es un mecanismo de seguridad fiable | **ABIERTO — crítico** | Las baterías de afasia de uso general no informan sobre fiabilidad de respuestas a preguntas cerradas; existe instrumento específico (YNQ, NCT03257696). El sesgo de aquiescencia es máximo justamente en formato sí/no |
| R2 | La IA no reconstruye intención con fidelidad suficiente | **ABIERTO** | Literatura 2025–2026 de prueba de concepto (`Sci Rep` 2025, doi:10.1038/s41598-025-24725-x) — texto completo pendiente |
| R3 | La escena de reparación en vivo (§58) no es alcanzable | **MITIGADO** | Decisión D-001 aprobada: caso de uso primario movido a pre-composición y asíncrono |
| R4 | El ASR comercial falla sobre habla afásica | **CONFIRMADO** | WER ~37% sobre habla afásica natural (arXiv:2408.14082); variación amplia por severidad. Mitigación: D-005 |
| R5 | Las mejoras en la app no se transfieren a comunicación funcional | **CONFIRMADO en su forma fuerte** | Big CACTUS: mejora en palabras entrenadas, **sin mejora en conversación** (Lancet Neurol 2019). Mitigación: D-004 |
| R6 | No usará el producto espontáneamente | **ABIERTO** | 30–50% de usuarios de AAC abandonan o subutilizan; reticencia al uso en público con desconocidos |
| R7 | Personal Voice con su voz pre-ACV puede no ser deseable (duelo, asimetría identitaria) | **ABIERTO** | Sin evidencia en afasia; la banca de voz nace en ELA, donde el lenguaje está intacto — no importable |
| R8 | La verificación de identidad del proveedor bloquea Personal Voice | **CONFIRMADO como riesgo real, con vía posible** | ElevenLabs exige verificación hablada y solo permite clonar la voz propia; existe *Impact Program* para pérdida permanente del habla por enfermedad diagnosticada, cuya cobertura de afasia post-ACV **está por confirmar** |
| R9 | "La app debe volverse menos necesaria" es un KPI perverso | **RESUELTO** | Decisión D-002 aprobada. Además, contradice la evidencia de dosis (ESO 2025, RELEASE 2022) |
| R10 | Registrar toda su comunicación es inaceptable y suprime el uso | **ABIERTO — mitigación diseñada** | Ley 21.719 clasifica voz como dato biométrico sensible con consentimiento explícito y separado. Mitigación: local-first y efímero por defecto (`15-privacy-security`) |
| R11 | Jurisdicción de datos mal asumida | **ABIERTO** | No es GDPR por defecto: Ley 21.719 (Chile), plena vigencia 1-dic-2026 — menos de tres meses |
| R12 | Inferir aburrimiento vs. fatiga desde señales conductuales es falsa precisión | **ABIERTO** | Sin evidencia localizada que respalde la inferencia. Mitigación propuesta: preguntárselo |
| R13 | Sobreasumir comprensión lectora preservada y llenar la UI de texto | **ABIERTO** | La alexia acompaña con frecuencia a la afasia. Bloquea media UI de §9–§12 |
| R14 | Viabilidad más allá de n=1: encaje persona-producto ≠ encaje producto-mercado | **ABIERTO** | Fuera de alcance de la Ola 1 |

## Los tres que pueden matar el proyecto esta semana, sin escribir código

1. **R1** — una sesión con el clínico y el protocolo YNQ.
2. **R8** — tres correos a proveedores.
3. **R11** — una pregunta sobre residencia.
