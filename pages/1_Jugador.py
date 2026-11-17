import time
from html import escape

import pandas as pd
import streamlit as st
from streamlit_mic_recorder import speech_to_text

from estilos import COLORES, aplicar_estilos, encabezado, paso, pantallita, tarjeta_estado
from mqtt_utils import TOPIC_COMANDO, get_cliente, limpiar_texto, publicar, set_jugador
from dispositivo import mostrar_dispositivo

aplicar_estilos()
encabezado("🎮", "Jugador", "Ejercita tu memoria: mira, recuerda y repite.")

client, datos = get_cliente()

DIFICULTADES = {
    "Lenta": "lenta",
    "Normal": "normal",
    "Rápida": "rapida",
    "Automática": "auto",
}

st.subheader("Conoce tu dispositivo")
mostrar_dispositivo()
# --- Cómo saber cuándo pulsar (siempre visible) ---
st.subheader("¿Cómo saber cuándo pulsar?")
semaforo = [
    ("1", "Mira y escucha", "El dispositivo muestra la secuencia con luces y notas sueltas. Todavía no pulses.", "#E53935"),
    ("2", "Espera el aviso", "Cuando termina, suena una melodía de tres notas y se encienden todas las luces juntas.", "#FDD835"),
    ("3", "¡Ahora pulsa!", "La pantallita dice «Tu turno». Repite el orden con los botones.", "#43A047"),
]
cols = st.columns(3)
for col, (n, t, x, c) in zip(cols, semaforo):
    col.markdown(paso(n, t, x, c), unsafe_allow_html=True)

with st.expander("📖 Guía rápida del juego", expanded=False):
    pasos = [
        ("1", "Escribe tu nombre", "Así tu puntaje queda guardado en el ranking.", COLORES[0]),
        ("2", "Pulsa Empezar", "También puedes decir «empezar» con el micrófono.", COLORES[1]),
        ("3", "Mira, escucha y espera", "No pulses hasta que suene la melodía de aviso.", COLORES[2]),
        ("4", "Repite el orden", "Pulsa los botones del dispositivo con los mismos colores.", COLORES[3]),
    ]
    cols = st.columns(4)
    for col, (n, t, x, c) in zip(cols, pasos):
        col.markdown(paso(n, t, x, c), unsafe_allow_html=True)
    st.markdown(
        "**Consejo:** cuando quieras parar, pulsa **Terminar** y tu puntaje "
        "quedará registrado."
    )

# --- 1. Nombre ---
st.subheader("1. Escribe tu nombre")
nombre = st.text_input(
    "Tu nombre",
    key="nombre",
    max_chars=20,
    placeholder="Por ejemplo: Pau",
    label_visibility="collapsed",
)
listo = bool(nombre.strip())
if not listo:
    st.info("Escribe tu nombre para poder empezar a jugar.")


def cambiar_dificultad():
    publicar(TOPIC_COMANDO, f"dificultad:{DIFICULTADES[st.session_state.dif]}")


def lineas_pantallita(estado, nivel, puntaje):
    """Mismo texto que muestra la pantalla LCD del dispositivo (16 letras por línea)."""
    if estado == "mostrando":
        return f"Nivel {nivel}", "Mira y escucha"
    if estado == "tu_turno":
        return f"Nivel {nivel}", "Tu turno: pulsa"
    if estado == "perdio":
        return "Casi lo logras!", f"Puntaje: {puntaje}"
    if estado == "termino":
        return "Partida guardada", f"Puntaje: {puntaje}"
    if estado == "gano":
        return "Increible!", "Completaste todo"
    if estado == "espera":
        return "Memoria Activa", "Pulsa un boton"
    return "Conectando...", ""


# --- Estado en vivo ---
@st.fragment(run_every=1)
def en_vivo():
    with datos["lock"]:
        ultimo = dict(datos["ultimo"])
        mensaje = dict(datos.get("mensaje", {}))
    if not datos["conectado"]:
        st.warning("Sin conexión con el broker MQTT. Recarga la página en unos segundos.")

    estado = ultimo.get("estado")
    nivel = ultimo.get("nivel", 0)
    puntaje = ultimo.get("puntaje", 0)

    st.markdown(tarjeta_estado(estado), unsafe_allow_html=True)

    st.markdown("**📟 Pantallita del dispositivo**")
    l1, l2 = lineas_pantallita(estado, nivel, puntaje)
    st.markdown(pantallita(l1, l2), unsafe_allow_html=True)
    st.caption(
        "Es lo mismo que ves en la pantalla pequeña del circuito: "
        "ahí aparecen tu nivel y los mensajes de tu familia."
    )

    if mensaje.get("texto") and time.time() - mensaje.get("hora", 0) < 300:
        st.markdown(
            f'<div class="mensaje-familia">💬 <b>Mensaje de tu familia:</b> '
            f'{escape(mensaje["texto"])}</div>',
            unsafe_allow_html=True,
        )

    tiempo = ultimo.get("tiempo", 0) / 1000
    velocidad = ultimo.get("velocidad", 0) / 1000
    c1, c2 = st.columns(2)
    c1.metric("Nivel", nivel)
    c2.metric("Puntaje", puntaje)
    c3, c4 = st.columns(2)
    c3.metric("Tiempo de respuesta", f"{tiempo:.1f} s" if tiempo > 0 else "—")
    c4.metric("Duración de cada luz", f"{velocidad:.1f} s" if velocidad > 0 else "—")


