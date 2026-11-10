import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from buscar import buscar_propiedades
from extraer_filtros import extraer_filtros

load_dotenv()
app = App(token=os.environ["SLACK_BOT_TOKEN"])

@app.event("app_mention")
def responder_mencion(event, say):
    texto = event["text"]
    pregunta = texto.split(">", 1)[-1].strip()
    filtros = extraer_filtros(pregunta)
    resultados = buscar_propiedades(pregunta, **filtros.model_dump())

    if not resultados:
        say("No encontré propiedades parecidas. Probá con otras palabras.")
        return

    lineas = [f"• {r['titulo']} ({r['zona']}) - {r['moneda']} {r['precio']}" for r in resultados]
    aplicados = {k: v for k, v in filtros.model_dump().items() if v is not None}
    encabezado = f"Entendí estos filtros: {aplicados}\n" if aplicados else ""
    say(encabezado + "Encontré esto:\n" + "\n".join(lineas))

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()