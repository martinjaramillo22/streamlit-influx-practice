import os
import time
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import timedelta
from influxdb_client import InfluxDBClient
from sklearn.linear_model import LinearRegression

# =========================
# CONFIGURACIÓN INICIAL
# =========================
st.set_page_config(page_title="📊 Digitalización de Planta — Extreme Manufacturing",
                   layout="wide")

st.title("📊 Tablero de Monitoreo y Análisis Predictivo — Extreme Manufacturing")
st.caption("DHT22 (Temperatura/Humedad) • MPU6050 (Vibración/Giro) • InfluxDB + Streamlit")

# --- Credenciales InfluxDB (modo local / pruebas) ---
INFLUXDB_URL = "https://us-east-1-1.aws.cloud2.influxdata.com"
INFLUXDB_TOKEN = "JcKXoXE30JQvV9Ggb4-zv6sQc0Zh6B6Haz5eMRW0FrJEduG2KcFJN9-7RoYvVORcFgtrHR-Q_ly-52pD7IC6JQ=="
INFLUXDB_ORG = "0925ccf91ab36478"
INFLUXDB_BUCKET = "EXTREME_MANUFACTURING"

# Cliente InfluxDB
try:
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    query_api = client.query_api()
except Exception as e:
    st.error(f"❌ Error conectando a InfluxDB: {e}")
    st.stop()

# =========================
# CONTROLES DE UI
# =========================
with st.sidebar:
    st.header("⚙️ Controles")
    sensor = st.selectbox("Sensor", ["DHT22", "MPU6050"], index=0)

    # Rango de tiempo
    rango_dias = st.slider("Rango de tiempo (días hacia atrás)", 1, 30, 3)

    # Resampling y suavizado
    freq_map = {"1 s": "1s", "5 s": "5s", "10 s": "10s", "30 s": "30s", "1 min": "1min", "5 min": "5min"}
    freq_label = st.selectbox("Frecuencia de muestreo (resample)", list(freq_map.keys()), index=4)
    resample_rule = freq_map[freq_label]

    window_ma = st.slider("Ventana Promedio Móvil (puntos)", 1, 50, 5)

    # Anomalías
    z_thr = st.slider("Umbral anomalías (|z-score|)", 1.0, 5.0, 2.5, 0.1)

    # Predicción
    horizon_min = st.slider("Horizonte de predicción (min)", 5, 120, 30, step=5)

    auto_refresh = st.checkbox("Auto-actualizar cada 60 s", value=False)

