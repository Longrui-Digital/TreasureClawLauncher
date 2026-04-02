"""Generate ja / ko / pt-br / es from zh-tw.json only."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from deep_translator import GoogleTranslator

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "zh-tw.json"

TARGETS = {"ja": "ja", "ko": "ko", "pt-br": "pt", "es": "es"}


def translate_text(text: str, target: str) -> str:
    if not text or not text.strip():
        return text
    t = GoogleTranslator(source="zh-TW", target=target)
    if len(text) <= 4500:
        return t.translate(text)
    parts = []
    for i in range(0, len(text), 4000):
        parts.append(t.translate(text[i : i + 4000]))
        time.sleep(0.12)
    return "".join(parts)


def main() -> None:
    with SRC.open(encoding="utf-8") as f:
        src: dict[str, str] = json.load(f)
    n = len(src)
    for stem, gcode in TARGETS.items():
        out_path = ROOT / f"{stem}.json"
        data: dict[str, str] = {}
        for i, (k, v) in enumerate(src.items()):
            try:
                data[k] = translate_text(v, gcode)
            except Exception as e:
                print(stem, k, e, file=sys.stderr)
                data[k] = v
            time.sleep(0.06)
            if (i + 1) % 15 == 0:
                print(f"{stem} {i + 1}/{n}", flush=True)
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("wrote", out_path, flush=True)


if __name__ == "__main__":
    main()
