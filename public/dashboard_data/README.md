# Datos para el Dashboard de Préstamos de la Biblioteca Pública de Seattle (SPL)

Este directorio contiene las tablas de datos preparadas y optimizadas en formato CSV para alimentar el tablero de control (*dashboard*) del proyecto de análisis de préstamos de la Biblioteca Pública de Seattle.

Todos los archivos fueron generados mediante scripts de Python estructurados en celdas de porcentaje (`# %%`) ubicados en `scripts/`, siguiendo estrictamente las reglas del proyecto (`AGENTS.md`) y las especificaciones metodológicas de `data/README.md`.

---

## Índice de Archivos y Trazabilidad (Provenance)

### 1. `annual_digital_physical_share.csv`
- **Descripción:** Totales anuales de préstamos y cuota de participación proporcional para las clases física y digital durante los 20 años completos del periodo (2006–2025). Excluye los años parciales 2005 (inicia en abril) y 2026 (corta en abril).
- **Tipo de dato:** Censo completo (volumen total agregado).
- **Archivo fuente:** `data/combined_checkout_totals_by_month_usageclass.csv`
- **Script generador:** `scripts/annual_digital_physical_share.py`
- **Qué representa una fila:** Un año calendario completo (2006 a 2025).
- **Dimensiones:** 20 filas, 6 columnas.
- **Columnas:**
  - `checkout_year` (int): Año calendario (2006–2025).
  - `physical_checkouts` (int): Total acumulado de préstamos físicos en el año.
  - `digital_checkouts` (int): Total acumulado de préstamos digitales en el año.
  - `total_checkouts` (int): Total consolidado anual (`physical_checkouts + digital_checkouts`).
  - `digital_share` (float): Proporción digital (`digital_checkouts / total_checkouts`).
  - `physical_share` (float): Proporción física (`physical_checkouts / total_checkouts`).
- **Comando de regeneración:**
  ```powershell
  .venv\Scripts\python scripts/annual_digital_physical_share.py
  ```

---

### 2. `digital_top_sampled_titles_by_year.csv`
- **Descripción:** Título número 1 con mayor volumen de préstamos registrados dentro de la muestra balanceada digital para cada año (2006–2025), preservando la totalidad de sus metadatos bibliográficos.
- **Tipo de dato:** Muestra balanceada por año (12,500 filas título-mes por año).
- **Archivo fuente:** `data/digital_checkout_title_sample_balanced_250k.csv`
- **Script generador:** `scripts/digital_top_sampled_titles.py`
- **Qué representa una fila:** El título digital líder en préstamos muestreados en un año calendario.
- **Dimensiones:** 20 filas, 11 columnas.
- **Columnas:**
  - `checkout_year` (int): Año calendario.
  - `title` (str): Título de la obra.
  - `creator` (str): Autor, creador o entidad responsable.
  - `materialtype` (str): Formato del material (ej. EBOOK, AUDIOBOOK, VIDEO).
  - `checkouttype` (str): Plataforma o sistema de préstamo (ej. OverDrive, Hoopla).
  - `subjects` (str): Descriptores temáticos.
  - `publisher` (str): Editorial o casa publicadora.
  - `publicationyear` (str): Año de publicación.
  - `isbn` (str): Identificador ISBN normalizado en texto.
  - `usageclass` (str): Clase de uso (`Digital`).
  - `checkouts` (int): Suma de préstamos del título en los meses muestreados del año.
- **Comando de regeneración:**
  ```powershell
  .venv\Scripts\python scripts/digital_top_sampled_titles.py
  ```

---

### 3. `physical_top_sampled_titles_by_year.csv`
- **Descripción:** Título número 1 con mayor volumen de préstamos registrados dentro de la muestra balanceada física para cada año (2006–2025), preservando la totalidad de sus metadatos bibliográficos.
- **Tipo de dato:** Muestra balanceada por año (12,500 filas título-mes por año).
- **Archivo fuente:** `data/physical_checkout_title_sample_balanced_250k.csv`
- **Script generador:** `scripts/physical_top_sampled_titles.py`
- **Qué representa una fila:** El título físico líder en préstamos muestreados en un año calendario.
- **Dimensiones:** 20 filas, 11 columnas.
- **Columnas:**
  - `checkout_year` (int): Año calendario.
  - `title` (str): Título de la obra.
  - `creator` (str): Autor o creador.
  - `materialtype` (str): Formato del material (ej. BOOK, VIDEODISC, SOUNDDISC).
  - `checkouttype` (str): Plataforma de préstamo (ej. Horizon).
  - `subjects` (str): Materias y descriptores.
  - `publisher` (str): Editorial.
  - `publicationyear` (str): Año de catalogación física (puede incluir texto libre/puntuación).
  - `isbn` (str): Código ISBN.
  - `usageclass` (str): Clase de uso (`Physical`).
  - `checkouts` (int): Suma de préstamos del título en los meses muestreados del año.
