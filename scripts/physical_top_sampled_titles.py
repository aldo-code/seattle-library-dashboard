# %% [markdown]
# # Título más prestado por año en la muestra física (2006-2025)
#
# Este script identifica el título más prestado en cada año dentro de la muestra
# balanceada de préstamos físicos de la Biblioteca Pública de Seattle (SPL).
#
# - **Entrada:** `data/physical_checkout_title_sample_balanced_250k.csv`
# - **Salida:** `dashboard_data/physical_top_sampled_titles_by_year.csv`
# - **Comando para ejecutar desde la carpeta raíz:**
#   `.venv\Scripts\python scripts/physical_top_sampled_titles.py`
#
# Audiencia objetivo: Estudiantes con un semestre de experiencia en Python.
# Código explícito, modular y comentado paso a paso.

# %% 1. Importación de librerías y configuración de rutas
from pathlib import Path

# Copia para el dashboard: lee los datos crudos de Session 1/data y escribe en dashboard/public/dashboard_data.
# Funciona desde cualquier carpeta: las rutas se calculan desde la ubicación de este archivo.
DASHBOARD_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = DASHBOARD_DIR.parent
import pandas as pd

# Definición de rutas relativas de entrada y salida
INPUT_FILE = PROJECT_ROOT / "data" / "physical_checkout_title_sample_balanced_250k.csv"
OUTPUT_DIR = DASHBOARD_DIR / "public" / "dashboard_data"
OUTPUT_FILE = OUTPUT_DIR / "physical_top_sampled_titles_by_year.csv"

# Crear la carpeta de salida si no existe
OUTPUT_DIR.mkdir(exist_ok=True)

# %% 2. Carga del conjunto de datos físico
# Leemos el archivo CSV. Forzamos los tipos string para 'isbn' y 'publicationyear'
# para evitar problemas con valores mixtos o ceros iniciales.
df = pd.read_csv(
    INPUT_FILE,
    dtype={"isbn": "string", "publicationyear": "string"}
)

# Validación 1: Verificar que la muestra contenga exactamente 250,000 filas
print(f"Filas leídas del archivo físico: {len(df)}")
assert len(df) == 250000, f"Error: Se esperaban 250,000 filas, pero se leyeron {len(df)}"

# %% 3. Sumar préstamos anuales por título y preservar metadatos
# Cada fila en la muestra representa el registro de un título en un mes particular.
# Agrupamos por año ('checkoutyear') y 'title'.
# Usamos .agg() para sumar los préstamos ('checkouts') y tomar el primer valor
# disponible para cada una de las columnas de metadatos descriptivos.
annual_titles = df.groupby(["checkoutyear", "title"], as_index=False).agg({
    "checkouts": "sum",
    "creator": "first",
    "materialtype": "first",
    "checkouttype": "first",
    "subjects": "first",
    "publisher": "first",
    "publicationyear": "first",
    "isbn": "first",
    "usageclass": "first",
})

# Renombramos 'checkoutyear' a 'checkout_year' para cumplir con el esquema estándar
annual_titles = annual_titles.rename(columns={"checkoutyear": "checkout_year"})

# %% 4. Seleccionar el título número 1 más prestado por cada año (2006 a 2025)
# Ordenamos primero por año ascendente y luego por préstamos descendente (mayor a menor)
annual_titles_sorted = annual_titles.sort_values(
    by=["checkout_year", "checkouts"],
    ascending=[True, False]
)

# Conservamos únicamente el registro con mayor número de préstamos de cada año (rango 1)
top_titles = annual_titles_sorted.drop_duplicates(subset=["checkout_year"], keep="first").copy()

# Ordenamos cronológicamente por año
top_titles = top_titles.sort_values(by="checkout_year").reset_index(drop=True)

# %% 5. Selección y orden de columnas finales
final_columns = [
    "checkout_year",
    "title",
    "creator",
    "materialtype",
    "checkouttype",
    "subjects",
    "publisher",
    "publicationyear",
    "isbn",
    "usageclass",
    "checkouts",
]
top_titles = top_titles[final_columns]

# %% 6. Aserciones y validaciones de calidad
# Validación 2: Exactamente 20 años (2006 a 2025)
print(f"Años únicos en el resultado: {len(top_titles)}")
assert len(top_titles) == 20, f"Error: Se esperaban 20 filas (una por año), pero se obtuvieron {len(top_titles)}"

# Validación 3: Rango de años exactamente de 2006 a 2025
unique_years = sorted(top_titles["checkout_year"].unique())
expected_years = list(range(2006, 2026))
assert unique_years == expected_years, f"Error: Los años no coinciden con 2006-2025: {unique_years}"

# Validación 4: Préstamos mayores a cero
assert (top_titles["checkouts"] > 0).all(), "Error: Existen títulos con préstamos menores o iguales a cero"

# %% 7. Guardar el archivo procesado
top_titles.to_csv(OUTPUT_FILE, index=False)
print(f"Archivo generado exitosamente en: {OUTPUT_FILE}")
print(top_titles[["checkout_year", "title", "checkouts"]])
