import os
import time
import datetime
import json
import pyautogui

# -------- PATHS & SETTINGS --------

SAVE_DIR = r"C:\Users\IIcee\Desktop\picture"
JSON_PATH = r"C:\Users\IIcee\car_counter\pictures.json"

INTERVAL_SECONDS = 60  # 60 seconds between rounds

# Each camera: description + region (left, top, width, height)
CAMERAS = [
    # 2nd Ave @ 49 St (unchanged)
    {
        "description": "2nd_Ave_49_st",
        "region": (729, 593, 980 - 729, 715 - 593)     # (729, 593, 251, 122)
    },
    # Queens Midtown Tunnel (updated)
    {
        "description": "Queens_Midtown_Tunnel",
        "region": (1105, 567, 1461 - 1105, 674 - 567)  # (1105, 567, 356, 107)
    },
    # Queens Plaza North (updated)
    {
        "description": "Queens_Plaza_North",
        "region": (1217, 854, 1379 - 1217, 1016 - 854) # (1217, 854, 162, 162)
    },
    # E 63 St (updated)
    {
        "description": "E_63_St",
        "region": (1712, 522, 1814 - 1712, 698 - 522)  # (1712, 522, 102, 176)
    },
    # S Conduit Ave 150 (updated)
    {
        "description": "S_Conduit_Ave_150",
        "region": (722, 885, 900 - 722, 1038 - 885)    # (722, 885, 178, 153)
    },
]

# -------- LOAD / INIT STATE --------

os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)


def load_state(path):
    # New default structure
    base = {
        "TOTALNUMBEROFPICTURES": 0,
        "DESCRIPTION_TOTALS": {},
        "pictures": []
    }

    if not os.path.exists(path):
        return base

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return base

    # If dict with "pictures", normalize totals
    if isinstance(data, dict) and "pictures" in data:
        pics = data.get("pictures", [])
        # recompute totals from list (ignore any old totals)
        desc_totals = {}
        for p in pics:
            d = p.get("description")
            if d:
                desc_totals[d] = desc_totals.get(d, 0) + 1

        data["pictures"] = pics
        data["TOTALNUMBEROFPICTURES"] = len(pics)
        data["DESCRIPTION_TOTALS"] = desc_totals
        return data

    # If old style list of pictures
    if isinstance(data, list):
        desc_totals = {}
        for p in data:
            d = p.get("description")
            if d:
                desc_totals[d] = desc_totals.get(d, 0) + 1
        return {
            "TOTALNUMBEROFPICTURES": len(data),
            "DESCRIPTION_TOTALS": desc_totals,
            "pictures": data
        }

    return base


state = load_state(JSON_PATH)

print(f"Saving screenshots to: {SAVE_DIR}")
print(f"Logging to JSON: {JSON_PATH}")
print(f"Interval: {INTERVAL_SECONDS} seconds")
print("Press Ctrl+C in this window to stop.\n")

# -------- MAIN LOOP --------

try:
    while True:
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H-%M-%S")

        for cam in CAMERAS:
            desc = cam["description"]
            region = cam["region"]

            # Global picture count (all descriptions)
            state["TOTALNUMBEROFPICTURES"] += 1
            global_index = state["TOTALNUMBEROFPICTURES"]

            # Per-description count (this is what goes in the filename)
            desc_count = state["DESCRIPTION_TOTALS"].get(desc, 0) + 1
            state["DESCRIPTION_TOTALS"][desc] = desc_count

            # Filename uses per-description count
            filename = f"{desc}_{desc_count}.png"
            filepath = os.path.join(SAVE_DIR, filename)

            # Capture and save
            img = pyautogui.screenshot(region=region)
            img.save(filepath)

            # Log one entry
            entry = {
                "index": global_index,          # global index across all cameras
                "filename": filename,
                "date": date_str,
                "time": time_str,
                "description": desc,
                "description_total": desc_count  # how many for this description so far
            }
            state["pictures"].append(entry)

            print(
                f"Saved {filepath} | "
                f"global={global_index} | {desc} #{desc_count}"
            )

        # Write JSON after each round over all cameras
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

        time.sleep(INTERVAL_SECONDS)

except KeyboardInterrupt:
    print("\nStopped by user.")
