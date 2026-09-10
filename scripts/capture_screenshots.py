import subprocess
import time
import os

CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT_DIR = "docs/screenshots"
os.makedirs(OUT_DIR, exist_ok=True)

screens = [
    ("overview.png", "http://localhost:5173/?tab=overview"),
    ("evidence_graph.png", "http://localhost:5173/?tab=graph"),
    ("geolocation_map.png", "http://localhost:5173/?tab=geomap"),
    ("header_forensics.png", "http://localhost:5173/?tab=forensics"),
    ("observed_iocs.png", "http://localhost:5173/?tab=iocs"),
    ("campaign_dna.png", "http://localhost:5173/?tab=campaign"),
    ("counterfactual_simulator.png", "http://localhost:5173/?tab=counterfactual"),
    ("response_playbook.png", "http://localhost:5173/?tab=playbook"),
    ("forensic_dossier.png", "http://localhost:5173/?report=true")
]

for filename, url in screens:
    out_path = os.path.join(OUT_DIR, filename)
    print(f"Capturing {filename} from {url}...")
    cmd = [
        CHROME_BIN,
        "--headless",
        "--disable-gpu",
        "--window-size=1440,920",
        f"--screenshot={out_path}",
        "--virtual-time-budget=4000",
        url
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

print("All screenshots successfully captured:")
for f in os.listdir(OUT_DIR):
    if f.endswith(".png"):
        print(" -", f, f"({os.path.getsize(os.path.join(OUT_DIR, f))} bytes)")
