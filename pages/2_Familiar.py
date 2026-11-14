import pandas as pd
import streamlit as st

from estilos import COLORES, aplicar_estilos, encabezado, paso
from mqtt_utils import ESTADOS, TOPIC_MENSAJE, get_cliente, publicar

aplicar_estilos()
encabezado("💬", "Familiar", "Acompaña el progreso y envía mensajes de ánimo.")

client, datos = get_cliente()

with st.expander("📖 ¿Cómo acompañar? (guía rápida)", expanded=True):
    pasos = [
        ("1", "Escribe un mensaje", "Una frase corta de cariño o de ánimo.", COLORES[0]),
        ("2", "Envíalo", "Aparecerá en la pantalla del dispositivo con un aviso sonoro.", COLORES[2]),
        ("3", "Mira el progreso", "Revisa el ranking y cómo mejoran los puntajes.", COLORES[1]),
    ]
    cols = st.columns(3)
    for col, (n, t, x, c) in zip(cols, pasos):
        col.markdown(paso(n, t, x, c), unsafe_allow_html=True)

# --- Mensajes ---
st.subheader("Envía un mensaje de ánimo")
mensaje = st.text_input(
    "Escribe tu mensaje",
    max_chars=60,
    placeholder="¡Muy bien, tú puedes!",
)
if st.button("Enviar mensaje", type="primary"):
    if mensaje.strip():
        publicar(TOPIC_MENSAJE, mensaje.strip())
        st.success(f"Enviado: {mensaje.strip()}")
    else:
        st.warning("Escribe un mensaje primero.")

st.caption("O elige un mensaje rápido:")
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

    st.subheader("Seguimiento")
    c1, c2 = st.columns(2)
    c1.metric("Partidas jugadas", len(historial))
    c2.metric("Mejor puntaje", max((h["puntaje"] for h in historial), default=0))
    c3, c4 = st.columns(2)
    tiempos = [h["tiempo_s"] for h in historial if h["tiempo_s"] > 0]
    c3.metric(
        "Tiempo de respuesta medio",
        f"{sum(tiempos) / len(tiempos):.1f} s" if tiempos else "—",
    )
    c4.metric("Estado actual", ESTADOS.get(ultimo.get("estado"), "Sin datos"))

    if not historial:
        st.info("Aún no hay partidas terminadas. Cuando alguien juegue, aparecerán aquí.")
        return

    df = pd.DataFrame(historial)

    st.subheader("🏆 Ranking de jugadores")
    ranking = (
        df.groupby("jugador")
        .agg(mejor_puntaje=("puntaje", "max"), partidas=("puntaje", "count"))
        .sort_values("mejor_puntaje", ascending=False)
        .reset_index()
    )
    medallas = ["🥇", "🥈", "🥉"]
    ranking.insert(0, "puesto", [medallas[i] if i < 3 else str(i + 1) for i in range(len(ranking))])
    st.dataframe(ranking, hide_index=True, use_container_width=True)

    st.subheader("📈 Evolución del puntaje")
    st.bar_chart(df.set_index("partida")["puntaje"])

    st.subheader("⏱ Tiempo de respuesta por partida (segundos)")
    st.line_chart(df.set_index("partida")["tiempo_s"])
    st.caption(
        "Un tiempo menor indica que el jugador responde más rápido. "
        "Es solo un seguimiento del juego, no una medida médica."
    )

    st.subheader("📋 Historial de partidas")
    st.dataframe(df, hide_index=True, use_container_width=True)

    st.download_button(
        "Descargar historial (CSV)",
        df.to_csv(index=False).encode("utf-8"),
        file_name="historial_memoria_activa.csv",
        mime="text/csv",
        key="descargar_historial",
    )


seguimiento()

st.caption("El historial vive en la memoria de la app: si la app se reinicia, se borra.")
