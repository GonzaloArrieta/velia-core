import os 
import httpx 
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODELO = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

def responder (mensaje: str) -> str:
    respuesta = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
        json={
            "model": MODELO, 
            "messages": [
                {"role": "system", "content": "Sos el asistente de una inmobiliaria. Respondé en una o dos frases."},
                {"role": "user", "content": mensaje},
             ],
        },
        timeout=30,
    )
    
    respuesta.raise_for_status()
    datos = respuesta.json ()
    return datos["choices"][0]["message"]["content"]

if __name__ == "__main__":
    print(responder("Hola, ¿tienen departamenos de 2 ambientes en Caseros?"))

