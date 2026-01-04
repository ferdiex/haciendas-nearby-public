import os
import json
import math
import re
from datetime import datetime
from typing import Any, Dict, List, Tuple

import streamlit as st
import pandas as pd
import pydeck as pdk

# --------------------------------------------------------------------
# Settings and paths
# --------------------------------------------------------------------

DEFAULT_LAT = 19.050501
DEFAULT_LON = -98.135887
DEFAULT_RADIUS_KM = 25

CATALOG_JSON = "catalog_public.json"

# --------------------------------------------------------------------
# Internationalization (i18n)
# --------------------------------------------------------------------

LANGS = {"es": "Español", "en": "English"}

TEXTS: Dict[str, Dict[str, str]] = {
    "app_title": {
        "es": "Haciendas Nearby – Versión pública (solo lectura)",
        "en": "Haciendas Nearby – Public read-only version",
    },
    "sidebar_language_label": {
        "es": "Idioma / Language",
        "en": "Language / Idioma",
    },
    "sidebar_search_center_header": {
        "es": "Centro de búsqueda",
        "en": "Search center",
    },
    "sidebar_lat_label": {
        "es": "Latitud",
        "en": "Latitude",
    },
    "sidebar_lon_label": {
        "es": "Longitud",
        "en": "Longitude",
    },
    "sidebar_current_center_label": {
        "es": "Centro actual (copiar/pegar si quieres):",
        "en": "Current center (copy/paste if you like):",
    },
    "sidebar_open_center_gmaps": {
        "es": "Abrir centro en Google Maps",
        "en": "Open center in Google Maps",
    },
    "sidebar_reset_center_btn": {
        "es": "Reiniciar centro a valor por defecto (Amalucan)",
        "en": "Reset center to default (Amalucan)",
    },
    "sidebar_reset_center_success": {
        "es": "Centro de búsqueda y radio reiniciados a los valores por defecto (Amalucan, {radius} km).",
        "en": "Search center and radius reset to default values (Amalucan, {radius} km).",
    },
    "sidebar_radius_label": {
        "es": "Radio (km)",
        "en": "Radius (km)",
    },
    "sidebar_filters_header": {
        "es": "Filtros",
        "en": "Filters",
    },
    "sidebar_filters_radius_note": {
        "es": "Todos los filtros se aplican únicamente a las haciendas dentro del radio seleccionado.",
        "en": "All filters apply only to haciendas inside the selected radius.",
    },
    # New: quick help in the sidebar
    "sidebar_help_header": {
        "es": "Ayuda rápida",
        "en": "Quick help",
    },
    "sidebar_help_text": {
        "es": (
            "- Selecciona el idioma en la parte superior.\n"
            "- Ajusta el centro de búsqueda con latitud/longitud o usa el botón para reiniciar a Amalucan.\n"
            "- Define el radio en kilómetros con el deslizador.\n"
            "- Aplica filtros por nombre, región o presencia de foto.\n"
            "- Explora resultados en la tabla y en el mapa interactivo.\n"
            "- Haz clic en una hacienda para ver detalles y foto (si disponible).\n"
            "- Exporta los resultados en CSV, GeoJSON o GPX."
        ),
        "en": (
            "- Choose your language at the top.\n"
            "- Set the search center with latitude/longitude or reset to Amalucan.\n"
            "- Adjust the radius in kilometers using the slider.\n"
            "- Apply filters by name, region, or photo availability.\n"
            "- Explore results in the table and interactive map.\n"
            "- Click a hacienda to view details and photo (if available).\n"
            "- Export results as CSV, GeoJSON, or GPX."
        ),
    },
    "sidebar_filter_name_contains": {
        "es": "Filtrar por nombre (contiene)",
        "en": "Filter by name (contains)",
    },
    "sidebar_filter_region": {
        "es": "Filtrar por región (opcional)",
        "en": "Filter by region (optional)",
    },
    "sidebar_region_all_option": {
        "es": "(todas)",
        "en": "(all)",
    },
    "sidebar_filter_only_with_photo": {
        "es": "Solo elementos con foto local",
        "en": "Show only items with local photo",
    },
    "sidebar_filter_only_without_photo": {
        "es": "Solo elementos SIN foto local",
        "en": "Show only items WITHOUT local photo",
    },
    "sidebar_conflicting_photo_filters": {
        "es": "Ambos filtros de foto no pueden estar activos a la vez. Se mantiene 'con foto' y se desactiva 'sin foto'.",
        "en": "Both photo filters cannot be active at once. Keeping 'with photo' and disabling 'without photo'.",
    },
    "results_header": {
        "es": "Resultados dentro del radio",
        "en": "Results within radius",
    },
    "results_caption_template": {
        "es": (
            "Centro: ({lat:.6f}, {lon:.6f}) • "
            "Radio: {radius} km • "
            "Coincidencias: {total} (con foto: {with_photo}, sin foto: {without_photo})"
        ),
        "en": (
            "Center: ({lat:.6f}, {lon:.6f}) • "
            "Radius: {radius} km • "
            "Matches: {total} (with photo: {with_photo}, without photo: {without_photo})"
        ),
    },
    "no_items_in_radius_info": {
        "es": "No se encontraron haciendas en el radio/filtro actual.",
        "en": "No haciendas found in the current radius/filter.",
    },
    "table_name_col": {
        "es": "Nombre",
        "en": "Name",
    },
    "table_region_col": {
        "es": "Región",
        "en": "Region",
    },
    "table_lat_col": {
        "es": "Latitud",
        "en": "Latitude",
    },
    "table_lon_col": {
        "es": "Longitud",
        "en": "Longitude",
    },
    "table_distance_col": {
        "es": "Distancia (km)",
        "en": "Distance (km)",
    },
    "table_has_photo_col": {
        "es": "Foto local",
        "en": "Local photo",
    },
    "map_header": {
        "es": "Mapa",
        "en": "Map",
    },
    "map_tip_caption": {
        "es": "Consejo: pasa el cursor sobre los marcadores para ver nombre, región y distancia.",
        "en": "Tip: hover markers to see name, region, and distance.",
    },
    "map_stats": {
        "es": "Elementos visibles: {items} • Con foto local: {local} • Sin foto local: {without}",
        "en": "Visible items: {items} • With local photo: {local} • Without local photo: {without}",
    },
    "selected_item_header": {
        "es": "Hacienda seleccionada (vista rápida)",
        "en": "Selected hacienda (quick view)",
    },
    "selected_item_need_selection": {
        "es": "Selecciona una hacienda de la tabla para verla aquí.",
        "en": "Select a hacienda from the table to view it here.",
    },
    "selected_choose_label": {
        "es": "Elige hacienda para ver detalles",
        "en": "Choose hacienda to view details",
    },
    "selected_coords_label": {
        "es": "Coordenadas",
        "en": "Coordinates",
    },
    "selected_distance_label": {
        "es": "Distancia desde el centro actual",
        "en": "Distance from current center",
    },
    "selected_region_label": {
        "es": "Región",
        "en": "Region",
    },
    "selected_no_photo": {
        "es": "Todavía no hay foto disponible para esta hacienda.",
        "en": "No photo available yet for this hacienda.",
    },
    "use_hacienda_as_center_btn": {
        "es": "Usar esta hacienda como centro de búsqueda",
        "en": "Use this hacienda as search center",
    },
    "use_hacienda_as_center_success": {
        "es": "Centro de búsqueda actualizado a esta hacienda. (Solo afecta tu sesión actual.)",
        "en": "Search center updated to this hacienda. (Affects only your current session.)",
    },
    "export_header": {
        "es": "Exportar resultados (solo lectura)",
        "en": "Export results (read-only)",
    },
    "export_none": {
        "es": "No hay elementos en el filtro actual para exportar.",
        "en": "There are no items in the current filter to export.",
    },
    "export_csv_label": {
        "es": "Descargar CSV (nombre, lat, lon, región, has_photo)",
        "en": "Download CSV (name, lat, lon, region, has_photo)",
    },
    "export_geojson_label": {
        "es": "Descargar GeoJSON",
        "en": "Download GeoJSON",
    },
    "export_gpx_label": {
        "es": "Descargar waypoints GPX",
        "en": "Download GPX waypoints",
    },
    "catalog_not_found_warning": {
        "es": "No se encontró catalog.json junto a la app. La versión pública necesita un catálogo exportado desde la app privada.",
        "en": "catalog.json was not found next to this app. The public version needs a catalog exported from the private app.",
    },
    "footer_text": {
        "es": (
            "Esta es una versión pública de solo lectura. "
            "Los datos vienen de un catálogo curado manualmente a partir del libro y un KML original. "
            "Puedes explorar, filtrar, cambiar el centro y exportar, pero no modificar el catálogo."
        ),
        "en": (
            "This is a public read-only version. "
            "Data comes from a catalog manually curated from the book and an original KML. "
            "You can explore, filter, change the center, and export, but cannot modify the catalog."
        ),
    },
}


