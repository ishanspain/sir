import base64
import ssl
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

AC = 165
START_PART = 266
END_PART = 295

BASE_URL = "https://ceowestbengal.wb.gov.in/RollPDF/GetDraft"
OUTPUT_DIR = Path("rolls")


class LegacyRenegotiationAdapter(HTTPAdapter):
    """Allow this site's obsolete TLS renegotiation without disabling verification."""

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        context = ssl.create_default_context()
        context.options |= ssl.OP_LEGACY_SERVER_CONNECT
        pool_kwargs["ssl_context"] = context
        super().init_poolmanager(connections, maxsize, block=block, **pool_kwargs)


def build_session() -> requests.Session:
    retries = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
    )
    session = requests.Session()
    session.mount(BASE_URL, LegacyRenegotiationAdapter(max_retries=retries))
    return session


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    with build_session() as session:
        for part in range(START_PART, END_PART + 1):
            filename = f"AC{AC}PART{part}.pdf"
            key = base64.b64encode(filename.encode()).decode()
            params = {"acId": AC, "key": key}

            print(f"Downloading part {part}...")

            try:
                response = session.get(BASE_URL, params=params, timeout=60)
            except requests.RequestException as error:
                print(f"  X Failed: {error}")
                continue

            if response.status_code == 200 and response.content.startswith(b"%PDF"):
                (OUTPUT_DIR / filename).write_bytes(response.content)
                print(f"  OK {filename}")
            else:
                print(
                    f"  X Failed ({response.status_code}, "
                    f"{len(response.content)} bytes)"
                )


if __name__ == "__main__":
    main()
