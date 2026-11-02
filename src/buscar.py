from db import get_conn
from embeddings import generar_embedding
from cargar_embeddings import vector_a_texto

def buscar_propiedades(pregunta: str, cantidad: int = 3) -> list[dict]:
    vector = vector_a_texto(generar_embedding(pregunta))

    with get_conn() as conn:
        filas = conn.execute(
            """
            select id, titulo, zona, precio, moneda,
                   1 - (embedding <=> %s::vector) as similitud
            from public.propiedades
            where embedding is not null
            order by embedding <=> %s::vector
            limit %s
            """,
            (vector, vector, cantidad),
        ).fetchall()

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
    for propiedad in buscar_propiedades("tengo un perro grande"):
        print(propiedad)

