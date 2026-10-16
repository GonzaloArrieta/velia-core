from clasificador import normalizar 


def test_normaliza_mayusculas_y_punto():
    assert normalizar("Lead.\n") == "lead"


def test_respuesta_rara_es_desconocido():
    assert normalizar("No estoy seguro") == "desconocido"

    