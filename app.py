import streamlit as st
import pandas as pd
import ezdxf  # Librería para crear archivos de AutoCAD

st.set_page_config(layout="wide", page_title="NOVOSA Pro: CAD-Migrator")

st.title("🏗️ NOVOSA - Generador de Capas para AutoCAD")

st.info("""
**Flujo de Trabajo Pro:**
1. Sube tu catálogo (Excel o CSV).
2. Descarga el archivo DXF.
3. Ábrelo en AutoCAD y 'calca' usando las capas automáticas.
""")

# 1. Carga del Catálogo
cat_file = st.file_uploader("Subir Catálogo de Conceptos (Excel o CSV)", type=["xlsx", "csv"])

if cat_file:
    # Leer el archivo dependiendo del formato
    if cat_file.name.endswith('.xlsx'):
        df_cat = pd.read_excel(cat_file)
    else:
        df_cat = pd.read_csv(cat_file)
    
    st.write("### Vista previa del catálogo detectado:")
    st.dataframe(df_cat.head())

    # 2. Generación del archivo DXF
    if st.button("🚀 GENERAR ARCHIVO DE CAPAS PARA AUTOCAD"):
        # Crear un nuevo dibujo DXF
        doc = ezdxf.new('R2010') # Versión compatible con casi cualquier AutoCAD
        
        # Intentar encontrar la columna de conceptos
        # Buscamos columnas que se llamen 'Concepto', 'Nombre' o la primera columna
        col_name = df_cat.columns[0]
        for col in df_cat.columns:
            if 'concepto' in col.lower() or 'descripcion' in col.lower():
                col_name = col
                break
        
        conceptos = df_cat[col_name].unique()
        
        # Crear una capa por cada concepto
        for concepto in conceptos:
            # Limpiar el nombre (AutoCAD no acepta ciertos caracteres en capas)
            nombre_capa = str(concepto)[:31].replace("/", "-").replace(":", "-")
            if nombre_capa not in doc.layers:
                doc.layers.new(name=nombre_capa)
        
        # Guardar en memoria
        import io
        buf = io.StringIO()
        doc.write(buf)
        dxf_content = buf.getvalue()
        
        st.success(f"✅ Se han creado {len(conceptos)} capas basadas en tu catálogo.")
        
        st.download_button(
            label="📥 DESCARGAR PLANTILLA (.DXF)",
            data=dxf_content,
            file_name="Plantilla_Capas_NOVOSA.dxf",
            mime="application/dxf"
        )

st.divider()
st.caption("Próximo paso: Creador de extractor de medidas desde archivos DWG/DXF dibujados.")
