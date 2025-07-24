import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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
        background-color: #fff !important;
        border: 2px dashed #e63946;
        color: #1a3700;
        border-radius: 15px;
        margin: 0 auto 18px auto;
        padding: 18px 30px 10px 30px;
        font-size: 1.2em;
        max-width: 680px;
    }
    .gold-metric-block {
        text-align: center;
        margin: 35px 0 15px 0;
    }
    .gold-label {
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.09em;
        color: #D4AF37;
        margin-bottom: 5px;
        gap: 8px;
    }
    .gold-coin {
        display: inline-block;
        width: 29px; height: 29px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 35%, #ffe57f 0%, #FFD700 65%, #E6BE8A 100%);
        border: 2.4px solid #bfa200;
        box-shadow: 0 1px 4px 0 #E6BE8A88, 0 0 0 1px #ffe57f inset;
        margin-right: 3px;
        vertical-align: middle;
    }
    .gold-value {
        font-size: 3.3em;
        font-weight: 700;
        color: #333;
        letter-spacing: 0.02em;
        margin-bottom: 3px;
    }
    .gold-caption {
        color: #333;
        font-size: 1.1em;
        margin-top: 3px;
    }
    .main-text {
        text-align: center;
        font-size: 1.45em;
        color: #1a3700;
        margin: 24px 0 6px 0;
        font-weight: 600;
    }
    </style>
    <div class="monopoly-title">
        🏦💶 ECB MONOPOLY: EL ORO NUNCA PIERDE<br>💸🪙
    </div>
    <div class="monopoly-intro">
        Bienvenido a la demo educativa del Monopoly del BCE.<br><br>
        <b>Empiezas en 1999 solo con <span style='color:#228B22;'>100.000 €</span> en efectivo.</b><br><br>
        <b>¿Cuántas onzas de oro podrías comprar con ese dinero cada año?</b> Descubre cómo el euro pierde poder adquisitivo frente al oro y compáralo con el balance real del BCE.<br><br>
        <span style="color:#2266c6;"><b>¡Pulsa para empezar la animación!</b></span>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([3,2,3])
with col2:
    if st.button("🎲 Empezar a jugar"):
        st.session_state['start_game'] = True
        st.session_state['animation_year_idx'] = 0
        st.session_state['animation_finished'] = False

