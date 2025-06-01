# Ecuador Economic Assistant

## Visión
- **Sistema RAG** avanzado para análisis económico de Ecuador.
- **Datos**: FMI (44 indicadores, 51 años: 1980-2030).
- **IA**: **Claude API** para insights inteligentes.

## Arquitectura y Stack
- **Flujo**: Datos FMI -> Procesamiento -> RAG (FAISS) -> Claude -> App Streamlit.
- **Tecnologías**: Streamlit, Plotly, Sentence Transformers, FAISS, Claude 3.5 Sonnet, Pandas, GitHub, Streamlit Cloud.

## Funcionalidades Principales
- **Chat RAG Inteligente**: Búsqueda semántica y respuestas contextuales de Claude sobre 44 indicadores.
- **Explorador de Datos**: Visualizaciones interactivas, filtros temporales.
- **Dashboard Ejecutivo**: Métricas clave y análisis de tendencias.
- **Búsqueda Avanzada**: Por palabras clave y categorías.

## Sistema RAG Clave
- **Base de Conocimiento**: 45 documentos (indicadores + contexto Ecuador).
- **Proceso**: Query -> Búsqueda Vectorial (FAISS) -> Contexto -> Análisis Claude -> Respuesta.

## Implementación y Deploy
- **Archivos Esenciales**: `app.py`, `requirements.txt`.
- **Deploy Sencillo (Streamlit Cloud)**:
    1. Fork/clonar repo en GitHub.
    2. Configurar `ANTHROPIC_API_KEY` en Secrets de Streamlit Cloud.
    3. Conectar y desplegar.

## Impacto y Diferenciadores
- **Valor Único**: Herramienta de análisis profesional (no solo demo).
- **Datos Reales**: FMI oficial, cobertura temporal extensa (51 años).
- **Inteligencia Avanzada**: RAG + LLM (Claude) para análisis profundo.
- **Costos Bajos**: Principalmente Claude API ($2-10/mes uso personal).
- **Ideal Para**:
    - **Portfolio Destacado**: Demuestra skills en RAG, LLMs, APIs.
    - **Aprendizaje Práctico**: Caso de uso real con datos económicos.

## Conclusión
Una herramienta potente y profesional para el análisis económico de Ecuador, ideal para destacar y aprender tecnologías de IA de vanguardia.