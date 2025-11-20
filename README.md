# Dashboard NO2‚ y T21 - Península de Yucatán

Dashboard interactivo para análisis de datos satelitales de dióxido de nitrógeno (NO2) y temperatura de brillo (T21/incendios) en la Península de Yucatán.

## Datos requeridos

Este proyecto requiere los siguientes archivos en la carpeta raíz:
- `datos_no2_t21.csv`
- `metadata.json`
- Carpeta `monthly_images/` con las imágenes PNG mensuales

## Ejecutar localmente
```bash
pip install -r requirements.txt
streamlit run streamlit_app_optimized.py
```