en_vivo()

# --- 2. Controles ---
st.subheader("2. Controla la partida")
col1, col2, col3 = st.columns(3)
if col1.button("▶ Empezar", type="primary", use_container_width=True, disabled=not listo):
    set_jugador(nombre)
    publicar(TOPIC_COMANDO, "iniciar")
    st.toast(f"¡Suerte, {nombre.strip()}!")
if col2.button("↻ Reiniciar", use_container_width=True, disabled=not listo):
    set_jugador(nombre)
    publicar(TOPIC_COMANDO, "reiniciar")
    st.toast("Partida reiniciada")
if col3.button("■ Terminar", use_container_width=True, disabled=not listo):
    publicar(TOPIC_COMANDO, "terminar")
    st.toast("Terminando la partida...")
st.caption(
    "**Empezar:** comienza una partida nueva. **Reiniciar:** vuelve a empezar desde el nivel 1. "
    "**Terminar:** cierra la partida y guarda tu puntaje."
)

# --- 3. Dificultad ---
st.subheader("3. Elige la dificultad")
st.select_slider(
    "Dificultad",
    options=list(DIFICULTADES),
    value="Normal",
    key="dif",
    on_change=cambiar_dificultad,
    label_visibility="collapsed",
)
st.caption(
    "**Lenta:** ideal para empezar. **Normal:** un buen ritmo. "
    "**Rápida:** más reto, y ganas más puntos por cada nivel. "
    "**Automática:** el juego se adapta a tu ritmo: si respondes rápido se acelera, "
    "y si necesitas más tiempo se hace más lento."
)

# --- 4. Voz ---
st.subheader("4. Usa tu voz (opcional)")
st.caption(
    "Pulsa el micrófono y di: «empezar», «reiniciar», «terminar», "
    "«lenta», «normal», «rápida» o «automática»."
)

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
        if listo:
            set_jugador(nombre)
            publicar(TOPIC_COMANDO, "reiniciar")
            st.success(f"Entendí «{dictado}»: reiniciar la partida")
        else:
            st.warning("Escribe tu nombre primero.")
    elif "termin" in t or "acab" in t or "guard" in t or "parar" in t:
        publicar(TOPIC_COMANDO, "terminar")
        st.success(f"Entendí «{dictado}»: terminar y guardar el puntaje")
    elif "empez" in t or "inici" in t or "comenz" in t or "jugar" in t:
        if listo:
            set_jugador(nombre)
            publicar(TOPIC_COMANDO, "iniciar")
            st.success(f"Entendí «{dictado}»: empezar la partida")
        else:
            st.warning("Escribe tu nombre primero.")
    elif "lent" in t:
        publicar(TOPIC_COMANDO, "dificultad:lenta")
        st.success(f"Entendí «{dictado}»: dificultad lenta")
    elif "normal" in t:
        publicar(TOPIC_COMANDO, "dificultad:normal")
        st.success(f"Entendí «{dictado}»: dificultad normal")
    elif "rapid" in t:
        publicar(TOPIC_COMANDO, "dificultad:rapida")
        st.success(f"Entendí «{dictado}»: dificultad rápida")
    elif "automat" in t:
        publicar(TOPIC_COMANDO, "dificultad:auto")
        st.success(f"Entendí «{dictado}»: dificultad automática")
    else:
        st.warning(f"No entendí «{dictado}». Prueba con «empezar» o «terminar».")

st.divider()


# --- Partidas del jugador ---
@st.fragment(run_every=2)
def mis_partidas():
    n = st.session_state.get("nombre", "").strip()
    if not n:
        return
    with datos["lock"]:
        mias = [h for h in datos["historial"] if h["jugador"].lower() == n.lower()]
    st.subheader(f"🏅 Tus partidas, {n}")
    if not mias:
        st.caption("Aún no tienes partidas guardadas. ¡Juega una y aparecerá aquí!")
        return
    st.metric("Tu mejor puntaje", max(h["puntaje"] for h in mias))
    st.dataframe(
        pd.DataFrame(mias)[["partida", "puntaje", "nivel", "dificultad", "tiempo_s", "resultado"]],
        hide_index=True,
        use_container_width=True,
    )


mis_partidas()
