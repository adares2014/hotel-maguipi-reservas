import streamlit as st
import pandas as pd
import openai
from datetime import datetime

st.set_page_config(page_title="Asistente de Reservas Magüipi", page_icon="🏖️")

st.title("🏖️ Asistente de Reservas - Hotel Magüipi")

# --- Ingreso de clave OpenAI ---
api_key = st.sidebar.text_input("2E1mGsimsFI81IALLiokLJT9mjY2fPGhFd8BqvAA", type="password")

# --- Cargar Excel ---
@st.cache_data
def cargar_tarifas():
    df = pd.read_excel(r"C:\Users\aaruj\OneDrive\Escritorio/tarifas_maguipi.xlsx")
    df.columns = df.columns.map(str).str.strip()
    df['Temporada'] = df['Temporada'].str.lower()
    df['Aire/Ventilador'] = df['Aire/Ventilador'].str.lower()
    df['NO DE PAX'] = df['NO DE PAX'].str.upper()
    return df

tarifas_df = cargar_tarifas()

# --- Determinar temporada ---
def obtener_temporada(fecha: datetime) -> str:
    a = fecha.year
    bajas = [
        (datetime(a, 1, 15), datetime(a, 4, 12)),
        (datetime(a, 5, 1), datetime(a, 6, 15)),
        (datetime(a, 10, 30), datetime(a, 12, 20))
    ]
    for inicio, fin in bajas:
        if inicio <= fecha <= fin:
            return "baja"
    return "alta"

# --- Buscar tarifa ---
def buscar_tarifa(temporada, tipo, noches, pax):
    pax = str(pax)
    noches = noches.upper()
    resultado = tarifas_df[
        (tarifas_df['Temporada'] == temporada) &
        (tarifas_df['Aire/Ventilador'].str.contains(tipo)) &
        (tarifas_df['NO DE PAX'] == noches)
    ]
    if resultado.empty:
        return None
    return resultado.iloc[0][pax]

# --- Inicializar historial de mensajes ---
if "chat" not in st.session_state:
    st.session_state.chat = []

# --- Mostrar historial como burbujas ---
for msg in st.session_state.chat:
    if msg["role"] == "user":
        st.chat_message("user").markdown(msg["content"])
    else:
        st.chat_message("assistant").markdown(msg["content"])

# --- Entrada del usuario ---
prompt = st.chat_input("Escribe tu solicitud de reserva...")

if prompt and api_key:
    openai.api_key = api_key
    st.session_state.chat.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)

    # --- Definir comportamiento del bot ---
    system_prompt = (
        "Eres Lucelcy, asesora virtual del Hotel Magüipi. "
        "Tu trabajo es ayudar a los clientes a cotizar reservas. "
        "Solicita fechas, cantidad de personas y tipo de habitación. "
        "Responde de forma amable, clara y usa emojis si es apropiado. "
        "Cuando tengas los datos, llama a la función de Python para calcular el valor."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": system_prompt}] + st.session_state.chat
        )
        respuesta = response.choices[0].message.content
        st.session_state.chat.append({"role": "assistant", "content": respuesta})
        st.chat_message("assistant").markdown(respuesta)

    except Exception as e:
        st.chat_message("assistant").markdown(f"⚠️ Error al conectar con OpenAI: {e}")

elif prompt and not api_key:
    st.warning("Debes ingresar tu OpenAI API Key en la barra lateral.")
