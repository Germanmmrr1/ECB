import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import io
import base64

# Load your CSV
df = pd.read_csv("pivoted_ecb_items_clean.csv", index_col=0)

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

# Sidebar for controls
st.sidebar.header("Controles del Dashboard")

# Date range selector
min_date = df.columns.min()
max_date = df.columns.max()
date_range = st.sidebar.date_input(
    "Seleccionar rango de fechas:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    key="date_range"
)

# Metric comparison selector
st.sidebar.subheader("Comparación de Métricas")
compare_metrics = st.sidebar.multiselect(
    "Seleccionar métricas para comparar:",
    options=list(metricas.keys()),
    default=[],
    format_func=lambda x: metricas[x]["nombre"]
)

# Chart options
st.sidebar.subheader("Opciones de Visualización")
use_log_scale = st.sidebar.checkbox("Escala logarítmica", value=False)
show_growth_rate = st.sidebar.checkbox("Mostrar tasa de crecimiento (%)", value=False)
show_moving_avg = st.sidebar.checkbox("Mostrar media móvil (12 períodos)", value=False)
show_crisis_periods = st.sidebar.checkbox("Destacar períodos de crisis", value=True)

# Filter data based on date range
if len(date_range) == 2:
    start_date, end_date = date_range
    mask = (df.columns >= pd.Timestamp(start_date)) & (df.columns <= pd.Timestamp(end_date))
    df_filtered = df.loc[:, mask]
else:
    df_filtered = df

# Crisis periods definition
crisis_periods = [
    {"name": "Crisis Financiera Global", "start": "2008-01-01", "end": "2009-12-31", "color": "rgba(255,0,0,0.2)"},
    {"name": "Crisis Deuda Europea", "start": "2010-01-01", "end": "2012-12-31", "color": "rgba(255,165,0,0.2)"},
    {"name": "Pandemia COVID-19", "start": "2020-03-01", "end": "2021-12-31", "color": "rgba(128,0,128,0.2)"}
]

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

st.image("bce_animacion.gif", use_column_width=True)

# Metric search functionality
st.subheader("🔍 Búsqueda de Métricas")
search_term = st.text_input("Buscar métrica:", placeholder="Ej: préstamos, bonos, reservas...")

if search_term:
    filtered_metrics = {k: v for k, v in metricas.items() 
                       if search_term.lower() in v["nombre"].lower() or search_term.lower() in v["desc"].lower()}
    if filtered_metrics:
        st.write(f"Encontradas {len(filtered_metrics)} métricas:")
        for key, value in filtered_metrics.items():
            st.write(f"• **{value['nombre']}**: {value['desc']}")
    else:
        st.write("No se encontraron métricas que coincidan con la búsqueda.")

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

