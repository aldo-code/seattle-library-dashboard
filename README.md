# Dashboard – Préstamos de la Biblioteca Pública de Seattle (2006–2025)

Dashboard estático (HTML, CSS y JavaScript con Plotly.js) que lee sus datos en tiempo de ejecución desde archivos CSV. No hay datos incrustados en la página.

## Estructura

```
dashboard/
  public/                      <- lo que se publica en GitHub Pages
    index.html, index.css, app.js
    dashboard_data/            <- 5 CSV + README de procedencia
  scripts/                     <- scripts percent-cell que generan los CSV
  .github/workflows/pages.yml  <- publica public/ en GitHub Pages
```

| CSV | Script | Datos de origen | Tipo |
|---|---|---|---|
| `annual_digital_physical_share.csv` | `scripts/annual_digital_physical_share.py` | agregado mensual | completo |
| `digital_top_sampled_titles_by_year.csv` | `scripts/digital_top_sampled_titles.py` | muestra digital | muestra |
| `physical_top_sampled_titles_by_year.csv` | `scripts/physical_top_sampled_titles.py` | muestra física | muestra |
| `digital_material_type_shares_by_year.csv` | `scripts/digital_material_type_shares.py` | muestra digital | muestra |
| `physical_material_type_shares_by_year.csv` | `scripts/physical_material_type_shares.py` | muestra física | muestra |

Detalle de columnas y procedencia: `public/dashboard_data/README.md`.

## Regenerar los datos

Los scripts leen los datos crudos de `Session 1/data/` (no se copian aquí porque las muestras pesan ~125 MB) y escriben en `public/dashboard_data/`. Las rutas se calculan desde la ubicación de cada script, así que funcionan desde cualquier carpeta. Desde `Session 1`:

```
.venv\Scripts\python dashboard\scripts\annual_digital_physical_share.py
.venv\Scripts\python dashboard\scripts\digital_top_sampled_titles.py
.venv\Scripts\python dashboard\scripts\physical_top_sampled_titles.py
.venv\Scripts\python dashboard\scripts\digital_material_type_shares.py
.venv\Scripts\python dashboard\scripts\physical_material_type_shares.py
```

## Ver el dashboard localmente

La página carga los CSV con `fetch`, así que necesita un servidor local (abrir `index.html` con doble clic no funciona):

```
.venv\Scripts\python -m http.server 8765 --bind 127.0.0.1 --directory dashboard\public
```

y abrir http://127.0.0.1:8765

## Origen

- Datos: Seattle Open Data, "Checkouts by Title" (`tmmm-ytt6`).
- Los CSV del dashboard fueron generados por subagentes de Antigravity (Sesión 3) y verificados de forma independiente con Claude Code.
- La página fue construida con Claude Code; colores de la paleta oficial de Duke (https://brand.duke.edu/colors).
