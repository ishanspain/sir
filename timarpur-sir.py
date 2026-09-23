import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

AC = 61
START_PART = 1
END_PART = 100

# The `id` on validateUser_2002BK.aspx is an encrypted value for one specific
# PDF, so passing a filename as that parameter does not work. ECI also hosts
# the same 2002 rolls at this official, predictable URL.
URL_TEMPLATE = (
    "https://www.eci.gov.in/sir/f4/U05/data/OLDSIRROLL/"
    "U05/{ac}/U05_{ac}_{part}.pdf"
)
OUTPUT_DIR = Path("timarpur_2002")
RETRIES = 3
TIMEOUT = 60


def download_pdf(url: str, output: Path) -> None:
    """Download one PDF and replace the destination only after validation."""
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})

    with urlopen(request, timeout=TIMEOUT) as response:
        content = response.read()
        content_type = response.headers.get_content_type()

    if not content.startswith(b"%PDF"):
        raise ValueError(
            f"server returned {len(content)} bytes of {content_type}, not a PDF"
        )

    temporary = output.with_suffix(output.suffix + ".part")
    temporary.write_bytes(content)
    temporary.replace(output)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    downloaded = 0
    skipped = 0
    failed = 0

    for part in range(START_PART, END_PART + 1):
        filename = f"A{AC:03d}{part:04d}.PDF"
        output = OUTPUT_DIR / filename
        url = URL_TEMPLATE.format(ac=AC, part=part)

        if output.exists() and output.read_bytes()[:4] == b"%PDF":
            print(f"SKIP {filename} (already downloaded)")
            skipped += 1
            continue

        print(f"Downloading part {part}: {url}")

        for attempt in range(1, RETRIES + 1):
            try:
                download_pdf(url, output)
                print(f"  OK {filename}")
                downloaded += 1
                break
            except (HTTPError, URLError, TimeoutError, ValueError, OSError) as error:
                if attempt == RETRIES:
                    print(f"  FAILED {filename}: {error}")
                    failed += 1
                else:
                    print(f"  Retry {attempt}/{RETRIES - 1}: {error}")
                    time.sleep(attempt)

    print(
        f"Finished: {downloaded} downloaded, {skipped} skipped, {failed} failed"
    )


if __name__ == "__main__":
    main()