# Mobile-friendly responsive design improvements
st.markdown("""
    <style>
    @media (max-width: 768px) {
        .stPlotlyChart {
            height: 400px !important;
        }
        .centered-title {
            font-size: 1.2em !important;
        }
        .sidebar .sidebar-content {
            width: 250px;
        }
    }
    
    .metric-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    
    .glossary-term {
        background: #e3f2fd;
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-left: 4px solid #2196f3;
        border-radius: 0.25rem;
    }
    
    .event-timeline {
        border-left: 3px solid #ff9800;
        padding-left: 1rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Helper function to create interactive charts
def create_interactive_chart(data_dict, title, y_label, description, show_comparison=False):
    fig = go.Figure()
    
    for item_name, data_info in data_dict.items():
        data = data_info['data']
        name = data_info['name']
        
        # Apply transformations based on options
        if show_growth_rate and len(data) > 1:
            data = data.pct_change() * 100
            y_label = "Tasa de crecimiento (%)"
        
        # Add main line
        fig.add_trace(go.Scatter(
            x=df_filtered.columns,
            y=data.values,
            mode='lines',
            name=name,
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Fecha: %{x}<br>' +
                         'Valor: %{y:,.0f}<br>' +
                         '<extra></extra>',
            line=dict(width=2)
        ))
        
        # Add moving average if requested
        if show_moving_avg and len(data) >= 12:
            ma_data = data.rolling(window=12).mean()
            fig.add_trace(go.Scatter(
                x=df_filtered.columns,
                y=ma_data.values,
                mode='lines',
                name=f"{name} (MA 12)",
                line=dict(dash='dash', width=1),
                opacity=0.7,
                hovertemplate='<b>%{fullData.name}</b><br>' +
                             'Fecha: %{x}<br>' +
                             'Valor: %{y:,.0f}<br>' +
                             '<extra></extra>'
            ))
    
    # Add crisis period shading
    if show_crisis_periods:
        for crisis in crisis_periods:
            crisis_start = pd.Timestamp(crisis['start'])
            crisis_end = pd.Timestamp(crisis['end'])
            if crisis_start <= df_filtered.columns.max() and crisis_end >= df_filtered.columns.min():
                fig.add_vrect(
                    x0=crisis_start, x1=crisis_end,
                    fillcolor=crisis['color'],
                    layer="below",
                    line_width=0,
                    annotation_text=crisis['name'],
                    annotation_position="top"
                )
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="Año",
        yaxis_title=y_label,
        yaxis_type="log" if use_log_scale else "linear",
        hovermode='x unified',
        height=500,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_xaxes(showgrid=True)
    fig.update_yaxes(showgrid=True)
    
    return fig

# Function to create download link
def create_download_link(data, filename, link_text):
    csv = data.to_csv(index=True)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{link_text}</a>'
    return href

# Metric comparison section
if compare_metrics:
    st.markdown('<div class="centered-title">Comparación de Métricas Seleccionadas</div>', unsafe_allow_html=True)
    
    comparison_data = {}
    for metric in compare_metrics:
        if metric in df_filtered.index:
            comparison_data[metric] = {
                'data': df_filtered.loc[metric].astype(float),
                'name': metricas[metric]["nombre"]
            }
    
    if comparison_data:
        comparison_fig = create_interactive_chart(
            comparison_data, 
            "Comparación de Métricas del BCE",
            "Millones de euros",
            "Comparación de las métricas seleccionadas",
            show_comparison=True
        )
        st.plotly_chart(comparison_fig, use_container_width=True)
        
        # Export functionality for comparison
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Exportar datos de comparación (CSV)"):
                comparison_df = pd.DataFrame({metricas[k]['nombre']: v['data'] for k, v in comparison_data.items()})
                st.markdown(create_download_link(comparison_df, "comparacion_metricas_bce.csv", "Descargar CSV"), unsafe_allow_html=True)
        
        st.markdown("---")

# Total Assets chart at the top
st.markdown(f'<div class="centered-title">Evolución total de activos del BCE</div>', unsafe_allow_html=True)
if "Assets" in df_filtered.index:
    assets_data = {
        'Assets': {
            'data': df_filtered.loc["Assets"].astype(float),
            'name': 'Total de Activos'
        }
    }
    
    assets_fig = create_interactive_chart(
        assets_data,
        "Evolución del Total de Activos del BCE",
        "Millones de euros",
        "Evolución histórica del balance total"
    )
    
    st.plotly_chart(assets_fig, use_container_width=True)
    
    # Export functionality for assets
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Exportar datos de activos (CSV)"):
            assets_df = pd.DataFrame({'Total_Activos': df_filtered.loc['Assets'].astype(float)})
            st.markdown(create_download_link(assets_df, "activos_totales_bce.csv", "Descargar CSV"), unsafe_allow_html=True)
    
    st.caption(
        "Este gráfico muestra la evolución del total de activos en el balance del BCE desde 1999. "
        "El total de activos representa el tamaño del balance del banco central: cuanto más alto, más dinero y liquidez ha creado el BCE para apoyar la economía de la zona euro. "
        "Un fuerte aumento suele estar ligado a políticas de estímulo como la compra masiva de activos (expansión cuantitativa) o a respuestas ante crisis económicas."
    )
else:
    st.warning("No se encuentra la línea 'Assets' en los datos.")

# Plot each key metric
for item in items_to_plot:
    if item in df_filtered.index:
        nombre = metricas[item]["nombre"]
        desc = metricas[item]["desc"]

        st.markdown(f'<div class="centered-title">{nombre}</div>', unsafe_allow_html=True)

        metric_data = {
            item: {
                'data': df_filtered.loc[item].astype(float),
                'name': nombre
            }
        }
        
        metric_fig = create_interactive_chart(
            metric_data,
            nombre,
            "Millones de euros",
            desc
        )
        
        st.plotly_chart(metric_fig, use_container_width=True)
        
        # Export functionality for individual metrics
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"📊 Exportar {nombre} (CSV)", key=f"export_{item}"):
                metric_df = pd.DataFrame({nombre: df_filtered.loc[item].astype(float)})
                filename = f"{nombre.lower().replace(' ', '_')}_bce.csv"
                st.markdown(create_download_link(metric_df, filename, "Descargar CSV"), unsafe_allow_html=True)
        
        st.caption(desc)
        st.markdown("---")

# Glossary section
st.markdown('<div class="centered-title">📚 Glosario de Términos Económicos</div>', unsafe_allow_html=True)

with st.expander("🔍 Ver Glosario Completo"):
    glossary_terms = {
        "Balance del BCE": "Documento contable que muestra todos los activos (lo que posee) y pasivos (lo que debe) del Banco Central Europeo en un momento determinado.",
        "Expansión Cuantitativa (QE)": "Política monetaria no convencional donde el banco central compra grandes cantidades de bonos del gobierno y corporativos para inyectar dinero en la economía.",
        "Facilidad de Depósito": "Herramienta que permite a los bancos depositar dinero en el BCE durante la noche, generalmente a un tipo de interés muy bajo o negativo.",
        "Reservas Bancarias": "Dinero que los bancos comerciales mantienen en depósito en el banco central, ya sea por requisitos legales o por elección propia.",
        "Operaciones de Política Monetaria": "Transacciones realizadas por el BCE para influir en la cantidad de dinero en circulación y los tipos de interés.",
        "Base Monetaria": "Total de dinero en circulación (billetes y monedas) más las reservas bancarias en el banco central.",
        "Liquidez": "Capacidad de convertir rápidamente activos en efectivo sin afectar significativamente su precio de mercado.",
        "Zona Euro": "Región económica compuesta por los países de la Unión Europea que han adoptado el euro como moneda oficial."
    }
    
    for term, definition in glossary_terms.items():
        st.markdown(f"**{term}**: {definition}")
        st.markdown("")

# Major economic events annotations
st.markdown('<div class="centered-title">📊 Eventos Económicos Importantes</div>', unsafe_allow_html=True)

with st.expander("📅 Ver Cronología de Eventos Clave"):
    economic_events = [
        {
            "fecha": "1999",
            "evento": "Lanzamiento del Euro",
            "descripcion": "Inicio de la Unión Económica y Monetaria. El BCE comienza sus operaciones y el euro se introduce como moneda única."
        },
        {
            "fecha": "2001",
            "evento": "Crisis de las Puntocom",
            "descripcion": "Explosión de la burbuja tecnológica que affectó los mercados globales y llevó a una recesión."
        },
        {
            "fecha": "2008-2009",
            "evento": "Crisis Financiera Global",
            "descripcion": "La crisis de las hipotecas subprime en EE.UU. se extiende globalmente. El BCE reduce tipos de interés y aumenta la liquidez."
        },
        {
            "fecha": "2010-2012",
            "evento": "Crisis de Deuda Europea",
            "descripcion": "Crisis de deuda soberana en varios países de la eurozona (Grecia, Irlanda, Portugal, España). El BCE implementa programas de rescate."
        },
        {
            "fecha": "2012",
            "evento": "'Whatever it takes' - Mario Draghi",
            "descripcion": "Declaración del presidente del BCE que calmó los mercados y marcó el inicio de políticas más agresivas."
        },
        {
            "fecha": "2015",
            "evento": "Inicio del QE Europeo",
            "descripcion": "El BCE lanza su programa de compra de activos (PSPP) para combatir la deflación y estimular el crecimiento."
        },
        {
            "fecha": "2020-2021",
            "evento": "Pandemia COVID-19",
            "descripcion": "El BCE lanza el PEPP (Pandemic Emergency Purchase Programme) por 1.85 billones de euros para mitigar el impacto económico."
        },
        {
            "fecha": "2022-2023",
            "evento": "Inflación Post-Pandemia",
            "descripcion": "El BCE comienza a subir tipos de interés para combatir la inflación más alta en décadas, exacerbada por la guerra en Ucrania."
        }
    ]
    
    for event in economic_events:
        st.markdown(f"### {event['fecha']}: {event['evento']}")
        st.markdown(f"{event['descripcion']}")
        st.markdown("---")

# Footer with additional information
st.markdown("""
---
### 📊 Información Adicional

**Fuente de Datos**: Banco Central Europeo (BCE) - Statistical Data Warehouse  
**Frecuencia**: Datos semanales desde enero de 1999  
**Unidades**: Millones de euros  
**Última Actualización**: Los datos se actualizan semanalmente

**Nota**: Este dashboard está diseñado con fines educativos para facilitar la comprensión de la política monetaria europea y su impacto en la economía.
""")
