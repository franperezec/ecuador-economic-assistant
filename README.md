# 🇪🇨 Ecuador Economic Data Assistant

## 🎯 Propósito
- Asistente IA con **RAG** para consultar datos económicos FMI de Ecuador (1980-2030 (previsiones)).
- **Indicadores Principales**: PIB, Inflación, Desempleo, Deuda Pública, Cuenta Corriente, PIB p.c.

## ✨ Características Clave
- Chat RAG inteligente.
- Visualizaciones interactivas (Plotly).
- Dashboard económico.
- Búsqueda semántica.

## 🛠️ Stack Tecnológico
- **App**: Streamlit.
- **IA/RAG**: FAISS, Sentence Transformers, Anthropic Claude.
- **Datos**: Pandas.

## 🚀 Uso Rápido

### Local
1.  `git clone <URL_REPO>`
2.  `cd <NOMBRE_REPO>`
3.  `python -m venv venv && source venv/bin/activate` (Win: `venv\Scripts\activate`)
4.  `pip install -r requirements.txt`
5.  (Opcional) Crear `.env` con `ANTHROPIC_API_KEY="tu_clave_sk-ant..."`
6.  `streamlit run app.py`

### Deploy (Streamlit Cloud)
1.  Subir código a un repositorio de GitHub.
2.  Conectar GitHub a `share.streamlit.io`.
3.  Seleccionar repo, branch `main`, archivo principal `app.py`.
4.  **Importante**: En `App Settings -> Secrets` de Streamlit, añadir `ANTHROPIC_API_KEY = "tu_clave_sk-ant..."`.
5.  Deploy.

## 🤖 Cómo Funciona RAG (Esencia)
Datos FMI -> Textos -> Embeddings (Vectores) -> Búsqueda Rápida (FAISS) -> Contexto + Claude -> Respuesta Inteligente.

## 🔐 API Key (Anthropic Claude)
- **Necesaria para**: Respuestas más inteligentes y análisis profundo.
- **Configuración**:
    - **Local**: En archivo `.env`.
    - **Streamlit Cloud**: En `Settings -> Secrets`.
- *La app funciona con respuestas básicas sin la API Key.*