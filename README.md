# 🧠 Digitalización de Plantas Productivas — Tablero Extreme Manufacturing

**Autor:** Martin jaramillo, Santigo Gonzalez y Nicolas Espinal   
**Universidad EAFIT — Ingeniería de Producción**  
**Docente:** Miguel Ángel Carrillo  
**Año:** 2025  

---

## 🎯 Objetivo

Desarrollar un **tablero digital de monitoreo y análisis predictivo** para las variables industriales de **temperatura, humedad y vibración**, registradas por los sensores **DHT22** y **MPU6050**, conectados a una base de datos **InfluxDB**.  
El tablero permite visualizar, analizar y predecir el comportamiento de las variables en una celda de producción simulada del proceso de secado de la empresa **Extreme Manufacturing**.

---

## ⚙️ Tecnologías utilizadas

| Componente | Herramienta |
|-------------|--------------|
| Lenguaje principal | Python 3.11 |
| Visualización | Streamlit + Plotly |
| Base de datos | InfluxDB Cloud |
| Librerías clave | `influxdb-client`, `pandas`, `numpy`, `scikit-learn`, `plotly`, `streamlit` |
| Modelo predictivo | Regresión lineal + Suavizado (promedio móvil) |
| Hosting | Streamlit Cloud |

---

## 🧩 Estructura del proyecto

