# 07 — Personal Voice: archivo de voz, proveedores, consentimiento y viabilidad

**Versión:** 0.1 · **Estado:** protocolo de auditoría definido · **GO/NO-GO: PENDIENTE**

> **Nada de esto se ha ejecutado todavía.** No se ha auditado ningún archivo, no se ha subido audio a
> ningún proveedor, no se ha entrenado ningún modelo. Este documento define **cómo** se evaluaría.

## Posición del proyecto

Personal Voice queda **en la arquitectura desde el día uno y fuera del MVP**. El sistema hablará con TTS
estándar en V1, detrás de una abstracción `TextToSpeechProvider`, de modo que sustituirlo por la voz
autorizada de Cristián no exija rehacer nada. `[ENGINEERING DECISION]`

Y nunca es punto único de fallo. Jerarquía de salida obligatoria:
`Personal Voice (si autorizada y disponible) → TTS estándar de alta calidad → texto en pantalla`.
La comunicación debe completarse aunque caiga la red, el proveedor o el modelo.

---

## Hallazgo que puede bloquear la función (riesgo R8)

**Los proveedores serios de clonación profesional exigen verificación de identidad mediante una grabación
hablada.** En ElevenLabs, todo Professional Voice Clone requiere un proceso de verificación para
confirmar que la voz es del solicitante, idealmente con el mismo equipo y con un tono y entrega similares
a las muestras; y la política establece que **solo se puede clonar la propia voz, no la de otra persona
aun con su consentimiento**.
> ElevenLabs — *Can I create a Professional Voice Clone of someone else's voice?* y *Professional Voice Cloning* (documentación del producto)

Cristián probablemente **no puede leer en voz alta una frase de verificación**. Eso convierte la
verificación en un bloqueador de proceso, no de tecnología.

**Existe una vía posible, pero no está confirmada para su caso.** ElevenLabs opera un *Impact Program*
que da licencias de voz gratuitas a personas con **pérdida permanente del habla causada por una
enfermedad diagnosticada**, mayores de 18 años, con solicitud directa del paciente o de su fonoaudiólogo,
terapeuta ocupacional o especialista en AAC; los clínicos pueden solicitar licencia propia para guiar el
proceso. El programa nació para ELA/EMN y se ha extendido a atrofia multisistémica y cáncer oral a través
de organizaciones asociadas. Existe además un *Impact Voice Lab* con voluntarios que limpian grabaciones
de archivo para hacer posible la restauración de voz.
> ElevenLabs — *Impact Program*, *Apply for free Impact voices directly on ElevenLabs*, *Impact Voice Lab*

**Zona gris a resolver por escrito, antes que nada:** la afasia **no es pérdida de la producción de voz**.
Cristián probablemente conserva fonación y articulación; lo que ha perdido es el acceso al lenguaje. No
está claro que encaje en la definición de "pérdida permanente del habla" del programa, ni que las
organizaciones asociadas actuales cubran ACV/afasia. Es exactamente la pregunta que hay que hacer antes
de gastar una hora en auditar archivos.

### Paso 0 — Consultas bloqueantes (1 semana, coste ~0)

1. A 3+ proveedores, por escrito: *¿aceptan una vía de verificación alternativa (atestación legal,
   consentimiento notarial, verificación mediada por clínico) cuando la persona conserva la voz pero no
   puede producir bajo demanda la frase de verificación por una discapacidad adquirida del lenguaje?*
2. A ElevenLabs específicamente: *¿la afasia post-ACV sin pérdida de fonación califica para el Impact Program?*
3. Titularidad de las grabaciones históricas: entrevistas y apariciones públicas pueden pertenecer a
   canales o productoras. Inventario de derechos **antes** de procesar los archivos.
4. Terceros que aparecen en las mismas grabaciones: su voz no se procesa, no se conserva y no se sube.

**Si las tres primeras respuestas son negativas, Personal Voice se congela y se documenta como bloqueada.**
No se audita el archivo. No se contrata. No se promete.

---

## VoiceArchive — protocolo de auditoría (solo medición)

Pipeline conceptual, ejecutado **en local**, sin que ningún archivo salga del entorno controlado:

```
fuente → extracción de audio → diarización → identificación del hablante objetivo
       → segmentación → scoring de calidad → cobertura fonética → informe GO/NO-GO
```

### Metadatos por fuente
origen · fecha (**debe ser pre-ACV**) · contenedor · códec · bitrate · frecuencia de muestreo · canales ·
duración total · titularidad · si es recodificación de una recodificación.

### Criterios de calidad por segmento
*Umbrales de trabajo; se ajustan al proveedor que sobreviva al Paso 0.*

