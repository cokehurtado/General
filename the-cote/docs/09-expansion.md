# 09 · Estrategia de expansión

> Tesis geográfica (doc 01): Panamá no es el mercado, es el hub. La expansión no es "abrir país por país un marketplace local"; es **extender el alcance de demanda sobre una única operación física centralizada en Panamá**, y solo regionalizar operaciones cuando el volumen de un país lo justifique.

## El modelo hub-and-spoke

```
                 [ HUB: Panamá ]
        Vault · Autenticación · Escrow · Compliance · Datos
                        │
     ┌──────────┬───────┼───────┬──────────┐
   Costa Rica  Guate  El Salv  Honduras  Rep. Dom.  ...  (spokes de demanda)
                        │
              [ México · Colombia ]  (spokes que eventualmente exigen operación local)
```

- **Spoke = demanda + logística.** Un país nuevo se "abre" habilitando: pagos locales, envío asegurado hacia/desde Panamá, KYC de ese país, marketing en español localizado. La autenticación y el escrow siguen en Panamá.
- **Regionalización de operaciones** (segundo laboratorio de autenticación, cuenta escrow local) solo cuando un país supera un umbral de GMV que amortice el costo fijo. Candidatos: México y Colombia.

## Secuencia y por qué

| Ola | Mercados | Razón / gatillo |
|---|---|---|
| **0. Hub** | Panamá | Dólar, ZLC, hub aéreo, banca. Se construye todo aquí |
| **1. Nearshore dolarizado / alto ingreso** | Costa Rica, Rep. Dominicana, Panamá | CR y RD: alto ingreso relativo, turismo, conectividad aérea directa con PTY. RD además es puerta al Caribe |
| **2. Triángulo Norte** | Guatemala, El Salvador, Honduras | Guatemala: la economía más grande de CA, élite con apetito de lujo. El Salvador: bancarizado en USD, pro-tech. Nicaragua al final (mercado y riesgo) |
| **3. Grandes mercados** | México, Colombia | El verdadero TAM. Requieren operación local, competencia mayor, y el playbook ya probado. Aquí se decide el destino unicornio |
| **4. Frontera** | Perú, Chile, Brasil (portugués) | Solo tras dominar México/Colombia; Brasil es otro idioma y otro juego |

## Playbook de entrada por spoke (repetible)

1. **Datos primero (Capa 1).** Se enciende el terminal para ese país sin operación: fair value, alertas, screener con fuentes globales + regionales. Cero costo marginal físico, empieza a construir audiencia y a medir demanda real (¿cuánta gente consulta desde ese país?).
2. **Oferta cautiva de dealers.** Onboarding manual de 10-20 dealers del país (mismo give-to-get). Ellos traen inventario y credibilidad local.
3. **Primeras transacciones asistidas.** Concierge humano para las primeras N transacciones (curado, no self-serve) — genera los primeros cierres reales y casos de confianza.
4. **Habilitar rails locales.** Pagos, KYC, logística del país. Abrir self-serve.
5. **Escalar demanda.** Marketing de contenido (el índice, reportes de mercado), referidos, partnerships con boutiques/relojerías locales.

## Adaptaciones por país (no es copy-paste)

- **Pagos:** cada país tiene su rail (Yappy en PA, SINPE en CR, PSE en Colombia, SPEI en México). El módulo `escrow` usa adaptadores; agregar país = agregar adaptador.
- **KYC/AML:** documentos y listas de sanción por país (el proveedor tier-1 cubre la mayoría; reglas locales encima).
- **Aduanas y tributación:** el mayor dolor operativo. La estructura de zona franca en Panamá (reexportación) es precisamente lo que evita nacionalizar cada pieza. Asesoría fiscal por corredor comercial es un workstream permanente.
- **Idioma/cultura de marca:** español localizado; Brasil (portugués) es un rediseño, no una traducción.

## Riesgos de expansión y mitigación

- **Diseconomías de operar 7 países chicos:** por eso hub-and-spoke — una sola operación física, N mercados de demanda. No se abre operación local hasta que el GMV lo pague.
- **Competencia despierta en México/Colombia:** entrar tarde y bien (con datos, marca y confianza ya probadas en CA) supera entrar temprano y frágil. CA es el terreno de práctica donde los errores son baratos.
- **Concentración logística en PTY:** un punto único de falla. Mitigación de Fase 3: segundo hub (probablemente México) cuando el volumen justifique redundancia.

## Métrica de "listo para el siguiente spoke"

No se abre el país N+1 hasta que el país N muestre: liquidez sana (tiempo a venta bajando), contribución por transacción positiva, y demanda orgánica del terminal por encima de umbral. Disciplina > banderas en el mapa.