def get_lang() -> str:
    return st.session_state.get("lang", "es")


def t(key: str, **fmt: Any) -> str:
    lang = get_lang()
    base = TEXTS.get(key, {})
    text = base.get(lang) or base.get("es") or key
    if fmt:
        try:
            return text.format(**fmt)
        except Exception:
            return text
    return text


# --------------------------------------------------------------------
# Utils
# --------------------------------------------------------------------

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km."""
    R = 6371.0088
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon1 - lon2)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def clean_url(url: str | None) -> str | None:
    if not url:
        return None
    u = str(url).strip()
    if not u:
        return None
    if re.match(r"^https?://", u):
        return u
    if u.startswith("//"):
        return "https:" + u
    return None


def has_photo_live(item: Dict[str, Any]) -> bool:
    lp = str(item.get("local_photo_path") or "").strip()
    if not lp:
        return False
    return os.path.exists(lp)


def load_catalog(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {"items": []}
    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception:
            return {"items": []}
    if "items" not in data or not isinstance(data["items"], list):
        return {"items": []}
    return data


def normalize_public_items(raw_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize items for public display:
    - Keep only KML-sourced, region-assigned items.
    - Compute has_photo from local_photo_path.
    - Clean photo_url.
    """
    items: List[Dict[str, Any]] = []
    for it in raw_items:
        source = it.get("source") or "kml"
        region = it.get("region")
        if source != "kml":
            continue
        if region is None:
            continue
        region_str = str(region).strip()
        if not region_str or region_str.lower() == "sin asignar":
            continue

        try:
            lat = float(it["lat"])
            lon = float(it["lon"])
        except Exception:
            continue

        cleaned = dict(it)
        cleaned["lat"] = lat
        cleaned["lon"] = lon
        cleaned["region"] = region_str
        cleaned["name"] = str(it.get("name") or "Untitled").strip()
        cleaned["photo_url"] = clean_url(it.get("photo_url"))
        cleaned["has_photo"] = has_photo_live(it)
        items.append(cleaned)
    return items