| Criterio | Umbral |
|---|---|
| Hablante único, sin solapamiento | Obligatorio — se descarta todo segmento con dos voces |
| Música de fondo / jingles / cortinas | Descarte |
| Relación señal-ruido | Objetivo ≥ 20 dB |
| Reverberación de sala marcada | Descarte |
| Frecuencia de muestreo | ≥ 16 kHz; preferible 44.1 / 48 kHz |
| Audio telefónico de banda estrecha, MP3 de bitrate bajo | Descarte o marcado como último recurso |
| Procesamiento broadcast agresivo (compresión de rango, limitador, de-esser) | Descarte — altera el timbre que queremos preservar |
| Duración de segmento útil | ≥ 3 s; ideal 5–15 s de habla continua |

### Volumen total
- **Escenario alta fidelidad:** orden de 30–60 min de audio limpio.
- **Escenario "instant cloning":** 1–3 min bastan, con pérdida notable de identidad.
El informe debe reportar **ambos escenarios**, porque determinan si el resultado se parece a él o solo
suena humano.

Como referencia del orden de magnitud del enfoque tradicional: la banca de voz clásica requiere grabar
entre 350 y 1.600 frases para construir una voz sintética personalizada.
> RCSLT — *Voice banking: clinical information for SLTs*

### Diversidad fonética y prosódica
Lo que más se olvida y más determina el resultado:
- Cobertura del inventario fonémico del español, con atención a fonemas de baja frecuencia.
- **Variedad prosódica**: declarativas, interrogativas, énfasis, risa, pausas. Un archivo compuesto solo
  de conferencias produce una voz que solo sabe dar conferencias.
- Variedad de velocidad y de registro (formal / coloquial).
- Número de *tokens* distintos, no solo minutos totales.

### Español y acento — criterio de descarte
Requisito explícito: **preservar su variante latinoamericana/chilena.** La mayoría de los modelos están
sesgados hacia español peninsular o "neutro". Se evalúa empíricamente con una muestra mínima autorizada.
Una voz que suena como él pero **habla como un locutor de doblaje no es su voz**, y no pasa el gate.

---

## Comparativa de proveedores — criterios (tabla a completar tras el Paso 0)

Calidad de voz · audio fuente requerido · **soporte de audio histórico/de archivo** · calidad en español ·
preservación de acento latinoamericano · similitud de identidad · latencia · streaming · calidad de API ·
idoneidad móvil · coste · privacidad · retención de datos · **política de entrenamiento con datos del
cliente** · requisitos de consentimiento · implicaciones legales · **borrado verificable del modelo** ·
términos comerciales.

`[ENGINEERING DECISION]` No se acopla la arquitectura a ningún proveedor: `PersonalVoiceProvider` es una
abstracción y la comparativa precede a la elección.

---

## Reacción humana antes que inversión técnica (riesgo R7)

**Antes de cualquier compromiso técnico o económico:** escuchar con él, acompañado, una grabación
original suya (no sintética) y después una muestra sintética corta. Y preguntar.

Dos riesgos que la literatura de banca de voz no cubre bien para este caso:
- **Duelo.** Escuchar la voz que perdió puede ser doloroso, no restaurador.
- **Asimetría identitaria.** La voz sintética suena fluida y articulada; su habla actual no. Puede
  ensanchar la brecha que siente en lugar de cerrarla. Este riesgo es específico de la afasia: en ELA,
  donde nació la banca de voz, el lenguaje está intacto y solo falla el aparato fonador. **No somos ese
  caso, y no podemos importar su evidencia sin más.**

Si la reacción es negativa, se detiene. No hay métrica de producto que justifique lo contrario.

---

## Reglas no negociables

1. Personal Voice **solo pronuncia contenido confirmado por el usuario**. El sistema nunca genera y habla
   autónomamente una afirmación con su voz.
2. Personal Voice **nunca puede saltarse la confirmación del mensaje**.
3. Audio fuente y modelo se tratan como **dato biométrico sensible** (ver `15-privacy-security`).
4. Prohibición contractual de usar su voz para entrenar modelos de propósito general.
5. Borrado verificable del modelo y de las fuentes, a petición, en cualquier momento.
6. Acceso restringido y auditado.
7. Consentimiento informado en **formato accesible para afasia**, con apoyo a la toma de decisiones,
   revocable sin penalización.

---

## Separar dos cosas que el master prompt ya separa bien (§18)

| Valor comunicativo y de identidad | Afirmación terapéutica |
|---|---|
| Plausible y potencialmente muy alto: agencia, identidad, aceptación del AAC, personalización | **Sin evidencia.** No se afirma que Personal Voice mejore la recuperación de la afasia |

No se hará ninguna afirmación de beneficio rehabilitador de la voz personalizada sin evidencia que la
respalde. Ni en el producto, ni en materiales, ni ante la familia.

---

## Qué cambiaría este documento

- Una confirmación escrita de que existe vía de verificación alternativa desbloquea el Paso 1 y cambia
  la prioridad de toda la función.
- Un archivo con menos de ~3 minutos de audio limpio de hablante único degrada el objetivo de "su voz" a
  "una voz personalizada aproximada", y eso hay que decírselo antes, no después.
- Una reacción emocional negativa a la muestra cancela la función, independientemente de la viabilidad
  técnica.
