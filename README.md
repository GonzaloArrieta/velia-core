# velia-core

Núcleo en Python de **Velia**, un agente de IA para WhatsApp que clasifica conversaciones, califica leads y los deriva a vendedores. Hoy Velia corre en n8n; este repo es la reescritura de su núcleo en código.

## Qué hace hoy

- Recibe mensajes de WhatsApp (formato de Evolution API) en un webhook con FastAPI.
- Valida el payload con Pydantic.
- Descarta mensajes duplicados con una restricción única en PostgreSQL (Supabase).
- Incluye un cliente para llamar a un LLM vía Groq, con el modelo configurable por variable de entorno (todavía no está conectado al webhook).

## Stack

Python 3.13 · FastAPI · Pydantic · PostgreSQL (Supabase) · psycopg · httpx · pytest

## Cómo correrlo

1. Instalar las dependencias:

```
python -m pip install -r requirements.txt
```

2. Copiar `.env.example` como `.env` y completar los valores.
3. La base necesita una tabla `mensajes_procesados` con `message_id` único.
4. Levantar el servidor:

```
python src/main.py
```

5. Correr los tests:

```
python -m pytest -v
```

## Decisiones de diseño

- **Deduplicación en la base, no en memoria.** El webhook puede recibir el mismo mensaje más de una vez. La restricción única en PostgreSQL sigue funcionando aunque el servidor se reinicie o lleguen dos webhooks a la vez.
- **Tests repetibles.** Cada test genera un ID único con `uuid`, así el resultado no depende de lo que quedó guardado en la base.

## Próximos pasos

- Conectar el webhook con el LLM, con tests que no llamen a la API real.
- Que los tests no dependan de la base real (hoy usan Supabase).
- Validar un token secreto en el webhook.
- Dockerfile, deploy y CI con GitHub Actions.