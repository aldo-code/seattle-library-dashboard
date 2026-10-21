# %% [markdown]
# # Proporciones de tipos de material por año: Préstamos Físicos
#
# Este script calcula la distribución de tipos de material (material type shares)
# para los préstamos físicos de la Biblioteca Pública de Seattle (2006-2025).
#
# - **Entrada:** `data/physical_checkout_title_sample_balanced_250k.csv`
#   (Muestra balanceada de 250,000 registros de títulos-mes físicos, 12,500 filas por año).
# - **Salida:** `dashboard_data/physical_material_type_shares_by_year.csv`
#   (Distribución anual de tipos de material con filas, préstamos y proporciones).
# - **Comando para re-ejecutar:**
#   `.venv\Scripts\python scripts/physical_material_type_shares.py`

# %% Importar librerías necesarias
from pathlib import Path

# Copia para el dashboard: lee los datos crudos de Session 1/data y escribe en dashboard/public/dashboard_data.
# Funciona desde cualquier carpeta: las rutas se calculan desde la ubicación de este archivo.
DASHBOARD_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = DASHBOARD_DIR.parent
import pandas as pd

# %% Definir rutas de archivos
INPUT_FILE = PROJECT_ROOT / "data" / "physical_checkout_title_sample_balanced_250k.csv"
OUTPUT_DIR = DASHBOARD_DIR / "public" / "dashboard_data"
OUTPUT_FILE = OUTPUT_DIR / "physical_material_type_shares_by_year.csv"

# Asegurar que el directorio de salida existe
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# %% Cargar los datos de la muestra física
print("Cargando datos desde:", INPUT_FILE)
df = pd.read_csv(INPUT_FILE)

# %% Validar tamaño general y estructura de la muestra
print(f"Filas cargadas: {len(df):,}")
assert len(df) == 250000, f"Se esperaban 250,000 filas pero se encontraron {len(df)}"

# Validar que cada año tenga exactamente 12,500 filas muestreadas
rows_per_year = df.groupby("checkoutyear").size()
assert len(rows_per_year) == 20, f"Se esperaban 20 años pero se encontraron {len(rows_per_year)}"
assert (rows_per_year == 12500).all(), "Cada año entre 2006 y 2025 debe tener exactamente 12,500 filas"

# %% Normalizar el tipo de material (materialtype)
# En el conjunto de datos de la biblioteca, los tipos de material presentan pequeñas variaciones
# de mayúsculas/minúsculas (por ejemplo, 'BOOK' vs 'Book', 'VIDEODISC' vs 'Videodisc').
# Para evitar que una misma categoría se divida en grupos duplicados, convertimos todos
# los valores a mayúsculas usando .str.upper().
df["materialtype"] = df["materialtype"].str.upper()

# %% Agrupar por año y tipo de material
# Contamos cuántas filas corresponden a cada tipo de material (sampled_rows)
# y sumamos la cantidad de préstamos que registraron esos títulos (sampled_checkouts).
grouped = (
    df.groupby(["checkoutyear", "materialtype"])
    .agg(
        sampled_rows=("checkouts", "count"),
        sampled_checkouts=("checkouts", "sum"),
    )
    .reset_index()
)

# Renombrar columnas para usar formato estándar descriptivo
grouped = grouped.rename(
    columns={
        "checkoutyear": "checkout_year",
        "materialtype": "material_type",
    }
)

# %% Calcular proporciones (shares)
# 1. Proporción de filas (row_share):
# Como cada año tiene exactamente 12,500 filas en el diseño muestral balanceado,
# dividimos las filas del material entre 12,500.
grouped["row_share"] = grouped["sampled_rows"] / 12500.0

# 2. Proporción de préstamos (checkout_share):
# Calculamos el total de préstamos muestreados en cada año y dividimos los préstamos
# de cada tipo de material entre el total de su respectivo año.
annual_total_checkouts = grouped.groupby("checkout_year")["sampled_checkouts"].transform("sum")
grouped["checkout_share"] = grouped["sampled_checkouts"] / annual_total_checkouts

# %% Ordenar datos
# Ordenamos por año ascendente y luego por cantidad de filas muestreadas descendente
grouped = grouped.sort_values(
    by=["checkout_year", "sampled_rows"],
    ascending=[True, False],
).reset_index(drop=True)

# Seleccionar y reordenar las columnas requeridas
columns_order = [
    "checkout_year",
    "material_type",
    "sampled_rows",
    "sampled_checkouts",
    "row_share",
    "checkout_share",
]
grouped = grouped[columns_order]

# %% Validaciones mediante aserciones (assert)
# 1. Comprobar que para cada año (2006 a 2025), la suma de row_share sea 1.0 (dentro de tolerancia de 1e-5)
annual_row_share_sums = grouped.groupby("checkout_year")["row_share"].sum()
for year, share_sum in annual_row_share_sums.items():
    assert abs(share_sum - 1.0) < 1e-5, f"La suma de row_share en {year} es {share_sum}, se esperaba 1.0"

# 2. Comprobar que para cada año (2006 a 2025), la suma de checkout_share sea 1.0 (dentro de tolerancia de 1e-5)
annual_checkout_share_sums = grouped.groupby("checkout_year")["checkout_share"].sum()
for year, share_sum in annual_checkout_share_sums.items():
    assert abs(share_sum - 1.0) < 1e-5, f"La suma de checkout_share en {year} es {share_sum}, se esperaba 1.0"

# 3. Comprobar que no haya valores nulos
assert grouped.isna().sum().sum() == 0, "No debe haber valores nulos en el resultado final"

print("Todas las validaciones pasaron exitosamente.")

# %% Guardar el resultado en archivo CSV
grouped.to_csv(OUTPUT_FILE, index=False)
print(f"Archivo guardado exitosamente en: {OUTPUT_FILE}")
print(f"Total de registros generados: {len(grouped)}")
