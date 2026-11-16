# velia-core

Python core of **Velia**, a WhatsApp AI agent that classifies conversations, qualifies leads and routes them to salespeople. Velia runs on n8n today; this repo is the rewrite of its core in code.

**Status:** deployed and running in shadow mode on a self-hosted server. It currently processes test traffic — no external customer depends on it yet. A first external pilot is the next milestone.

---

## What it does today

**Ingestion**
- FastAPI webhook that receives WhatsApp messages in Evolution API format.
- Payload validated with Pydantic.
- Duplicate messages dropped through a unique constraint in PostgreSQL (Supabase), not in memory.
- Protected with a secret token compared in constant time.
- Accepts link, audio and image messages (fixed a 422 that rejected them in production).

**Classification**
- `src/clasificador.py` classifies every message as `lead`, `cliente` or `spam` using an LLM through Groq at `temperature 0`.
- If the model answers anything outside those three categories, the message is stored as `desconocido` rather than inventing one.
- The category is persisted with the message.

**Semantic search**
- Local embeddings over a property catalog, stored in pgvector.
- Combined with exact SQL filters (operation, area, max price), so the model narrows and the database decides.

**Slack bot**
- Answers questions using that search.
- An LLM extracts the filters from the question as structured output validated with Pydantic.
- Safe fallback when the model answers badly or the API fails.

---

## Measurement

Model quality is measured with evaluation sets, separately from the test suite.

**Message classifier — 20/20**

`evals/mensajes.csv` holds 20 real real-estate messages with their correct category, including hard cases: transcribed audio without accents, tenants asking about a different property, disguised spam.

```bash
python evals/run_evals.py
```

The first run scored 19/20. A tenant asking about another property came out as `lead`. That was not a model failure — it was a missing business rule. I defined the rule (a tenant is still a `cliente`), added it to the prompt, and re-ran the full set to confirm nothing else broke.

**Semantic search — hit@3 8/8**

Measured with its own evaluation set: the correct property appears in the top 3 results in 8 of 8 queries.

---

## Tests and CI

- 18 pytest tests with the LLM mocked, including its failure cases.
- On every push, GitHub Actions spins up a temporary PostgreSQL, creates the schema from `schema.sql`, runs the tests and builds the Docker image.
- Tests never touch the production database and never call the model's API.

---

## Deployment

Docker on a self-hosted server (Easypanel, Traefik, HTTPS), running in **shadow mode**: the n8n agent forwards every incoming message, which is classified and stored without touching the live reply path. This lets the Python core be validated against real message formats before it takes over any customer-facing behaviour.

---

## Stack

Python 3.13 · FastAPI · Pydantic · PostgreSQL (Supabase) · pgvector · psycopg · httpx · Slack Bolt · pytest · Docker · GitHub Actions

---

## Design decisions

**Deduplication in the database, not in memory.** The webhook can receive the same message more than once. A unique constraint in PostgreSQL keeps working after a restart and when two webhooks arrive at the same time.

**The model is only called when it is needed.** An empty message (a sticker, for example) is stored as `desconocido` without spending an API call.

**The LLM is replaced in the tests.** With `monkeypatch`, the tests use a fake classifier: fast, free and deterministic. Model quality is measured separately, with the evaluation sets.

**Repeatable tests.** Each test generates a unique ID with `uuid`, so results never depend on what a previous run left in the database.

**Scoring in code, not in the prompt.** The model extracts structured data; the lead score is calculated in code with explicit rules, so results stay predictable when the model changes.

**Degrade, do not guess.** Every LLM call has a defined fallback. An unparseable answer becomes `desconocido`; a failed API call returns a safe response instead of a wrong one.

---

## Running it

1. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill in the values.
3. The database needs the schema in `schema.sql`.
4. Start the server:

```bash
python src/main.py
```

5. Run the tests:

```bash
python -m pytest -v
```

---

## What's next

- **First external pilot.** Run the core against a real business's traffic and measure before and after.
- **Tracing and observability** for LLM calls, so quality is monitored continuously instead of only at evaluation time.
- **Move more of the n8n agent into the core**, starting with lead qualification.

---

Built by [Gonzalo Arrieta](https://github.com/GonzaloArrieta) · [LinkedIn](https://linkedin.com/in/pablo-gonzalo-arrieta)
