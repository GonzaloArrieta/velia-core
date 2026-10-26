from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from psycopg.errors import UniqueViolation
from db import get_conn  # Importamos tu conexión a Postgres
from clasificador import clasificar # Importamos la función de clasificación

# 1. Modelos Pydantic
class KeyInfo(BaseModel):
    remoteJid: str
    id: str

class MessageInfo(BaseModel):
    conversation: str

class DataPayload(BaseModel):
    key: KeyInfo
    message: MessageInfo

class EvolutionWebhook(BaseModel):
    data: DataPayload

# 2. Lógica de Base de Datos
def registrar_mensaje(mensaje_id: str, telefono: str):
    """Intenta guardar en la BD. Si el ID ya existe, Postgres tira error y devolvemos False."""
    try:
        with get_conn() as conn:
            conn.execute(
                "insert into public.mensajes_procesados (message_id, telefono) values (%s, %s)",
                (mensaje_id, telefono)
            )
        return True
    except UniqueViolation:
        return False

def guardar_categoria(mensaje_id: str, categoria: str):
    """Guarda la categoría del mensaje en la fila que ya registramos."""
    with get_conn() as conn:
        conn.execute(
            "update public.mensajes_procesados set categoria = %s where message_id = %s",
            (categoria, mensaje_id)
        )

# 3. Inicialización de la app
app = FastAPI()

@app.post("/webhook/whatsapp")
def recibir_mensaje(payload: EvolutionWebhook):
    mensaje_id = payload.data.key.id
    jid = payload.data.key.remoteJid
    texto = payload.data.message.conversation
    telefono = jid.split("@")[0]
 
    # 4. Freno de seguridad de Postgres
    if not registrar_mensaje(mensaje_id, telefono):
        print(f"Freno de BD: Mensaje {mensaje_id} duplicado. Ignorando.")
        return {"status": "ignorado", "motivo": "duplicado"}
        
    if texto.strip():
        categoria = clasificar(texto)
    else:
        categoria = "desconocido"

    guardar_categoria(mensaje_id, categoria)
    
    print(f"Nuevo mensaje de {telefono} ({categoria}): {texto}")
    return {"status": "ok", "telefono": telefono, "categoria": categoria}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
