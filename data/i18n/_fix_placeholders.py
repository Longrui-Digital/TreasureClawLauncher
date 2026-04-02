"""Align {...} placeholders in locale JSON with zh-tw.json (machine translation often breaks them)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ZH_PATH = ROOT / "zh-tw.json"

PH = re.compile(r"\{[^}]+\}")


def merge_placeholders(template: str, translated: str) -> str:
    zh_parts = PH.split(template)
    zh_phs = PH.findall(template)
    tr_parts = PH.split(translated)
    if len(zh_parts) != len(tr_parts) or len(zh_phs) != len(tr_parts) - 1:
        # Fallback: replace foreign {...} in order
        tr_phs = PH.findall(translated)
        if len(zh_phs) == len(tr_phs):
            out = translated
            for tr, zh in zip(tr_phs, zh_phs):
                out = out.replace(tr, zh, 1)
            return out
        return translated
    out = tr_parts[0]
    for i, ph in enumerate(zh_phs):
        out += ph + tr_parts[i + 1]
    return out


def main() -> None:
    with ZH_PATH.open(encoding="utf-8") as f:
        zh: dict[str, str] = json.load(f)
    for path in sorted(ROOT.glob("*.json")):
        if path.name.startswith("_") or path.name == "zh-tw.json":
            continue
        with path.open(encoding="utf-8") as f:
            data: dict[str, str] = json.load(f)
        changed = 0
        for k, tmpl in zh.items():
            if k not in data:
                continue
            before = data[k]
            after = merge_placeholders(str(tmpl), str(data[k]))
            if after != before:
                data[k] = after
                changed += 1
        if changed:
            with path.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(path.name, "fixed", changed, "keys")


if __name__ == "__main__":
    main()
