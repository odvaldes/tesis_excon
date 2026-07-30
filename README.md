Dashboard Predictivo de Inventario EXCON
Aplicación Streamlit asociada al Notebook 4 de la tesis.
Funcionalidades
Indicadores principales de inventario y riesgo.
Histograma de órdenes o materiales inmovilizados.
Boxplot de órdenes o materiales inmovilizados.
Distribución del Índice de Riesgo de Inmovilización (IRI).
Indicadores generados por el Notebook 2.
Comparación de modelos y métricas del Notebook 3.
Importancia de variables.
Matriz de confusión.
Tabla priorizada para decisiones de compra, transferencia o redistribución.
Descarga de resultados filtrados en Excel.
Estructura del repositorio
```text
dashboard-excon/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── salidas_modelo/
    ├── Dataset_Modelo_EXCON.parquet
    ├── Dataset_Scoring_Actual_EXCON.parquet
    ├── Scoring_Actual_IRI_EXCON.parquet
    ├── Comparacion_Modelos_EXCON.xlsx
    ├── Metricas_Test_EXCON.xlsx
    ├── Importancia_Variables_EXCON.xlsx
    ├── Resultados_Test_IRI_EXCON.xlsx
    ├── Reporte_Notebook_2.xlsx
    └── Resumen_Notebook_3_EXCON.xlsx
```
Ejecución local
Instalar dependencias:
```bash
pip install -r requirements.txt
```
Ejecutar la aplicación:
```bash
streamlit run app.py
```
Publicación en GitHub
Crea un repositorio nuevo en GitHub.
Sube `app.py`, `requirements.txt`, `README.md`, `.gitignore` y la carpeta `salidas_modelo`.
Verifica que la rama principal sea `main`.
No subas información confidencial o identificadores sensibles del ERP.
Publicación en Streamlit Community Cloud
Ingresa a Streamlit Community Cloud.
Selecciona Create app.
Conecta tu cuenta de GitHub.
Selecciona el repositorio y la rama `main`.
En Main file path, escribe:
```text
app.py
```
Presiona Deploy.
Seguridad de datos
Antes de publicar el repositorio como público, elimina o anonimiza:
nombres de proveedores;
nombres de clientes;
números de documentos;
datos personales;
valores contractuales confidenciales;
identificadores internos sensibles.
Una alternativa más segura es mantener el repositorio privado y publicar solamente una muestra anonimizada.
