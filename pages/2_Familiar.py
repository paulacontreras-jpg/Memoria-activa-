import pandas as pd
import streamlit as st

from mqtt_utils import ESTADOS, TOPIC_MENSAJE, get_cliente, publicar

st.title("Familiar")
st.caption("Acompaña el progreso y envía mensajes de ánimo al dispositivo.")

client, datos = get_cliente()

# --- Mensajes ---
st.subheader("Mensaje de ánimo")
mensaje = st.text_input("Escribe un mensaje", max_chars=60, placeholder="¡Muy bien, tú puedes!")
if st.button("Enviar mensaje", type="primary"):
    if mensaje.strip():
        publicar(TOPIC_MENSAJE, mensaje.strip())
        st.success(f"Enviado: {mensaje.strip()}")
    else:
        st.warning("Escribe un mensaje primero.")

st.caption("Mensajes rápidos:")
rapidos = ["¡Tú puedes!", "¡Vas muy bien!", "Te quiero mucho"]
cols = st.columns(len(rapidos))
for col, texto in zip(cols, rapidos):
    if col.button(texto, use_container_width=True):
        publicar(TOPIC_MENSAJE, texto)
        st.success(f"Enviado: {texto}")

st.divider()


# --- Seguimiento ---
@st.fragment(run_every=2)
def seguimiento():
    with datos["lock"]:
        historial = list(datos["historial"])
        ultimo = dict(datos["ultimo"])

    c1, c2, c3 = st.columns(3)
    c1.metric("Partidas jugadas", len(historial))
    c2.metric("Mejor puntaje", max((h["puntaje"] for h in historial), default=0))
    c3.metric("Estado actual", ESTADOS.get(ultimo.get("estado"), "Sin datos"))

    if not historial:
        st.info("Aún no hay partidas terminadas en esta sesión.")
        return

    df = pd.DataFrame(historial)
    st.subheader("Evolución del puntaje")
    st.bar_chart(df.set_index("partida")["puntaje"])
    st.dataframe(df, hide_index=True, use_container_width=True)


seguimiento()

st.caption(
    "El historial vive en la memoria de la app: si la app se reinicia, se borra."
)
