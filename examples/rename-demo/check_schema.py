#!/usr/bin/env python3
"""Validiert Demo-Zielnamen gegen das Schema aus rules/SCHEMA.md."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def build_schema_regex(schema_path: Path) -> re.Pattern[str]:
    schema = schema_path.read_text(encoding="utf-8")
    if "YYMMDD_<Kategorie>_<Absender>_<Dokumenttyp>[_<Detail>].pdf" not in schema:
        raise ValueError("Schema-Format in rules/SCHEMA.md nicht gefunden")
    if "PRX/PRV/SNX" not in schema:
        raise ValueError("Kategorie-Liste in rules/SCHEMA.md nicht gefunden")
    if "a-z, A-Z, 0-9, `_`, `-`, `.`" not in schema:
        raise ValueError("Zeichensatz-Regel in rules/SCHEMA.md nicht gefunden")

    token = r"[A-Za-z0-9][A-Za-z0-9-]*"
    sender_or_type = rf"{token}(?:_{token})*"
    duplicate = r"(?:__[1-9][0-9]*)?"
    return re.compile(
        rf"^[0-9]{{6}}_(?:PRX|PRV|SNX)_{sender_or_type}_{sender_or_type}{duplicate}\.pdf$"
    )


def names_from_results(path: Path) -> list[str]:
    names: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 2:
            continue
        target = cells[1]
        if target.startswith("`") and target.endswith("`"):
            names.append(target.strip("`"))
    return names


def validate_name(name: str, regex: re.Pattern[str]) -> tuple[bool, str]:
    if "__" in name:
        stem = name.rsplit(".", 1)[0]
        if not re.search(r"__[1-9][0-9]*$", stem):
            return False, "Doppel-Unterstrich ist nur als Duplikat-Suffix erlaubt"
    if regex.fullmatch(name):
        return True, "ok"
    return False, "Schema-Match fehlgeschlagen"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--results", type=Path)
    parser.add_argument("--name")
    args = parser.parse_args()

    regex = build_schema_regex(args.schema)
    names: list[str] = []
    if args.results:
        names.extend(names_from_results(args.results))
    if args.name:
        names.append(args.name)
    if not names:
        raise SystemExit("Keine Namen zur Validierung uebergeben")

    failed = False
    for name in names:
        ok, reason = validate_name(name, regex)
        status = "PASS" if ok else "FAIL"
        print(f"{status} {name} ({reason})")
        failed = failed or not ok
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
