#!/usr/bin/env python3
"""Mini-Demo fuer das Cortex-Rename-Regelwerk.

Diese Datei liest fiktive Quelldateinamen, leitet Demo-Metadaten ab und
schreibt eine Markdown-Tabelle. Sie ersetzt keine produktive Engine.
"""

from __future__ import annotations

import argparse
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path


UMLAUTS = str.maketrans({
    "ä": "ae",
    "ö": "oe",
    "ü": "ue",
    "Ä": "Ae",
    "Ö": "Oe",
    "Ü": "Ue",
    "ß": "ss",
})

OCR_FIXES = {
    "B3fund": "Befund",
    "Pseud0": "Pseudo",
    "Lab0r": "Labor",
}


@dataclass(frozen=True)
class VendorPattern:
    key: str
    match_terms: tuple[str, ...]
    prefix: str
    category: str
    doctype_hints: tuple[str, ...]


def read_fixture(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def split_backtick_values(line: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in re.findall(r"`([^`]+)`", line))


def load_vendor_patterns(path: Path) -> list[VendorPattern]:
    patterns: list[VendorPattern] = []
    current: dict[str, object] | None = None

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("### "):
            if current:
                patterns.append(to_vendor_pattern(current))
            current = {"key": line[4:].strip(), "doctype_hints": []}
            continue
        if not current:
            continue
        if line.startswith("- match:"):
            current["match_terms"] = split_backtick_values(line)
        elif line.startswith("- prefix:"):
            values = split_backtick_values(line)
            current["prefix"] = values[0] if values else ""
        elif line.startswith("- category:"):
            current["category"] = line.split(":", 1)[1].strip().split()[0]
        elif line.startswith("- doctype_hints:"):
            current["doctype_hints"] = list(split_backtick_values(line))
        elif line.startswith("  - ") and "→" in line:
            current.setdefault("doctype_hints", [])
            hint = line.split("→", 1)[0].strip(" -`*")
            current["doctype_hints"].append(hint)

    if current:
        patterns.append(to_vendor_pattern(current))

    return patterns


def to_vendor_pattern(raw: dict[str, object]) -> VendorPattern:
    category = str(raw.get("category", "PRX"))
    if category not in {"PRX", "PRV", "SNX"}:
        category = "PRX"
    return VendorPattern(
        key=str(raw.get("key", "UNKNOWN")),
        match_terms=tuple(raw.get("match_terms", ())),
        prefix=str(raw.get("prefix", "Unbekannt")),
        category=category,
        doctype_hints=tuple(raw.get("doctype_hints", ())),
    )


def apply_ocr_fixes(text: str) -> str:
    for bad, good in OCR_FIXES.items():
        text = text.replace(bad, good)
    return text


def sanitize_token(value: str) -> str:
    value = value.translate(UMLAUTS)
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^A-Za-z0-9_-]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_-")
    value = re.sub(r"-{2,}", "-", value)
    return value or "Unbekannt"


def extract_extension(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    return suffix if suffix else ".pdf"


def extract_date(text: str) -> str:
    patterns = [
        (r"(?P<y>20\d{2})[-_.](?P<m>\d{2})[-_.](?P<d>\d{2})", ("y", "m", "d")),
        (r"(?P<y>20\d{2})(?P<m>\d{2})(?P<d>\d{2})", ("y", "m", "d")),
        (r"(?P<d>\d{2})\.(?P<m>\d{2})\.(?P<y>20\d{2})", ("y", "m", "d")),
    ]
    for pattern, _ in patterns:
        match = re.search(pattern, text)
        if match:
            return f"{match.group('y')[2:]}{match.group('m')}{match.group('d')}"

    year = re.search(r"\b(20\d{2})\b", text)
    if year:
        return f"{year.group(1)[2:]}0000"
    return "000000"


def match_vendor(text: str, vendors: list[VendorPattern]) -> VendorPattern:
    lowered = text.lower()
    for vendor in vendors:
        if any(term.lower() in lowered for term in vendor.match_terms):
            return vendor
    return VendorPattern("UNKNOWN", (), "Unbekannt", "PRX", ("Schreiben",))


def classify_category(vendor: VendorPattern, text: str) -> str:
    lowered = text.lower()
    if vendor.key.startswith("PSEUDO-Vers"):
        if any(word in lowered for word in ("lebensversicherung", "rentenversicherung", "risikoversicherung")):
            return "PRV"
        return "PRX"
    return vendor.category


def infer_doctype(vendor: VendorPattern, text: str) -> str:
    lowered = text.lower()
    if "rechnung" in lowered:
        return "Rechnung"
    if "befund" in lowered:
        return "Laborbefund"
    if "mitgliederbescheinigung" in lowered:
        return "Mitgliederbescheinigung"
    if "quartalsabrechnung" in lowered:
        return "Quartalsabrechnung"
    if "amtsanfrage" in lowered:
        return "Amtsanfrage"
    if "bescheid" in lowered:
        return "Bescheid"
    if "rentenversicherung" in lowered:
        return "Rentenversicherung"
    if "berufshaftpflicht" in lowered:
        return "Berufshaftpflicht"
    for hint in vendor.doctype_hints:
        first = hint.split("/", 1)[0].strip()
        if first and first.lower() in lowered:
            return first
    return "Schreiben"


def infer_detail(text: str) -> str | None:
    if re.search(r"\bmahnung\b", text, re.IGNORECASE):
        number = re.search(r"\bmahnung\D*(\d+)\b", text, re.IGNORECASE)
        return f"Mahnung-{number.group(1)}" if number else "Mahnung"
    probe = re.search(r"\bProbe[-_ ]?(\d+)\b", text, re.IGNORECASE)
    if probe:
        return f"Probe-{probe.group(1)}"
    if "0000" in extract_date(text):
        return "Datum-zu-pruefen"
    return None


def build_target(filename: str, vendors: list[VendorPattern]) -> str:
    cleaned = apply_ocr_fixes(filename)
    vendor = match_vendor(cleaned, vendors)
    date = extract_date(cleaned)
    category = classify_category(vendor, cleaned)
    doctype = infer_doctype(vendor, cleaned)
    detail = infer_detail(cleaned)

    parts = [
        date,
        category,
        sanitize_token(vendor.prefix),
        sanitize_token(doctype),
    ]
    if detail:
        parts.append(sanitize_token(detail))
    return "_".join(parts) + extract_extension(filename)


def write_markdown(rows: list[tuple[str, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Rename-Demo Ergebnis",
        "",
        "| Vorher | Nachher |",
        "|---|---|",
    ]
    for source, target in rows:
        lines.append(f"| `{source}` | `{target}` |")
    lines.append("")
    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--rules-dir", required=True, type=Path)
    args = parser.parse_args()

    vendors = load_vendor_patterns(args.rules_dir / "VENDOR_PATTERNS_EXAMPLE.md")
    rows = [(source, build_target(source, vendors)) for source in read_fixture(args.input)]
    write_markdown(rows, args.output)
    print(f"Demo-Ergebnis geschrieben: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
