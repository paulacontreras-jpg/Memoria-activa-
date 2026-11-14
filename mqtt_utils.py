import json
import random
import threading
import unicodedata

import paho.mqtt.client as mqtt
import streamlit as st

BROKER = "broker.mqttdashboard.com"
PORT = 1883
TOPIC_COMANDO = "pau/memoria/comando"
TOPIC_MENSAJE = "pau/memoria/mensaje"
TOPIC_ESTADO = "pau/memoria/estado"

ESTADOS = {
    "espera": "En espera",
    "mostrando": "Mostrando secuencia",
    "tu_turno": "Turno del jugador",
    "perdio": "Partida terminada",
    "termino": "Partida terminada",
    "gano": "¡Completó el juego!",
}

# Estados que cierran una partida y se guardan en el historial
RESULTADOS = {
    "perdio": "Perdió",
    "termino": "Terminó",
    "gano": "Completó el juego",
}


def limpiar_texto(texto: str) -> str:
    """Quita tildes y signos que la LCD no puede mostrar."""
    texto = texto.replace("¿", "").replace("¡", "")
    normalizado = unicodedata.normalize("NFD", texto)
    return "".join(c for c in normalizado if unicodedata.category(c) != "Mn")


@st.cache_resource
def get_cliente():
    """Un único cliente MQTT en segundo plano, compartido por las dos páginas."""
    datos = {
        "lock": threading.Lock(),
        "conectado": False,
        "jugador": "Anónimo",
        "ultimo": {"estado": "desconocido", "nivel": 0, "puntaje": 0, "dificultad": "normal"},
        "historial": [],
    }

    def on_connect(client, userdata, flags, rc):
        datos["conectado"] = (rc == 0)
        client.subscribe(TOPIC_ESTADO)

    def on_disconnect(client, userdata, rc):
        datos["conectado"] = False

    def on_message(client, userdata, msg):
        try:
            info = json.loads(msg.payload.decode("utf-8"))
        except ValueError:
            return
        with datos["lock"]:
            datos["ultimo"] = info
            # El mensaje retenido es el último estado guardado en el broker:
            # no cuenta como una partida nueva.
            estado = info.get("estado")
            if estado in RESULTADOS and not msg.retain:
                datos["historial"].append(
                    {
                        "partida": len(datos["historial"]) + 1,
                        "jugador": datos["jugador"],
                        "puntaje": info.get("puntaje", 0),
                        "nivel": info.get("nivel", 0),
                        "dificultad": info.get("dificultad", "normal"),
                        "resultado": RESULTADOS[estado],
                    }
                )

    client = mqtt.Client(client_id=f"streamlit-memoria-{random.randint(0, 99999)}")
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_start()
    return client, datos


def publicar(topic: str, texto: str) -> None:
    client, _ = get_cliente()
    client.publish(topic, limpiar_texto(texto))


def set_jugador(nombre: str) -> None:
    """Guarda quién está jugando, para asignarle el puntaje al terminar."""
    _, datos = get_cliente()
    with datos["lock"]:
        datos["jugador"] = nombre.strip() or "Anónimo"
