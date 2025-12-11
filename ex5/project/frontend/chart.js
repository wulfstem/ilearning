import { getRandomColor } from './utils.js';

export function createChart(chartType, labels, datasets) {
    const options = { 
        responsive: true,
        maintainAspectRatio: true,
        plugins: { 
            legend: {
                position: 'top',
                labels: {
                    boxWidth: 15,
                    padding: 15,
                    usePointStyle: true,
                    font: {
                        size: 11,
                        family: "'Segoe UI', sans-serif"
                    }
                }
            },
            tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                padding: 12,
                titleFont: { size: 13, weight: 'bold' },
                bodyFont: { size: 12 },
                cornerRadius: 8
            }
        },
        layout: {
            padding: {
                top: 10,
                bottom: 10
            }
        },
        scales: {
            x: {
                grid: {
                    display: false
                },
                ticks: {
                    callback: function(value, index) {
                        const step = 10;
                        return (index % step === 0) ? this.getLabelForValue(value) : '';
                    },
                    maxRotation: 45,
                    minRotation: 0,
                    font: { size: 10 }
                }
            },
            y: {
                grid: {
                    color: 'rgba(0, 0, 0, 0.05)'
                },
                ticks: {
                    font: { size: 10 }
                }
            }
        }
    };

    if (chartType === 'stackedBar') {
        options.scales.x.stacked = true;
        options.scales.y.stacked = true;
    }

    return new Chart(document.getElementById("chart"), {
        type: chartType === 'stackedBar' ? 'bar' : chartType,
        data: { labels, datasets },
        options
    });
}

export function buildDatasets(allAnalysis, selectedColumns, headers, chartType) {
    const datasets = [];

    allAnalysis.forEach((analysis, index) => {
        const c = selectedColumns[index];
        const values = analysis.values.map(v => parseFloat(v));
        const trend = analysis.trend.map(v => parseFloat(v));

        datasets.push({
            label: headers[c],
            data: values,
            borderColor: getRandomColor(index),
            backgroundColor: getRandomColor(index, 0.1),
            fill: chartType === 'line' ? false : true,
            tension: 0.4,
            pointRadius: 3,
            pointHoverRadius: 6,
            borderWidth: 2
        });

        datasets.push({
            label: headers[c] + " (Trend)",
            data: trend,
            borderColor: getRandomColor(index, 0.5),
            borderDash: [8, 4],
            fill: false,
            pointRadius: 0,
            borderWidth: 2
        });
    });

    return datasets;
}