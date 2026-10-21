// Dashboard de préstamos de la Biblioteca Pública de Seattle.
// Todos los datos se leen en tiempo de ejecución desde dashboard_data/*.csv (no hay datos incrustados).
// Las cifras de los textos de hallazgos se calculan aquí a partir de esos mismos CSV.

const DATA = "dashboard_data/";
const COLORS = {
  navy: "#012169", royal: "#00539B", copper: "#C84E00", eno: "#339898",
  persimmon: "#E89923", ironweed: "#993399", graphite: "#666666", limestone: "#E5E5E5",
};
// Colores de series: todos con contraste >= 3:1 contra blanco (WCAG 1.4.11). Navy 14,8:1, Copper 4,6:1,
// Eno 3,5:1, gris #767676 4,5:1. Entre segmentos se dibuja un borde blanco para que cada color quede junto a blanco.
const SERIES_COLORS = [COLORS.navy, COLORS.copper, COLORS.eno];
// Color del texto dentro de cada barra (contraste >= 4,5:1): blanco sobre Navy/Copper/gris, negro sobre Eno (6,1:1).
const SERIES_TEXT_COLORS = ["#FFFFFF", "#FFFFFF", "#000000"];
const OTHER_COLOR = "#767676";
const REDUCED_MOTION = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const PLOT_CONFIG = { responsive: true, displaylogo: false, modeBarButtonsToRemove: ["lasso2d", "select2d"] };
// Si el sistema pide menos movimiento, las transiciones de Plotly duran 0 ms.
const TRANSITION = REDUCED_MOTION ? { duration: 0 } : { duration: 300 };
const BASE_LAYOUT = {
  font: { family: "Arial, sans-serif", size: 15, color: "#262626" },
  margin: { t: 20, r: 20, b: 60, l: 70 },
  paper_bgcolor: "#FFFFFF", plot_bgcolor: "#FFFFFF",
  xaxis: { title: { text: "Año" }, dtick: 2, gridcolor: COLORS.limestone },
  legend: { orientation: "h", y: -0.18 },
  hoverlabel: { font: { size: 15 } },
};

const pct = (x, digits = 0) => (x * 100).toLocaleString("es-CO", { maximumFractionDigits: digits, minimumFractionDigits: digits }) + " %";
const millions = (x) => (x / 1e6).toLocaleString("es-CO", { maximumFractionDigits: 1, minimumFractionDigits: 1 }) + " M";
const intFmt = (x) => Number(x).toLocaleString("es-CO");

function loadCsv(file) {
  return new Promise((resolve, reject) => {
    Papa.parse(DATA + file, {
      download: true, header: true, dynamicTyping: true, skipEmptyLines: true,
      complete: (result) => resolve(result.data),
      error: (err) => reject(new Error(file + ": " + err)),
    });
  });
}

