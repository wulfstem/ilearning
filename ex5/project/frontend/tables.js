import { formatList } from './utils.js';

export function buildStatsTable(allAnalysis, selectedColumns, headers) {
    let statsTableContent = '';

    allAnalysis.forEach((analysis, index) => {
        const c = selectedColumns[index];
        statsTableContent += `<tr>
            <td><strong>${headers[c]}</strong></td>
            <td>${analysis.stats.mean.toFixed(2)}</td>
            <td>${analysis.stats.std.toFixed(2)}</td>
            <td>${analysis.stats.median.toFixed(2)}</td>
            <td>${analysis.stats.iqr.toFixed(2)}</td>
        </tr>`;
    });

    return `<table>
        <tr><th>Mine</th><th>Mean</th><th>Std Dev</th><th>Median</th><th>IQR</th></tr>
        ${statsTableContent}
    </table>`;
}

export function buildAnomalyTable(allAnalysis, selectedColumns, headers) {
    let anomalyTableContent = '';

    allAnalysis.forEach((analysis, index) => {
        const c = selectedColumns[index];
        const anomalies = analysis.anomalies;

        anomalyTableContent += `<tr>
            <td><strong>${headers[c]}</strong></td>
            <td>${formatList(anomalies.iqr)}</td>
            <td>${formatList(anomalies.zscore)}</td>
            <td>${formatList(anomalies.moving_avg)}</td>
            <td>${formatList(anomalies.grubbs)}</td>
        </tr>`;
    });

    return `<table>
        <tr><th>Mine</th><th>IQR</th><th>Z-Score</th><th>Moving Avg</th><th>Grubbs</th></tr>
        ${anomalyTableContent}
    </table>`;
}