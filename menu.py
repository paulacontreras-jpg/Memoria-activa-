import streamlit as st

from estilos import COLORES

CSS_MENU = """
<style>
[data-testid="stSidebar"] {
    background: #F3EBDD;
    border-right: 4px solid #2F6F73;
}
.marca { text-align: center; padding: 0.6rem 0 1.2rem; }
.marca-puntos { margin-bottom: 0.4rem; }
.marca-puntos .punto { border: none; margin: 0 4px; width: 16px; height: 16px; }
.marca-titulo { font-size: 1.8rem; font-weight: 800; color: #2F6F73; line-height: 1.2; }
.marca-sub { font-size: 1.05rem; color: #555555; margin-top: 0.2rem; }

[data-testid="stSidebar"] [data-testid="stPageLink"] a {
    background: #FFFFFF;
    border: 3px solid transparent;
    border-radius: 18px;
    padding: 1rem 1.1rem;
    margin-bottom: 0.5rem;
    font-size: 1.3rem;
    font-weight: 700;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
    border-color: #2F6F73;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] {
    background: #2F6F73;
    border-color: #2F6F73;
    box-shadow: 0 4px 12px rgba(47, 111, 115, 0.35);
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] * {
    color: #FFFFFF !important;
}

.ayuda-menu {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 1rem 1.1rem;
    font-size: 1.05rem;
    line-height: 1.5;
    border-left: 8px solid #FDD835;
}
</style>
"""


def menu_lateral():
    st.markdown(CSS_MENU, unsafe_allow_html=True)
    with st.sidebar:
        puntos = "".join(
            f'<span class="punto" style="background:{c}"></span>' for c in COLORES
        )
        st.markdown(
            f'<div class="marca"><div class="marca-puntos">{puntos}</div>'
            f'<div class="marca-titulo">🧠 Memoria Activa</div>'
            f'<div class="marca-sub">Ejercita tu memoria jugando</div></div>',
            unsafe_allow_html=True,
        )

        st.page_link("inicio.py", label="Inicio", icon="🏠")
        st.page_link("pages/1_Jugador.py", label="Jugador", icon="🎮")
        st.page_link("pages/2_Familiar.py", label="Familiar", icon="💬")

        st.markdown(
            '<div class="ayuda-menu"><b>¿Necesitas ayuda?</b><br>'
            "Si vas a jugar, entra a <b>Jugador</b>. "
            "Si acompañas a alguien, entra a <b>Familiar</b>.</div>",
            unsafe_allow_html=True,
        )
