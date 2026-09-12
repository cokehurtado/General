# 03 — Modelo de usuario

**Versión:** 0.1 · **Estado:** PARCIALMENTE BLOQUEADO

> Este documento está incompleto **a propósito**. Las casillas marcadas `[BLOQUEADO]` requieren
> información clínica que no tenemos y que **no vamos a inferir**. Rellenarlas con supuestos sería
> exactamente el error que el master prompt prohíbe en §3.

## Lo que sí sabemos

Adulto con afasia adquirida tras ACV, clínicamente confirmada, con rehabilitación neurológica previa
sustancial. Intelectualmente capaz. Usuario intensivo de smartphone, autónomo con el dispositivo.
Dificultad persistente con lenguaje hablado y escrito. Capaz de entender y pensar sobre temas
sofisticados. Frustrado o aburrido por terapia simplista o repetitiva. **Su objetivo primario es
comunicar.**

## El principio que gobierna el diseño

**Afasia ≠ pérdida de inteligencia.** Nunca confundir *dificultad para expresar una idea* con
*dificultad para entenderla o pensarla*. El sistema modela dos ejes independientes:

```
complejidad de CONTENIDO   ──  alta   (ej. 9/10: consecuencias macroeconómicas de la IA)
complejidad de LENGUAJE    ──  ajustable (ej. 4/10)
```

**Regla:** mantener la idea compleja, andamiar el lenguaje. Nunca achicar su mundo intelectual porque
expresarlo sea difícil.

### El error simétrico, que el master prompt no cubre

Existe el error opuesto y también daña: **asumir comprensión lectora preservada** y llenar la interfaz de
texto adulto denso. La alexia acompaña con frecuencia a la afasia. §27 obliga a evaluar comprensión por
separado de la producción; **esa regla debe aplicarse también a nuestra propia interfaz**, no solo al
contenido terapéutico. Media UI de §9–§12 depende de leer.

---

## Determinantes de diseño pendientes

Reportados idealmente por su fonoaudiólogo/a. **No inferir. No estimar. No asumir.**

### Bloque crítico — decide si el producto es viable

| # | Pregunta | Por qué decide algo | Estado |
|---|---|---|---|
| 1 | **¿Es fiable su respuesta sí/no?** ¿Y ante dos opciones? | Toda la confirmación del mensaje depende de esto. Instrumento disponible: YNQ (ver `01-clinical-evidence`) | `[BLOQUEADO]` |
| 2 | **Comprensión lectora**: ¿palabra, frase, texto? | Si hay alexia asociada, la UI basada en texto es inservible y hay que rediseñarla sobre audio e iconos | `[BLOQUEADO]` |
| 3 | Comprensión auditiva: ¿palabra, frase, párrafo? | Decide si el sistema puede hablarle o debe mostrarle | `[BLOQUEADO]` |

### Bloque de modalidad

| # | Pregunta | Implicación | Estado |
|---|---|---|---|
| 4 | ¿Perfil predominante no fluente/agramático o fluente/anómico? | Prioriza voz vs. selección de conceptos como entrada principal | `[BLOQUEADO]` |
| 5 | Escritura: ¿acceso a la primera letra? ¿teclado útil? | Decide si el teclado nativo es una vía real o decorativa | `[BLOQUEADO]` |
| 6 | ¿Apraxia del habla asociada? | Cambia por completo el módulo de repetición y práctica | `[BLOQUEADO]` |

### Bloque físico — restricciones duras de la UI móvil

| # | Pregunta | Implicación | Estado |
|---|---|---|---|
| 7 | Hemiparesia: ¿qué lado? ¿mano dominante? | Uso a una mano no es una comodidad, es un requisito. Y puede ser con la mano no dominante | `[BLOQUEADO]` |
| 8 | ¿Déficit de campo visual o negligencia? | Con hemianopsia izquierda, **los botones a la izquierda no existen**. Reubica toda la navegación | `[BLOQUEADO]` |
| 9 | Audición | Decide el peso del canal auditivo | `[BLOQUEADO]` |

### Bloque de contexto

| # | Pregunta | Estado |
|---|---|---|
| 10 | Tiempo desde el ACV | `[BLOQUEADO]` |
| 11 | ¿Terapia activa? ¿El/la fonoaudiólogo/a participaría como co-diseñador? | **Aprobado en principio, factibilidad por confirmar** |
| 12 | Idiomas: ¿solo español? ¿variante chilena? ¿usa inglés? | `[BLOQUEADO]` |
| 13 | Sus 4–5 interlocutores principales y por qué canal | `[BLOQUEADO]` |
| 14 | Qué apps usa hoy, cuáles abandonó y por qué | `[BLOQUEADO]` |
| 15 | Modelo de iPhone y versión de iOS | `[BLOQUEADO]` |
| 16 | Residencia y jurisdicción de datos | `[BLOQUEADO]` — bloquea también `15-privacy-security` |
| 17 | Capacidad y forma de consentimiento; quién lo acompaña | `[BLOQUEADO]` |
| 18 | Titularidad de las grabaciones históricas | `[BLOQUEADO]` — bloquea `07-personal-voice` |

### Material de diseño — lo más valioso que pueden traernos

| # | Petición | Estado |
|---|---|---|
| 19 | **10–20 cosas concretas que quiso decir esta semana y no pudo**, con contexto | `[PENDIENTE]` |

Esto es el corpus de diseño del MVP. Sin él, estamos diseñando para un usuario imaginario.

---

## Requisitos de accesibilidad que ya son firmes

Independientes de las respuestas anteriores: `[ENGINEERING DECISION]`

- Texto grande y extra grande; alto contraste; movimiento reducido.
- Objetivos táctiles grandes; uso a una mano; alcance con el pulgar.
- Tiempo de respuesta configurable; velocidad de habla configurable; repetición de audio.
- Respeto de los ajustes de accesibilidad del sistema operativo.
- **El silencio prolongado NO termina automáticamente la grabación de voz.** La afasia requiere más
  tiempo de respuesta, y cortarle la frase es el fallo más humillante que puede cometer el producto.
- Una acción primaria por pantalla siempre que sea posible.
- Objetivo de interacción: `abrir app → un toque → empezar a comunicar`.

## Lo que no vamos a hacer

- No inferir subtipo, severidad, pronóstico, plazo de recuperación ni funciones preservadas/afectadas.
- No usar el rendimiento en la app como sustituto de evaluación clínica.
- No tratar el desinterés como incapacidad cognitiva.

## Qué cambiaría este documento

Cualquier respuesta del bloque crítico. La pregunta 1 en particular puede obligar a rediseñar el flujo
central del producto antes de escribir una línea de código.
