import streamlit as st
import pandas as pd
import openai
from datetime import datetime
from dotenv import load_dotenv
import os

# Cargar variable de entorno desde archivo .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Asistente de Reservas Magüipi", page_icon="🏖️")

st.title("🏖️ Asistente de Reservas - Hotel Magüipi")

# --- Cargar Excel ---
@st.cache_data
def cargar_tarifas():
    df = pd.read_excel("tarifas_maguipi.xlsx")
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
def calcular_reserva(fecha: str, noches: int, cantidad_personas: int, tipo_habitacion: str) -> str:
    try:
        fecha_dt = datetime.strptime(fecha + " 2025", "%d de %B %Y")
        temporada = obtener_temporada(fecha_dt)
        pax = str(cantidad_personas)

        noches_str = {
            1: "1N2D",
            2: "2N3D",
            3: "3N4D",
            4: "4N5D",
            5: "5N6D",
            6: "6N7D"
        }.get(noches, "2N3D")

        tipo = tipo_habitacion.lower()
        if "ventilador" in tipo:
            tipo = "ventilador"
        elif "aire" in tipo:
            tipo = "aire acondicionado"

        resultado = tarifas_df[
            (tarifas_df['Temporada'] == temporada) &
            (tarifas_df['Aire/Ventilador'].str.contains(tipo)) &
            (tarifas_df['NO DE PAX'] == noches_str)
        ]

        if resultado.empty:
            return "No se encontró una tarifa para esos criterios."

        valor = resultado.iloc[0][pax]

        return (
            f"🏨 Reserva para {cantidad_personas} persona(s) en habitación con {tipo},\n"
            f"🗓️ Fecha: {fecha_dt.strftime('%d de %B de %Y')} - {noches} noche(s)\n"
            f"🌺 Temporada: {temporada.upper()}\n"
            f"💰 Tarifa total: ${valor:,.0f} COP\n\n¡Gracias por consultar! 😊"
        )
    except Exception as e:
        return f"Lo siento, no pude calcular la reserva. Error: {e}"

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
    client = openai.OpenAI(api_key=api_key)
    st.session_state.chat.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)

    # --- System prompt con instrucciones ---
    system_prompt = (
        "Eres Lucelcy, asesora virtual del Hotel Magüipi.\n"
        "Actúas como vendedora del hotel y asistes a los clientes con reservas.\n"
        "Identificas fecha, número de personas, cantidad de noches y tipo de habitación.\n"
        "Puedes interpretar lenguaje informal como 'con ventilador', 'cuarto con airecito', 'pieza con abanico', etc.\n"
        "Cuando tengas los datos, usas la función calcular_reserva(fecha, noches, cantidad_personas, tipo_habitacion).\n"
        "Nunca llames a calcular_precio.\n"
        "Habla con calidez, usa emojis y responde como una vendedora cordial.\n"
        "Si falta información, pídela amablemente."
    )

    try:
        if "reserva(" in prompt:
            for palabra in ["calcular_precio(", "calculando_reserva(", "cotizar_reserva("]:
                prompt = prompt.replace(palabra, "calcular_reserva(")

            args = prompt.replace("calcular_reserva(", "").replace(")", "")
            partes = [x.split("=")[-1].strip().strip('"') for x in args.split(",")]
            respuesta = calcular_reserva(*partes)
        else:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": system_prompt}] + st.session_state.chat
            )
            respuesta = response.choices[0].message.content

        st.session_state.chat.append({"role": "assistant", "content": respuesta})
        st.chat_message("assistant").markdown(respuesta)

    except Exception as e:
        st.chat_message("assistant").markdown(f"⚠️ Error al conectar con OpenAI: {e}")

elif prompt and not api_key:
    st.warning("No se pudo cargar la clave OpenAI desde el archivo .env")
