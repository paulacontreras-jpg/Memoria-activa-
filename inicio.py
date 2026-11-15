import streamlit as st

from estilos import COLORES, aviso, encabezado, paso

encabezado("🧠", "Memoria Activa", "Ejercita tu memoria jugando, acompañado por tu familia.")

st.write(
    "Un juego sencillo de luces y sonidos: el dispositivo te muestra una secuencia "
    "de colores y tú la repites. Cada vez que aciertas, la secuencia crece un poquito."
)

st.subheader("¿Cómo funciona?")
pasos = [
    ("1", "Mira y escucha", "Las luces de colores se encienden una por una, cada una con su nota.", COLORES[0]),
    ("2", "Espera el aviso", "Cuando termina, suena una melodía de tres notas: es tu señal.", COLORES[1]),
    ("3", "Repite", "Con el aviso, pulsa los botones en el mismo orden de las luces.", COLORES[2]),
    ("4", "Sube de nivel", "Si aciertas, la secuencia se alarga y ganas puntos.", COLORES[3]),
]
cols = st.columns(4)
for col, (n, t, x, c) in zip(cols, pasos):
    col.markdown(paso(n, t, x, c), unsafe_allow_html=True)

aviso(
    "<b>No pulses antes de tiempo.</b> Espera a que termine la secuencia y suene la melodía "
    "de aviso. También mira la pantallita del dispositivo: ahí aparecen tu nivel y los "
    "mensajes de tu familia."
)

st.subheader("Elige tu lugar")
st.page_link("pages/1_Jugador.py", label="Soy el jugador: quiero jugar", icon="🎮")
st.page_link("pages/2_Familiar.py", label="Soy familiar: quiero acompañar", icon="💬")

aviso(
    "<b>Importante:</b> este juego es un ejercicio de entretenimiento y estimulación. "
    "No es un dispositivo médico ni reemplaza la atención de un profesional de la salud."
)
