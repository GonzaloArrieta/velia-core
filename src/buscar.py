from db import get_conn
from embeddings import generar_embedding
from cargar_embeddings import vector_a_texto

def buscar_propiedades(
    pregunta: str,
    cantidad: int = 3,
    operacion: str | None = None,
    zona: str | None = None,
    precio_max: float | None = None,
    moneda: str | None = None,
) -> list[dict]:
    vector = vector_a_texto(generar_embedding(pregunta))

    condiciones = ["embedding is not null"]
    parametros = [vector]

    if operacion:
        condiciones.append("operacion = %s")
        parametros.append(operacion)
    if zona:
        condiciones.append("zona ilike %s")
        parametros.append(zona)
    if precio_max is not None:
        condiciones.append("precio <= %s")
        parametros.append(precio_max)
    if moneda:
        condiciones.append("moneda = %s")
        parametros.append(moneda)

    where = " and ".join(condiciones)
    parametros += [vector, cantidad]

    sql = f"""
        select id, titulo, zona, precio, moneda,
               1 - (embedding <=> %s::vector) as similitud
        from public.propiedades
        where {where}
        order by embedding <=> %s::vector
        limit %s
    """
    with get_conn() as conn:
        filas = conn.execute(sql, parametros).fetchall()

    return [
        {
            "id": f[0],
            "titulo": f[1],
            "zona": f[2],
            "precio": f[3],
            "moneda": f[4],
            "similitud": round(f[5], 2),
        }
        for f in filas
    ]


if __name__ == "__main__":
    print("Sin filtro:")
    for p in buscar_propiedades("algo con patio"):
        print(p)

    print("Solo alquiler:")
    for p in buscar_propiedades("algo con patio", operacion="alquiler"):
        print(p)