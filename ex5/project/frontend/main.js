import { fetchData, fetchAnalysis } from './api.js';
import { showLoading, hideLoading } from './utils.js';
import { createChart, buildDatasets } from './chart.js';
import { buildStatsTable, buildAnomalyTable } from './tables.js';
import { generatePDF } from './pdfGenerator.js';

let chart;
let rawData;
let headers;

async function renderMineFilter() {
    const data = await fetchData();
    headers = data.headers;
    rawData = data.rawData;

    const container = document.getElementById("mineFilterContainer");
    container.innerHTML = '';

    headers.slice(1).forEach((h, i) => {
        const chip = document.createElement('div');
        chip.textContent = h;
        chip.dataset.col = i + 1;
        chip.className = 'mine-chip selected';
        chip.onclick = () => {
            chip.classList.toggle('selected');
            drawDashboard();
        };
        container.appendChild(chip);
    });
}

window.selectAllMines = function() {
    document.querySelectorAll('.mine-chip').forEach(chip => {
        chip.classList.add('selected');
    });
    drawDashboard();
}

window.deselectAllMines = function() {
    document.querySelectorAll('.mine-chip').forEach(chip => {
        chip.classList.remove('selected');
    });
    drawDashboard();
}

function getSelectedColumns() {
    return Array.from(document.querySelectorAll('.mine-chip.selected'))
        .map(b => parseInt(b.dataset.col));
}

async function drawDashboard() {
    const selectedColumns = getSelectedColumns();
    if (selectedColumns.length === 0) {
        hideLoading();
        if (chart) chart.destroy();
        document.getElementById("statsTable").innerHTML = '<p style="text-align: center; color: #a0aec0; padding: 40px;">No mines selected. Please select at least one mine to view statistics.</p>';
        document.getElementById("anomalyTable").innerHTML = '<p style="text-align: center; color: #a0aec0; padding: 40px;">No mines selected. Please select at least one mine to view anomalies.</p>';
        return;
    }

    showLoading();

    try {
        const chartType = document.getElementById("chartType").value;
        const trendDegree = parseInt(document.getElementById("trendDegree").value);

        const labels = rawData.map(r => r[0]);

        const analysisPromises = selectedColumns.map(c => fetchAnalysis(c, trendDegree));
        const allAnalysis = await Promise.all(analysisPromises);

        const datasets = buildDatasets(allAnalysis, selectedColumns, headers, chartType);

        document.getElementById("statsTable").innerHTML = buildStatsTable(allAnalysis, selectedColumns, headers);
        document.getElementById("anomalyTable").innerHTML = buildAnomalyTable(allAnalysis, selectedColumns, headers);

        if (chart) chart.destroy();
        chart = createChart(chartType, labels, datasets);
    }
    catch (err) {
        console.error(err);
        alert("Error building dashboard: " + err.message);
    }
    finally {
        hideLoading();
    }
}

window.generateReport = function() {
    generatePDF(rawData);
}

document.getElementById("chartType").addEventListener("change", drawDashboard);
document.getElementById("trendDegree").addEventListener("change", drawDashboard);

await renderMineFilter();
drawDashboard();