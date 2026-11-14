import streamlit as st

st.set_page_config(page_title="Memoria Activa", page_icon="🧠")

st.title("🧠 Memoria Activa")
st.write(
    "Juego de memoria de secuencias para estimulación cognitiva. "
    "El juego corre en un dispositivo simulado en Wokwi y esta aplicación "
    "lo controla y le da seguimiento mediante MQTT."
)

st.page_link("pages/1_Jugador.py", label="Jugador (voz y controles)", icon="🎮")
st.page_link("pages/2_Familiar.py", label="Familiar (mensajes y seguimiento)", icon="💬")
