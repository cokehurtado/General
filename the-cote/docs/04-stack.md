# 04 · Stack tecnológico (decisiones justificadas)

> Criterio general: **aburrido en el plano transaccional, agresivo en el plano de datos/IA.** El dinero exige tecnología predecible; la ventaja competitiva vive en datos y modelos. Cada elección optimiza para: velocidad de un equipo pequeño + generabilidad por Claude Code + costo de salida bajo.

## Resumen

| Capa | Elección MVP | Evoluciona a | Por qué |
|---|---|---|---|
| Backend transaccional | **TypeScript + NestJS** (monolito modular) | Extraer módulos calientes | Tipado end-to-end con el frontend, DI y módulos = fronteras claras, el framework más productivo para CRUD+workflows |
| Backend datos/ML | **Python + FastAPI** | igual | Ecosistema ML/scraping sin rival |
| Frontend web | **Next.js 15 + Tailwind + shadcn/ui** | igual | SSR para SEO (cada instrumento es una landing indexable — el growth loop de Zillow), velocity máxima |
| Gráficos | **TradingView Lightweight Charts** | igual | Gratis, canvas, exactamente la estética Bloomberg/broker que queremos |
| Mobile | **Expo (React Native)** | igual | Un solo lenguaje, OTA updates |
| DB principal | **PostgreSQL 16 (RDS)** + **TimescaleDB** para series | + réplicas de lectura | Un solo motor para relacional + JSONB (raw payloads) + series temporales + `pgvector` (embeddings). Menos piezas = menos fallas |
| Analítica | Timescale continuous aggregates | **ClickHouse** cuando >100M filas de eventos | No pagar el costo operativo de ClickHouse antes de necesitarlo |
| Cache | **Redis (ElastiCache)** | igual | Cache + rate limiting + colas ligeras |
| Búsqueda | **Meilisearch** | OpenSearch si se necesita facetado masivo | Typo-tolerance excelente para "Rolex Submarnier", operación trivial, perfecto para catálogo <10M docs |
| Colas / eventos | **Redis Streams + BullMQ** (TS) / **Celery** (Py) | **NATS JetStream o Kafka** en Fase 3 | El volumen del MVP no justifica Kafka; el esquema de eventos versionado hace la migración mecánica |
| Workflows durables | **Temporal (Temporal Cloud)** | igual | Escrow, peritaje y logística son máquinas de estado de días/semanas con compensaciones — escribirlas a mano es donde nacen los bugs que cuestan dinero |
| ORM / migraciones | **Drizzle** (TS), **SQLAlchemy + Alembic** (Py) | igual | SQL explícito, migraciones versionadas |
| Auth | **Clerk** | Propio sobre `identity` si el costo/lock-in duele | No construir auth en el MVP; MFA y device management gratis |
| KYC/AML | **Sumsub** (o Persona) | + motor de reglas propio | Cobertura de documentos LatAm probada |
| Pagos | **Yappy (Banco General) + tarjetas vía dLocal/PagueloFacil** para cobro local; **Stripe** para suscripciones/SaaS; **Wise/transferencia** para payouts regionales | Adquirencia directa | Realidad panameña: Stripe no cubre adquirencia local completa; Yappy es ubicuo en Panamá; dLocal resuelve LatAm cross-border. Alto ticket (> $5k) inicia por transferencia bancaria a cuenta escrow — es como el mercado ya opera |
| Escrow | Cuenta fiduciaria en banco panameño + **ledger propio de doble entrada** | Licencia fiduciaria propia | El ledger es nuestro; el banco es un adaptador |
| Scraping | **Playwright + Crawlee (Python)**, proxies residenciales (Bright Data/Oxylabs u alternativa), CapSolver para CAPTCHA donde sea lícito | Fleet auto-escalable | Ver doc 05 |
| IA / LLM | **Claude API** (extracción, matching difícil, agentes), **embeddings + pgvector**, **LightGBM** para pricing | Fine-tuning si el volumen lo paga | LLM para lenguaje/visión y colas ambiguas; **números con modelos estadísticos, nunca con LLM** |
| Cloud | **AWS us-east-1** (ECS Fargate, RDS, S3, CloudFront) | EKS solo si el fleet lo exige | Latencia excelente a Panamá, madurez, créditos para startups |
| IaC | **Terraform** | igual | Estándar, revisable en PR |
| CI/CD | **GitHub Actions** + Turborepo remote cache; deploy por servicio con path filters | igual | Ya vivimos en GitHub |
| Observabilidad | **OpenTelemetry → Grafana Cloud (Loki/Tempo/Mimir) + Sentry** | Datadog si el presupuesto post-Serie A lo permite | OTel evita lock-in; Sentry para errores de producto |
| Analytics de producto | **PostHog** (self-host barato) | igual | Funnels + feature flags + session replay en uno |
| Data warehouse / BI | Postgres réplica + **Metabase** | ClickHouse + dbt | Suficiente hasta Serie A |

## Decisiones que alguien va a cuestionar (y la defensa)

**¿Por qué no microservicios desde el día 1?**
Porque el riesgo del negocio está en mercado y operaciones, no en escala técnica. 10k listings/día y cientos de transacciones/mes caben en un monolito bien modularizado con margen de 100x. Los módulos NestJS + contratos zod hacen que extraer un servicio sea un refactor, no una reescritura.

**¿Por qué dos lenguajes?**
Porque un solo lenguaje es dogma, no ingeniería. El scraping/ML en TS es remar contra el ecosistema; el transaccional en Python pierde el tipado compartido con el frontend. La frontera entre planos es física (eventos + API), así que el costo de dos lenguajes es bajo.

**¿Por qué Temporal en un MVP?**
Porque el flujo `pago → envío → peritaje → liberación` con timeouts de días y compensaciones de dinero real es exactamente el problema que Temporal resuelve. Un cron + flags a mano fallaría silenciosamente con dinero de clientes; ese bug mata la confianza que es todo el negocio.

**¿Por qué Meilisearch y no Elastic/OpenSearch?**
Catálogo de decenas de miles de instrumentos y cientos de miles de listings: Meili da mejor DX, mejor tolerancia a typos (crítico: "Datejust", "Date-Just", "DJ41") y cuesta una fracción operar. OpenSearch queda documentado como salida si el facetado analítico lo exige.

**¿Por qué no blockchain para el pasaporte digital?**
Porque el problema del pasaporte es pericial (¿quién certifica que ESTE reloj es auténtico?), no criptográfico. Un registro firmado + audit log inmutable da la misma garantía práctica sin fricción. Si un estándar de la industria (Aura, Arianee) gana tracción, se integra como adaptador.

## Entornos

- `local`: docker-compose (Postgres+Timescale, Redis, Meilisearch, Temporal dev, mailhog). Un comando: `make up`.
- `staging`: réplica reducida en AWS, datos sintéticos + fuentes de scraping en modo sandbox.
- `prod`: multi-AZ; RPO 15 min (PITR), RTO 4h documentado.
