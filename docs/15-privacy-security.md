# 15 — Privacidad y seguridad

**Versión:** 0.1 · **Estado:** gate — debe cerrarse antes de recolectar el primer dato

> Este documento es un **gate**: ninguna grabación, ninguna transcripción y ningún archivo de voz se
> recolecta antes de que sus decisiones estén tomadas y el consentimiento firmado.

## La corrección de jurisdicción

El master prompt indicaba "GDPR-first". **Si Cristián reside en Chile, el marco aplicable no es el GDPR
sino la Ley 21.719**, publicada el 13 de diciembre de 2024, que regula el tratamiento de datos personales
y crea la Agencia de Protección de Datos Personales, **con entrada en plena vigencia el 1 de diciembre
de 2026**.
> Ley 21.719, Biblioteca del Congreso Nacional de Chile — bcn.cl/leychile (idNorma 1209272)

Tres consecuencias inmediatas y concretas:

**1. La voz es dato biométrico, y por tanto sensible.** La ley enumera como datos sensibles, entre otros,
los relativos a la salud, el perfil biológico humano y **los datos biométricos** — huella, iris, rostro y
**voz**. El tratamiento de datos biométricos exige consentimiento e información previa sobre el sistema
utilizado, la finalidad, el periodo de uso y cómo ejercer derechos.

**2. El consentimiento para datos sensibles debe ser explícito y otorgado por separado.** El titular debe
saber exactamente qué datos se tratarán y puede retirarlo en cualquier momento sin penalización. No sirve
un consentimiento general de términos y condiciones.

**3. La fecha importa para la planificación.** A 12 de septiembre de 2026 quedan menos de tres meses para
la plena vigencia. Cualquier recolección que empiece ahora debe diseñarse ya bajo el régimen final, no
adaptarse después. `[ENGINEERING DECISION]`

`[PENDIENTE — BLOQUEANTE]` Confirmar residencia de Cristián y jurisdicción de almacenamiento. Si hay
componente europeo, se aplica además el GDPR (datos de salud y biométricos = art. 9, categorías
especiales). **El piso de diseño es el más estricto de los marcos aplicables**; lo que no se hace es
asumir cuál es sin verificarlo.

---

## Clasificación de datos

| Categoría | Ejemplos | Tratamiento |
|---|---|---|
| **Biométrico sensible** | Grabaciones fuente de la voz pre-ACV, modelo de Personal Voice, audio de sus intentos de habla | Máxima protección. Consentimiento explícito y separado. Cifrado. Acceso auditado. Borrado verificable |
| **Salud sensible** | Perfil de lenguaje, rendimiento, historial de fallos comunicativos | Consentimiento explícito y separado. Nunca expuesto a terceros sin decisión suya |
| **Comunicación privada** | Mensajes reconstruidos, fragmentos, historial, fotos | **Local-first y efímero por defecto** (ver abajo) |
| **Terceros** | Voces y rostros de otras personas en grabaciones y fotos | No se procesa, no se conserva, no se sube |
| **Operacional** | Métricas de uso agregadas, latencias, errores | Minimizado, seudonimizado |

---

## La tensión central: el motor quiere lo que el usuario no querrá dar

El motor adaptativo (§36) y la cola de práctica personal (§35) funcionan mejor cuanto más completo sea el
registro de su vida comunicativa: qué le dijo a su mujer, qué no logró decirle a su hijo. Eso es
exactamente lo que una persona adulta no quiere entregar.

Y el riesgo no es solo legal: **si lo percibe como vigilancia, deja de usarlo**, y un producto que no se
usa es un producto fracasado (riesgo R10). La privacidad aquí no es cumplimiento, es adherencia.

### Decisiones de diseño `[PRODUCT HYPOTHESIS]`

1. **Local-first y efímero por defecto.** Un intento de comunicación se procesa y se descarta. No se
   guarda salvo acción explícita.
2. **"Guardar esto" es por mensaje**, nunca global, nunca por defecto activado.
3. **Nunca se graba ni conserva audio de terceros.** Si el micrófono capta a otra persona, ese audio no
   persiste.
4. **La familia no accede al contenido.** Pueden aportar a Mi Mundo (personas, lugares, vocabulario,
   intereses) y reportar comunicación del mundo real; **no pueden leer sus mensajes ni su historial**.
   §42 debe reescribirse con esta restricción.
5. **Sin perfilado publicitario, sin analítica de terceros, sin SDKs de terceros en el cliente.** Ninguno.
6. Antes de cada envío a un proveedor de IA se aplica **minimización**: se envía el fragmento necesario,
   no el historial completo.

---

## Requisitos técnicos

- Cifrado en tránsito y en reposo; almacenamiento local en el enclave seguro del dispositivo.
- Autenticación robusta; RBAC estricto si alguna vez existe rol clínico o familiar.
- Registro de auditoría sobre todo acceso a datos biométricos y de salud.
- Exportación y **borrado verificable** a petición, incluidos modelo de voz y fuentes.
- Política de retención explícita y con fecha, por categoría.
- Contratos con proveedores de IA/TTS/ASR que prohíban el entrenamiento con sus datos y fijen retención cero
  o mínima documentada.
- Evaluación de impacto en protección de datos antes de la primera recolección.

`[PENDIENTE]` Región de almacenamiento del backend. Si se usa Supabase, la elección de región deja de ser
un detalle de latencia y pasa a ser una decisión legal.

---

## Consentimiento accesible para afasia

El consentimiento estándar es un texto denso. Para una persona con afasia, **un consentimiento que no
puede leer no es un consentimiento informado**. Requisitos:

- Formato adaptado: frases cortas, apoyo visual, una idea por pantalla, lectura en voz alta disponible.
- Verificación de comprensión por elección forzada, no por sí/no (ver riesgo R1 en `20-risk-register`).
- Apoyo a la toma de decisiones con una persona de confianza presente, **sin sustituir su voluntad**.
- Revocable en cualquier momento, sin penalización y sin fricción.
- Consentimiento **separado** para: (a) uso de la app, (b) almacenamiento de comunicaciones,
  (c) archivo de voz y Personal Voice, (d) cualquier uso con fines de investigación.

---

## Qué cambiaría este documento

- La confirmación de jurisdicción puede añadir obligaciones (GDPR) o precisar plazos (Ley 21.719).
- Si el fonoaudiólogo/a se incorpora y hay historia clínica de por medio, aparece regulación sanitaria
  adicional y la figura de responsable/encargado del tratamiento cambia.
- Si en algún momento el producto se ofrece a más de un usuario, deja de ser un proyecto personal y pasa
  a requerir estructura formal de responsable de tratamiento.
