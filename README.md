# Haciendas Nearby – Public Read-Only Explorer / Explorador Público de Haciendas

---

## 1. Overview / Descripción general

**Haciendas Nearby – Public** is a read-only, bilingual (Spanish/English) web application built with [Streamlit](https://streamlit.io/).  
The app provides an interactive explorer of historical *haciendas* in the state of Puebla (Mexico), based on a manually curated catalog derived from:

- A printed reference book on Puebla haciendas:
  * Álvarez, A. G. (2013). Arquitectura de la memoria: haciendas poblanas. Benemérita Universidad Autónoma de Puebla  
- An original KML dataset that was validated, cleaned, and georeferenced.

This **public** version:

- Exposes only a *frozen* catalog (`catalog_public.json`) generated from a separate, private curation tool.
- Does **not** allow any modification of the catalog (no edits, no new entries, no rating changes).
- Focuses on exploration, filtering, map visualization, and export of the currently visible subset.

---

## 2. Data and scope / Datos y alcance

The core dataset is stored in:

- `catalog_public.json` – a JSON file with an `"items"` array.  
  Each item represents one hacienda (or related historical site) with at least:

- `name`: human-readable name of the hacienda.
- `region`: region used for filtering (e.g., “Atlixco”, “Tepeaca”, “Cholula”).
- `lat`, `lon`: latitude and longitude in decimal degrees (WGS84).
- `photo_url`: optional remote photo URL (may or may not be valid over time).
- `local_photo_path`: optional path to a local JPEG in `fotos_public/`.

The app further **normalizes** these items for public display:

- Only items whose `source` is `"kml"` and that have a non-empty, assigned `region` are included.
- Coordinates are validated and coerced to floats.
- A computed `has_photo` flag indicates whether there is a usable *local* photo on disk.

> **Note (español):**  
> Este repositorio NO es la herramienta de edición del catálogo.  
> Solo contiene una exportación pública, estática, en formato JSON más fotos locales.

---

## 3. Application features / Funcionalidades de la aplicación

The main user-facing script is:

- `app_public.py` – the bilingual Streamlit application.

Key features:

1. **Language toggle / Selector de idioma**

   - The UI is fully bilingual: Spanish (`es`) and English (`en`).
   - A language selector in the sidebar stores the chosen language in `st.session_state["lang"]`.
   - All user-facing strings are defined in a `TEXTS` dictionary and accessed via the helper function `t(key, **fmt)`.

2. **Search center and radius / Centro de búsqueda y radio**

   - Default center: Amalucan, Puebla (`lat = 19.050501`, `lon = -98.135887`).
   - Default radius: `25 km`.
   - Users can:
     - Manually edit latitude and longitude.
     - Inspect and copy the current center coordinates (text field).
     - Open the center in Google Maps with a one-click link.
     - Reset center and radius to default values.

3. **Filtering / Filtros**

   All filters apply *only* to items within the current search radius:

   - **By name**: simple substring search (case-insensitive).
   - **By region**: dropdown from all regions present in `catalog_public.json`, plus an “(all)” option.
   - **By local photo status**:
     - “Only items with local photo”.
     - “Only items WITHOUT local photo”.
     - If both are checked simultaneously, the app enforces a consistent state and keeps only the “with photo” filter active.

4. **Results table / Tabla de resultados**

   - Displays all items that match the spatial and attribute filters, sorted by distance and name.
   - Columns (language-dependent labels):
     - Name
     - Region
     - Distance (km) from the current center
     - Latitude
     - Longitude
     - Local photo (Yes / No)

5. **Interactive map (pydeck) / Mapa interactivo (pydeck)**

   - Uses [pydeck](https://deck.gl/) to render:
     - A geodesic circle representing the search radius.
     - A red marker for the current center.
     - One marker per hacienda within the radius.
   - Visual encoding:
     - Greenish markers for items with local photo.
     - Greyish markers for items without local photo.
   - Hover tooltip shows:
     - Name
     - Region
     - Distance (km)

6. **Selected hacienda quick view / Vista rápida de hacienda seleccionada**

   - Two-step selection:
     1. Choose a hacienda name.
     2. Disambiguate by a label containing coordinates (if necessary).
   - Shows:
     - Name and region.
     - Coordinates and distance from the current center.
     - Local photo if available; otherwise remote `photo_url` if valid; otherwise an informative message.
   - Single-click button:
     - “Use this hacienda as search center” – updates the center and re-runs the app.

7. **Data export (read-only) / Exportación de datos (solo lectura)**

   For the currently filtered set of items (`df`):

   - **CSV** (`haciendas_public.csv`):
     - Columns: `name`, `lat`, `lon`, `region`, `has_photo`.
   - **GeoJSON** (`haciendas_public.geojson`):
     - One `Point` feature per hacienda with properties `name`, `region`, `has_photo`.
   - **GPX** (`haciendas_public.gpx`):
     - Waypoints (`<wpt>`) for each hacienda, suitable for GPS devices and mapping software.

8. **Read-only guarantee / Garantía de solo lectura**

   - The public app **never writes** back to `catalog_public.json`.
   - Session state changes (center, radius, language, selection) affect only the current user’s session in memory.

---

## 4. Internationalization (i18n) / Internacionalización

The app implements a very simple but robust i18n strategy:

- A global dictionary `TEXTS: Dict[str, Dict[str, str]]` maps string keys (e.g., `"app_title"`) to language variants.
- The helper function:

  ```python
  def t(key: str, **fmt: Any) -> str:
      lang = st.session_state.get("lang", "es")
      base = TEXTS.get(key, {})
      text = base.get(lang) or base.get("es") or key
      if fmt:
          try:
              return text.format(**fmt)
          except Exception:
              return text
      return text
  ```

  ensures:

  - Spanish is the fallback if the requested language is missing.
  - The key name itself is last-resort fallback.
  - Optional runtime formatting parameters can be injected via `.format`.

> **Nota (español):**  
> Esto permite mantener el código de la interfaz en un solo archivo (`app_public.py`) al mismo tiempo que agrega soporte bilingüe sin dependencias externas.

---

## 5. Installation and local development / Instalación y desarrollo local

### 5.1. Requirements / Requisitos

- Python 3.9+ (recommended).
- A working Git installation.
- (Optional but recommended) a virtual environment (e.g. `venv`, `conda`, `pyenv`).

The `requirements.txt` file defines the runtime dependencies:

```text
streamlit
pandas
pydeck
```

### 5.2. Clone the repository / Clonar el repositorio

On your local machine (Mac, Linux, or Windows):

```bash
git clone https://github.com/ferdiex/haciendas-nearby-public.git
cd haciendas-nearby-public
```

### 5.3. Create and activate a virtual environment / Crear y activar entorno virtual

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 5.4. Install dependencies / Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 6. Running the app locally / Ejecutar la app localmente

From the root of the repository, with the virtual environment activated:

```bash
streamlit run app_public.py
```

Streamlit will print a local URL, typically:

- `http://localhost:8501`

Open that URL in your browser. You should see:

- The bilingual title.
- The sidebar with language selection, center/radius controls, and filters.
- The table and map populated from `catalog_public.json`.

> **Important (español):**  
> Para ver las fotos locales, asegúrate de que la carpeta `fotos_public/` exista y contenga las imágenes mencionadas en `local_photo_path` dentro de `catalog_public.json`.

---

## 7. Deployment on Streamlit Cloud / Despliegue en Streamlit Cloud

Because the app is a standard Streamlit script, deploying to [Streamlit Community Cloud](https://streamlit.io/cloud) is straightforward:

1. Push the repository to GitHub (see section 8 below).
2. In Streamlit Cloud:
   - Create a new app.
   - Connect your GitHub account.
   - Select the repo: `ferdiex/haciendas-nearby-public`.
   - Select the main file: `app_public.py`.
3. Configure secrets only if necessary (this public version typically does not require secrets).
4. Deploy.

Streamlit will provision the environment using `requirements.txt` and run `app_public.py` automatically.

---

## 8. Git workflow: commit and push from the command line  
## 8. Flujo de trabajo Git: commit y push desde la línea de comandos

Below is a concise command-line workflow for macOS (applies similarly to Linux and Windows).

### 8.1. Check repository status / Ver estado del repositorio

```bash
cd /path/to/haciendas-nearby-public
git status
```

This shows:

- Modified files (`app_public.py`, `README.md`, etc.).
- Untracked files (new files that Git does not know yet).

### 8.2. Stage your changes / Agregar cambios al área de staging

To stage all modified and new files:

```bash
git add .
```

Or, to be more explicit and academic/clear:

```bash
git add README.md
git add app_public.py
git add catalog_public.json
```

### 8.3. Write a meaningful commit message / Crear un commit descriptivo

Use a concise, descriptive message (English is recommended for consistency):

```bash
git commit -m "Add bilingual academic README and document public Streamlit app"
```

If Git complains about user identity (name/email), configure it once:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Then re-run the `git commit` command.

### 8.4. Push to GitHub / Enviar cambios a GitHub

Assuming the default branch is `main`:

```bash
git push origin main
```

If this is the first push and you get an error about the upstream branch, you can set it explicitly:

```bash
git push -u origin main
```

After a successful push:

- The updated `README.md` and any code changes will be visible on GitHub.
- If you have Streamlit Cloud configured, it will typically auto-redeploy with the latest version.

---

## 9. Project structure / Estructura del proyecto

A minimal expected layout is:

```text
haciendas-nearby-public/
├─ app_public.py           # Main bilingual Streamlit app (public, read-only)
├─ catalog_public.json     # Public catalog of haciendas (curated, static)
├─ fotos_public/           # Local photo assets referenced by catalog_public.json
│  ├─ *.jpg
│  └─ ...
├─ requirements.txt        # Python dependencies
└─ README.md               # This bilingual academic-style README
```

> **Nota (español):**  
> Los archivos adicionales (por ejemplo, notebooks, scripts de exportación, etc.) deben documentarse aquí si afectan el flujo público.

---

## 10. Methodological and academic notes / Notas metodológicas y académicas

From an academic and digital-humanities perspective, this project can be characterized as:

- A **geospatial humanities resource**, focusing on historical haciendas in Puebla.
- Built with open-source tools (Python, Streamlit, pandas, pydeck).
- Designed for **reproducible exploration**:
  - The code that implements the filtering and distance calculations is fully transparent (`app_public.py`).
  - The dataset (`catalog_public.json`) is explicit and machine-readable.
- Using the **Haversine formula** (`haversine_km`) to compute great-circle distances between the search center and each hacienda, in kilometers, under a spherical Earth approximation.

---

## 11. License and attribution / Licencia y atribución

> **Important (español):**  
> Completa esta sección según los derechos de autor del libro base y del KML original.

Suggested structure:

- State the software license (e.g. MIT License, or another license of your choice).
- Clarify the status of the underlying data:
  - Whether it is open data.
  - Whether it is subject to any usage restrictions due to the source (book, KML, images).

Example (you must adapt to your actual terms):

> The code in this repository is released under the MIT License.  
> The underlying catalog data and images are based on a manually curated interpretation of a printed book and an original KML file.  
> Please verify and respect any copyright and usage restrictions that may apply to the original sources.

---

## 12. Acknowledgements / Agradecimientos

- Original author(s) of the book on Puebla haciendas.
- Contributors to the KML dataset.
- Community feedback and testers.
- Streamlit community and open-source ecosystem.

> **Gracias / Thank you** for using and contributing to this public explorer of Puebla’s haciendas.

