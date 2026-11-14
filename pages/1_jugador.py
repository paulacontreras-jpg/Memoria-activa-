import streamlit as st
from streamlit_mic_recorder import speech_to_text

from mqtt_utils import ESTADOS, TOPIC_COMANDO, get_cliente, limpiar_texto, publicar

st.title("Jugador")
st.caption("Controla la partida con la voz o con los botones.")

client, datos = get_cliente()

DIFICULTADES = {"Lenta": "lenta", "Normal": "normal", "Rápida": "rapida"}


def cambiar_dificultad():
    publicar(TOPIC_COMANDO, f"dificultad:{DIFICULTADES[st.session_state.dif]}")


# --- Estado en vivo ---
@st.fragment(run_every=1)
def en_vivo():
    with datos["lock"]:
        ultimo = dict(datos["ultimo"])
    if not datos["conectado"]:
        st.warning("Sin conexión con el broker MQTT. Recarga la página en unos segundos.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Nivel", ultimo.get("nivel", 0))
    c2.metric("Puntaje", ultimo.get("puntaje", 0))
    c3.metric("Estado", ESTADOS.get(ultimo.get("estado"), "Sin datos"))
    if ultimo.get("estado") == "perdio":
        st.info("¡Casi lo logras! Pulsa Empezar para intentarlo de nuevo.")
    elif ultimo.get("estado") == "gano":
        st.success("¡Increíble, completaste todos los niveles!")


en_vivo()

st.divider()

# --- Botones ---
st.subheader("Controles")
col1, col2 = st.columns(2)
if col1.button("▶ Empezar", type="primary", use_container_width=True):
    publicar(TOPIC_COMANDO, "iniciar")
    st.toast("Partida iniciada")
if col2.button("↻ Reiniciar", use_container_width=True):
    publicar(TOPIC_COMANDO, "reiniciar")
    st.toast("Partida reiniciada")

st.select_slider(
    "Dificultad (velocidad de la secuencia)",
    options=list(DIFICULTADES),
    value="Normal",
    key="dif",
    on_change=cambiar_dificultad,
)

st.divider()

# --- Voz ---
st.subheader("Control por voz")
st.caption("Di «empezar», «reiniciar» o el nombre de una dificultad: «lenta», «normal» o «rápida».")

dictado = speech_to_text(
    language="es",
    start_prompt="🎤 Dictar comando",
    stop_prompt="⏹ Detener",
    just_once=True,
    use_container_width=True,
    key="stt",
)

if dictado:
    t = limpiar_texto(dictado).lower()
    if "reinici" in t or "otra vez" in t or "de nuevo" in t:
        publicar(TOPIC_COMANDO, "reiniciar")
        st.success(f"Entendí «{dictado}»: reiniciar la partida")
    elif "empez" in t or "inici" in t or "comenz" in t or "jugar" in t:
        publicar(TOPIC_COMANDO, "iniciar")
        st.success(f"Entendí «{dictado}»: empezar la partida")
    elif "lent" in t:
        publicar(TOPIC_COMANDO, "dificultad:lenta")
        st.success(f"Entendí «{dictado}»: dificultad lenta")
    elif "normal" in t:
        publicar(TOPIC_COMANDO, "dificultad:normal")
        st.success(f"Entendí «{dictado}»: dificultad normal")
    elif "rapid" in t:
        publicar(TOPIC_COMANDO, "dificultad:rapida")
        st.success(f"Entendí «{dictado}»: dificultad rápida")
    else:
        st.warning(f"No entendí «{dictado}». Prueba con «empezar» o «reiniciar».")