# =========================
# QUERIES FLUX
# =========================
def build_flux_query(measurement: str, fields: list[str], days_back: int) -> str:
    fields_filter = " or ".join([f'r._field == "{f}"' for f in fields])
    q = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
      |> range(start: -{days_back}d)
      |> filter(fn: (r) => r._measurement == "{measurement}")
      |> filter(fn: (r) => {fields_filter})
    '''
    return q

DHT_FIELDS = ["humedad", "temperatura", "sensacion_termica"]
MPU_FIELDS = ["accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y", "gyro_z", "temperature"]

# =========================
# CARGA Y CACHÉ DE DATOS
# =========================
@st.cache_data(ttl=60, show_spinner=False)
def load_dataframe(query: str) -> pd.DataFrame:
    try:
        df = query_api.query_data_frame(org=INFLUXDB_ORG, query=query)
        if isinstance(df, list) and len(df) > 0:
            df = pd.concat(df, ignore_index=True)
        if isinstance(df, pd.DataFrame) and not df.empty:
            df = df[["_time", "_field", "_value"]].rename(
                columns={"_time": "Tiempo", "_field": "Variable", "_value": "Valor"}
            )
            df["Tiempo"] = pd.to_datetime(df["Tiempo"], utc=True).dt.tz_convert("America/Bogota")
            df = df.sort_values("Tiempo")
        return df
    except Exception as e:
        raise RuntimeError(f"Error consultando InfluxDB: {e}")

# Consulta dinámica
if sensor == "DHT22":
    flux = build_flux_query("studio-dht22", DHT_FIELDS, rango_dias)
else:
    flux = build_flux_query("mpu6050", MPU_FIELDS, rango_dias)

try:
    df = load_dataframe(flux)
except Exception as e:
    st.error(str(e))
    st.stop()

if df is None or df.empty:
    st.warning("⚠️ No se encontraron datos para el rango seleccionado.")
    st.stop()

# =========================
# PREPROCESO Y FEATURES
# =========================
wide = df.pivot_table(index="Tiempo", columns="Variable", values="Valor", aggfunc="last")
wide = wide.sort_index()
wide = wide.resample(resample_rule).mean()

if {"accel_x", "accel_y", "accel_z"}.issubset(wide.columns):
    wide["accel_mag"] = np.sqrt(wide["accel_x"]**2 + wide["accel_y"]**2 + wide["accel_z"]**2)

vars_disponibles = [c for c in wide.columns if pd.api.types.is_numeric_dtype(wide[c])]
if not vars_disponibles:
    st.warning("No hay variables numéricas tras el resampling.")
    st.stop()

vars_sel = st.multiselect("Variables a visualizar", vars_disponibles, default=[vars_disponibles[0]])

# =========================
# KPIs
# =========================
st.subheader("🧠 KPIs Rápidos")
k1, k2, k3, k4 = st.columns(4)
for i, col in enumerate([k1, k2, k3, k4]):
    if i < len(vars_disponibles):
        vname = vars_disponibles[i]
        serie = wide[vname].dropna()
        if serie.empty:
            col.metric(vname, "—", "—")
        else:
            col.metric(f"{vname}",
                       f"{serie.iloc[-1]:.2f}",
                       f"Δ {serie.iloc[-1] - serie.iloc[max(0,len(serie)-2)]:+.2f}")

# =========================
# VISUALIZACIÓN + SUAVIZADO
# =========================
st.subheader("📈 Visualización")
for v in vars_sel:
    if v not in wide.columns:
        continue
    plot_df = wide[[v]].copy()
    plot_df["MA"] = plot_df[v].rolling(window=window_ma, min_periods=1).mean()

    fig = px.line(plot_df, x=plot_df.index, y=[v, "MA"],
                  labels={"value": "Valor", "Tiempo": "Tiempo", "variable": "Serie"},
                  title=f"{v} — crudo vs. promedio móvil ({window_ma})",
                  template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

# =========================
# ANOMALÍAS (z-score)
# =========================
st.subheader("🚨 Detección de Anomalías (z-score)")
for v in vars_sel:
    serie = wide[v].dropna()
    if serie.empty or serie.std() == 0:
        st.info(f"{v}: sin suficiente variabilidad para z-score.")
        continue
    z = (serie - serie.mean()) / serie.std()
    anomalies = z[np.abs(z) > z_thr]
    fig = px.line(serie, x=serie.index, y=serie.values,
                  labels={"x": "Tiempo", "y": v},
                  title=f"Anomalías en {v} (|z|>{z_thr})",
                  template="plotly_white")
    if not anomalies.empty:
        fig.add_scatter(x=anomalies.index, y=serie.loc[anomalies.index],
                        mode="markers", name="Anomalía",
                        marker=dict(size=9, color="red", symbol="x"))
    st.plotly_chart(fig, use_container_width=True)

# =========================
# PREDICCIÓN LINEAL SIMPLE
# =========================
st.subheader("🔮 Predicción Lineal (baseline)")
st.caption("Modelo baseline para mostrar tendencia futura. Para producción, considerar ARIMA/ETS/Prophet.")

for v in vars_sel:
    serie = wide[v].dropna()
    if len(serie) < 10:
        st.info(f"{v}: se requieren ≥10 puntos para ajustar regresión.")
        continue

    t0 = serie.index[0]
    X = (serie.index - t0).total_seconds().values.reshape(-1, 1)
    y = serie.values

    model = LinearRegression()
    model.fit(X, y)
    y_hat = model.predict(X)

    last_t = serie.index[-1]
    freq_seconds = max(1, int(pd.Timedelta(resample_rule).total_seconds() or 60))
    steps = int((horizon_min * 60) / freq_seconds)
    fut_index = [last_t + (i+1)*pd.Timedelta(seconds=freq_seconds) for i in range(steps)]
    X_fut = ((pd.Index(fut_index) - t0).total_seconds()).values.reshape(-1, 1)
    y_fut = model.predict(X_fut)

    pred_df = pd.DataFrame({
        "Tiempo": list(serie.index) + fut_index,
        "Valor": list(serie.values) + [np.nan]*len(fut_index),
        "Predicción": list(y_hat) + list(y_fut)
    }).set_index("Tiempo")

    fig = px.line(pred_df[["Valor", "Predicción"]],
                  labels={"value": v, "Tiempo": "Tiempo", "variable": "Serie"},
                  title=f"{v} — Ajuste lineal + {horizon_min} min de horizonte",
                  template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

# =========================
# TABLA, EXPORT Y AUTOREFRESH
# =========================
with st.expander("📄 Ver datos (resampleados)"):
    st.dataframe(wide.tail(500))

csv = wide.to_csv(index=True).encode("utf-8")
st.download_button("⬇️ Descargar CSV (resampleado)", data=csv, file_name="datos_resampleados.csv", mime="text/csv")

if auto_refresh:
    with st.spinner("Actualizando en 60 s…"):
        time.sleep(60)
        st.rerun()
