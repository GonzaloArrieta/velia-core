from db import get_conn
from embeddings import generar_embedding

def vector_a_texto(vector: list[float]) -> str:
    return "[" + ",".join(str(x) for x in vector) + "]"

def cargar_embeddings():
    with get_conn() as conn:
        filas = conn.execute(
            "select id, titulo, descripcion from public.propiedades where embedding is null"
        ).fetchall()

        for id_, titulo, descripcion in filas:
            texto = f"{titulo}. {descripcion}"
            vector = generar_embedding(texto)
            conn.execute(
                "update public.propiedades set embedding = %s::vector where id = %s",
                (vector_a_texto(vector), id_),
            )
            print(f"Propiedad {id_}: embedding guardado")

    print(f"Listo: {len(filas)} propiedades")

if __name__ == "__main__":
    cargar_embeddings()