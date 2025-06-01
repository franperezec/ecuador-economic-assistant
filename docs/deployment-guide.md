# Deploy Guide: Ecuador Economic Assistant

## 1. Requisitos
- Código del proyecto listo (`app.py`, `requirements.txt`).
- Git, Python, cuenta de GitHub.
- (Opcional) Claude API Key.

## 2. Prepara y Sube a GitHub
1.  **Local**:
    ```bash
    git init
    git add .
    git commit -m "Versión inicial"
    ```
2.  **GitHub**:
    * Crea un repositorio **público**.
    * Conecta y sube:
        ```bash
        git remote add origin [https://github.com/TU_USUARIO/NOMBRE_REPO.git](https://github.com/TU_USUARIO/NOMBRE_REPO.git)
        git branch -M main
        git push -u origin main
        ```

## 3. Despliega en Streamlit Cloud
1.  **Accede**: `share.streamlit.io` (con GitHub).
2.  **Nueva App**:
    * Selecciona tu repositorio, branch `main`, archivo `app.py`.
3.  **Secretos (API)**:
    * En `Settings` -> `Secrets`, añade `ANTHROPIC_API_KEY = "sk-ant-tu_clave_aqui"`.
4.  **Deploy!**

## 4. Actualizaciones
- Modifica código local -> `git add .` -> `git commit -m "cambios"` -> `git push`.
- *Streamlit Cloud actualiza automáticamente.*

## Principales Soluciones a Problemas
- **`Module not found`**: Verifica `requirements.txt`.
- **Error API**: Revisa API Key en Secrets y créditos de Anthropic.
- **Repo no hallado**: Asegura que sea público en GitHub.