from buscar import buscar_propiedades

CASOS = [
    {"pregunta": "algo con patio", "operacion": "alquiler", "esperados": {15}},
    {"pregunta": "casa con pileta para la familia", "operacion": "venta", "esperados": {6, 12}},
    {"pregunta": "depto cerca del tren para invertir", "operacion": "venta", "esperados": {8}},
    {"pregunta": "local para poner un negocio", "operacion": "alquiler", "esperados": {5}},
    {"pregunta": "algo amoblado para entrar ya", "operacion": "alquiler", "esperados": {11}},
    {"pregunta": "casa para refaccionar", "operacion": "venta", "esperados": {9}},
    {"pregunta": "oficina para mi estudio", "operacion": "alquiler", "esperados": {13}},
    {"pregunta": "dúplex con jardin", "operacion": "venta", "esperados": {10}},
]

aciertos = 0

for caso in CASOS:
    resultados = buscar_propiedades(caso["pregunta"], cantidad=3, operacion=caso["operacion"])
    ids = [r["id"] for r in resultados]
    acerto = bool(caso["esperados"] & set(ids))
    marca = "OK " if acerto else "MAL"
    print(marca, caso["pregunta"])
    for r in resultados:
        print("    ", r["id"], r["titulo"], r["similitud"])
    if acerto:
        aciertos += 1
    
    print(f"\nAciertos: {aciertos}/{len(CASOS)}")