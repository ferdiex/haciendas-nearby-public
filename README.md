# Haciendas Nearby – Public Read-Only Explorer / Explorador Público de Haciendas

---

## 1. Overview / Descripción general

**Haciendas Nearby – Public** is a read-only, bilingual (Spanish/English) web application built with [Streamlit](https://streamlit.io/).  
The app provides an interactive explorer of historical *haciendas* in the state of Puebla (Mexico), based on a manually curated catalog derived from:

- A printed reference book on Puebla haciendas:  
  *Guzmán-Álvarez, A. (2013).* **Arquitectura de la memoria: haciendas poblanas**. Benemérita Universidad Autónoma de Puebla.  
  Disponible en el catálogo de la IBERO Puebla:  
  [Álvarez, A. G. (2013) – Ficha en el catálogo de la IBERO Puebla](https://biblio.iberopuebla.mx/cgi-bin/koha/opac-ISBDdetail.pl?biblionumber=172455)
- An original KML dataset that was validated, cleaned, and georeferenced.

This **public** version:

- Exposes only a *frozen* catalog (`catalog_public.json`) generated from a separate, private curation tool.
- Does **not** allow any modification of the catalog (no edits, no new entries, no rating changes).
- Focuses on exploration, filtering, map visualization, and export of the currently visible subset.

> **Nota (español):**  
> Esta app pública es un visor de solo lectura.  
> No incluye la herramienta privada de edición ni los procesos detallados de curaduría.

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

- Coordinates are validated and coerced to floats.
- A computed `has_photo` flag indicates whether there is a usable *local* photo on disk.

> **Nota (español):**  
> Este repositorio **no** es la herramienta de edición del catálogo.  
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
> Esto permite mantener el código de la interfaz en un solo archivo (`app_public.py`) y tener soporte bilingüe sin dependencias externas.

---

## 5. Installation and local development / Instalación y desarrollo local

### 5.1. Requirements / Requisitos

- Python 3.9+ (recommended).
- A working Git installation.
- (Optional but recommended) a virtual environment, either:
  - `venv` (Python standard library), or  
  - `conda` / `mamba` (Anaconda, Miniconda, etc.).

The `requirements.txt` file defines the minimal runtime dependencies:

```text
streamlit
pandas
pydeck
```

### 5.2. Clone the repository / Clonar el repositorio

On your local machine (macOS, Linux, or Windows):

```bash
git clone https://github.com/ferdiex/haciendas-nearby-public.git
cd haciendas-nearby-public
```

### 5.3. Option A – venv-based environment / Entorno con `venv`

**macOS or Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Then install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5.4. Option B – Conda environment / Entorno con `conda`

If you prefer `conda` (Anaconda or Miniconda):

```bash
conda create -n haciendas-nearby-public python=3.10
conda activate haciendas-nearby-public
pip install --upgrade pip
pip install -r requirements.txt
```

> **Nota (español):**  
> Aunque `conda` también puede instalar paquetes, aquí se usa `pip` para respetar directamente `requirements.txt`.  
> Si lo prefieres, puedes traducir ese archivo a un `environment.yml`.

---

## 6. Running the app locally / Ejecutar la app localmente

From the root of the repository, with your environment activated (`venv` o `conda`):

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

## 7. Project structure / Estructura del proyecto

The minimal expected layout is:

```text
haciendas-nearby-public/
├─ app_public.py           # Main bilingual Streamlit app (public, read-only)
├─ catalog_public.json     # Public catalog of haciendas (curated, static)
├─ fotos_public/           # Local photo assets referenced by catalog_public.json
│  ├─ *.jpg
│  └─ ...
├─ requirements.txt        # Python dependencies
└─ README.md               # This bilingual README
```

> **Nota (español):**  
> Archivos adicionales (por ejemplo, notebooks o scripts de exportación) se pueden documentar aquí si afectan el flujo público.

---

## 8. Methodological and academic notes / Notas metodológicas y académicas

From an academic and digital-humanities perspective, this project can be characterized as:

- A **geospatial humanities resource**, focusing on historical haciendas in Puebla.
- Built with open-source tools (Python, Streamlit, pandas, pydeck).
- Designed for **reproducible exploration**:
  - The code that implements the filtering and distance calculations is fully transparent (`app_public.py`).
  - The dataset (`catalog_public.json`) is explicit and machine-readable.
- Using the **Haversine formula** (`haversine_km`) to compute great-circle distances between the search center and each hacienda, in kilometers, under a spherical Earth approximation.

---

## 9. License and attribution / Licencia y atribución

### 9.1. Code / Código

Unless otherwise noted, the **application code** in this repository (e.g. `app_public.py`) is released under the MIT License:

> **Copyright © 2026 FERDIEX**  
>  
> Permission is hereby granted, free of charge, to any person obtaining a copy  
> of this software and associated documentation files (the "Software"), to deal  
> in the Software without restriction, including without limitation the rights  
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell  
> copies of the Software, and to permit persons to whom the Software is  
> furnished to do so, subject to the following conditions:  
>  
> The above copyright notice and this permission notice shall be included in all  
> copies or substantial portions of the Software.  
>  
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,  
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE  
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  
> LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,  
> OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE  
> SOFTWARE.

> **Nota (español):**  
> Si prefieres otra licencia de software (p. ej. Apache‑2.0, GPL, BSD), puedes cambiar este apartado y añadir el archivo de licencia correspondiente.

### 9.2. Catalog data and derived dataset / Datos del catálogo y conjunto derivado

The **curated public catalog** contained in `catalog_public.json` (and, when applicable, simple derived exports such as the CSV/GeoJSON/GPX generated by the app) is licensed under:

> **Creative Commons Attribution–NonCommercial 4.0 International (CC BY‑NC 4.0)**  
> [https://creativecommons.org/licenses/by-nc/4.0/](https://creativecommons.org/licenses/by-nc/4.0/)

This means, in summary:

- You are free to **share** (copy and redistribute) and **adapt** (remix, transform, and build upon) the catalog.
- Under the following terms:
  - **Attribution** – You must give appropriate credit to this project and provide a link to the license.
  - **NonCommercial** – You may not use the material for commercial purposes.

> **Importante (español):**  
> Para usar una licencia Creative Commons no necesitas “tramitar” nada especial:  
> basta con elegir la licencia adecuada y mencionarla explícitamente (como aquí).  
> Aun así, esta licencia solo se aplica a los elementos sobre los que sí tienes derechos (el catálogo curado, tus anotaciones, tus descripciones, etc.).

### 9.3. Underlying sources and original book / Fuentes de origen y libro base

The curated catalog is **based on** external sources that **do have their own copyright**:

- The printed book:  
  *Guzmán-Álvarez, A. (2013).* **Arquitectura de la memoria: haciendas poblanas**. Benemérita Universidad Autónoma de Puebla.
- The original KML dataset (no incluido aquí) y otras fuentes complementarias.

The rights to the full text, images, and layout of the book belong to their respective copyright holders.  
This project **does not** grant any additional rights over the book itself.

> **Nota (español):**  
> El uso detallado de contenido del libro (por ejemplo, textos extensos, fotografías originales o reproducciones completas) solo debe hacerse **previa solicitud y autorización expresa del autor y/o los titulares de derechos**.  
>  
> El catálogo público en este repositorio contiene una selección y organización propia de datos geográficos y nombres, pero **no sustituye** al libro original ni reproduce su contenido textual de forma sustancial.

---

## 10. Acknowledgements / Agradecimientos

- Thanks to Architect Ambrosio Guzmán for providing a copy of the original book and for his reference work on the haciendas of Puebla.
- Streamlit community and open-source ecosystem.

> **Gracias / Thank you** for using and exploring this public read-only viewer of Puebla’s haciendas.

## 11. Live app and citation / App en vivo y citación

### 11.1. Live public app / App pública en vivo

The public, read-only version of this explorer is available on Streamlit Cloud:

- Live app: https://haciendas-nearby.streamlit.app/  
- Source code: https://github.com/ferdiex/haciendas-nearby-public

![QR code to open the app](images/QR.jpg)

> **Nota (español):**  
> La app en Streamlit Cloud es una vista pública de solo lectura basada en este repositorio.

### 11.2. Suggested citation / Citación sugerida

If you use this tool in academic work, you may cite it as:

> Montes-Gonzalez, F. ([2026]). *Haciendas Nearby – Public read-only explorer: Historical haciendas in Puebla (Mexico).*  
> Streamlit web application. Retrieved from https://haciendas-nearby.streamlit.app/

And for the underlying printed reference:

> Guzmán-Álvarez, A. (2013). *Arquitectura de la memoria: haciendas poblanas.* Benemérita Universidad Autónoma de Puebla.  
> Available in the IBERO Puebla catalog: https://biblio.iberopuebla.mx/cgi-bin/koha/opac-ISBDdetail.pl?biblionumber=172455