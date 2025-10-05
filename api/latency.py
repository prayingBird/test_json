# api/latency.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import json

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

with open("data.json", "r") as f:
    telemetry = json.load(f)  # expect list of dicts

@app.post("/api/latency")
async def check_latency(request: Request):
    req_body = await request.json()
    regions = req_body.get("regions", [])
    threshold = req_body.get("threshold_ms", 180)

    results = {}
    for region in regions:
        # filter data for region
        region_data = [r for r in telemetry if r["region"] == region]
        latencies = [r["latency_ms"] for r in region_data]
        uptimes = [r["uptime"] for r in region_data]

        if not latencies:
            results[region] = {}
            continue

        avg_latency = float(np.mean(latencies))
        p95_latency = float(np.percentile(latencies, 95))
        avg_uptime = float(np.mean(uptimes))
        breaches = int(sum(l > threshold for l in latencies))

        results[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches,
        }
    return results
