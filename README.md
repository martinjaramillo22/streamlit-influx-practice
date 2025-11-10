# Digitalización de Plantas Productivas — Tablero Extreme Manufacturing

**Autor:** Martin jaramillo, Santigo Gonzalez y Nicolas Espinal   
**Universidad EAFIT — Ingeniería de Producción**  
**Docente:** Miguel Ángel Carrillo  
**Año:** 2025  

---

## Objetivo

Desarrollar un **tablero digital de monitoreo y análisis predictivo** para las variables industriales de **temperatura, humedad y vibración**, registradas por los sensores **DHT22** y **MPU6050**, conectados a una base de datos **InfluxDB**.  
El tablero permite visualizar, analizar y predecir el comportamiento de las variables en una celda de producción simulada del proceso de secado de la empresa **Extreme Manufacturing**.

---

##  Tecnologías utilizadas

| Componente | Herramienta |
|-------------|--------------|
| Lenguaje principal | Python 3.11 |
| Visualización | Streamlit + Plotly |
| Base de datos | InfluxDB Cloud |
| Librerías clave | `influxdb-client`, `pandas`, `numpy`, `scikit-learn`, `plotly`, `streamlit` |
| Modelo predictivo | Regresión lineal + Suavizado (promedio móvil) |
| Hosting | Streamlit Cloud |

---


---

Si quieres hacerlo **más visual (como en repos profesionales)**, puedes añadir íconos y breves descripciones así:

```markdown
## 🧩 Estructura del proyecto

📁 **/digitalizacion-extreme/**  
│  
├── **app.py** → Código principal del tablero en Streamlit.  
│   Contiene la conexión a InfluxDB, visualización, KPIs y modelo predictivo.  
│  
├── **requirements.txt** → Lista de librerías necesarias para ejecutar la aplicación.  
│  
├── **README.md** → Documento descriptivo del proyecto (este archivo).  
│  
├── **.streamlit/** → Carpeta de configuración de Streamlit.  
│   └── **secrets.toml** → Credenciales seguras de InfluxDB (no subir a GitHub).  
│  
├── **/docs/** → Capturas de pantalla o imágenes para el informe.  
│  
└── **/data/** → Datos exportados o de prueba local.


##  Características principales

 Conexión funcional a base de datos **InfluxDB**  
 Visualización interactiva de las variables **DHT22 y MPU6050**  
 Cálculo de **KPIs en tiempo real** (valor actual, variación, promedio, máx/min)  
 Filtros de **rango de tiempo, frecuencia y variables**  
 **Detección de anomalías** (Z-Score configurable)  
 **Modelo predictivo lineal** para estimar tendencias futuras  
 **Exportación de datos CSV** y actualización automática  


##  Método predictivo aplicado

El modelo predictivo implementado se basa en una **Regresión Lineal Simple**, donde se toma el tiempo (en segundos) como variable independiente y la variable industrial (temperatura, humedad o vibración) como dependiente.  
El modelo se ajusta sobre los datos históricos y proyecta un **horizonte configurable en minutos**.  
Se complementa con un **promedio móvil** para suavizar la tendencia y eliminar ruido.

---

##  Ejecución local

```bash
pip install -r requirements.txt
streamlit run app.py

