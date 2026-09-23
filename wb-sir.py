import requests
import base64
from pathlib import Path

AC = 165
START_PART = 266
END_PART = 295

base_url = "https://ceowestbengal.wb.gov.in/RollPDF/GetDraft"

Path("rolls").mkdir(exist_ok=True)

for part in range(START_PART, END_PART + 1):
    filename = f"AC{AC}PART{part}.pdf"
    key = base64.b64encode(filename.encode()).decode()

    params = {
        "acId": AC,
        "key": key
    }

    print(f"Downloading part {part}...")

    r = requests.get(base_url, params=params, timeout=60)

    if r.status_code == 200 and r.content[:4] == b"%PDF":
        Path(f"rolls/{filename}").write_bytes(r.content)
        print(f"  ✓ {filename}")
    else:
        print(f"  ✗ Failed ({r.status_code}, {len(r.content)} bytes)")