def df_for_radius(
    items: List[Dict[str, Any]],
    center_lat: float,
    center_lon: float,
    radius_km: float,
    only_with_photo: bool,
    only_without_photo: bool,
    name_query: str,
    region_filter: str,
) -> pd.DataFrame:
    """
    Build filtered DataFrame for public view:
    - Applies radius filter.
    - Optionally filters by name (contains).
    - Optionally filters by region.
    - Optionally filters by local-photo presence.
    """
    rows: List[Dict[str, Any]] = []
    name_query_lower = (name_query or "").strip().lower()

    for it in items:
        dkm = haversine_km(center_lat, center_lon, it["lat"], it["lon"])
        if dkm > radius_km:
            continue

        photo_now = has_photo_live(it)

        if only_with_photo and not photo_now:
            continue
        if only_without_photo and photo_now:
            continue

        if name_query_lower and name_query_lower not in it["name"].lower():
            continue

        if region_filter and region_filter != t("sidebar_region_all_option"):
            if str(it.get("region") or "") != region_filter:
                continue

        rows.append(
            {
                "id": it.get("id") or f"{it['name']}\n{it['lon']},{it['lat']}",
                "name": it["name"],
                "region": it["region"],
                "lat": it["lat"],
                "lon": it["lon"],
                "distance_km": round(dkm, 3),
                "has_photo": photo_now,
                "photo_url": it.get("photo_url"),
                "local_photo_path": it.get("local_photo_path"),
            }
        )

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(by=["distance_km", "name"]).reset_index(drop=True)
    return df


def geodesic_circle_polygon(lat: float, lon: float, radius_km: float, n_points: int = 128):
    """Return polygon (lon,lat) points approximating a geodesic circle."""
    R = 6371.0088
    d = radius_km / R
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)
    pts: List[Tuple[float, float]] = []
    for k in range(n_points):
        b = 2 * math.pi * (k / n_points)
        lat2 = math.asin(
            math.sin(lat1) * math.cos(d)
            + math.cos(lat1) * math.sin(d) * math.cos(b)
        )
        lon2 = lon1 + math.atan2(
            math.sin(b) * math.sin(d) * math.cos(lat1),
            math.cos(d) - math.sin(lat1) * math.sin(lat2),
        )
        pts.append([math.degrees(lon2), math.degrees(lat2)])
    pts.append(pts[0])
    return pts


