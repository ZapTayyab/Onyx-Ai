"""Fetch hero background video from Pinterest pin."""
import re
import sys
import urllib.request
from pathlib import Path

PIN_URL = "https://www.pinterest.com/pin/879468633457143339/"
OUT = Path(__file__).resolve().parent.parent / "assets" / "hero-bg.mp4"


def find_video_url(html: str) -> str | None:
    patterns = [
        r"https://v\d\.pinimg\.com/videos/[^\s\"\\]+\.mp4",
        r'"url"\s*:\s*"(https://[^"]+\.mp4[^"]*)"',
    ]
    for pat in patterns:
        match = re.search(pat, html)
        if match:
            return match.group(1 if match.lastindex else 0)
    return None


def main() -> int:
    req = urllib.request.Request(PIN_URL, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", errors="ignore")
    video_url = find_video_url(html)
    if not video_url:
        print("Could not find video URL in pin page.", file=sys.stderr)
        return 1
    print(f"Video URL: {video_url}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(video_url, OUT)
    print(f"Saved to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
