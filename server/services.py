import pandas as pd
import geopandas as gpd
import xml.etree.ElementTree as ET
from shapely.geometry import Point
from zoneinfo import ZoneInfo
from datetime import datetime
from django.conf import settings
import os
from .models import SafeguardReport


def process_files():

    BASE_DIR = settings.BASE_DIR
    DATA_DIR = os.path.join(BASE_DIR, "data")
    
    ENGINE_FILE = os.path.join(DATA_DIR, "EngineStatusMessages-844585.xml")
    LOC_FILES = [
        os.path.join(DATA_DIR, "LocationMessages-844585-page_1.xml"),
        os.path.join(DATA_DIR, "LocationMessages-844585-page_2.xml"),
    ]
    CAMINOS_FILE = os.path.join(DATA_DIR, "CAMINOS_7336.shp")

    for file_path in [ENGINE_FILE] + LOC_FILES + [CAMINOS_FILE]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

    ns = {"iso": "http://standards.iso.org/iso/15143/-3"}
    engine_root = ET.parse(ENGINE_FILE).getroot()

    engine_data = []
    for es in engine_root.findall("iso:EngineStatus", ns):
        dt = es.attrib.get("datetime")
        running = es.findtext("iso:Running", namespaces=ns)
        engine_data.append({
            "timestamp_utc": datetime.fromisoformat(dt.replace("Z", "+00:00")),
            "running": running.lower() == "true"
        })

    df_engine = pd.DataFrame(engine_data).sort_values("timestamp_utc")
    df_engine["prev_running"] = df_engine["running"].shift(1)
    df_engine["is_off_event"] = (~df_engine["running"]) & (df_engine["prev_running"] == True)

    tz = ZoneInfo("America/Santiago")
    df_engine["timestamp_local"] = df_engine["timestamp_utc"].dt.tz_convert(tz)

    hora_inicio = datetime.strptime("08:30", "%H:%M").time()
    hora_fin = datetime.strptime("19:30", "%H:%M").time()

    df_engine["outside_shift"] = df_engine["timestamp_local"].apply(
        lambda d: not (hora_inicio <= d.time() <= hora_fin)
    )

    df_off = df_engine[df_engine["is_off_event"] & df_engine["outside_shift"]]

    loc_data = []
    for path in LOC_FILES:
        loc_root = ET.parse(path).getroot()
        for loc in loc_root.findall("iso:Location", ns):
            dt = loc.attrib.get("datetime")
            lat = float(loc.findtext("iso:Latitude", namespaces=ns))
            lon = float(loc.findtext("iso:Longitude", namespaces=ns))
            loc_data.append({
                "timestamp_utc": datetime.fromisoformat(dt.replace("Z", "+00:00")),
                "latitude": lat,
                "longitude": lon
            })

    df_loc = pd.DataFrame(loc_data).sort_values("timestamp_utc")

    reports = []
    for _, row in df_off.iterrows():
        before = df_loc[df_loc["timestamp_utc"] <= row["timestamp_utc"]]
        if not before.empty:
            pos = before.iloc[-1]
            reports.append({
                "engine_off_timestamp": row["timestamp_utc"],
                "latitude": pos["latitude"],
                "longitude": pos["longitude"]
            })

    if not reports:
        return 0

    df = pd.DataFrame(reports)

    caminos = gpd.read_file(CAMINOS_FILE).to_crs(epsg=32718)
    puntos = gpd.GeoDataFrame(
        df,
        geometry=[Point(xy) for xy in zip(df.longitude, df.latitude)],
        crs="EPSG:4326"
    ).to_crs(epsg=32718)

    df["distance_to_road_m"] = puntos.geometry.apply(lambda g: caminos.distance(g).min())
    df["is_safe"] = df["distance_to_road_m"] >= 50

    created_count = 0
    for _, r in df.iterrows():
        SafeguardReport.objects.create(
            engine_off_timestamp=r.engine_off_timestamp,
            latitude=r.latitude,
            longitude=r.longitude,
            distance_to_road_m=r.distance_to_road_m,
            is_safe=r.is_safe
        )
        created_count += 1

    return created_count