def zoom_for_radius(radius_km: float) -> int:
    if radius_km <= 5:
        return 12
    if radius_km <= 10:
        return 11
    if radius_km <= 25:
        return 10
    if radius_km <= 50:
        return 9
    if radius_km <= 100:
        return 8
    return 7


def build_geojson(df_selected: pd.DataFrame) -> Dict[str, Any]:
    features: List[Dict[str, Any]] = []
    for _, row in df_selected.iterrows():
        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(row["lon"]), float(row["lat"])],
                },
                "properties": {
                    "name": row["name"],
                    "region": row["region"],
                    "has_photo": bool(row["has_photo"]),
                },
            }
        )
    return {"type": "FeatureCollection", "features": features}


def build_gpx(df_selected: pd.DataFrame) -> str:
    from xml.sax.saxutils import escape

    lines: List[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<gpx version="1.1" creator="HaciendasNearbyPublic" xmlns="http://www.topografix.com/GPX/1/1">',
    ]
    for _, row in df_selected.iterrows():
        lat = float(row["lat"])
        lon = float(row["lon"])
        name = escape(str(row["name"]))
        lines.append(f'  <wpt lat="{lat:.6f}" lon="{lon:.6f}">')
        lines.append(f"    <name>{name}</name>")
        lines.append("  </wpt>")
    lines.append("</gpx>")
    return "\n".join(lines)


# --------------------------------------------------------------------
# Streamlit app – public read-only
# --------------------------------------------------------------------

st.set_page_config(page_title="Haciendas Nearby – Public", page_icon="🏛️", layout="wide")

# Language selector
if "lang" not in st.session_state:
    st.session_state["lang"] = "es"

with st.sidebar:
    st.selectbox(
        t("sidebar_language_label"),
        options=list(LANGS.keys()),
        format_func=lambda k: LANGS[k],
        index=0 if st.session_state["lang"] == "es" else 1,
        key="lang",
    )

st.image("images/hacienda.png", width=250)
st.title(t("app_title"))

# Initialize session defaults
if "center_lat" not in st.session_state:
    st.session_state["center_lat"] = DEFAULT_LAT
if "center_lon" not in st.session_state:
    st.session_state["center_lon"] = DEFAULT_LON
if "radius_km" not in st.session_state:
    st.session_state["radius_km"] = DEFAULT_RADIUS_KM

center_lat = float(st.session_state["center_lat"])
center_lon = float(st.session_state["center_lon"])
radius_km = float(st.session_state["radius_km"])

# Sidebar: center & radius
st.sidebar.header(t("sidebar_search_center_header"))

center_lat_input = st.sidebar.number_input(
    t("sidebar_lat_label"),
    value=center_lat,
    format="%.6f",
)
center_lon_input = st.sidebar.number_input(
    t("sidebar_lon_label"),
    value=center_lon,
    format="%.6f",
)

st.session_state["center_lat"] = center_lat_input
st.session_state["center_lon"] = center_lon_input
center_lat = center_lat_input
center_lon = center_lon_input

center_coords_str = f"{center_lat:.6f},{center_lon:.6f}"
st.sidebar.markdown(f"**{t('sidebar_current_center_label')}**")
st.sidebar.code(center_coords_str, language="text")

gmaps_center_url = (
    f"https://www.google.com/maps/search/?api=1&query={center_lat:.6f},{center_lon:.6f}"
)
st.sidebar.markdown(f"[{t('sidebar_open_center_gmaps')}]({gmaps_center_url})")

if st.sidebar.button(t("sidebar_reset_center_btn")):
    st.session_state["center_lat"] = DEFAULT_LAT
    st.session_state["center_lon"] = DEFAULT_LON
    st.session_state["radius_km"] = DEFAULT_RADIUS_KM
    st.success(t("sidebar_reset_center_success", radius=DEFAULT_RADIUS_KM))
    st.rerun()

radius_km = st.sidebar.slider(
    t("sidebar_radius_label"),
    min_value=1,
    max_value=200,
    value=int(st.session_state["radius_km"]),
    step=1,
)
st.session_state["radius_km"] = float(radius_km)

# Sidebar: filters
st.sidebar.header(t("sidebar_filters_header"))
st.sidebar.caption(t("sidebar_filters_radius_note"))

