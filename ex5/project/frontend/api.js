const API_BASE = "https://task5-abfk.onrender.com";

export async function fetchData() {
    const res = await fetch(`${API_BASE}/data`);
    if (!res.ok) {
        throw new Error(`Failed to fetch data: ${res.status}`);
    }
    const json = await res.json();
    const headers = json.headers;
    const rawData = json.rows.map(row => row.map(v => isNaN(v) ? v : parseFloat(v)));
    return { headers, rawData };
}

export async function fetchAnalysis(column, degree) {
    const res = await fetch(`${API_BASE}/analyze?column=${column}&trend_degree=${degree}`);
    
    if (!res.ok) {
        const text = await res.text();
        console.error('API Error Response:', text);
        throw new Error(`API returned ${res.status}: ${text.substring(0, 200)}`);
    }
    
    const contentType = res.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
        const text = await res.text();
        console.error('Non-JSON Response:', text);
        throw new Error(`Expected JSON but got ${contentType}. Response: ${text.substring(0, 200)}`);
    }
    
    return await res.json();
}