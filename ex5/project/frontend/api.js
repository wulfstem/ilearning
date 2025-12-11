const API_BASE = "http://localhost:8000";

export async function fetchData() {
    const res = await fetch(`${API_BASE}/data`);
    const json = await res.json();
    const headers = json.headers;
    const rawData = json.rows.map(row => row.map(v => isNaN(v) ? v : parseFloat(v)));
    return { headers, rawData };
}

export async function fetchAnalysis(column, degree) {
    const res = await fetch(`${API_BASE}/analyze?column=${column}&trend_degree=${degree}`);
    return await res.json();
}