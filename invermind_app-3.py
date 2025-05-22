# invermind_app.py

# Streamlit web app de IA: análisis de mercado + asistente de inversión
import streamlit as st
import openai
import yfinance as yf
import datetime
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="InverMind AI", layout="centered")
st.title("📈 InverMind AI")
st.subheader("Análisis de mercado + Asistente de inversión personalizado")

# Función 1: Asistente de inversión
def generate_portfolio(perfil, capital):
    instrucciones = f"Soy un asesor financiero. Sugiere un portafolio de inversión diversificado para un perfil {perfil} con ${capital}. Incluye acciones, ETFs o criptomonedas, con porcentajes."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": instrucciones}]
        )
        return response.choices[0].message['content']
    except Exception as e:
        return f"Error al generar portafolio: {e}"

# Función 2: Análisis de mercado
def scrape_trending_products(site_url):
    try:
        response = requests.get(site_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        products = [item.text.strip() for item in soup.find_all('h2') if item.text.strip() != ""]
        return products[:10] if products else ["No se encontraron productos en <h2>"]
    except Exception as e:
        return [f"Error al obtener datos del sitio: {e}"]

def analyze_sentiment(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Califica el sentimiento de este texto como positivo, negativo o neutral: {text}"}]
        )
        return response.choices[0].message['content']
    except Exception as e:
        return f"Error: {e}"

def generate_wordcloud(data):
    try:
        wordcloud = WordCloud(width=800, height=400).generate(" ".join(data))
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error al generar la nube de palabras: {e}")

# Interfaz usuario
menu = st.sidebar.radio("Selecciona una herramienta:", ["🔍 Análisis de mercado", "💼 Asistente de inversión"])

if menu == "💼 Asistente de inversión":
    perfil = st.selectbox("Selecciona tu perfil de riesgo:", ["bajo", "medio", "alto"])
    capital = st.number_input("¿Cuánto deseas invertir? (USD)", min_value=100.0, step=50.0)
    if st.button("Generar portafolio"):
        resultado = generate_portfolio(perfil, capital)
        st.markdown("### Tu portafolio sugerido")
        st.write(resultado)

elif menu == "🔍 Análisis de mercado":
    url = st.text_input("Ingresa la URL de un sitio con tendencias (usa https://example.com para prueba):")
    if st.button("Analizar tendencias") and url:
        productos = scrape_trending_products(url)
        if "Error" in productos[0] or "No se encontraron" in productos[0]:
            st.error(productos[0])
        else:
            sentimientos = [analyze_sentiment(p) for p in productos]
            df = pd.DataFrame({'Producto': productos, 'Sentimiento': sentimientos})
            st.dataframe(df)
            st.markdown("### Nube de palabras")
            generate_wordcloud(productos)
