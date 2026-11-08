# Roadmap de velia-core

velia-core es el núcleo en Python de Velia, un agente de IA para WhatsApp para inmobiliarias. Hoy el agente conversa desde n8n, y velia-core recibe una copia de cada mensaje en modo sombra. La meta es que velia-core haga de punta a punta lo que hoy hace n8n, más lo que n8n no puede hacer bien: buscar en las propiedades, medir la calidad y escalar.

## Hecho

| Qué | Por qué importa |
|---|---|
| Webhook en FastAPI con validación Pydantic | Recibir datos de otro sistema sin romperse con un payload inesperado |
| Deduplicación con restricción única en PostgreSQL | Idempotencia: el mismo mensaje no se procesa dos veces, aunque se reinicie el servidor |
| Clasificador con LLM (lead, cliente, spam) y salida normalizada | Usar un LLM como componente confiable, no como caja negra |
| Set de evaluación de 20 mensajes de prueba, 20/20 | Medir antes de cambiar un prompt o un modelo |
| 11 tests con el LLM simulado | Tests rápidos, gratis y deterministas |
| CI en GitHub Actions con PostgreSQL temporal y build de Docker | Cada push se prueba solo |
| Token secreto comparado en tiempo constante, fail closed | Seguridad básica de una API pública |
| Deploy con Docker en Easypanel, detrás de Traefik con HTTPS | Un servicio real en producción, no un notebook |
| Modo sombra: n8n reenvía cada mensaje a velia-core | Probar un servicio nuevo con tráfico real sin riesgo |

## Fase 1: robustez (semana 1 de noviembre)

- [x] Leer el texto de los mensajes con link o que responden a otro (`extendedTextMessage.text`), que hoy dan 422
- [x] Aceptar audios, imágenes y stickers sin error: guardarlos como `desconocido`
- [ ] Leer el texto de las fotos con descripción (`imageMessage.caption`)
- [ ] Base de datos separada para los tests locales
- [ ] Logs claros de cada mensaje procesado

## Fase 2: RAG sobre las propiedades (semanas 1 y 2)

- [ ] Activar pgvector en Supabase y crear la tabla `propiedades`
- [ ] Cargar propiedades de prueba (datos ficticios de "Brújula Sur Propiedades")
- [ ] Generar embeddings con un modelo multilingüe local (fastembed), sin API externa
- [ ] Búsqueda híbrida: filtros SQL para lo exacto (operación, zona, precio, ambientes) y similitud de embeddings para lo descriptivo ("luminoso", "con patio")
- [ ] Endpoint que responde con el LLM usando solo las propiedades encontradas y citando cada una
- [ ] Set de evaluación de búsqueda: ¿la propiedad correcta aparece entre las 3 primeras?

Decisión de diseño: cada propiedad es un texto corto y va entera como un solo fragmento. Partirla en chunks empeoraría la búsqueda.

## Fase 3: calificación de leads en Python (noviembre)

- [ ] Extracción estructurada con el LLM (operación, zona, presupuesto, forma de pago, visita), validada con Pydantic
- [ ] Puntaje calculado en código, con reglas explícitas y tests
- [ ] Leads guardados en PostgreSQL en lugar de Google Sheets
- [ ] Endpoint `GET /leads` protegido, para que el portal muestre datos reales

## Fase 4: responder por WhatsApp (noviembre y diciembre)

- [ ] Enviar respuestas a través de Evolution API, en un número de prueba separado
- [ ] Ignorar los mensajes que manda el propio bot
- [ ] Memoria de conversación en PostgreSQL
- [ ] Derivar a una persona cuando el cliente lo pide o el agente no sabe

## Fase 5: producción y observabilidad (diciembre)

- [ ] Medir latencia, errores y costo de cada llamada al LLM
- [ ] Reintentos con espera creciente cuando falla el proveedor
- [ ] Procesamiento asíncrono: responder al webhook al instante y procesar en segundo plano con una cola
- [ ] Actualización automática del deploy en cada push a `main`

## Fase 6: agente con herramientas (enero)

- [ ] El LLM elige qué herramienta usar: buscar propiedades, agendar una visita o derivar a una persona
- [ ] Límites y validaciones para que el agente no ejecute acciones indebidas
- [ ] Evaluación de conversaciones completas, no solo de mensajes sueltos

## Habilidades que cubre cada fase

| Habilidad que piden los avisos | Fase |
|---|---|
| APIs, webhooks, integraciones | Hecho, 1 y 4 |
| Bases de datos y SQL | Hecho, 2 y 3 |
| RAG, embeddings, bases vectoriales | 2 |
| Salida estructurada y evaluación de LLMs | Hecho, 2 y 3 |
| Testing y CI/CD | Hecho, en todas |
| Docker y deploy | Hecho y 5 |
| Monitoreo, reintentos, colas | 5 |
| Agentes con herramientas y guardrails | 6 |