import httpx
import extraer_filtros as modulo


class RespuestaFalsa:
    def __init__(self, contenido):
        self.contenido = contenido

    def raise_for_status(self):
        pass

    def json(self):
        return {"choices": [{"message": {"content": self.contenido}}]}


def simular_llm(monkeypatch, contenido):
    monkeypatch.setattr(modulo.httpx, "post", lambda *args, **kwargs: RespuestaFalsa(contenido))

def test_json_valido_se_convierte_en_filtros(monkeypatch):
    simular_llm(monkeypatch, '{"operacion": "alquiler", "zona": "Haedo", "precio_max": null, "moneda": null}')
    filtros = modulo.extraer_filtros("algo en Haedo para alquilar")
    assert filtros.operacion == "alquiler"
    assert filtros.zona == "Haedo"


def test_valor_no_permitido_devuelve_filtros_vacios(monkeypatch):
    simular_llm(monkeypatch, '{"operacion": "rent"}')
    assert modulo.extraer_filtros("algo") == modulo.Filtros()


def test_texto_que_no_es_json_devuelve_filtros_vacios(monkeypatch):
    simular_llm(monkeypatch, "No sé qué responder")
    assert modulo.extraer_filtros("algo") == modulo.Filtros()


def test_si_groq_falla_devuelve_filtros_vacios(monkeypatch):
    def falla(*args, **kwargs):
        raise httpx.ConnectError("sin conexión")
    monkeypatch.setattr(modulo.httpx, "post", falla)
    assert modulo.extraer_filtros("algo") == modulo.Filtros()