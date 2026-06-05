# Kern-Regeln R-001 bis R-013

> Generische Regeln für jede Engine-Implementierung. Tenant-spezifische
> Erweiterungen gehören in `VENDOR_PATTERNS_TENANT.md` (gitignored) bzw.
> ins jeweilige Tenant-Repo.

## R-001: OCR-Fallback immer aktivieren

PDF-Textextraktion muss IMMER einen OCR-Fallback haben (native
PDF-Textebene → bei leerem Ergebnis Tesseract oder vergleichbare OCR).
Begründung: gescannte PDFs ohne Text-Layer sind häufig im Praxis-Alltag.

## R-002: Multi-PSM-OCR für Verträge

Bei OCR mindestens **zwei Page-Segmentation-Modes** (PSM) versuchen
(z.B. Tesseract PSM 6 für strukturierte Dokumente und PSM 3 für
generischen Text), das längere Ergebnis verwenden. Strukturierte
Dokumente (Verträge, Tabellen) profitieren von PSM 6.

## R-003: Hierarchische Datumsextraktion

11 Datums-Patterns in Priorität prüfen (siehe `SCHEMA.md` Datumsextraktion).
Niemals eine generische Jahreszahl als vollständiges Datum verwenden —
Tag/Monat auf `0000` setzen und Eintrag in Tenant-Fehlerprotokoll
(`FEHLERPROTOKOLL_TENANT.md`).

## R-004: Versicherungen differenzieren

Versicherungs-Absender können PRX oder PRV sein:
- **Firmen-/Praxis-Versicherung** → PRX (z.B. Berufshaftpflicht)
- **Persönliche Versicherung** → PRV (Leben/Rente/Risiko/Haftpflicht-Privat)

Die Differenzierung muss explizit in der `sanitize_filename`-Funktion
implementiert sein, nicht über Vendor-Name allein (manche Versicherer
betreiben beide Sparten).

## R-005: Doppelte Präfixe verhindern

Die `sanitize_filename`-Funktion wird automatisch nach jeder Benennung
aufgerufen und prüft auf:
- `KV_KV`, `Laborgemeinschaft_Laborgemeinschaft` (Absender-Dopplung)
- Doppel-Unterstrich `__` nur an reservierter Stelle (Duplikat-Suffix)
- Bindestriche/Leerzeichen-Reste aus unsauberen Quell-Namen

## R-006: OCR-Korrupt-Mapping pflegen

OCR-Engines erzeugen reproduzierbare Fehler bei bestimmten Schriftarten/
Scan-Qualitäten. Tenants pflegen ein Mapping in
`OCR_CORRECTIONS_TENANT.md`:

```
Beispiel (generische Pattern-Struktur):
  "KV-Hesseh" → "KV_Hessen"        (h statt n häufiger Tesseract-Fehler)
  "<Vendor>-l" → "<Vendor>"        (-l als OCR-Artefakt am Seitenende)
```

Konkrete Vendor-Mapping-Tabellen mit echten Absender-Namen gehören in
die jeweilige Tenant-Datei (`OCR_CORRECTIONS_TENANT.md`), nicht in den
generischen Cortex-Rename-Layer.

Bei neuen unbekannten Mustern: Mapping erweitern UND in der Engine die
Robustheit erhöhen (Regex statt Exact-Match).

## R-007: Bulk-Operationen batch-weise

Bei >500 Dateien immer in Batches à ~300 aufteilen, Timeout pro Batch
mindestens 300 Sekunden. Begründung: OCR-Schwankungen + Memory-Verbrauch
bei großen Dateien können sonst die Pipeline kippen.

## R-008: Kollisionsprüfung bei Umbenennungen

Vor jeder `mv`/`rename`-Operation prüfen, ob Zieldatei existiert. Bei
Kollision: NICHT überschreiben — Duplikat-Suffix `__1`, `__2` setzen.

## R-009: Vendor-Regeln zentral pflegen

Eine `build_rules()`-Funktion (oder vergleichbares Konstrukt) sammelt
ALLE Vendor-Erkennungs-Regeln an einer Stelle. Jede Regel besteht aus
einer Match-Funktion (`is_this_vendor(text) → bool`) und einer
Rename-Funktion (`how_to_name(text) → (absender, typ)`).

Tenant-spezifische Vendor-Regeln werden NICHT in dieses OSS-Repo
committed, sondern lokal in `VENDOR_PATTERNS_TENANT.md` (gitignored)
oder im jeweiligen Tenant-Repo gepflegt.

## R-010: Nach jeder Session Skripte aktualisieren

Jede Rename-Session, bei der neue Vendor-Patterns, Datums-Muster oder
OCR-Fehler entdeckt werden, MUSS mit einem Update enden in:
- Vendor-Patterns → Engine + Tenant-Liste
- Datums-Muster → `extract_date_hierarchical()` Engine-Code
- OCR-Korrekturen → `OCR_CORRECTIONS_TENANT.md`
- Neue Fehler-Klassen → `FEHLERPROTOKOLL_TENANT.md`

Das ist NICHT optional. Ohne Wissens-Rückfluss veraltet die Engine.

## R-011: Cloud-Drive-Lock-Vermeidung

Bei Dateien aus Cloud-Drive-Mountpoints (Google Drive, iCloud, Dropbox,
…) kann das Betriebssystem File-Locks setzen, die `cp` oder
`shutil.copy2` zu **0-Byte-Zieldateien ohne Fehlermeldung** führen.

Workaround: Native-Tool-Kopie über OS-eigene API (z.B. macOS:
`osascript` mit `do shell script`-Bridge), nicht aus VM-Mountpoint.

## R-012: 0-Byte-Check nach jedem Batch

Nach jedem abgeschlossenen Rename-Batch alle Ziel-Dateien auf
Größe > 0 prüfen. 0-Byte-Dateien sind ein Symptom von R-011 oder
korrupten Quell-Dateien — niemals als „erfolgreich" markieren.

## R-013: IN/OUT-Parität

Anzahl der Dateien im Quell-Ordner muss exakt der Anzahl im
Ziel-Ordner entsprechen (ignoriert OS-Metadata-Files wie `.DS_Store`).
Bei Abweichung: in `FEHLERPROTOKOLL_TENANT.md` dokumentieren, manuell
nachpflegen.

```
ls -1 IN/  | grep -v ".DS_Store" | wc -l    # Quell-Anzahl
ls -1 OUT/ | grep -v ".DS_Store" | wc -l    # Ziel-Anzahl
```

Beide müssen identisch sein.
