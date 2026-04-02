# One-off: generate locale JSON from zh-tw.json (run from repo venv).
import json
import time
from pathlib import Path

from deep_translator import GoogleTranslator

ROOT = Path(__file__).resolve().parent
SRC_PATH = ROOT / "zh-tw.json"

# filename stem -> Google Translate target code (source: zh-TW)
TARGETS = {
    "hi": "hi",
    "en": "en",
    "id": "id",
    "ms": "ms",
    "th": "th",
    "zh-hk": "zh-TW",  # handled by hk_from_tw(), not Google
    "ja": "ja",
    "ko": "ko",
    "pt-br": "pt",
    "es": "es",
}


def translate_text(text: str, target: str) -> str:
    if not text or not text.strip():
        return text
    t = GoogleTranslator(source="zh-TW", target=target)
    # Google free API limit ~5k per request
    if len(text) <= 4500:
        return t.translate(text)
    parts = []
    chunk = 4000
    for i in range(0, len(text), chunk):
        piece = text[i : i + chunk]
        parts.append(t.translate(piece))
        time.sleep(0.15)
    return "".join(parts)


def hk_from_tw(s: str) -> str:
    """Light Hong Kong Traditional Chinese wording (not full MT)."""
    rep = (
        ("軟體", "軟件"),
        ("程式", "程式"),
        ("帳號", "帳戶"),
        ("預設", "預設"),
        ("網路", "網絡"),
        ("記憶體", "記憶體"),
        ("螢幕", "螢幕"),
        ("影片", "影片"),
        ("資訊", "資訊"),
        ("點數", "點數"),
        ("登入", "登入"),
    )
    out = s
    for a, b in rep:
        out = out.replace(a, b)
    return out


def main() -> None:
    with SRC_PATH.open(encoding="utf-8") as f:
        src: dict[str, str] = json.load(f)

    for stem, gcode in TARGETS.items():
        out_path = ROOT / f"{stem}.json"
        if stem == "zh-hk":
            data = {k: hk_from_tw(v) for k, v in src.items()}
        else:
            data = {}
            for i, (k, v) in enumerate(src.items()):
                try:
                    data[k] = translate_text(v, gcode)
                except Exception as e:
                    print(stem, k, e)
                    data[k] = v
                time.sleep(0.08)
                if (i + 1) % 10 == 0:
                    print(stem, i + 1, "/", len(src))
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("wrote", out_path)


if __name__ == "__main__":
    main()
