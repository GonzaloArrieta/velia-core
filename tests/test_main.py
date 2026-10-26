import uuid
import pytest
from fastapi.testclient import TestClient
import main
from main import app
from db import get_conn

client = TestClient (app)  

@pytest.fixture(autouse=True)
def clasificador_falso(monkeypatch):
    monkeypatch.setattr(main, "clasificar", lambda texto: "lead")

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

def test_mensaje_nuevo_trae_categoria():
    payload = {
        "data": {
            "key": {"id": nuevo_id(), "remoteJid": "5491160061295@s.whatsapp.net"},
            "message": {"conversation": "Hola, vi el depto"}
        }
    }
    respuesta = client.post("/webhook/whatsapp", json=payload)
    assert respuesta.json()["categoria"] == "lead"


def test_mensaje_vacio_no_llama_al_modelo():
    payload = {
        "data": {
            "key": {"id": nuevo_id(), "remoteJid": "5491160061295@s.whatsapp.net"},
            "message": {"conversation": ""}
        }
    }
    respuesta = client.post("/webhook/whatsapp", json=payload)
    assert respuesta.json()["categoria"] == "desconocido"

def test_categoria_se_guarda_en_la_base():
    mensaje_id = nuevo_id()
    payload = {
        "data": {
            "key": {"id": mensaje_id, "remoteJid": "5491160061295@s.whatsapp.net"},
            "message": {"conversation": "Hola, vi el depto"}
        }
    }
    client.post("/webhook/whatsapp", json=payload)
    with get_conn() as conn:
        fila = conn.execute(
            "select categoria from public.mensajes_procesados where message_id = %s",
            (mensaje_id,)
        ).fetchone()
    assert fila[0] == "lead"