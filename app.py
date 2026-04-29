import streamlit as st
import pandas as pd
import fitz, io
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates

st.set_page_config(layout="wide", page_title="NOVOSA Pro")

@st.cache_data
def get_img(b, z):
    d = fitz.open(stream=b, filetype="pdf")
    p = d.load_page(0).get_pixmap(matrix=fitz.Matrix(z, z))
    return Image.open(io.BytesIO(p.tobytes("png"))).convert("RGB")

if 'db' not in st.session_state: st.session_state.db = pd.DataFrame(columns=['Eje', 'Largo', 'Alto', 'Total'])
if 'sc' not in st.session_state: st.session_state.sc = 1.0
if 'pts' not in st.session_state: st.session_state.pts = []

st.title("🏗️ NOVOSA - Medidor")

with st.sidebar:
    f = st.file_uploader("Subir PDF", type="pdf")
    z = st.slider("Zoom", 0.5, 3.0, 1.5)
    st.divider()
    dist_real = st.number_input("1. Valor de Cota (m)", value=1.0)
    if st.button("2. 📏 CALIBRAR CON PUNTOS"):
        if len(st.session_state.pts) == 2:
            p1, p2 = st.session_state.pts
            px = ((p2['x']-p1['x'])**2 + (p2['y']-p1['y'])**2)**0.5
            st.session_state.sc = dist_real / px
            st.success("Escala ajustada")
            st.session_state.pts = []
            st.rerun()
    st.divider()
    eje = st.text_input("Eje", "Eje 1")
    alt = st.number_input("Altura (m)", value=2.5)

if f:
    img = get_img(f.read(), z)
    dib = img.copy(); can = ImageDraw.Draw(dib)
    for i, p in enumerate(st.session_state.pts):
        can.ellipse((p['x']-5, p['y']-5, p['x']+5, p['y']+5), fill="red")
        if i > 0: can.line((st.session_state.pts[i-1]['x'], st.session_state.pts[i-1]['y'], p['x'], p['y']), fill="red", width=3)

    c1, c2 = st.columns([2, 1])
    with c1:
        out = streamlit_image_coordinates(dib, key="v_final")
        if out and (not st.session_state.pts or out != st.session_state.pts[-1]):
            if len(st.session_state.pts) >= 2: st.session_state.pts = [out]
            else: st.session_state.pts.append(out)
            st.rerun()
        
        if len(st.session_state.pts) == 2:
            p1, p2 = st.session_state.pts
            dpx = ((p2['x']-p1['x'])**2 + (p2['y']-p1['y'])**2)**0.5
            m = round(dpx * st.session_state.sc, 2)
            st.write(f"### Medida: {m} m")
            if st.button("💾 GUARDAR TRAMO"):
                row = pd.DataFrame([{'Eje': eje, 'Largo': m, 'Alto': alt, 'Total': round(m*alt, 2)}])
                st.session_state.db = pd.concat([st.session_state.db, row], ignore_index=True)
                st.session_state.pts = []
                st.rerun()

    with c2:
        st.dataframe(st.session_state.db, use_container_width=True)
        if not st.session_state.db.empty:
            csv = st.session_state.db.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 EXCEL", csv, "medidas.csv", "text/csv")
