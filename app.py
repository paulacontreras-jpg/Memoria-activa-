import streamlit as st

from estilos import aplicar_estilos
from menu import menu_lateral

st.set_page_config(page_title="Memoria Activa", page_icon="🧠", layout="centered")

paginas = [
    st.Page("inicio.py", title="Inicio", icon="🏠", default=True),
    st.Page("pages/1_Jugador.py", title="Jugador", icon="🎮"),
    st.Page("pages/2_Familiar.py", title="Familiar", icon="💬"),
]
pg = st.navigation(paginas, position="hidden")

aplicar_estilos()
menu_lateral()
pg.run()
