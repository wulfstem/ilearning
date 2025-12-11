export function generatePDF(rawData) {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    
    const selectedMines = Array.from(document.querySelectorAll('.mine-chip.selected'))
        .map(chip => chip.textContent);
    const chartType = document.getElementById("chartType").selectedOptions[0].text;
    const trendDegree = document.getElementById("trendDegree").selectedOptions[0].text;
    const now = new Date();

    addCoverPage(doc, now, selectedMines);
    addChartsPage(doc, chartType, trendDegree);
    addStatsPage(doc);
    addAnomalyPage(doc);

    doc.save(`Weyland-Yutani-Report-${now.toISOString().split('T')[0]}.pdf`);
}

function addCoverPage(doc, now, selectedMines) {
    doc.setFillColor(102, 126, 234);
    doc.rect(0, 0, 210, 100, 'F');
    doc.setFillColor(118, 75, 162);
    doc.rect(0, 100, 210, 197, 'F');
    
    doc.setFontSize(48);
    doc.setFont(undefined, 'bold');
    doc.setTextColor(255, 255, 255);
    doc.text("WY", 105, 80, { align: 'center' });
    
    doc.setFontSize(28);
    doc.text("WEYLAND-YUTANI", 105, 110, { align: 'center' });
    
    doc.setFontSize(22);
    doc.text("Mining Operations", 105, 125, { align: 'center' });
    
    doc.setFontSize(16);
    doc.setFont(undefined, 'normal');
    doc.text("Analytics Report", 105, 145, { align: 'center' });
    
    doc.setFontSize(11);
    doc.setTextColor(240, 240, 240);
    doc.text(`Date: ${now.toLocaleDateString()} ${now.toLocaleTimeString()}`, 105, 170, { align: 'center' });
    doc.text(`Mines: ${selectedMines.join(', ')}`, 105, 180, { align: 'center' });
}

function addChartsPage(doc, chartType, trendDegree) {
    doc.addPage();
    
    doc.setFillColor(102, 126, 234);
    doc.rect(0, 0, 210, 25, 'F');
    doc.setFontSize(18);
    doc.setFont(undefined, 'bold');
    doc.setTextColor(255, 255, 255);
    doc.text("Production Trends", 14, 16);
    
    const chartCanvas = document.getElementById("chart");
    const chartImg = chartCanvas.toDataURL("image/png", 1.0);
    doc.addImage(chartImg, 'PNG', 10, 35, 190, 120);
    
    doc.setFontSize(10);
    doc.setTextColor(80, 80, 80);
    doc.setFont(undefined, 'normal');
    doc.text(`Chart Type: ${chartType}`, 14, 165);
    doc.text(`Trend Analysis: ${trendDegree}`, 14, 172);
    
    addFooter(doc, 2);
}

function addStatsPage(doc) {
    doc.addPage();
    
    doc.setFillColor(102, 126, 234);
    doc.rect(0, 0, 210, 25, 'F');
    doc.setFontSize(18);
    doc.setFont(undefined, 'bold');
    doc.setTextColor(255, 255, 255);
    doc.text("Statistical Analysis", 14, 16);
    
    const statsTable = document.querySelector("#statsTable table");
    if (statsTable) {
        doc.autoTable({ 
            html: statsTable, 
            startY: 35, 
            theme: 'striped',
            headStyles: { 
                fillColor: [102, 126, 234],
                textColor: [255, 255, 255],
                fontStyle: 'bold',
                fontSize: 10,
                halign: 'center'
            },
            bodyStyles: {
                fontSize: 9,
                halign: 'center'
            },
            alternateRowStyles: {
                fillColor: [245, 247, 250]
            },
            margin: { left: 14, right: 14 }
        });
    }
    
    addFooter(doc, 3);
}

function addAnomalyPage(doc) {
    doc.addPage();
    
    doc.setFillColor(118, 75, 162);
    doc.rect(0, 0, 210, 25, 'F');
    doc.setFontSize(18);
    doc.setFont(undefined, 'bold');
    doc.setTextColor(255, 255, 255);
    doc.text("Anomaly Detection", 14, 16);
    
    const anomalyTable = document.querySelector("#anomalyTable table");
    if (anomalyTable) {
        doc.autoTable({ 
            html: anomalyTable, 
            startY: 35,
            theme: 'striped',
            headStyles: { 
                fillColor: [118, 75, 162],
                textColor: [255, 255, 255],
                fontStyle: 'bold',
                fontSize: 9,
                halign: 'center'
            },
            bodyStyles: {
                fontSize: 8,
                halign: 'center',
                cellPadding: 4
            },
            alternateRowStyles: {
                fillColor: [245, 247, 250]
            },
            columnStyles: {
                0: { fontStyle: 'bold', fillColor: [250, 250, 250] }
            },
            margin: { left: 14, right: 14 }
        });
    }
    
    addFooter(doc, 4);
}

function addFooter(doc, pageNum) {
    doc.setFontSize(8);
    doc.setTextColor(150, 150, 150);
    doc.text("Weyland-Yutani Corporation", 14, 285);
    doc.text(`Page ${pageNum}`, 196, 285, { align: 'right' });
}