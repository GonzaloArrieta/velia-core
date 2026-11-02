from fastembed import TextEmbedding

MODELO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
_modelo = None

def generar_embedding(texto: str) -> list[float]:
    global _modelo
    if _modelo is None:
        _modelo = TextEmbedding(MODELO)
    vector = next(_modelo.embed([texto]))
    return vector.tolist()

if __name__ == "__main__":
    vector = generar_embedding("Departamento luminoso cerca del tren")
    print(len(vector), vector[:5])