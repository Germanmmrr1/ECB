import streamlit as st
import numpy as np
import time

# ----------- Welcome Screen -----------
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
        <b>Empiezas en 1999 solo con <span style='color:#228B22;'>100.000 €</span> en efectivo.</b><br><br>
        <b>Tu objetivo:</b> Descubrir de forma divertida cómo el BCE crea dinero, cómo eso afecta los precios de casas, hoteles y todo lo que tienes, y qué pasa cuando el dinero deja de valer lo mismo.<br><br>
        <span style="color:#2266c6;"><b>¿Listo para ver cómo tu dinero se convierte en billetes del Monopoly?</b></span>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([3,2,3])
with col2:
    if st.button("🎲 Empezar a jugar"):
        st.session_state['start_game'] = True

if st.session_state.get('start_game'):

    st.markdown("""
        <h3 style='text-align:center; margin-top:12px;'>Tu partida comienza en 1999...</h3>
        <div style='text-align:center; font-size:1.18em;'>Tienes <b>100.000 €</b> en efectivo.<br>
        El balance del BCE está a punto de cambiar el destino de tu dinero...</div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # ----------- Game Logic -----------
    # Simulated asset prices
    years = np.arange(1999, 2025+1)
    house_prices = 100_000 + (years - 1999) * 10_000 + np.where(years > 2008, (years-2008)*5_000, 0)
    gold_prices = 250 + (years - 1999) * 20 + np.where(years > 2007, (years-2007)*90, 0)

    # Session state for animation
    if 'auto_year' not in st.session_state:
        st.session_state['auto_year'] = int(years[0])
    if 'is_animating' not in st.session_state:
        st.session_state['is_animating'] = False

    # Play (animate) button
    col1, col2, col3 = st.columns([3,2,3])
    with col2:
        if st.button("▶️ Animar años"):
            st.session_state['is_animating'] = True

    # Animation logic: advance year if animating
    if st.session_state['is_animating']:
        current_year = st.session_state['auto_year']
    if current_year < int(years[-1]):
        next_year = current_year + 1
        time.sleep(0.23)
        st.session_state['auto_year'] = next_year
        st.experimental_rerun()
    else:
        st.session_state['is_animating'] = False


    # The slider: value from session_state (also lets user drag)
    selected_year = st.slider(
        "Avanza en el tiempo:",
        int(years[0]), int(years[-1]),
        value=int(st.session_state['auto_year']),
        key="auto_year"
    )

    # When user drags, stop animation
    if selected_year != st.session_state['auto_year']:
        st.session_state['auto_year'] = selected_year
        st.session_state['is_animating'] = False

    # Prices and calculations
    idx = selected_year - 1999
    current_house_price = house_prices[idx]
    current_gold_price = gold_prices[idx]
    cash = 100_000
    houses_you_can_buy = cash / current_house_price
    gold_you_can_buy = cash / current_gold_price

    st.markdown(f"""
    <div style='text-align:center; font-size:1.25em; margin-top:26px; margin-bottom:18px; color:#1a3700;'>
    Con <b>100.000 €</b> en <b>{selected_year}</b> puedes comprar:
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("🏠 % de una casa", f"{houses_you_can_buy:.2f}")
        st.markdown(f"<div style='text-align:center; color:#222;'>Precio casa: <b>{int(current_house_price):,} €</b></div>", unsafe_allow_html=True)
    with col2:
        st.metric("🪙 Onzas de oro", f"{gold_you_can_buy:.1f}")
        st.markdown(f"<div style='text-align:center; color:#222;'>Precio oro: <b>{int(current_gold_price):,} €</b></div>", unsafe_allow_html=True)

    # Visual feedback and monopoly message
    if houses_you_can_buy < 0.5:
        st.markdown("""
        <div style='text-align:center; margin-top:18px;'>
            <span style='color:#e63946; font-size:1.4em;'>¡Cuidado! Tu dinero se ha "monopolizado":<br>Ya no puedes ni comprar media casa... 🏠💸</span>
        </div>
        """, unsafe_allow_html=True)
    elif houses_you_can_buy < 1:
        st.markdown("""
        <div style='text-align:center; margin-top:16px;'>
            <span style='color:#f4a300; font-size:1.2em;'>Con el paso del tiempo, cada vez compras menos casa con el mismo dinero. 😬</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='text-align:center; margin-top:16px;'>
            <span style='color:#1a5f0a; font-size:1.1em;'>¡Felicidades! Todavía puedes comprar al menos una casa completa. 🏡</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='margin:34px 0;'>", unsafe_allow_html=True)

    # (Optional: conclusions or reset button)
    if selected_year == int(years[-1]):
        st.markdown("""
        <div style='background-color:#f0f8ff; border-left: 7px solid #2b5876; padding: 18px 24px; border-radius:8px; color:#222; margin-top:20px;'>
        <h2 style='color:#2b5876;'>🔔 Conclusiones</h2>
        <ul style='font-size:1.08em; color:#222;'>
          <li><b>El dinero en efectivo pierde poder adquisitivo con el tiempo.</b></li>
          <li><b>El aumento de los balances de los bancos centrales y la inflación de activos</b> hacen que cada vez puedas comprar menos cosas reales.</li>
          <li><b>Diversificar en activos reales</b> es clave para proteger tu riqueza a largo plazo.</li>
        </ul>
        <p style='margin-top:10px; font-size:1.02em; color:#384957;'><b>¿Quieres volver a intentarlo?</b> Refresca la página o mueve el slider para jugar de nuevo.</p>
        </div>
        """, unsafe_allow_html=True)
