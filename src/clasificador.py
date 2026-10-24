import os 
import httpx
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODELO = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

CATEGORIAS = {"lead", "cliente", "spam"}

PROMPT = """Sos el clasificador de mensajes de WhatsApp de una inmobiliaria.
Clasificá el mensaje en UNA de estas categorías:
- lead: alguien interesado en comprar, alquilar o tasar, que todavía no es cliente.
- cliente: alguien que ya opera con la inmobiliaria (contrato, llaves, pagos, reclamos).
- spam: publicidad, cadenas, estafas o mensajes que no tienen que ver con la inmobiliaria.
Si la persona dice que ya alquila, es propietaria o tiene un contrato con la inmobiliaria, es cliente aunque pregunte por otra propiedad.
Si la persona reporta un problema en la propiedad que alquila o habita (pérdida de agua, algo roto, reclamo de mantenimiento), es cliente.
Si el mensaje es solo un saludo o es muy corto y sin contexto (por ejemplo "hola" o "buenas"), es lead: es alguien que recién empieza a consultar.
Respondé solo con una palabra: lead, cliente o spam."""

def normalizar(respuesta: str) -> str:
    palabra = respuesta.strip().lower().strip(".!")
    if palabra in CATEGORIAS:
        return palabra
    return "desconocido"


def clasificar(texto: str) -> str:
    respuesta = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
        json={
            "model": MODELO,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": texto},
            ]
        },
    timeout=30,
    )
    respuesta.raise_for_status()
    contenido = respuesta.json()["choices"][0]["message"]["content"]
    return normalizar(contenido)
