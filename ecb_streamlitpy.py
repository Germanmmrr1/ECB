import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# Load your CSV
df = pd.read_csv("pivoted_ecb_items_clean.csv", index_col=0)

st.markdown("""
    <style>
    /* Hide Streamlit's top right menu, 'Share' button, and footer */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .st-emotion-cache-1avcm0n.ezrtsby0 {display: none;} /* GitHub icon menu */
    .stActionButton {display:none;}
    </style>
""", unsafe_allow_html=True)


# Attempt to parse columns to datetime robustly
def robust_date_parse(cols):
    # First, try standard YYYY-MM-DD
    try:
        parsed = pd.to_datetime(cols)
        # If all valid, return
        if not parsed.isnull().any():
            return parsed
    except Exception:
        pass
    # Next, try integer format (yyyymmdd)
    try:
        parsed = pd.to_datetime(cols.astype(str), format='%Y%m%d', errors='coerce')
        if not parsed.isnull().all():
            return parsed
    except Exception:
        pass
    # Try again with string YYYY-MM-DD
    try:
        parsed = pd.to_datetime(cols.astype(str), format='%Y-%m-%d', errors='coerce')
        if not parsed.isnull().all():
            return parsed
    except Exception:
        pass
    # If all fails, just return original
    return cols

df.columns = robust_date_parse(df.columns)

# Print to debug if needed
#print(df.columns)
#print([type(col) for col in df.columns])

# Friendly titles and descriptions
metricas = {
    'Lending to euro area credit institutions related to monetary policy operations denominated in euro': {
        "nombre": "Préstamos del BCE a bancos",
        "desc": "Refleja el total de préstamos que el BCE concede a bancos comerciales de la zona euro para asegurar liquidez y facilitar el crédito en la economía."
    },
    'Securities held for monetary policy purposes': {
        "nombre": "Bonos comprados por el BCE (política monetaria)",
        "desc": "Importe total de bonos y otros activos que el BCE ha comprado para estimular la economía (programas de expansión cuantitativa/QE)."
    },
    'Securities of euro area residents denominated in euro': {
        "nombre": "Bonos de la zona euro en balance",
        "desc": "Muestra el valor de los bonos emitidos por gobiernos y empresas de la zona euro que mantiene el BCE en su balance."
    },
    'Liabilities to euro area credit institutions related to monetary policy operations denominated in euro': {
        "nombre": "Reservas bancarias en el BCE",
        "desc": "Es el dinero que los bancos tienen depositado en el BCE como reservas obligatorias o voluntarias, clave para el funcionamiento del sistema financiero."
    },
    'Banknotes in circulation': {
        "nombre": "Billetes de euro en circulación",
        "desc": "El valor total de billetes de euro en manos del público y empresas; parte central de la base monetaria."
    },
    'Deposit facility': {
        "nombre": "Facilidad de depósito",
        "desc": "Permite a los bancos depositar su exceso de liquidez en el BCE, normalmente a un tipo de interés muy bajo (o incluso negativo en algunos periodos)."
    },
    'Current accounts': {
        "nombre": "Cuentas corrientes de bancos en el BCE",
        "desc": "Saldo total de las cuentas corrientes que los bancos comerciales mantienen en el BCE, utilizado principalmente para pagos entre bancos y reservas mínimas."
    }
}

items_to_plot = list(metricas.keys())

# Centered page title and intro
st.markdown("""
    <h1 style='text-align: center; font-size:2.5em; margin-bottom: 0.3em;'>
        Análisis del Balance del BCE y su Influencia en la Economía Europea
    </h1>
""", unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center; font-size:1.1em; margin-bottom: 2em;'>
    <ul style='list-style-type: disc; display: inline-block; text-align: left;'>
        <li><b>Visualiza</b> cómo ha cambiado el balance del BCE desde 1999 hasta hoy.</li>
        <li><b>Descubre</b> de forma sencilla los principales conceptos del balance: activos, préstamos, bonos, billetes y reservas.</li>
        <li><b>Comprende</b> cómo las decisiones del BCE influyen en la economía y la inflación de la zona euro.</li>
        <li><b>Gráficos claros</b> y explicaciones en español, pensadas para todos los públicos.</li>
        <li><b>Fuente de datos:</b> Banco Central Europeo (BCE).</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.image("bce_animacion.gif", use_container_width=True)

# Custom CSS for centered chart titles
st.markdown("""
    <style>
    .centered-title {
        text-align: center;
        font-size: 1.4em !important;
        font-weight: 600;
        margin-top: 32px;
        margin-bottom: 0px;
    }
    </style>
""", unsafe_allow_html=True)

# Total Assets chart at the top
st.markdown(f'<div class="centered-title">Evolución total de activos del BCE</div>', unsafe_allow_html=True)
if "Assets" in df.index:
    data = df.loc["Assets"].astype(float)
    # Plot using columns as x (should now be datetime)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df.columns, data.values)
    ax.xaxis.set_major_locator(mdates.YearLocator(base=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_xlim(df.columns[0], df.columns[-1])
    ax.set_xlabel("Año")
    ax.set_ylabel("Millones de euros")
    ax.grid(True)
    plt.tight_layout()
    st.pyplot(fig)
    st.caption(
        "Este gráfico muestra la evolución del total de activos en el balance del BCE desde 1999. "
        "El total de activos representa el tamaño del balance del banco central: cuanto más alto, más dinero y liquidez ha creado el BCE para apoyar la economía de la zona euro. "
        "Un fuerte aumento suele estar ligado a políticas de estímulo como la compra masiva de activos (expansión cuantitativa) o a respuestas ante crisis económicas."
    )
else:
    st.warning("No se encuentra la línea 'Assets' en los datos.")

# Plot each key metric
for item in items_to_plot:
    if item in df.index:
        nombre = metricas[item]["nombre"]
        desc = metricas[item]["desc"]

        st.markdown(f'<div class="centered-title">{nombre}</div>', unsafe_allow_html=True)

        data = df.loc[item].astype(float)
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df.columns, data.values)
        ax.xaxis.set_major_locator(mdates.YearLocator(base=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.set_xlim(df.columns[0], df.columns[-1])
        ax.set_xlabel("Año")
        ax.set_ylabel("Millones de euros")
        ax.grid(True)
        plt.tight_layout()
        st.pyplot(fig)
        st.caption(desc)
