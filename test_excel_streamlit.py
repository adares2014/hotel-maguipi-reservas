import streamlit as st
import pandas as pd

st.set_page_config(page_title="Test Carga Excel", page_icon="📄")

st.title("📄 Test de Carga de Archivo Excel")

@st.cache_data
def cargar_tarifas():
    df = pd.read_excel("tarifas_maguipi.xlsx")
    df.columns = df.columns.map(str).str.strip()
    return df

try:
    df = cargar_tarifas()
    st.success("Archivo cargado correctamente ✅")
    st.dataframe(df)
except FileNotFoundError:
    st.error("❌ No se encontró el archivo 'tarifas_maguipi.xlsx' en la raíz del proyecto.")
except Exception as e:
    st.error(f"⚠️ Error al cargar el archivo: {e}")