// ---------- 1. Físico vs. digital (archivo agregado completo) ----------
function renderShare(rows) {
  rows.sort((a, b) => a.checkout_year - b.checkout_year);
  const years = rows.map((r) => r.checkout_year);

  Plotly.newPlot("share-chart", [
    { x: years, y: rows.map((r) => r.physical_checkouts / 1e6), name: "Físico", mode: "lines+markers",
      line: { color: COLORS.copper, width: 4, dash: "dash" }, marker: { size: 9, symbol: "circle" },
      hovertemplate: "%{x}: %{y:.2f} M préstamos físicos<extra></extra>" },
    { x: years, y: rows.map((r) => r.digital_checkouts / 1e6), name: "Digital", mode: "lines+markers",
      line: { color: COLORS.navy, width: 4 }, marker: { size: 9, symbol: "square" },
      hovertemplate: "%{x}: %{y:.2f} M préstamos digitales<extra></extra>" },
  ], { ...BASE_LAYOUT, yaxis: { title: { text: "Préstamos (millones)" }, ticksuffix: " M", rangemode: "tozero", gridcolor: COLORS.limestone } }, PLOT_CONFIG);

  const first = rows[0];
  const last = rows[rows.length - 1];
  const crossover = rows.find((r) => r.digital_share > 0.5);
  const peakPhysical = rows.reduce((best, r) => (r.physical_checkouts > best.physical_checkouts ? r : best));

  document.getElementById("kpis").innerHTML = `
    <div class="kpi"><span class="value">${pct(first.digital_share, 1)}</span><span class="label">de los préstamos eran digitales en ${first.checkout_year}</span></div>
    <div class="kpi"><span class="value">${pct(last.digital_share)}</span><span class="label">son digitales en ${last.checkout_year}</span></div>
    <div class="kpi"><span class="value">${crossover.checkout_year}</span><span class="label">primer año con mayoría digital</span></div>
    <div class="kpi"><span class="value">${millions(last.total_checkouts)}</span><span class="label">préstamos en total en ${last.checkout_year}</span></div>`;

  document.getElementById("share-chart").setAttribute("aria-label",
    `Gráfico de líneas de préstamos anuales físicos y digitales, ${first.checkout_year}–${last.checkout_year}. ` +
    `Lo físico alcanzó su máximo en ${peakPhysical.checkout_year} y lo digital superó el 50 % en ${crossover.checkout_year}. ` +
    "La tabla con todos los datos está debajo del gráfico.");

  fillTable("share-table", ["Año", "Físico", "Digital", "% digital"],
    rows.map((r) => [r.checkout_year, intFmt(r.physical_checkouts), intFmt(r.digital_checkouts), pct(r.digital_share, 1)]));

  document.getElementById("share-finding").innerHTML =
    `El eje horizontal muestra los años ${first.checkout_year}–${last.checkout_year} y el vertical los préstamos en millones ` +
    "(línea continua con cuadrados: digital; línea discontinua con círculos: físico). " +
    `<strong>Hallazgo:</strong> los préstamos físicos llegaron a su máximo en ${peakPhysical.checkout_year} ` +
    `(${millions(peakPhysical.physical_checkouts)}) y luego bajaron. En ${crossover.checkout_year} lo digital pasó a ser mayoría ` +
    `(${pct(crossover.digital_share)}) y en ${last.checkout_year} sigue siéndolo con ${pct(last.digital_share)} del total.`;
}

// ---------- 2. Tipos de material (muestras) ----------
const materialData = {};

function topMaterialTypes(rows, howMany) {
  const totals = {};
  rows.forEach((r) => { totals[r.material_type] = (totals[r.material_type] || 0) + r.sampled_checkouts; });
  return Object.keys(totals).sort((a, b) => totals[b] - totals[a]).slice(0, howMany);
}

