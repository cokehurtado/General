# 16 — Seguridad clínica

**Versión:** 0.1 · **Estado:** gate

## Qué es y qué no es este producto

**No es** un sistema diagnóstico. **No es** un pronóstico neurológico. **No es** un sustituto de la
terapia fonoaudiológica. **No altera** tratamiento ni medicación.

Es un asistente de comunicación con un componente de práctica personalizada, que **complementa** la
rehabilitación profesional.

## Límites duros de la IA

La IA **puede**: reconstruir intención, generar aclaraciones, proveer andamiaje, sostener conversación,
personalizar práctica, adaptar contenido, identificar patrones de uso.

La IA **no puede, y el sistema debe impedirlo por diseño**:

1. Diagnosticar afasia ni ningún subtipo.
2. Predecir recuperación o plazos.
3. Inferir un nuevo evento neurológico a partir del rendimiento en la app.
4. Recomendar, modificar o comentar tratamiento o medicación.
5. Hablar con Personal Voice contenido no confirmado por el usuario.
6. Emitir un juicio de corrección sobre su habla que él pueda leer como veredicto clínico.

## Escalamiento por síntomas neurológicos nuevos

Si el usuario o la familia reportan síntomas neurológicos súbitos o nuevos, el flujo normal se
**interrumpe** y se recomienda evaluación médica urgente. Sin diagnóstico, sin tranquilización, sin
demora, sin continuar la sesión.

`[ENGINEERING DECISION]` Esta ruta es una interrupción explícita del flujo, no un mensaje en un pie de
página. Se diseña y se prueba como cualquier otra función crítica.

**Lo que el sistema no hace:** detectar deterioro por sí mismo y alarmar. Un descenso de rendimiento en
la app tiene decenas de explicaciones benignas — fatiga, aburrimiento, un mal día, un cambio de contexto.
Convertir eso en una alerta de salud es generar ansiedad con falsa precisión y es un daño real.

## Riesgo específico de este producto: el mensaje falsificado

El daño más probable de este sistema no es médico: es **poner en su boca algo que no quiso decir**.
Un mensaje erróneo aceptado por confirmación poco fiable y enviado a un tercero puede tener consecuencias
sociales, familiares o económicas reales.

Mitigaciones obligatorias, todas antes de cualquier salida:
1. Elección forzada entre 2–3 candidatos + "ninguna", en lugar de verificación binaria (riesgo R1).
2. Escucharlo en TTS antes de enviar.
3. "ESO NO ERA" permanentemente visible, en toda pantalla, sin jerarquía visual inferior a la acción positiva.
4. **Revocación posterior al envío**: poder decir "ese mensaje no era mío" y que la app genere la corrección.
5. Nunca diseñar la interacción de modo que "sí" sea el camino de menor esfuerzo.
6. Registro de mensajes comunicados que él haya marcado luego como erróneos — es nuestra métrica de daño,
   y se vigila como tal.

## Medición sin falsa precisión clínica

- **No se muestra un score clínico.** No se colapsa la información funcional en un número sin explicación.
- **No se puntúa automáticamente la corrección de su habla en V1.** Con una tasa de error de palabra en
  ASR sobre habla afásica en torno al 37% (ver `01-clinical-evidence`, E5), cualquier "correcto/incorrecto"
  automático es poco fiable y potencialmente humillante. En V1: autoinforme ("lo dije bien") y éxito
  comunicativo.
- **El perfil de lenguaje es configurable por el clínico, no inferido por la IA.** Es un conjunto de
  objetivos terapéuticos, no un diagnóstico.
- El progreso se comunica en lenguaje significativo, no en porcentajes con decimales.

## Frontera con el profesional

Lo que queda **siempre** bajo control clínico, nunca decidido por el sistema:
subtipo y severidad de la afasia · pronóstico · objetivos terapéuticos · estrategia de claves ·
interpretación de comprensión vs. producción · decisión de intensificar o suspender la práctica ·
interpretación de cualquier retroceso.

`[PENDIENTE]` La incorporación del fonoaudiólogo/a tratante está aprobada en principio y **sujeta a
confirmación de factibilidad**. Hasta que se confirme, ninguna función que dependa de configuración
clínica entra en el alcance, y el producto opera únicamente como asistente de comunicación.

## Qué cambiaría este documento

- Si Cristián resulta ser respondedor no fiable al sí/no, las mitigaciones del mensaje falsificado pasan
  de recomendadas a condición de existencia del producto.
- La incorporación de un clínico permite abrir el perfil de lenguaje configurable, hoy fuera de alcance.
