import streamlit as st

# Dibujo del dispositivo: pantallita, luces, botones y parlante
_COLORES = [
    ("#E53935", "ROJO", "#FFFFFF"),
    ("#43A047", "VERDE", "#FFFFFF"),
    ("#1E88E5", "AZUL", "#FFFFFF"),
    ("#FDD835", "AMARILLO", "#1B1B1B"),
]
_CENTROS = [190, 330, 470, 610]


def _svg() -> str:
    p = []
    p.append(
        "<svg viewBox='0 0 760 400' xmlns='http://www.w3.org/2000/svg' role='img' "
        "aria-label='Dibujo del dispositivo con pantallita, cuatro luces, cuatro botones y parlante' "
        "style='width:100%;max-width:760px;display:block;margin:0 auto;font-family:Arial,sans-serif'>"
    )
    p.append("<rect x='20' y='10' width='720' height='380' rx='28' fill='#F3EBDD' stroke='#2F6F73' stroke-width='4'/>")
    # 1. Pantallita
    p.append("<rect x='190' y='38' width='380' height='96' rx='10' fill='#1E3A2F' stroke='#555555' stroke-width='6'/>")
    p.append("<text x='214' y='80' font-family='Courier New,monospace' font-size='28' font-weight='700' fill='#B9F6CA'>Nivel 3</text>")
    p.append("<text x='214' y='116' font-family='Courier New,monospace' font-size='28' font-weight='700' fill='#B9F6CA'>Tu turno: pulsa</text>")
    p.append("<circle cx='120' cy='86' r='20' fill='#2F6F73'/><text x='120' y='93' text-anchor='middle' font-size='22' font-weight='700' fill='#FFFFFF'>1</text>")
    p.append("<text x='120' y='126' text-anchor='middle' font-size='15' font-weight='700' fill='#2B2B2B'>Pantallita</text>")
    # 4. Parlante
    p.append("<circle cx='650' cy='86' r='24' fill='#FFFFFF' stroke='#555555' stroke-width='4'/><circle cx='650' cy='86' r='6' fill='#555555'/>")
    p.append("<path d='M686 68 Q702 86 686 104' fill='none' stroke='#555555' stroke-width='4' stroke-linecap='round'/>")
    p.append("<path d='M698 56 Q726 86 698 116' fill='none' stroke='#555555' stroke-width='4' stroke-linecap='round'/>")
    p.append("<circle cx='650' cy='40' r='16' fill='#2F6F73'/><text x='650' y='46' text-anchor='middle' font-size='18' font-weight='700' fill='#FFFFFF'>4</text>")
    p.append("<text x='650' y='136' text-anchor='middle' font-size='15' font-weight='700' fill='#2B2B2B'>Parlante</text>")
    # 2. Luces y 3. Botones
    for (fill, nombre, txt), cx in zip(_COLORES, _CENTROS):
        p.append(f"<circle cx='{cx}' cy='215' r='40' fill='{fill}' stroke='#333333' stroke-width='3'/>")
        p.append(f"<circle cx='{cx - 12}' cy='203' r='10' fill='#FFFFFF' fill-opacity='0.4'/>")
        p.append(f"<rect x='{cx - 52}' y='278' width='104' height='56' rx='14' fill='{fill}' stroke='#333333' stroke-width='3'/>")
        p.append(f"<text x='{cx}' y='312' text-anchor='middle' font-size='16' font-weight='700' fill='{txt}'>{nombre}</text>")
    p.append("<circle cx='70' cy='215' r='20' fill='#2F6F73'/><text x='70' y='222' text-anchor='middle' font-size='22' font-weight='700' fill='#FFFFFF'>2</text>")
    p.append("<text x='70' y='255' text-anchor='middle' font-size='15' font-weight='700' fill='#2B2B2B'>Luces</text>")
    p.append("<circle cx='70' cy='306' r='20' fill='#2F6F73'/><text x='70' y='313' text-anchor='middle' font-size='22' font-weight='700' fill='#FFFFFF'>3</text>")
    p.append("<text x='70' y='346' text-anchor='middle' font-size='15' font-weight='700' fill='#2B2B2B'>Botones</text>")
    p.append("</svg>")
    return "".join(p)


def mostrar_dispositivo():
    """Dibujo de referencia con nombres, para que nadie se lleve una sorpresa al ver el simulador."""
    st.markdown(_svg(), unsafe_allow_html=True)
    st.markdown(
        "**1. Pantallita:** muestra tu nivel y los mensajes de tu familia.  \n"
        "**2. Luces:** se encienden una por una en el orden que debes recordar.  \n"
        "**3. Botones:** cada uno tiene el mismo color que su luz. Úsalos para repetir el orden.  \n"
        "**4. Parlante:** suena una nota por cada luz y una melodía de tres notas cuando es tu turno."
    )
    st.caption(
        "En el simulador de Wokwi verás estas mismas piezas, con cables y una placa verde en medio. "
        "Ignora los cables: solo mira la pantallita, las luces de colores y los botones de colores. "
        "Si las luces se ven pequeñas, acerca la imagen con el zoom del navegador (Ctrl y +)."
    )
