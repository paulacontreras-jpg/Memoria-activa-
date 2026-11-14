import streamlit as st

from estilos import COLORES, aviso, encabezado, paso

encabezado("🧠", "Memoria Activa", "Ejercita tu memoria jugando, acompañado por tu familia.")

st.write(
    "Un juego sencillo de luces y sonidos: el dispositivo te muestra una secuencia "
    "de colores y tú la repites. Cada vez que aciertas, la secuencia crece un poquito."
)

st.subheader("¿Cómo funciona?")
pasos = [
    ("1", "Mira", "Las luces de colores se encienden una por una.", COLORES[0]),
    ("2", "Recuerda", "Memoriza el orden en que aparecieron.", COLORES[1]),
    ("3", "Repite", "Pulsa los botones con los mismos colores, en el mismo orden.", COLORES[2]),
    ("4", "Sube de nivel", "Si aciertas, la secuencia se alarga y ganas puntos.", COLORES[3]),
]
cols = st.columns(4)
for col, (n, t, x, c) in zip(cols, pasos):
    col.markdown(paso(n, t, x, c), unsafe_allow_html=True)

st.subheader("Elige tu lugar")
st.page_link("pages/1_Jugador.py", label="Soy el jugador: quiero jugar", icon="🎮")
st.page_link("pages/2_Familiar.py", label="Soy familiar: quiero acompañar", icon="💬")

aviso(
    "<b>Importante:</b> este juego es un ejercicio de entretenimiento y estimulación. "
    "No es un dispositivo médico ni reemplaza la atención de un profesional de la salud."
)