name_query = st.sidebar.text_input(t("sidebar_filter_name_contains"), value="")

only_with_photo = st.sidebar.checkbox(
    t("sidebar_filter_only_with_photo"), value=False, key="f_with_photo_public"
)
only_without_photo = st.sidebar.checkbox(
    t("sidebar_filter_only_without_photo"), value=False, key="f_without_photo_public"
)

if only_with_photo and only_without_photo:
    only_without_photo = False
    st.sidebar.info(t("sidebar_conflicting_photo_filters"))

# Load and normalize catalog
catalog = load_catalog(CATALOG_JSON)
raw_items = catalog.get("items", [])
items_public = normalize_public_items(raw_items)

if not items_public:
    st.warning(t("catalog_not_found_warning"))
    st.stop()

# Region options based on public items
regions = sorted({it["region"] for it in items_public if it.get("region")})
region_all_label = t("sidebar_region_all_option")
region_options = [region_all_label] + regions
region_filter = st.sidebar.selectbox(
    t("sidebar_filter_region"),
    options=region_options,
    index=0,
)

# Sidebar: quick help (right below filters)
st.sidebar.header(t("sidebar_help_header"))
st.sidebar.markdown(t("sidebar_help_text"))

# Main layout
left, right = st.columns((1, 1))

# ------------------ Left: table & basic stats ------------------
with left:
    st.subheader(t("results_header"))

    df = df_for_radius(
        items_public,
        center_lat=center_lat,
        center_lon=center_lon,
        radius_km=radius_km,
        only_with_photo=only_with_photo,
        only_without_photo=only_without_photo,
        name_query=name_query,
        region_filter=region_filter,
    )

    if df.empty:
        st.info(t("no_items_in_radius_info"))
    else:
        n_total = len(df)
        n_with_photo = int(df["has_photo"].sum())
        n_without_photo = n_total - n_with_photo

        st.caption(
            t(
                "results_caption_template",
                lat=center_lat,
                lon=center_lon,
                radius=radius_km,
                total=n_total,
                with_photo=n_with_photo,
                without_photo=n_without_photo,
            )
        )

        # Human-friendly table (no rating)
        table_df = pd.DataFrame(
            {
                t("table_name_col"): df["name"],
                t("table_region_col"): df["region"],
                t("table_distance_col"): df["distance_km"],
                t("table_lat_col"): df["lat"],
                t("table_lon_col"): df["lon"],
                t("table_has_photo_col"): df["has_photo"].map(
                    lambda v: "Yes" if v else "No"
                ),
            }
        )
        st.dataframe(table_df, width="stretch")

# ------------------ Right: map ------------------
with right:
    st.subheader(t("map_header"))
    st.caption(t("map_tip_caption"))

    if df.empty:
        st.info(t("no_items_in_radius_info"))
    else:
        n_local = int(df["has_photo"].sum())
        n_without = len(df) - n_local
        st.write(
            t(
                "map_stats",
                items=len(df),
                local=n_local,
                without=n_without,
            )
        )

        # Prepare map data
        df_map = df.copy()
        df_map["color_r"] = df_map["has_photo"].map(lambda v: 34 if v else 160)
        df_map["color_g"] = df_map["has_photo"].map(lambda v: 197 if v else 160)
        df_map["color_b"] = df_map["has_photo"].map(lambda v: 94 if v else 160)

        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=zoom_for_radius(radius_km),
        )

        # Radius circle
        circle_pts = geodesic_circle_polygon(center_lat, center_lon, radius_km, n_points=128)
        polygon_data = [{"polygon": circle_pts, "name": "Search Radius"}]
        circle_layer = pdk.Layer(
            "PolygonLayer",
            data=polygon_data,
            get_polygon="polygon",
            get_fill_color=[59, 130, 246, 40],
            get_line_color=[59, 130, 246, 160],
            line_width_min_pixels=1,
        )

        center_layer = pdk.Layer(
            "ScatterplotLayer",
            data=pd.DataFrame(
                [
                    {
                        "lat": center_lat,
                        "lon": center_lon,
                        "color_r": 220,
                        "color_g": 38,
                        "color_b": 38,
                    }
                ]
            ),
            get_position="[lon, lat]",
            get_fill_color="[color_r, color_g, color_b, 220]",
            get_radius=350,
            radius_min_pixels=8,
            pickable=False,
        )

        markers_layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_map,
            get_position="[lon, lat]",
            get_fill_color="[color_r, color_g, color_b, 200]",
            get_radius=300,
            radius_min_pixels=6,
            radius_max_pixels=100,
            get_line_color=[0, 0, 0, 180],
            line_width_min_pixels=1.5,
            pickable=True,
        )

        tooltip = {
            "html": (
                "<b>{name}</b><br>"
                "Region: {region}<br>"
                "Distance: {distance_km} km"
            ),
            "style": {"backgroundColor": "white", "color": "black"},
        }

        deck = pdk.Deck(
            layers=[circle_layer, markers_layer, center_layer],
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style="light",
        )
        st.pydeck_chart(deck, height=600, width="stretch")

