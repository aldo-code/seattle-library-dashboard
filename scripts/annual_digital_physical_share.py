# %% [markdown]
# # Cuota anual de préstamos digitales vs. físicos (2006–2025)
#
# Este script procesa los datos mensuales agregados de la Biblioteca Pública de Seattle
# para calcular la distribución anual de préstamos entre materiales físicos y digitales.
#
# - **Entrada:** `data/combined_checkout_totals_by_month_usageclass.csv`
# - **Salida:** `dashboard_data/annual_digital_physical_share.csv`
# - **Comando para reejecutar:** `.venv\Scripts\python scripts/annual_digital_physical_share.py`

# %% Importar librerías necesarias
from pathlib import Path

# Copia para el dashboard: lee los datos crudos de Session 1/data y escribe en dashboard/public/dashboard_data.
# Funciona desde cualquier carpeta: las rutas se calculan desde la ubicación de este archivo.
DASHBOARD_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = DASHBOARD_DIR.parent
import pandas as pd

# %% Definir rutas de entrada y salida
INPUT_FILE = PROJECT_ROOT / "data" / "combined_checkout_totals_by_month_usageclass.csv"
OUTPUT_DIR = DASHBOARD_DIR / "public" / "dashboard_data"
OUTPUT_FILE = OUTPUT_DIR / "annual_digital_physical_share.csv"

# Crear el directorio de salida si no existe
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# %% Cargar los datos agregados mensuales
# Leemos el archivo CSV con los totales mensuales por clase de uso
aggregate_df = pd.read_csv(INPUT_FILE)

# Validación 1: Verificar el número total de filas esperadas en los datos crudos
assert len(aggregate_df) == 501, f"Se esperaban 501 filas en el archivo de entrada, pero se encontraron {len(aggregate_df)}"

# %% Filtrar para incluir únicamente años completos (2006 a 2025)
# Se excluyen los años parciales 2005 (inicia en abril) y 2026 (termina en abril)
complete_years_df = aggregate_df[(aggregate_df["checkout_year"] >= 2006) & (aggregate_df["checkout_year"] <= 2025)]

# Validación 2: Verificar que cada año filtrado tenga exactamente 12 meses
months_per_year = complete_years_df.groupby("checkout_year")["checkout_month"].nunique()
assert (months_per_year == 12).all(), "Todos los años entre 2006 y 2025 deben contener exactamente 12 meses"

# %% Agrupar y sumar los préstamos por año y clase de uso
# Agrupamos por año de préstamo y clase de uso ('Physical' o 'Digital')
annual_grouped = complete_years_df.groupby(["checkout_year", "usageclass"])["total_checkouts"].sum()
annual_grouped_df = annual_grouped.reset_index()

# %% Pivotear para organizar clases de uso en columnas separadas
# Reestructuramos la tabla para tener una fila por año y columnas para cada clase de uso
pivoted_df = annual_grouped_df.pivot(index="checkout_year", columns="usageclass", values="total_checkouts")

# Renombrar columnas a nombres descriptivos en minúsculas
renamed_df = pivoted_df.rename(columns={
    "Physical": "physical_checkouts",
    "Digital": "digital_checkouts"
})

# Restaurar el índice para que checkout_year sea una columna ordinaria
result_df = renamed_df.reset_index()
result_df.columns.name = None

# %% Calcular préstamos totales y las cuotas (shares) correspondientes
# Calculamos la suma total de préstamos por año
result_df["total_checkouts"] = result_df["physical_checkouts"] + result_df["digital_checkouts"]

# Calculamos la participación proporcional de cada clase
result_df["digital_share"] = result_df["digital_checkouts"] / result_df["total_checkouts"]
result_df["physical_share"] = result_df["physical_checkouts"] / result_df["total_checkouts"]

# Reordenar las columnas según la especificación requerida
ordered_columns = [
    "checkout_year",
    "physical_checkouts",
    "digital_checkouts",
    "total_checkouts",
    "digital_share",
    "physical_share"
]
result_df = result_df[ordered_columns]

# %% Validaciones de consistencia y completitud
# Validación 3: Debe haber exactamente 20 años completos (2006 a 2025)
assert len(result_df) == 20, f"Se esperaban 20 filas (años 2006 a 2025), pero se obtuvieron {len(result_df)}"

# Validación 4: La suma total de préstamos anuales debe ser idéntica a la suma de los datos mensuales
monthly_total_sum = complete_years_df["total_checkouts"].sum()
annual_total_sum = result_df["total_checkouts"].sum()
assert annual_total_sum == monthly_total_sum, (
    f"La suma total anual ({annual_total_sum}) no coincide con la suma mensual ({monthly_total_sum})"
)

# Validación 5: La suma de las proporciones digital y física debe redondear a 1.0 para cada año
shares_sum = (result_df["digital_share"] + result_df["physical_share"]).round(6)
assert (shares_sum == 1.0).all(), "La suma de digital_share y physical_share debe ser igual a 1.0 en todos los años"

# %% Guardar el resultado en formato CSV
result_df.to_csv(OUTPUT_FILE, index=False)
print(f"Archivo generado exitosamente en: {OUTPUT_FILE}")
print(f"Filas generadas: {len(result_df)}")
print("Primeras 5 filas:")
print(result_df.head())
