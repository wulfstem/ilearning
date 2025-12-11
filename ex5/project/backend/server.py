from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import numpy as np
from scipy import stats
import uvicorn
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "service_account.json")


SHEET_ID = "1xY11kAjYRfSq_JA3L3ew8yUEvbSAtch9O0t-ZyNvMY4"
RANGE = "FinalData!A1:F9999"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_sheet():
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_PATH,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=RANGE
    ).execute()
    values = sheet.get("values", [])
    return values

def compute_stats(arr):
    arr = np.array(arr, dtype=float)
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std()),
        "median": float(np.median(arr)),
        "iqr": float(stats.iqr(arr)),
    }

def detect_iqr(arr):
    q1 = np.percentile(arr, 25)
    q3 = np.percentile(arr, 75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return [i for i, x in enumerate(arr) if x < lower or x > upper]

def detect_zscore(arr, threshold=1.5):
    z = np.abs(stats.zscore(arr, nan_policy='omit'))
    return [i for i, v in enumerate(z) if v > threshold]

def detect_moving_average(arr, percent=30):
    arr = np.array(arr)
    window = max(3, len(arr) // 20)
    rolling = np.convolve(arr, np.ones(window)/window, mode='same')
    return [i for i in range(len(arr)) if abs(arr[i] - rolling[i]) / max(1, rolling[i]) * 100 > percent]

def detect_grubbs(arr, alpha=0.1):
    N = len(arr)
    mean = np.mean(arr)
    std = np.std(arr)
    abs_dev = np.abs(arr - mean)
    idx = np.argmax(abs_dev)
    G = abs_dev[idx] / std

    t_crit = stats.t.ppf(1 - alpha / (2 * N), N - 2)
    G_crit = ((N - 1) / np.sqrt(N)) * np.sqrt(t_crit**2 / (N - 2 + t_crit**2))

    return [idx] if G > G_crit else []

def poly_trendline(arr, degree):
    x = np.arange(len(arr))
    coeffs = np.polyfit(x, arr, degree)
    poly = np.poly1d(coeffs)
    return poly(x).tolist()

@app.get("/data")
def get_data():
    rows = load_sheet()

    headers = rows[0]
    data_rows = rows[1:]

    return {"headers": headers, "rows": data_rows}

@app.get("/analyze")
def analyze(column: int, trend_degree: int = 1):
    rows = load_sheet()
    data = [float(r[column]) for r in rows[1:] if r[column] != ""]
    arr = np.array(data)

    stats_data = compute_stats(arr)

    anomalies = {
        "iqr": detect_iqr(arr),
        "zscore": detect_zscore(arr),
        "moving_avg": detect_moving_average(arr),
        "grubbs": detect_grubbs(arr)
    }

    trend = poly_trendline(arr, trend_degree)

    return {
        "stats": stats_data,
        "anomalies": anomalies,
        "trend": trend,
        "values": data
    }

app.mount("/", StaticFiles(directory=os.path.join(BASE_DIR, "../frontend"), html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=False)
