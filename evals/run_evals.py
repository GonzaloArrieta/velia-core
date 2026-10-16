import csv
import sys
import time

sys.path.insert(0, "src")
from clasificador import clasificar

with open("evals/mensajes.csv", encoding="utf-8") as archivo:
    filas = list(csv.DictReader(archivo))

    aciertos = 0
errores = []
inicio = time.time()

for fila in filas:
    predicho = clasificar(fila["texto"])
    if predicho == fila["categoria"]:
        aciertos += 1
    else:
        errores.append((fila["texto"], fila["categoria"], predicho))

duracion = time.time() - inicio
print(f"Aciertos: {aciertos} de {len(filas)}")
print(f"Tiempo total: {duracion:.1f} s")
for texto, esperado, predicho in errores:
    print(f"- {texto} | esperado: {esperado} | dijo: {predicho}")