# velia-core

Núcleo en Python de **Velia**, un agente de IA para WhatsApp que clasifica conversaciones, califica leads y los deriva a vendedores. Hoy Velia corre en n8n; este repo es la reescritura de su núcleo en código.

## Qué hace hoy

- Recibe mensajes de WhatsApp (formato de Evolution API) en un webhook con FastAPI.
- Valida el payload con Pydantic.
- Descarta mensajes duplicados con una restricción única en PostgreSQL (Supabase).
- Clasifica cada mensaje nuevo como lead, cliente o spam con un LLM vía Groq y devuelve la categoría en la respuesta del webhook. Si el mensaje llega vacío, no llama al modelo.

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
- **El modelo solo se llama si hace falta.** Un mensaje vacío (por ejemplo, un sticker) queda como `desconocido` sin gastar una llamada a la API.
- **El LLM se reemplaza en los tests.** Con `monkeypatch`, los tests usan un clasificador falso: son rápidos, gratis y siempre dan el mismo resultado. La calidad del modelo se mide aparte, con el set de evaluación.

## Clasificador de mensajes

`src/clasificador.py` clasifica cada mensaje en `lead`, `cliente` o `spam` usando un modelo vía Groq, con `temperature 0`. Si el modelo responde algo fuera de esas tres categorías, el mensaje queda como `desconocido` en lugar de inventar una.

### Set de evaluación

`evals/mensajes.csv` tiene 20 mensajes reales del rubro inmobiliario con su categoría correcta, incluidos casos difíciles (audios transcriptos sin tildes, inquilinos que preguntan por otra propiedad, spam disfrazado).

```
python evals/run_evals.py
```

Resultado actual: **20/20**. La primera versión dio 19/20: un inquilino que preguntaba por otra propiedad salió como lead. Definí la regla de negocio (sigue siendo cliente), la agregué al prompt y volví a medir para confirmar que no se rompiera ningún otro caso.

## CI

En cada push, GitHub Actions levanta un PostgreSQL temporal, crea la tabla desde `schema.sql`, corre los tests y construye la imagen de Docker. Los tests no usan la base de producción ni llaman a la API del modelo.

## Próximos pasos

- Guardar la categoría de cada mensaje en la base.
- Validar un token secreto en el webhook.
- Deploy en Easypanel.