function renderMaterial(kind) {
  const rows = materialData[kind];
  const years = [...new Set(rows.map((r) => r.checkout_year))].sort((a, b) => a - b);
  const top = topMaterialTypes(rows, 3); // 3 tipos + "Otros" = 4 categorías (máximo del checklist)

  const shareOf = (year, type) => {
    const row = rows.find((r) => r.checkout_year === year && r.material_type === type);
    return row ? row.checkout_share : 0;
  };
  const otherShare = (year) => {
    let sum = 0;
    rows.forEach((r) => { if (r.checkout_year === year && !top.includes(r.material_type)) sum += r.checkout_share; });
    return sum;
  };

  const traces = top.map((type, i) => ({
    type: "bar", name: type, x: years, y: years.map((y) => shareOf(y, type) * 100),
    marker: { color: SERIES_COLORS[i], line: { color: "#FFFFFF", width: 1.5 } },
    text: years.map((y) => barLabel(shareOf(y, type))), textposition: "inside", insidetextanchor: "middle",
    textfont: { color: SERIES_TEXT_COLORS[i], size: 13 },
    hovertemplate: `${type} · %{x}: %{y:.1f} %<extra></extra>`,
  }));
  traces.push({
    type: "bar", name: "Otros", x: years, y: years.map((y) => otherShare(y) * 100),
    marker: { color: OTHER_COLOR, line: { color: "#FFFFFF", width: 1.5 } },
    text: years.map((y) => barLabel(otherShare(y))), textposition: "inside", insidetextanchor: "middle",
    textfont: { color: "#FFFFFF", size: 13 },
    hovertemplate: "Otros · %{x}: %{y:.1f} %<extra></extra>",
  });

  Plotly.react("material-chart", traces, {
    ...BASE_LAYOUT, barmode: "stack", bargap: 0.15, transition: TRANSITION,
    legend: { ...BASE_LAYOUT.legend, traceorder: "reversed" },
    yaxis: { title: { text: "% de préstamos en la muestra" }, range: [0, 100], ticksuffix: " %", gridcolor: COLORS.limestone },
  }, PLOT_CONFIG);

  // Hallazgo: tipo líder en el primer y en el último año, y año en que cambia el líder (si cambia)
  const leaderOf = (year) => top.reduce((best, t) => (shareOf(year, t) > shareOf(year, best) ? t : best), top[0]);
  const firstYear = years[0];
  const lastYear = years[years.length - 1];
  const firstLeader = leaderOf(firstYear);
  const lastLeader = leaderOf(lastYear);
  const label = kind === "digital" ? "digitales" : "físicos";
  let text = `<strong>Hallazgo:</strong> entre los préstamos ${label} de la muestra, en ${firstYear} dominaba <strong>${firstLeader}</strong> ` +
    `(${pct(shareOf(firstYear, firstLeader))})`;
  if (firstLeader !== lastLeader) {
    // Primer año a partir del cual el líder actual ya no pierde el primer lugar
    const yearsWithOtherLeader = years.filter((y) => leaderOf(y) !== lastLeader);
    const lastOtherYear = yearsWithOtherLeader[yearsWithOtherLeader.length - 1];
    const changeYear = years.find((y) => y > lastOtherYear);
    text += ` y desde ${changeYear} lidera <strong>${lastLeader}</strong>, con ${pct(shareOf(lastYear, lastLeader))} en ${lastYear}.`;
  } else {
    text += ` y en ${lastYear} sigue liderando con ${pct(shareOf(lastYear, lastLeader))}.`;
  }
  text += " Son porcentajes de la muestra, no de toda la colección.";
  document.getElementById("material-finding").innerHTML =
    "El eje horizontal muestra los años y el vertical el porcentaje de préstamos de la muestra de cada tipo de material " +
    "(cada barra suma 100 %). " + text;

  document.getElementById("material-chart").setAttribute("aria-label",
    `Gráfico de barras apiladas: participación por tipo de material en los préstamos ${label} de la muestra, ` +
    `${firstYear}–${lastYear}. Al inicio lidera ${firstLeader} y al final ${lastLeader}. La tabla con todos los datos está debajo del gráfico.`);

  fillTable("material-table", ["Año", ...top, "Otros"],
    years.map((y) => [y, ...top.map((t) => pct(shareOf(y, t), 1)), pct(otherShare(y), 1)]));
  document.getElementById("material-table-summary").textContent =
    `Ver los datos del gráfico en una tabla (${kind === "digital" ? "digital" : "físico"})`;
}

// ---------- 3. Título más prestado por año (muestras) ----------
const titleData = {};

// Los títulos físicos traen la ficha de catálogo completa ("Título [videorecording] / Productora ; ...").
// Para la tabla se muestra solo el título; el texto completo queda en el tooltip.
function shortTitle(title) {
  let short = String(title || "").split(" / ")[0];
  short = short.replace(/\s*\[[^\]]*\]\s*/g, " ").trim();
  return short || String(title || "");
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text == null ? "" : String(text);
  return div.innerHTML;
}

// La ficha completa se muestra en un <details> (accesible con teclado y lector de pantalla), no en un tooltip.
function titleCell(title) {
  const short = shortTitle(title);
  if (short === String(title || "").trim()) return escapeHtml(short);
  return `${escapeHtml(short)}<details class="full-record"><summary>Ficha completa</summary>${escapeHtml(title)}</details>`;
}

