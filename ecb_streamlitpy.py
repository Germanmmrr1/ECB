import streamlit as st

# Center the button using Streamlit columns
col1, col2, col3 = st.columns([3,2,3])
with col2:
    if st.button("🎲 Empezar a jugar"):
        st.session_state['start_game'] = True

# Monopoly style title and intro

st.markdown("""
    <style>
    .monopoly-title {
        text-align: center;
        font-size: 2.7em;
        font-family: 'Arial Black', Arial, sans-serif;
        color: #2B9348;
        letter-spacing: 1px;
        margin-bottom: 8px;
        text-shadow: 2px 2px 0px #fff176, 0 2px 4px #22222255;
    }
    .monopoly-intro {
        text-align: center;
        background-color: #f8ffd7;
        border: 2px dashed #e63946;
        border-radius: 15px;
        margin: 0 auto 18px auto;
        padding: 18px 30px 10px 30px;
        font-size: 1.2em;
        max-width: 680px;
    }
    </style>
    <div class="monopoly-title">
        🏦💶 ECB MONOPOLY: ¿QUIÉN QUIERE DINERO INFINITO? 💸🏠
    </div>
    <div class="monopoly-intro">
        ¡Bienvenido a la demo del Monopoly del Banco Central Europeo!<br>
        <br>
        <b>Tu objetivo:</b> Descubrir de forma divertida cómo el BCE crea dinero, cómo eso afecta los precios de casas, hoteles y todo lo que tienes, y qué pasa cuando el dinero deja de valer lo mismo.<br><br>
        <span style="color:#2266c6;"><b>¿Listo para ver cómo tu dinero se convierte en billetes del Monopoly?</b></span>
    </div>
""", unsafe_allow_html=True)

if st.button("🎲 Empezar a jugar"):
    st.session_state['start_game'] = True

# When ready, continue to the next step in your app:
if st.session_state.get('start_game'):
    st.markdown("""
        <h3 style='text-align:center; margin-top:12px;'>Tu partida comienza en 1999...</h3>
        <div style='text-align:center; font-size:1.18em;'>Tienes una casa (🏠) y 100.000 €.<br>
        El balance del BCE está a punto de cambiar el destino de tu dinero...</div>
    """, unsafe_allow_html=True)
    # Aquí irá el siguiente paso: slider del BCE, assets, precios, etc.
