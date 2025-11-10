# ============================================================
# 🚜 Desafío Telemetría Forestal – Procesamiento de Datos
# Autor: Katalina Escarlet Sepúlveda López
# Descripción: Analiza datos XML y shapefile para generar
#              informes de resguardo (motor apagado fuera de turno)
# ============================================================

import xml.etree.ElementTree as ET
from datetime import datetime, time
from zoneinfo import ZoneInfo
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# ------------------------------------------------------------
# 1️⃣ ARCHIVOS DE ENTRADA
# ------------------------------------------------------------
ENGINE_FILE = "EngineStatusMessages-844585.xml"
LOC_FILE_1 = "LocationMessages-844585-page_1.xml"
LOC_FILE_2 = "LocationMessages-844585-page_2.xml"
CAMINOS_FILE = "CAMINOS_7336.shp"

# ------------------------------------------------------------
# 2️⃣ PARSEAR ARCHIVO DE ESTADO DEL MOTOR
# ------------------------------------------------------------
def load_engine_data(path):
    ns = {"iso": "http://standards.iso.org/iso/15143/-3"}
    tree = ET.parse(path)
    root = tree.getroot()
    data = []

    for es in root.findall("iso:EngineStatus", ns):
        dt = es.attrib.get("datetime")
        running = es.findtext("iso:Running", default="", namespaces=ns)
        data.append({
            "timestamp_utc": datetime.fromisoformat(dt.replace("Z", "+00:00")),
            "running": running.lower() == "true"
        })
    df = pd.DataFrame(data).sort_values("timestamp_utc")
    df["prev_running"] = df["running"].shift(1)
    df["is_off_event"] = (~df["running"]) & (df["prev_running"] == True)
    return df

# ------------------------------------------------------------
# 3️⃣ PARSEAR ARCHIVOS DE LOCALIZACIÓN
# ------------------------------------------------------------
def load_location_data(paths):
    ns = {"iso": "http://standards.iso.org/iso/15143/-3"}
    data = []
    for path in paths:
        tree = ET.parse(path)
        root = tree.getroot()
        for loc in root.findall("iso:Location", ns):
            dt = loc.attrib.get("datetime")
            lat = float(loc.findtext("iso:Latitude", namespaces=ns))
            lon = float(loc.findtext("iso:Longitude", namespaces=ns))
            data.append({
                "timestamp_utc": datetime.fromisoformat(dt.replace("Z", "+00:00")),
                "latitude": lat,
                "longitude": lon
            })
    return pd.DataFrame(data).sort_values("timestamp_utc")

# ------------------------------------------------------------
# 4️⃣ DETECTAR APAGADOS FUERA DE HORARIO DE TURNO
# ------------------------------------------------------------
def filter_off_events(df_engine):
    tz = ZoneInfo("America/Santiago")
    df_engine["timestamp_local"] = df_engine["timestamp_utc"].dt.tz_convert(tz)
    shift_start, shift_end = time(8,30), time(19,30)

    def outside_shift(dt):
        t = dt.timetz()
        return not (shift_start <= t <= shift_end)

    df_engine["outside_shift"] = df_engine["timestamp_local"].apply(outside_shift)
    return df_engine[df_engine["is_off_event"] & df_engine["outside_shift"]].reset_index(drop=True)

# ------------------------------------------------------------
# 5️⃣ VINCULAR CADA APAGADO CON SU ÚLTIMA POSICIÓN
# ------------------------------------------------------------
def join_with_last_location(df_off, df_loc):
    joined = []
    for _, row in df_off.iterrows():
        before = df_loc[df_loc["timestamp_utc"] <= row["timestamp_utc"]]
        if not before.empty:
            last_pos = before.iloc[-1]
            joined.append({
                "engine_off_timestamp": row["timestamp_utc"],
                "latitude": last_pos["latitude"],
                "longitude": last_pos["longitude"]
            })
    return pd.DataFrame(joined)

# ------------------------------------------------------------
# 6️⃣ CALCULAR DISTANCIA A CAMINOS (SHAPEFILE)
# ------------------------------------------------------------
def compute_distances(df, shp_path):
    caminos = gpd.read_file(shp_path)
    caminos = caminos.to_crs(epsg=32718)  # proyección métrica (UTM 18S)
    puntos = gpd.GeoDataFrame(
        df,
        geometry=[Point(xy) for xy in zip(df["longitude"], df["latitude"])],
        crs="EPSG:4326"
    ).to_crs(epsg=32718)
    df["distance_to_road_m"] = puntos.geometry.apply(
        lambda g: caminos.distance(g).min()
    )
    df["is_safe"] = df["distance_to_road_m"] >= 50
    return df

# ------------------------------------------------------------
# 7️⃣ PROCESO PRINCIPAL
# ------------------------------------------------------------
def process_data():
    print("📡 Cargando datos del motor...")
    df_engine = load_engine_data(ENGINE_FILE)

    print("🛰️ Cargando datos de localización...")
    df_loc = load_location_data([LOC_FILE_1, LOC_FILE_2])

    print("🕒 Filtrando apagados fuera de turno...")
    df_off = filter_off_events(df_engine)

    print("📍 Vinculando ubicaciones...")
    df_joined = join_with_last_location(df_off, df_loc)

    print("🛣️ Calculando distancias a caminos...")
    df_final = compute_distances(df_joined, CAMINOS_FILE)

    print("✅ Proceso completado. Informes generados:")
    print(df_final[["engine_off_timestamp", "latitude", "longitude", "distance_to_road_m", "is_safe"]])
    df_final.to_csv("informes_resguardo.csv", index=False)
    print("\nArchivo guardado como 'informes_resguardo.csv'")

# ------------------------------------------------------------
# 8️⃣ EJECUCIÓN DIRECTA
# ------------------------------------------------------------
if __name__ == "__main__":
    process_data()
