import streamlit as st
import numpy as np
import pandas as pd
import time

# --- Welcome Screen ---
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
        st.session_state['animation_year_idx'] = 0
        st.session_state['animation_finished'] = False

if st.session_state.get('start_game'):

    # --- Datos de la animación ---
    years = np.arange(1999, 2026)

    # Precios reales del oro, interpolados
    gold_price_data = {
        1998: 264.3,
        1999: 261.4,
        2000: 302.8,
        2001: 302.8,
        2002: 328.0,
        2003: 321.2,
        2004: 329.1,
        2005: 358.3,
        2006: 480.5,
        2007: 506.8,
        2008: 593.2,
        2009: 696.9,
        2010: 925.1,
        2011: 1129.7,
        2012: 1298.4,
        2013: 1063.6,
        2014: 952.9,
        2015: 1045.2,
        2016: 1129.1,
        2017: 1114.2,
        2018: 1073.6,
        2019: 1244.9,
        2020: 1549.0,
        2021: 1520.7,
        2022: 1710.4,
        2023: 1795.0,
        2024: 2205.5,
        2025: 2880.0
    }
    gold_series = pd.Series(gold_price_data)
    gold_series = gold_series.reindex(years).interpolate().bfill().ffill()
    gold_prices = gold_series.values

    # (Puedes cambiar estos precios de la casa o poner los reales)
    house_prices = 100_000 + (years - 1999) * 10_000 + np.where(years > 2008, (years-2008)*5_000, 0)
    cash = 100_000

    if 'animation_year_idx' not in st.session_state:
        st.session_state['animation_year_idx'] = 0
    if 'animation_finished' not in st.session_state:
        st.session_state['animation_finished'] = False

    # Animación automática
    if not st.session_state['animation_finished']:
        idx = st.session_state['animation_year_idx']
        current_year = int(years[idx])
        current_house_price = house_prices[idx]
        current_gold_price = gold_prices[idx]
        houses_you_can_buy = cash / current_house_price
        gold_you_can_buy = cash / current_gold_price

        st.markdown(f"""
        <h3 style='text-align:center; margin-top:14px;'>Año: {current_year}</h3>
        <div style='text-align:center; font-size:1.25em; margin-bottom:18px; color:#1a3700;'>
        Con <b>100.000 €</b> en <b>{current_year}</b> puedes comprar:
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("🏠 % de una casa", f"{houses_you_can_buy:.2f}")
            st.markdown(f"<div style='text-align:center; color:#222;'>Precio casa: <b>{int(current_house_price):,} €</b></div>", unsafe_allow_html=True)
        with col2:
            st.metric("🪙 Onzas de oro", f"{gold_you_can_buy:.1f}")
            st.markdown(f"<div style='text-align:center; color:#222;'>Precio oro: <b>{current_gold_price:,.1f} €</b></div>", unsafe_allow_html=True)

        # Feedback visual
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

        # Avanza al siguiente año
        if idx < len(years) - 1:
            time.sleep(0.75)
            st.session_state['animation_year_idx'] += 1
            st.rerun()
        else:
            st.session_state['animation_finished'] = True

    # Conclusiones al final
    if st.session_state['animation_finished']:
        st.markdown("<hr style='margin:34px 0;'>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background-color:#f0f8ff; border-left: 7px solid #2b5876; padding: 18px 24px; border-radius:8px; color:#222; margin-top:20px;'>
        <h2 style='color:#2b5876;'>🔔 Conclusiones</h2>
        <ul style='font-size:1.08em; color:#222;'>
          <li><b>El dinero en efectivo pierde poder adquisitivo con el tiempo.</b></li>
          <li><b>El aumento de los balances de los bancos centrales y la inflación de activos</b> hacen que cada vez puedas comprar menos cosas reales.</li>
          <li><b>Diversificar en activos reales</b> es clave para proteger tu riqueza a largo plazo.</li>
        </ul>
        <p style='margin-top:10px; font-size:1.02em; color:#384957;'><b>¿Quieres volver a intentarlo?</b> Recarga la página para empezar de nuevo.</p>
        </div>
        """, unsafe_allow_html=True)