function renderTitles(kind) {
  const rows = [...titleData[kind]].sort((a, b) => a.checkout_year - b.checkout_year);
  document.querySelector("#titles-table tbody").innerHTML = rows.map((r) => `
    <tr>
      <td>${r.checkout_year}</td>
      <td>${titleCell(r.title)}</td>
      <td>${escapeHtml(r.creator || "—")}</td>
      <td>${escapeHtml(r.materialtype)}</td>
      <td class="num">${intFmt(r.checkouts)}</td>
    </tr>`).join("");

  // Hallazgo: título que más años aparece como líder, y material más común entre los líderes
  const countBy = (key) => {
    const counts = {};
    rows.forEach((r) => { const k = key(r); counts[k] = (counts[k] || 0) + 1; });
    return Object.entries(counts).sort((a, b) => b[1] - a[1])[0];
  };
  const [repeatedTitle, repeatedCount] = countBy((r) => shortTitle(r.title));
  const [mainMaterial, materialCount] = countBy((r) => r.materialtype);
  let text = `<strong>Hallazgo:</strong> el material más común entre los líderes anuales es <strong>${escapeHtml(mainMaterial)}</strong> ` +
    `(${materialCount} de ${rows.length} años).`;
  if (repeatedCount > 1) {
    text += ` <strong>${escapeHtml(repeatedTitle)}</strong> fue el más prestado de la muestra en ${repeatedCount} años distintos.`;
  } else {
    text += " Ningún título repite como líder: cada año gana uno distinto.";
  }
  document.getElementById("titles-finding").innerHTML = text;
}

// ---------- Tablas de datos accesibles (alternativa a los gráficos) ----------
function barLabel(share) {
  return share >= 0.08 ? Math.round(share * 100) + " %" : "";
}

function fillTable(tableId, headers, rows) {
  const table = document.getElementById(tableId);
  table.querySelector("thead").innerHTML =
    "<tr>" + headers.map((h, i) => `<th scope="col"${i > 0 ? ' class="num"' : ""}>${escapeHtml(h)}</th>`).join("") + "</tr>";
  table.querySelector("tbody").innerHTML = rows.map((cells) =>
    "<tr>" + cells.map((c, i) => (i === 0 ? `<th scope="row">${escapeHtml(c)}</th>` : `<td class="num">${escapeHtml(c)}</td>`)).join("") + "</tr>"
  ).join("");
}

// ---------- Botones digital / físico ----------
function setupToggle(attribute, render) {
  const buttons = document.querySelectorAll(`button[data-${attribute}]`);
  buttons.forEach((button) => button.addEventListener("click", () => {
    buttons.forEach((b) => b.setAttribute("aria-pressed", String(b === button)));
    render(button.dataset[attribute]);
  }));
}

// ---------- Inicio ----------
Promise.all([
  loadCsv("annual_digital_physical_share.csv"),
  loadCsv("digital_material_type_shares_by_year.csv"),
  loadCsv("physical_material_type_shares_by_year.csv"),
  loadCsv("digital_top_sampled_titles_by_year.csv"),
  loadCsv("physical_top_sampled_titles_by_year.csv"),
]).then(([share, digitalMaterial, physicalMaterial, digitalTitles, physicalTitles]) => {
  materialData.digital = digitalMaterial;
  materialData.physical = physicalMaterial;
  titleData.digital = digitalTitles;
  titleData.physical = physicalTitles;

  renderShare(share);
  renderMaterial("digital");
  renderTitles("digital");
  setupToggle("material", renderMaterial);
  setupToggle("titles", renderTitles);
}).catch((error) => {
  document.getElementById("kpis").innerHTML =
    `<p class="loading">No se pudieron cargar los datos (${escapeHtml(error.message)}). ` +
    "Abre la página con un servidor local: <code>python -m http.server</code> dentro de <code>dashboard/public</code>.</p>";
  console.error(error);
});