# ------------------ Selected hacienda quick view ------------------
st.subheader(t("selected_item_header"))

if df.empty:
    st.caption(t("selected_item_need_selection"))
else:
    names_for_preview = list(df["name"])
    if not names_for_preview:
        st.caption(t("selected_item_need_selection"))
    else:
        sel_name = st.selectbox(
            t("selected_choose_label"),
            options=sorted(set(names_for_preview)),
            key="sel_prev_name_public",
        )
        subset = df[df["name"] == sel_name]
        options = [
            f"{r['name']} @ ({float(r['lat']):.6f},{float(r['lon']):.6f})"
            for _, r in subset.iterrows()
        ]
        sel_label = st.selectbox(
            "Pinpoint", options=options, key="sel_prev_id_public"
        )

        try:
            latlon = sel_label.split("@")[1].strip().strip("()")
            lat_s, lon_s = latlon.split(",")
            sel_lat = round(float(lat_s), 6)
            sel_lon = round(float(lon_s), 6)
        except Exception:
            st.error("Could not parse selected coordinates.")
            sel_lat = sel_lon = None

        row = next(
            (
                r
                for _, r in df.iterrows()
                if r["name"] == sel_name
                and round(float(r["lat"]), 6) == sel_lat
                and round(float(r["lon"]), 6) == sel_lon
            ),
            None,
        )

        if row is None:
            st.caption(t("selected_item_need_selection"))
        else:
            st.markdown(f"**{row['name']}**")
            st.write(f"{t('selected_region_label')}: {row['region']}")
            st.write(
                f"{t('selected_coords_label')}: {float(row['lat']):.6f}, {float(row['lon']):.6f}"
            )
            st.write(
                f"{t('selected_distance_label')}: {float(row['distance_km']):.3f} km"
            )

            # Photo preview (read-only)
            shown = False
            local_path = row.get("local_photo_path")
            photo_url = clean_url(row.get("photo_url"))
            if local_path and os.path.exists(str(local_path)):
                st.image(local_path, width=360, caption=row["name"])
                shown = True
            elif photo_url:
                try:
                    st.image(photo_url, width=360, caption=row["name"])
                    shown = True
                except Exception:
                    shown = False

            if not shown:
                st.info(t("selected_no_photo"))

            if st.button(
                t("use_hacienda_as_center_btn"),
                key=f"use_center_public_{row['id']}",
            ):
                st.session_state["center_lat"] = float(row["lat"])
                st.session_state["center_lon"] = float(row["lon"])
                st.success(t("use_hacienda_as_center_success"))
                st.rerun()

# ------------------ Export (read-only) ------------------
st.subheader(t("export_header"))

if df.empty:
    st.caption(t("export_none"))
else:
    # Export data is exactly the filtered df; only safe columns are included
    export_df = df[["name", "lat", "lon", "region", "has_photo"]].copy()

    # CSV
    csv_bytes = export_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        t("export_csv_label"),
        csv_bytes,
        file_name="haciendas_public.csv",
        mime="text/csv",
    )

    # GeoJSON
    geojson_data = build_geojson(df)
    geojson_bytes = json.dumps(geojson_data, ensure_ascii=False, indent=2).encode("utf-8")
    st.download_button(
        t("export_geojson_label"),
        geojson_bytes,
        file_name="haciendas_public.geojson",
        mime="application/geo+json",
    )

    # GPX
    gpx_text = build_gpx(df)
    gpx_bytes = gpx_text.encode("utf-8")
    st.download_button(
        t("export_gpx_label"),
        gpx_bytes,
        file_name="haciendas_public.gpx",
        mime="application/gpx+xml",
    )

# ------------------ Footer ------------------
st.caption(t("footer_text"))
