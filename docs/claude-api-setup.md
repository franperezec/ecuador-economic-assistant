# 🔑 Configuración Claude API para Ecuador Economic Assistant

Este documento resume los pasos y consideraciones cruciales para integrar Claude API en tu aplicación "Ecuador Economic Assistant", permitiendo análisis económicos avanzados y respuestas contextuales.

### ¿Por qué Claude API?

* **Análisis Profundo**: Respuestas económicas personalizadas y con contexto.

* **Interpretación Inteligente**: Comprensión de matices económicos complejos.

* **Claridad**: Traducción de datos técnicos a insights comprensibles.

* **Análisis Comparativo**: Relación automática entre indicadores.

* **Perspectiva Histórica**: Contextualización temporal de los datos.

### Pasos Clave para la Configuración

1. **Crear Cuenta en Anthropic**:

   * Regístrate en [console.anthropic.com](https://console.anthropic.com).

   * Verifica tu correo electrónico.

2. **Configurar Facturación (Billing)**:

   * Ve a `Console → Settings → Billing`.

   * Añade un método de pago.

   * Establece un límite de gasto mensual (recomendado: $10-20 iniciales).

3. **Crear API Key**:

   * Ve a `Console → API Keys`.

   * Crea una nueva clave (ej. `Ecuador-Economic-Assistant`).

   * **Importante**: Copia y guarda la clave en un lugar seguro, ya que se muestra solo una vez.

4. **Integrar en tu Proyecto**:

   * **Desarrollo Local**:

     * Crea un archivo `.env` en la raíz del proyecto.

     * Añade: `ANTHROPIC_API_KEY=tu_clave_aqui`

   * **Streamlit Cloud**:

     * En tu app (`share.streamlit.io`), ve a `⚙️ Settings → Secrets`.

     * Añade: `ANTHROPIC_API_KEY = "tu_clave_aqui"`

     * Guarda y reinicia la aplicación.

### Consideraciones de Costo

* Claude API es eficiente en costos. Para uso personal, $5-10/mes suele ser suficiente.

* Ejemplos de costos estimados:

  * Desarrollo/Testing (100K tokens/mes): \~$0.30

  * Uso Personal (500K tokens/mes): \~$1.50

  * Uso Frecuente (2M tokens/mes): \~$6.00

### Seguridad de la API Key

* **SÍ HACER**:

  * Guardar en variables de entorno o secretos de Streamlit.

  * Configurar límites de gasto en Anthropic.

  * Regenerar la clave si se sospecha compromiso.

* **NO HACER**:

  * Compartir en repositorios públicos (GitHub) o código fuente.

  * "Hardcodear" (escribir directamente) en el código.

  * Enviar por email o chat.

### Verificación y Troubleshooting

* **Verificar Funcionamiento**:

  * **Local**: Ejecutar script de Python para importar `anthropic` y usar la variable de entorno.

  * **Streamlit**: Buscar mensaje de "Claude API ✅ Activa" y probar con una pregunta económica compleja.

* **Problemas Comunes**:

  * `Invalid API Key`: Revisa espacios, prefijo `sk-ant-`, o regenera la clave.

  * `Insufficient credits`: Verifica la facturación y el método de pago en Anthropic.

  * `Rate limit exceeded`: Reduce frecuencia de consultas, usa caché.

  * Respuestas básicas (API no conectada): Asegúrate que la clave esté en los secretos de Streamlit y reinicia la app.

### Optimización de Costos

* Utiliza caché para respuestas (`@st.cache_resource`).

* Configura límites de gasto en la consola de Anthropic.

* Desarrolla la UI con la API desactivada y actívala solo para pruebas de funcionalidad RAG.

### Impacto de la Integración

Integrar Claude API transforma tu asistente de respuestas básicas a un sistema capaz de ofrecer análisis económicos detallados, comparativos y con perspectiva histórica, similar al de un economista.