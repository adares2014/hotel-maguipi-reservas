import streamlit as st
import openai

st.set_page_config(page_title="Test Clave OpenAI", page_icon="🔑")
st.title("🔑 Test de API Key de OpenAI")

api_key = st.text_input("Ingresa tu clave OpenAI (sk-...):", type="password")

if api_key:
    try:
        client = openai.OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente amigable."},
                {"role": "user", "content": "¿Cuál es la capital de Francia?"}
            ]
        )

        respuesta = response.choices[0].message.content
        st.success("✅ Clave válida. Respuesta de OpenAI:")
        st.info(respuesta)

    except Exception as e:
        st.error(f"❌ Error al conectar con OpenAI: {e}")
else:
    st.warning("Por favor ingresa tu API Key para hacer la prueba.")
