import uuid
from fastapi.testclient import TestClient
from main import app

client = TestClient (app)  

def nuevo_id():
    return f"TEST_{uuid.uuid4().hex}"

def test_mensaje_nuevo_devuelve_ok():
    payload = {
        "data": {
            "key": {"id": nuevo_id(), "remoteJid": "5491160061295@s.whatsapp.net"},
            "message": {"conversation": "hola"}    
        }
    }
    respuesta = client.post("/webhook/whatsapp", json=payload)
    assert respuesta.status_code == 200 
    assert respuesta.json()["status"] == "ok"

def test_payload_sin_texto_no_rompe ():
    payload = {
        "data": {
            "key": {"id": nuevo_id(), "remoteJid": "5491160061295@s.whatsapp.net"},
            "message": {"conversation": ""}
        }
    }
    respuesta = client.post("/webhook/whatsapp", json=payload)
    assert respuesta.status_code == 200

def test_mensaje_duplicado_se_ignora():
    payload = {
        "data": {
            "key": {"id": nuevo_id(), "remoteJid": "5491160061295@s.whatsapp.net"},
            "message": {"conversation": "hola"}
        }
    }
    primera = client.post("/webhook/whatsapp", json=payload)
    segunda = client.post("/webhook/whatsapp", json=payload)
    assert primera.json()["status"] == "ok"
    assert segunda.json()["status"] == "ignorado"