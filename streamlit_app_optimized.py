"""
Dashboard Interactivo - NO₂ y T21 (Incendios) en la Península de Yucatán
Datos satelitales 2024 - Google Earth Engine
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from pathlib import Path
from PIL import Image
import numpy as np
import os

# ============================================
# CONFIGURACIÓN DE PÁGINA
# ============================================
st.set_page_config(
    page_title="NO₂ y T21 - Península de Yucatán",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CONFIGURACIÓN DE RUTAS DE DATOS
# ============================================
# Cambia esta ruta si guardaste los datos en otra carpeta:
DATA_DIR = "."

# ============================================
# ESTILOS CSS PERSONALIZADOS
# ============================================

# Selector de tema
theme = st.session_state.get('theme', 'Claro')
theme = st.radio('Tema:', ['Claro', 'Oscuro'], horizontal=True, key='theme_selector')
st.session_state['theme'] = theme

if theme == 'Oscuro':
    st.markdown("""
        <style>
        body {
            background-color: #181818;
            color: #f0f0f0;
        }
        .main-title {
            font-size: 2.8rem;
            font-weight: 700;
            background: linear-gradient(120deg, #00c6fb 0%, #005bea 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        .subtitle {
            font-size: 1.3rem;
            color: #f0f0f0;
            margin-bottom: 2rem;
        }
        .metric-container {
            background: linear-gradient(135deg, #232526 0%, #414345 100%);
            padding: 1.5rem;
            border-radius: 15px;
            color: #f0f0f0;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .info-box {
            background: #232526;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #00c6fb;
            color: #f0f0f0;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 10px 20px;
            background-color: #232526;
            border-radius: 10px 10px 0 0;
            color: #f0f0f0;
        }
        img {
            max-width: 100%;
            height: auto;
        }
        .stImage {
            margin: 0 auto;
        }
        </style>
    """, unsafe_allow_html=True)
    plotly_template = 'plotly_dark'
else:
    st.markdown("""
        <style>
        body {
            background-color: white;
            color: #222;
        }
        .main-title {
            font-size: 2.8rem;
            font-weight: 700;
            background: linear-gradient(120deg, #1f77b4 0%, #2ca02c 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        .subtitle {
            font-size: 1.3rem;
            color: #666;
            margin-bottom: 2rem;
        }
        .metric-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 15px;
            color: white;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .info-box {
            background: #f0f2f6;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #1f77b4;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 10px 20px;
            background-color: #f0f2f6;
            border-radius: 10px 10px 0 0;
        }
        img {
            max-width: 100%;
            height: auto;
        }
        .stImage {
            margin: 0 auto;
        }
        </style>
    """, unsafe_allow_html=True)
    plotly_template = 'plotly_white'

# ============================================
# FUNCIÓN PARA CARGAR DATOS
# ============================================
@st.cache_data
def load_data():
    """Cargar datos del CSV y metadata"""
    try:
        csv_path = os.path.join(DATA_DIR, 'datos_no2_t21.csv')
        metadata_path = os.path.join(DATA_DIR, 'metadata.json')
        
        df = pd.read_csv(csv_path)
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        return df, metadata, None
    except FileNotFoundError as e:
        error_msg = (
            f"⚠️ **Archivos no encontrados en: {os.path.abspath(DATA_DIR)}**\n\n"
            "Debes ejecutar primero el script de descarga:\n\n"
            "python 01_download_data.py\n\n"
            "Asegúrate de que DATA_DIR en app.py coincida con OUTPUT_DIR en 01_download_data.py\n\n"
            "Archivos esperados:\n"
            f"- {csv_path}\n"
            f"- {metadata_path}\n"
            f"- {os.path.join(DATA_DIR, 'monthly_images')}/"
        )
        return None, None, error_msg

# ============================================
# CARGAR DATOS
# ============================================
df, metadata, error = load_data()

if error:
    st.error(error)
    st.info("💡 Asegúrate de haber autenticado Earth Engine antes de ejecutar el script")
    st.code("import ee\nee.Authenticate()\nee.Initialize(project='tu-proyecto')")
    st.stop()

# ============================================
# ENCABEZADO
# ============================================
st.markdown('<p class="main-title">🌍 NO₂ y T21 (Incendios) en la Península de Yucatán</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Análisis de datos satelitales mensuales - 2024</p>', unsafe_allow_html=True)

# ============================================
## CONTROLES SUPERIORES
available_months = sorted(df['Fecha'].dt.strftime('%Y-%m').unique().tolist())
with st.container():
    col1, col2, col3, col4 = st.columns([2,2,2,3])
    with col1:
        selected_month = st.selectbox(
            "📅 Selecciona el mes:",
            options=available_months,
            index=len(available_months)-1
        )
    selected_data = df[df['Fecha'].dt.strftime('%Y-%m') == selected_month].iloc[0]
    with col2:
        st.metric(
            "NO₂ (Dióxido de Nitrógeno)",
            f"{selected_data['NO2']:.2e} mol/m²"
        )
    with col3:
        st.metric(
            "T21 (Temperatura de Brillo)",
            f"{selected_data['T21']:.1f} K"
        )
    with col4:
        if len(df) > 1:
            current_idx = df[df['Fecha'].dt.strftime('%Y-%m') == selected_month].index[0]
            if current_idx > 0:
                prev_no2 = df.iloc[current_idx - 1]['NO2']
                prev_t21 = df.iloc[current_idx - 1]['T21']
                delta_no2 = ((selected_data['NO2'] - prev_no2) / prev_no2) * 100
                delta_t21 = selected_data['T21'] - prev_t21
                st.metric(
                    "Δ NO₂",
                    f"{delta_no2:+.1f}%",
                    delta=f"{delta_no2:+.1f}%"
                )
                st.metric(
                    "Δ T21",
                    f"{delta_t21:+.1f} K",
                    delta=f"{delta_t21:+.1f} K"
                )
        st.info("💡 Usa las pestañas superiores para explorar diferentes visualizaciones", icon="ℹ️")

# ============================================
# TABS PRINCIPALES
# ============================================
tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Mapa Interactivo", "📊 Series Temporales", "🔗 Análisis de Correlación", "📖 Información"])

# ============================================
# TAB 1: MAPA INTERACTIVO
# ============================================
with tab1:
    st.subheader(f"🗺️ Visualización Espacial - {selected_month}")
    
    image_dir = Path(DATA_DIR) / 'monthly_images'
    
    if not image_dir.exists():
        st.warning("⚠️ Carpeta 'monthly_images' no encontrada. Ejecuta el script de descarga primero.")
    else:
        # Selector de modo de visualización
        view_mode = st.radio(
            "Modo de visualización:",
            ["Comparación lado a lado", "Superposición con control", "Vista individual"],
            horizontal=True
        )
        
        st.markdown("---")
        
        # MODO 1: Comparación lado a lado (default)
        if view_mode == "Comparación lado a lado":
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 💨 NO₂ - Dióxido de Nitrógeno")
                img_path = image_dir / f"no2_{selected_month}.png"
                if img_path.exists():
                    img = Image.open(img_path)
                    st.image(img, use_container_width=True)
                else:
                    st.error(f"Imagen no disponible: {img_path.name}")
            
            with col2:
                st.markdown("#### 🔥 T21 - Temperatura de Brillo (Incendios)")
                img_path = image_dir / f"t21_{selected_month}.png"
                if img_path.exists():
                    img = Image.open(img_path)
                    st.image(img, use_container_width=True)
                else:
                    st.error(f"Imagen no disponible: {img_path.name}")
        
        # MODO 2: Superposición con control de opacidad
        elif view_mode == "Superposición con control":
            st.markdown("#### 🎛️ Mapa Superpuesto con Control de Capas")
            
            # Controles
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                opacity_no2 = st.slider("Opacidad NO₂", 0.0, 1.0, 1.0, 0.1)
            
            with col2:
                opacity_t21 = st.slider("Opacidad T21", 0.0, 1.0, 0.5, 0.1)
            
            with col3:
                blend_mode = st.selectbox("Mezcla", ["Normal", "Multiplicar", "Pantalla"])
            
            # Cargar imágenes
            img_no2_path = image_dir / f"no2_{selected_month}.png"
            img_t21_path = image_dir / f"t21_{selected_month}.png"
            
            if img_no2_path.exists() and img_t21_path.exists():
                from PIL import ImageDraw
                
                # Cargar imágenes
                img_no2 = Image.open(img_no2_path).convert('RGBA')
                img_t21 = Image.open(img_t21_path).convert('RGBA')
                
                # Asegurar mismo tamaño
                if img_no2.size != img_t21.size:
                    img_t21 = img_t21.resize(img_no2.size, Image.Resampling.LANCZOS)
                
                # Crear capa base
                base = Image.new('RGBA', img_no2.size, (255, 255, 255, 255))
                
                # Aplicar opacidad a NO2
                img_no2_alpha = img_no2.copy()
                img_no2_alpha.putalpha(int(255 * opacity_no2))
                
                # Aplicar opacidad a T21
                img_t21_alpha = img_t21.copy()
                img_t21_alpha.putalpha(int(255 * opacity_t21))
                
                # Superponer capas
                result = Image.alpha_composite(base, img_no2_alpha)
                result = Image.alpha_composite(result, img_t21_alpha)
                
                # Mostrar resultado
                st.image(result, use_container_width=True)
                
                # Leyenda
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**NO₂** (Opacidad: {opacity_no2:.0%})")
                with col2:
                    st.markdown(f"**T21** (Opacidad: {opacity_t21:.0%})")
            else:
                st.error("Una o ambas imágenes no están disponibles")
        
        # MODO 3: Vista individual con selector
        else:
            layer_choice = st.radio(
                "Selecciona la capa a visualizar:",
                ["NO₂ - Dióxido de Nitrógeno", "T21 - Temperatura de Brillo (Incendios)"],
                horizontal=True
            )
            
            st.markdown("---")
            
            if "NO₂" in layer_choice:
                st.markdown("#### 💨 NO₂ - Dióxido de Nitrógeno")
                img_path = image_dir / f"no2_{selected_month}.png"
                if img_path.exists():
                    img = Image.open(img_path)
                    st.image(img, use_container_width=True)
                else:
                    st.error(f"Imagen no disponible")
            else:
                st.markdown("#### 🔥 T21 - Temperatura de Brillo (Incendios)")
                img_path = image_dir / f"t21_{selected_month}.png"
                if img_path.exists():
                    img = Image.open(img_path)
                    st.image(img, use_container_width=True)
                else:
                    st.error(f"Imagen no disponible")
        
        # Leyendas en expander (común para todos los modos)
        with st.expander("🎨 Ver Leyendas de Colores", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                **NO₂ (Dióxido de Nitrógeno)**
                - 🟣 Negro/Morado oscuro: Concentraciones muy bajas
                - 🔵 Azul/Morado: Concentraciones bajas
                - 🔴 Rojo: Concentraciones medias
                - 🟠 Naranja: Concentraciones altas
                - 🟡 Amarillo/Blanco: Concentraciones muy altas
                
                **Fuente**: Contaminación atmosférica, tráfico vehicular, industria
                """)
            with col2:
                st.markdown("""
                **T21 (Temperatura de Brillo)**
                - 🟨 Amarillo claro: 300-320K (temperatura normal)
                - 🟧 Naranja: 320-350K (calor moderado)
                - 🔴 Rojo: 350-380K (incendios activos)
                - 🟥 Rojo oscuro: >380K (incendios intensos)
                
                **Fuente**: Detección de incendios forestales y quemas agrícolas
                """)
        
        # Tips de uso
        st.info("""
        💡 **Tips de uso**:
        - **Comparación lado a lado**: Ideal para ver ambos datasets simultáneamente
        - **Superposición con control**: Permite ajustar la transparencia y ver relaciones espaciales
        - **Vista individual**: Enfócate en una sola variable a la vez
        """, icon="ℹ️")

# ============================================
# TAB 2: SERIES TEMPORALES
# ============================================
with tab2:
    st.subheader("📊 Evolución Temporal - Año 2024")
    
    # Gráfico combinado en dos subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('NO₂ - Dióxido de Nitrógeno', 'T21 - Temperatura de Brillo (Incendios)'),
        vertical_spacing=0.15,
        row_heights=[0.5, 0.5]
    )
    
    # Plot NO2
    fig.add_trace(
        go.Scatter(
            x=df['Fecha'],
            y=df['NO2'],
            mode='lines+markers',
            name='NO₂',
            line=dict(color='#E65C5C', width=3),
            marker=dict(size=10, symbol='circle'),
            hovertemplate='<b>%{x|%B %Y}</b><br>NO₂: %{y:.2e} mol/m²<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Línea de tendencia NO2
    z_no2 = np.polyfit(range(len(df)), df['NO2'], 1)
    p_no2 = np.poly1d(z_no2)
    fig.add_trace(
        go.Scatter(
            x=df['Fecha'],
            y=p_no2(range(len(df))),
            mode='lines',
            name='Tendencia NO₂',
            line=dict(color='rgba(230, 92, 92, 0.3)', width=3, dash='dash'),
            showlegend=True
        ),
        row=1, col=1
    )
    
    # Plot T21
    fig.add_trace(
        go.Scatter(
            x=df['Fecha'],
            y=df['T21'],
            mode='lines+markers',
            name='T21',
            line=dict(color='#FD8D3C', width=3),
            marker=dict(size=10, symbol='diamond'),
            hovertemplate='<b>%{x|%B %Y}</b><br>T21: %{y:.1f} K<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Línea de tendencia T21
    z_t21 = np.polyfit(range(len(df)), df['T21'], 1)
    p_t21 = np.poly1d(z_t21)
    fig.add_trace(
        go.Scatter(
            x=df['Fecha'],
            y=p_t21(range(len(df))),
            mode='lines',
            name='Tendencia T21',
            line=dict(color='rgba(253, 141, 60, 0.3)', width=3, dash='dash'),
            showlegend=True
        ),
        row=2, col=1
    )
    
    # Actualizar layout
    fig.update_xaxes(title_text="Mes", row=2, col=1, showgrid=True)
    fig.update_yaxes(title_text="Densidad (mol/m²)", row=1, col=1, showgrid=True)
    fig.update_yaxes(title_text="Temperatura (K)", row=2, col=1, showgrid=True)
    
    fig.update_layout(
        height=800,
        hovermode='x unified',
        showlegend=True,
        template=plotly_template,
        font=dict(size=12, color='#f0f0f0' if theme=='Oscuro' else '#222')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Estadísticas resumidas
    st.markdown("### 📊 Estadísticas del Año 2024")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "NO₂ Promedio",
            f"{df['NO2'].mean():.2e}",
            help="Promedio anual de densidad de columna"
        )
    with col2:
        st.metric(
            "NO₂ Máximo",
            f"{df['NO2'].max():.2e}",
            delta=f"{df['Fecha'][df['NO2'].idxmax()].strftime('%B')}",
            help="Valor máximo y mes de ocurrencia"
        )
    with col3:
        st.metric(
            "T21 Promedio",
            f"{df['T21'].mean():.1f} K",
            help="Promedio anual de temperatura de brillo"
        )
    with col4:
        st.metric(
            "T21 Máximo",
            f"{df['T21'].max():.1f} K",
            delta=f"{df['Fecha'][df['T21'].idxmax()].strftime('%B')}",
            help="Valor máximo y mes de ocurrencia"
        )
    
    # Tabla de datos
    with st.expander("📋 Ver Tabla de Datos Completa"):
        df_display = df.copy()
        df_display['Fecha'] = df_display['Fecha'].dt.strftime('%Y-%m')
        df_display['NO2'] = df_display['NO2'].apply(lambda x: f"{x:.2e}")
        df_display['T21'] = df_display['T21'].apply(lambda x: f"{x:.2f}")
        st.dataframe(df_display, use_container_width=True, hide_index=True)

# ============================================
# TAB 3: ANÁLISIS DE CORRELACIÓN
# ============================================
with tab3:
    st.subheader("🔗 Análisis de Correlación NO₂ vs T21")
    
    # Calcular correlación
    correlation = df['NO2'].corr(df['T21'])
    
    col1, col2 = st.columns([2.5, 1])
    
    with col1:
        # Gráfico de dispersión con línea de tendencia
        fig = go.Figure()
        
        # Puntos de dispersión
        fig.add_trace(go.Scatter(
            x=df['NO2'],
            y=df['T21'],
            mode='markers',
            marker=dict(
                size=15,
                color=df['T21'],
                colorscale='YlOrRd',
                showscale=True,
                colorbar=dict(
                    title="T21 (K)",
                    thickness=15,
                    len=0.7
                ),
                line=dict(width=1, color='white')
            ),
            text=df['Fecha'].dt.strftime('%B %Y'),
            hovertemplate='<b>%{text}</b><br>NO₂: %{x:.2e}<br>T21: %{y:.1f}K<extra></extra>',
            name='Datos mensuales'
        ))
        
        # Línea de tendencia
        z = np.polyfit(df['NO2'], df['T21'], 1)
        p = np.poly1d(z)
        x_trend = np.linspace(df['NO2'].min(), df['NO2'].max(), 100)
        
        fig.add_trace(go.Scatter(
            x=x_trend,
            y=p(x_trend),
            mode='lines',
            name='Línea de tendencia',
            line=dict(color='red', width=3, dash='dash')
        ))
        
        fig.update_layout(
            title='Relación entre NO₂ y Temperatura de Brillo',
            xaxis_title='NO₂ - Densidad de columna (mol/m²)',
            yaxis_title='T21 - Temperatura de Brillo (K)',
            height=550,
            template=plotly_template,
            hovermode='closest',
            font=dict(size=12, color='#f0f0f0' if theme=='Oscuro' else '#222')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Coeficiente de correlación
        st.markdown(f"""
        <div class="metric-container">
            <h3 style="margin: 0; font-size: 1.2rem;">Coeficiente de Correlación</h3>
            <h1 style="margin: 1rem 0; font-size: 4rem;">{correlation:.3f}</h1>
            <p style="margin: 0; font-size: 1rem;">Correlación de Pearson</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Interpretación
        if abs(correlation) < 0.3:
            interpretation = "Correlación Débil"
            color = "#FFC107"
            emoji = "📊"
            desc = "La relación entre las variables es mínima o inexistente."
        elif abs(correlation) < 0.7:
            interpretation = "Correlación Moderada"
            color = "#FF9800"
            emoji = "📈"
            desc = "Existe una relación parcial entre las variables."
        else:
            interpretation = "Correlación Fuerte"
            color = "#F44336"
            emoji = "🔥"
            desc = "Las variables están fuertemente relacionadas."
        
        st.markdown(f"""
        <div style="background: {color}; padding: 1.5rem; border-radius: 10px; color: white;">
            <h3 style="margin: 0;">{emoji} {interpretation}</h3>
            <p style="margin-top: 0.5rem; font-size: 0.95rem;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Explicación
        st.markdown("""
        ### 💡 Interpretación
        
        Una **correlación positiva** indica que cuando aumenta la temperatura 
        de brillo (incendios), también tiende a aumentar el NO₂ en la atmósfera.
        
        Esto sugiere que los **incendios forestales y quemas agrícolas** 
        contribuyen significativamente a las emisiones de dióxido de nitrógeno 
        en la Península de Yucatán.
        """)

# ============================================
# TAB 4: INFORMACIÓN
# ============================================
with tab4:
    st.markdown("""
    ## 📖 Acerca de este Dashboard
    
    ### 🛰️ Fuentes de Datos
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### NO₂ (Dióxido de Nitrógeno)
        
        - **Satélite**: Copernicus Sentinel-5P
        - **Sensor**: TROPOMI
        - **Resolución**: ~7×3.5 km
        - **Variable**: Densidad de columna troposférica
        - **Unidades**: mol/m²
        - **Actualización**: Diaria
        
        El NO₂ es un contaminante atmosférico producido principalmente por:
        - Combustión de vehículos
        - Procesos industriales
        - Incendios y quemas
        - Generación de energía
        """)
    
    with col2:
        st.markdown("""
        #### T21 (Temperatura de Brillo)
        
        - **Sistema**: FIRMS (NASA)
        - **Sensores**: MODIS/VIIRS
        - **Banda**: 4 μm (infrarrojo medio)
        - **Variable**: Temperatura de brillo
        - **Unidades**: Kelvin (K)
        - **Actualización**: Diaria
        
        T21 detecta incendios activos mediante:
        - Anomalías térmicas
        - Puntos de calor
        - Quemas agrícolas
        - Incendios forestales
        """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 🗺️ Región de Estudio
    
    **Península de Yucatán, México**
    - **Estados**: Yucatán, Quintana Roo, Campeche
    - **Coordenadas**: 19.4°N - 21.7°N, 86.7°W - 90.6°W
    - **Superficie**: ~145,000 km²
    - **Ecosistema**: Selva tropical, manglares, zona costera
    - **Periodo analizado**: Enero - Diciembre 2024
    
    ### 🔬 Metodología
    
    1. **Adquisición de datos**: Google Earth Engine API
    2. **Procesamiento temporal**: Promedios mensuales por región
    3. **Análisis estadístico**: Correlación de Pearson
    4. **Visualización**: Dashboard interactivo con Streamlit + Plotly
    
    ### 📊 Hallazgos Clave
    
    - La **temporada de incendios** en la Península de Yucatán ocurre típicamente entre **marzo y mayo** (temporada seca)
    - Los **incendios forestales y quemas agrícolas** contribuyen significativamente a las emisiones de NO₂
    - Existe una **correlación positiva** entre temperatura de brillo (T21) y concentraciones de NO₂
    - Las **áreas urbanas** muestran concentraciones de NO₂ más elevadas de forma constante
    
    ### 🛠️ Tecnologías Utilizadas
    
    - **Google Earth Engine**: Procesamiento de datos satelitales
    - **Python**: Análisis de datos (pandas, numpy)
    - **Streamlit**: Framework de visualización web
    - **Plotly**: Gráficos interactivos
    - **PIL**: Procesamiento de imágenes
    
    ### 📚 Referencias
    
    - [Sentinel-5P TROPOMI](https://sentinels.copernicus.eu/web/sentinel/missions/sentinel-5p)
    - [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/)
    - [Google Earth Engine](https://earthengine.google.com/)
    
    ### 👨‍💻 Desarrollo
    
    Este dashboard fue desarrollado para facilitar el análisis de datos satelitales 
    de calidad del aire e incendios en la Península de Yucatán.
    
    ---
    
    💡 **Sugerencia**: Usa este dashboard para identificar patrones estacionales, 
    correlacionar eventos de incendios con calidad del aire, y analizar tendencias 
    temporales de contaminación atmosférica.
    """)

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem 0;">
    <p style="margin: 0;">🌍 Desarrollado con Streamlit | Datos: Google Earth Engine</p>
    <p style="margin: 0; font-size: 0.9rem;">Península de Yucatán - Análisis Satelital 2024</p>
</div>
""", unsafe_allow_html=True)