- **Comando de regeneración:**
  ```powershell
  .venv\Scripts\python scripts/physical_top_sampled_titles.py
  ```

---

### 4. `digital_material_type_shares_by_year.csv`
- **Descripción:** Distribución anual de formatos (`material_type` normalizado a mayúsculas para unificar variantes como `EBOOK`/`Ebook`), detallando la cantidad de registros en la muestra, préstamos acumulados, cuota de filas (`row_share`) y cuota de préstamos (`checkout_share`).
- **Tipo de dato:** Muestra balanceada (12,500 filas por año).
- **Archivo fuente:** `data/digital_checkout_title_sample_balanced_250k.csv`
- **Script generador:** `scripts/digital_material_type_shares.py`
- **Qué representa una fila:** Un tipo de material digital en un año calendario determinado.
- **Dimensiones:** 99 filas, 6 columnas.
- **Columnas:**
  - `checkout_year` (int): Año calendario (2006–2025).
  - `material_type` (str): Tipo de material normalizado en mayúsculas (EBOOK, AUDIOBOOK, SONG, MUSIC, etc.).
  - `sampled_rows` (int): Cantidad de filas título-mes en la muestra.
  - `sampled_checkouts` (int): Suma de préstamos de ese material en la muestra del año.
  - `row_share` (float): Participación sobre el total de filas del año (`sampled_rows / 12500`).
  - `checkout_share` (float): Participación sobre el total de préstamos muestreados del año.
- **Comando de regeneración:**
  ```powershell
  .venv\Scripts\python scripts/digital_material_type_shares.py
  ```

---

### 5. `physical_material_type_shares_by_year.csv`
- **Descripción:** Distribución anual de formatos físicos (`material_type` normalizado a mayúsculas para unificar variantes como `BOOK`/`Book`), detallando la cantidad de registros en la muestra, préstamos acumulados, cuota de filas (`row_share`) y cuota de préstamos (`checkout_share`).
- **Tipo de dato:** Muestra balanceada (12,500 filas por año).
- **Archivo fuente:** `data/physical_checkout_title_sample_balanced_250k.csv`
- **Script generador:** `scripts/physical_material_type_shares.py`
- **Qué representa una fila:** Un tipo de material físico en un año calendario determinado.
- **Dimensiones:** 282 filas, 6 columnas.
- **Columnas:**
  - `checkout_year` (int): Año calendario (2006–2025).
  - `material_type` (str): Tipo de material normalizado en mayúsculas (BOOK, SOUNDDISC, VIDEODISC, etc.).
  - `sampled_rows` (int): Cantidad de filas título-mes en la muestra.
  - `sampled_checkouts` (int): Suma de préstamos de ese material en la muestra del año.
  - `row_share` (float): Participación sobre el total de filas del año (`sampled_rows / 12500`).
  - `checkout_share` (float): Participación sobre el total de préstamos muestreados del año.
- **Comando de regeneración:**
  ```powershell
  .venv\Scripts\python scripts/physical_material_type_shares.py
  ```

---

## Cómo regenerar todos los datos del Dashboard

Desde la carpeta raíz del proyecto (`Session 1`), ejecutar con el entorno virtual `.venv`:

```powershell
# 1. Cuota anual digital vs física
.venv\Scripts\python scripts/annual_digital_physical_share.py

# 2. Títulos más prestados en la muestra digital y física
.venv\Scripts\python scripts/digital_top_sampled_titles.py
.venv\Scripts\python scripts/physical_top_sampled_titles.py

# 3. Participación por tipos de material digital y físico
.venv\Scripts\python scripts/digital_material_type_shares.py
.venv\Scripts\python scripts/physical_material_type_shares.py
```

---

## Advertencias Metodológicas para Visualizaciones y Consumidores del Dashboard

1. **Años parciales excluidos:** Las series anuales cubren estrictamente 2006 a 2025. Los años 2005 (inicio en abril) y 2026 (corte en abril) no deben sumarse como años enteros porque producirían caídas falsas.
2. **Propiedades de la muestra vs. Universo:** Las tablas derivadas de las muestras de 250k filas reflejan distribuciones dentro de una muestra balanceada (12,500 filas por año). **No deben usarse los totales de `sampled_checkouts` para inferir el volumen absoluto total de préstamos de la biblioteca**; para totales se debe emplear siempre `annual_digital_physical_share.csv`.
3. **Normalización de formatos:** En los datos fuente, algunos formatos diferían únicamente por uso de mayúsculas (ej. `EBOOK` y `Ebook`). Los scripts han unificado los nombres a mayúsculas para evitar categorías duplicadas en el dashboard.
