import json
import os
from typing import Literal

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
MODELO = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

class Filtros(BaseModel):
    operacion: Literal["venta", "alquiler"] | None = None
    zona: str | None = None
    precio_max: float | None = None
    moneda: Literal["USD", "ARS"] | None = None

PROMPT = """Extraé los filtros de búsqueda de la consulta de un cliente de una inmobiliaria.
Respondé SOLO con un JSON con estas claves:
- "operacion": "venta" o "alquiler", o null si no lo dice.
- "zona": el barrio o localidad, o null.
- "precio_max": el presupuesto máximo como número, o null.
- "moneda": "USD" o "ARS", o null.
No inventes datos: si la consulta no menciona algo, poné null."""

def extraer_filtros(pregunta: str) -> Filtros:
    try:
        respuesta = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": MODELO,
                "temperature": 0,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": PROMPT},
                    {"role": "user", "content": pregunta},
                ],
            },
            timeout=30,
        )
        respuesta.raise_for_status()
        contenido = respuesta.json()["choices"][0]["message"]["content"]
        return Filtros.model_validate_json(contenido)
    except (httpx.HTTPError, ValidationError, KeyError) as error:
        print(f"No se pudieron extraer filtros: {error}")
        return Filtros()

if __name__ == "__main__":
    for p in ["algo con patio para alquilar", "casa en Castelar hasta 250 mil dólares", "hola"]:
        print(p, "->", extraer_filtros(p))