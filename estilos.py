import streamlit as st

# Los cuatro colores de las luces del juego
COLORES = ["#E53935", "#43A047", "#1E88E5", "#FDD835"]

CSS = """
<style>
.stApp { font-size: 20px; }
.stMarkdown p, .stMarkdown li { font-size: 1.15rem; line-height: 1.6; }
[data-testid="stWidgetLabel"] p { font-size: 1.15rem; font-weight: 600; }
[data-testid="stCaptionContainer"] { font-size: 1.05rem; }
.stTextInput input { font-size: 1.25rem; padding: 0.8rem; }
h3 { font-size: 1.7rem !important; color: #2F6F73; }

.stButton > button, .stDownloadButton > button {
    font-size: 1.3rem; font-weight: 700; min-height: 3.4rem;
    border-radius: 16px; border: 2px solid #2F6F73;
}
.stButton > button[kind="primary"] { box-shadow: 0 4px 10px rgba(47, 111, 115, 0.3); }
[data-testid="stPageLink"] a {
    background: #FFFFFF; border: 2px solid #2F6F73; border-radius: 16px;
    padding: 0.9rem 1.2rem; font-size: 1.3rem; font-weight: 700;
}
[data-testid="stMetricValue"] { font-size: 3rem; color: #2F6F73; }
[data-testid="stMetricLabel"] p { font-size: 1.15rem; }
[data-testid="stExpander"] { border-radius: 16px; background: #FFFFFF; }

.encabezado {
    background: linear-gradient(135deg, #2F6F73, #4C9A74); color: #FFFFFF;
    padding: 1.6rem 1.8rem; border-radius: 22px; margin-bottom: 1.2rem;
    box-shadow: 0 6px 18px rgba(47, 111, 115, 0.25);
}
.enc-titulo { font-size: 2.4rem; font-weight: 800; line-height: 1.2; margin-top: 0.4rem; }
.enc-sub { font-size: 1.25rem; margin-top: 0.3rem; }
.punto {
    display: inline-block; width: 18px; height: 18px; border-radius: 50%;
    margin-right: 8px; border: 2px solid rgba(255, 255, 255, 0.85);
}

.paso {
    background: #FFFFFF; border-radius: 18px; padding: 1rem 1.1rem;
    border-top: 8px solid var(--c); box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
    min-height: 11rem;
}
.paso-num {
    display: inline-flex; align-items: center; justify-content: center;
    width: 2.6rem; height: 2.6rem; border-radius: 50%; background: var(--c);
    color: #1B1B1B; font-weight: 800; font-size: 1.4rem;
}
.paso-titulo { font-size: 1.3rem; font-weight: 700; margin: 0.5rem 0 0.2rem; }
.paso-texto { font-size: 1.1rem; color: #444444; line-height: 1.4; }

.aviso {
    background: #FFF3CD; border-left: 8px solid #F0B400; padding: 1rem 1.2rem;
    border-radius: 12px; font-size: 1.1rem; margin: 1rem 0;
}
.estado {
    display: flex; align-items: center; gap: 1rem; padding: 1rem 1.3rem;
    border-radius: 18px; border: 3px solid; margin: 0.6rem 0 1rem;
}
.estado-icono { font-size: 2.8rem; }
.estado-titulo { font-size: 1.6rem; font-weight: 800; }
.estado-texto { font-size: 1.15rem; }
</style>
"""

# clave -> (icono, título, texto, color de fondo, color del borde)
ESTADOS_AMIGABLES = {
    "espera": ("🟢", "Listo para jugar", "Escribe tu nombre y pulsa Empezar.", "#E8F5E9", "#43A047"),
    "mostrando": ("👀", "Mira con atención", "Observa las luces y los sonidos del dispositivo.", "#E3F2FD", "#1E88E5"),
    "tu_turno": ("👆", "¡Es tu turno!", "Pulsa los botones en el mismo orden de las luces.", "#FFF8E1", "#F0B400"),
    "perdio": ("💪", "¡Casi lo logras!", "Pulsa Empezar para intentarlo otra vez.", "#FDECEA", "#E53935"),
    "termino": ("✅", "Partida guardada", "Tu puntaje ya está en el ranking.", "#E8F5E9", "#43A047"),
    "gano": ("🏆", "¡Increíble!", "Completaste todos los niveles.", "#FFF8E1", "#F0B400"),
}
POR_DEFECTO = ("⏳", "Conectando con el dispositivo", "Un momento, por favor.", "#F5F5F5", "#9E9E9E")


def aplicar_estilos():
    st.markdown(CSS, unsafe_allow_html=True)


def encabezado(icono, titulo, subtitulo):
    puntos = "".join(f'<span class="punto" style="background:{c}"></span>' for c in COLORES)
    st.markdown(
        f'<div class="encabezado"><div>{puntos}</div>'
        f'<div class="enc-titulo">{icono} {titulo}</div>'
        f'<div class="enc-sub">{subtitulo}</div></div>',
        unsafe_allow_html=True,
    )


def paso(numero, titulo, texto, color):
    return (
        f'<div class="paso" style="--c:{color}"><div class="paso-num">{numero}</div>'
        f'<div class="paso-titulo">{titulo}</div><div class="paso-texto">{texto}</div></div>'
    )


def aviso(texto):
    st.markdown(f'<div class="aviso">{texto}</div>', unsafe_allow_html=True)


def tarjeta_estado(clave):
    icono, titulo, texto, fondo, borde = ESTADOS_AMIGABLES.get(clave, POR_DEFECTO)
    return (
        f'<div class="estado" style="background:{fondo};border-color:{borde}">'
        f'<div class="estado-icono">{icono}</div>'
        f'<div><div class="estado-titulo">{titulo}</div>'
        f'<div class="estado-texto">{texto}</div></div></div>'
    )
