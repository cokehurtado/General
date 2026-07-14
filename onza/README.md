# ONZA — El mercado financiero del lujo en Latinoamérica

> **Bloomberg + Nasdaq + Chrono24 para activos de lujo.**
> Compra, vende, valora e invierte en relojes, carteras y joyería con datos de mercado en tiempo real.

**HQ y mercado inicial:** Panamá 🇵🇦 · **Ambición:** el marketplace + terminal de datos de lujo #1 de LatAm.

---

## Qué es este repositorio

Este es el paquete fundacional de ONZA: tesis, análisis crítico, arquitectura técnica, diseño de agentes de IA, motor financiero, modelo de negocio, estrategia de expansión, roadmap a 3 años y un backlog ejecutable por Claude Code, módulo por módulo.

## La tesis en 5 líneas

1. Los artículos de lujo se comportan como instrumentos financieros: tienen oferta, demanda, liquidez, volatilidad, spread y profundidad — pero **no existe un precio de referencia único** y el mercado LatAm es el más fragmentado del mundo (WhatsApp, Instagram, dealers, boutiques, Mercado Libre).
2. El que construye la **cinta de precios (price tape)** del lujo en LatAm se convierte en la infraestructura sobre la que todos los demás operan.
3. La secuencia ganadora es **datos → confianza → liquidez**: primero el "Bloomberg" (terminal de precios, sin cold-start), después el "escrow + autenticación" (la confianza que WhatsApp no puede dar), y al final el "Nasdaq" (vault con custodia: el activo entra una vez, se autentica una vez, y cambia de dueño N veces sin moverse).
4. Panamá no es el mercado — es el **hub**: dólar, Zona Libre de Colón, hub aéreo de las Américas, banca, turismo de compras. La demanda es regional desde el día 1.
5. El moat no es el software: son los **datos transaccionales propios de LatAm**, la **red física de autenticación/custodia** y el **rail de confianza (escrow + KYC/AML)** — tres cosas que un competidor global no replica sin años y capital en la región.

## Índice de documentos

| # | Documento | Contenido |
|---|-----------|-----------|
| 01 | [Tesis y visión](docs/01-tesis-y-vision.md) | Problema, hipótesis, producto, por qué ahora, por qué Panamá |
| 02 | [Análisis crítico](docs/02-analisis-critico.md) | Riesgos, debilidades, competencia real, moats, cómo ser 10x |
| 03 | [Arquitectura](docs/03-arquitectura.md) | Sistema completo, diagramas, estructura del monorepo |
| 04 | [Stack tecnológico](docs/04-stack.md) | Decisiones de stack justificadas, capa por capa |
| 05 | [Datos y scraping](docs/05-datos-y-scraping.md) | Motor de ingesta distribuido, ETL, versionado, matching |
| 06 | [Agentes de IA](docs/06-agentes-ia.md) | Los 8 agentes: matching, pricing, arbitraje, autenticación, antifraude, negociación, inversión, market-making |
| 07 | [Motor financiero](docs/07-motor-financiero.md) | Fair value, métricas Bloomberg-style, motor de arbitraje, índice ONZA 50 |
| 08 | [Modelo de negocio](docs/08-modelo-de-negocio.md) | 12 líneas de ingreso, unit economics, pricing |
| 09 | [Expansión](docs/09-expansion.md) | Panamá → Centroamérica → México/Colombia |
| 10 | [Roadmap 3 años](docs/10-roadmap.md) | 4 fases, milestones, KPIs por fase |
| 11 | [Backlog ejecutable](docs/11-backlog.md) | Epics, user stories, prioridades, dependencias, estimaciones para Claude Code |

## Cómo usar este repo con Claude Code

Cada epic del [backlog](docs/11-backlog.md) está escrito como una unidad de trabajo autocontenida: contexto, criterios de aceptación, dependencias y módulo del monorepo donde vive. El flujo:

```
1. Elegir el siguiente epic desbloqueado del backlog (respetando dependencias)
2. Abrir una sesión de Claude Code apuntando al módulo correspondiente (ver docs/03-arquitectura.md)
3. Pegar el epic + sus user stories como prompt
4. Revisar el PR, mergear, marcar el epic como completado
```

La estructura de carpetas objetivo del monorepo está en [docs/03-arquitectura.md](docs/03-arquitectura.md#estructura-del-monorepo).
