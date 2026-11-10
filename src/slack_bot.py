import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from buscar import buscar_propiedades

load_dotenv()
app = App(token=os.environ["SLACK_BOT_TOKEN"])

@app.event("app_mention")
def responder_mencion(event, say):
    texto = event["text"]
    pregunta = texto.split(">", 1)[-1].strip()
    resultados = buscar_propiedades(pregunta)

    if not resultados:
        say("No encontré propiedades parecidas. Probá con otras palabras.")
        return

    lineas = [f"• {r['titulo']} ({r['zona']}) - {r['moneda']} {r['precio']}" for r in resultados]
    say("Encontré esto:\n" + "\n".join(lineas))

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()