if st.session_state.get('start_game'):
    # --- Oro real e interpolación ---
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

    years = list(range(1999, 2026))
    gold_series = pd.Series(gold_price_data)
    gold_series = gold_series.reindex(years).interpolate().bfill().ffill()
    gold_prices = gold_series.values
    cash = 100_000

    # --- BALANCE BCE REAL EN MILLONES DE EUROS (JULIO DE CADA AÑO) ---
    balance_bce_millones = [
        721_569, 791_179, 842_370, 765_635, 795_274, 868_840, 979_453, 1_107_838, 1_185_364,
        1_427_348, 1_875_712, 1_986_989, 1_957_194, 3_099_646, 2_403_333, 2_062_474, 2_518_972,
        3_249_177, 4_229_286, 4_599_857, 4_684_376, 6_322_604, 7_950_657, 8_765_687, 7_205_494,
        6_494_463, 6_118_884
    ]  # en millones de euros

    if 'animation_year_idx' not in st.session_state:
        st.session_state['animation_year_idx'] = 0
    if 'animation_finished' not in st.session_state:
        st.session_state['animation_finished'] = False

    idx = st.session_state['animation_year_idx']
    current_year = years[idx]
    current_gold_price = gold_prices[idx]
    gold_you_can_buy = cash / current_gold_price

    st.markdown(f"""
    <div class="main-text">
        Año: <b style="font-size:1.22em;">{current_year}</b>
    </div>
    <div class="main-text" style="color:#215312; font-size:1.11em; margin-top:-7px;">
        Con <b style="color:#228B22;">100.000 €</b> en <b>{current_year}</b> puedes comprar:
    </div>
    """, unsafe_allow_html=True)

    # --- Onzas de oro centradas y visuales ---
    st.markdown(f"""
    <div class="gold-metric-block">
        <div class="gold-label">
            <span class="gold-coin"></span>
            Onzas de oro
        </div>
        <div class="gold-value">{gold_you_can_buy:.1f}</div>
        <div class="gold-caption">Precio oro: <b>{current_gold_price:,.1f} €</b></div>
    </div>
    """, unsafe_allow_html=True)

    # --- Gráfica doble (oro y balance BCE) ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;font-size:1.25em;font-weight:700;margin-bottom:14px;color:#252d42;">Evolución del poder de compra del euro frente al oro y tamaño del balance real del BCE</div>', unsafe_allow_html=True)
    fig, ax1 = plt.subplots(figsize=(8, 4))
    ozs_hist = cash / gold_prices[:idx+1]
    ax1.plot(years[:idx+1], ozs_hist, marker="o", linewidth=2, color="#2979FF", label="Onzas de oro")
    ax1.set_xlabel("Año", fontsize=13)
    ax1.set_ylabel("Onzas de oro (100.000 €)", fontsize=13, color="#2979FF")
    ax1.tick_params(axis='y', labelcolor="#2979FF")
    ax1.grid(True, alpha=0.25)
    # Punto actual oro
    ax1.scatter([current_year], [gold_you_can_buy], color='#FFD700', edgecolor="#A48413", s=190, label="Año actual", zorder=10)

    # Segundo eje: balance BCE (en billones de €)
    ax2 = ax1.twinx()
    ax2.plot(years[:idx+1], np.array(balance_bce_millones[:idx+1])/1e6, '--', color="#D18900", linewidth=2.6, label="Balance BCE")
    ax2.set_ylabel("Balance BCE (billones €)", fontsize=13, color="#D18900")
    ax2.tick_params(axis='y', labelcolor="#D18900")
    # Leyendas
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper right")
    st.pyplot(fig, use_container_width=True)

    # Feedback visual
    if gold_you_can_buy < 50:
        st.markdown("""
        <div style='text-align:center; margin-top:18px;'>
            <span style='color:#e63946; font-size:1.4em;'>¡Alerta! Tu dinero ya compra muy poco oro... <span style="color:#FFD700;">●</span></span>
        </div>
        """, unsafe_allow_html=True)
    elif gold_you_can_buy < 200:
        st.markdown("""
        <div style='text-align:center; margin-top:16px;'>
            <span style='color:#f4a300; font-size:1.2em;'>El euro cada vez compra menos oro. 😬</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='text-align:center; margin-top:16px;'>
            <span style='color:#1a5f0a; font-size:1.1em;'>En este año, aún puedes comprar mucho oro. <span style="color:#FFD700;">●</span></span>
        </div>
        """, unsafe_allow_html=True)

    # --- Avanza al siguiente año ---
    if not st.session_state['animation_finished']:
        if idx < len(years) - 1:
            time.sleep(0.75)
            st.session_state['animation_year_idx'] += 1
            st.rerun()
        else:
            st.session_state['animation_finished'] = True

    # --- Conclusión final ---
    if st.session_state['animation_finished']:
        st.markdown("<hr style='margin:34px 0;'>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background-color:#f0f8ff; border-left: 7px solid #2b5876; padding: 18px 24px; border-radius:8px; color:#222; margin-top:20px;'>
        <h2 style='color:#2b5876;'>🔔 Conclusión</h2>
        <ul style='font-size:1.08em; color:#222;'>
          <li><b>El euro pierde poder adquisitivo frente al oro de forma muy notable en el tiempo.</b></li>
          <li><b>El tamaño del balance del BCE crece de forma casi constante y está muy correlacionado con la caída del poder adquisitivo de la moneda.</b></li>
          <li><b>La animación muestra de manera visual la depreciación monetaria causada por las políticas del BCE y la inflación acumulada.</b></li>
        </ul>
        <p style='margin-top:10px; font-size:1.02em; color:#384957;'><b>¿Quieres volver a ver la animación?</b> Recarga la página.</p>
        </div>
        """, unsafe_allow_html=True)
