import os
import time
import random
import requests

# Target API URL Configuration
# If running inside a container, Docker automatically maps 'http://api-core:8000'
# If running locally on your computer, it gracefully falls back to 'http://127.0.0.1:8000'
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/v1/telemetry")

# Pre-defined array IDs representing physical edge hardware field setups
NODES = ["ARRAY-HSR-01", "ARRAY-HSR-02", "ARRAY-WHITEFIELD-01", "ARRAY-KORAMANGALA-01"]

print("🚀 SolarMatrix Edge Node Simulator Initialized...")
print(f"Targeting Gateway API at: {API_URL}")
print("Press CTRL+C to close the telemetry stream.\n")

while True:
    for node in NODES:
        # Generate real-world solar light levels (Irradiance in W/m²)
        base_irradiance = random.choice([250.0, 550.0, 850.0, 1000.0])
        irradiance = round(base_irradiance + random.uniform(-50.0, 50.0), 2)
        
        # 5% probability mathematical threshold to trigger a random hardware anomaly
        is_anomaly = random.random() < 0.05
        
        if is_anomaly:
            # Drop the voltage and current to simulate dirty solar panels or a drop in grid efficiency
            voltage = round(random.uniform(1.0, 5.0), 2)
            current = round(random.uniform(0.1, 0.8), 2)
            print(f"⚠️  [SIMULATOR ENGINE] Injecting intentional operational fault state into {node}...")
        else:
            # Generate optimal daytime solar array electrical readings
            voltage = round(random.uniform(32.0, 42.0), 2)
            current = round(random.uniform(6.0, 9.5), 2)

        # Structure the network payload contract to match the backend Pydantic model expectations
        payload = {
            "node_id": node,
            "voltage": voltage,
            "current": current,
            "irradiance": irradiance
        }

        try:
            # Execute standard HTTP POST network broadcast request
            response = requests.post(API_URL, json=payload, timeout=5)
            
            # Validation: 202 Accepted confirms our async server has safely locked the data into RAM
            if response.status_code in [201, 202]:
                print(f"✅ Queued -> {node} | Network Status: {response.status_code} Accepted")
            else:
                print(f"❌ Server Error Unexpected Response: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Fault! Ensure your main.py FastAPI backend server is up and listening.")
        except requests.exceptions.Timeout:
            print("❌ Connection Timeout! The task worker pool is congested.")

    # Separation break line between distinct data cycle sweeps
    print("-" * 60)
    
    # Broadcast telemetry scans into the backend task pool every 3 seconds
    time.sleep(3)