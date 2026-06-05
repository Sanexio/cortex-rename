# Workflow — von der unsortierten Eingabe zur kanonischen Ausgabe

## Vor dem Batch

1. **IN-Ordner inventarisieren.** Anzahl der zu verarbeitenden Dateien
   ermitteln, Überblick verschaffen.
2. **OUT-Ordner prüfen.** Wenn nicht leer: bewusst entscheiden, ob alte
   Ergebnisse archiviert werden oder mit neuem Batch kombiniert werden.
3. **Engine + Abhängigkeiten verfügbar?** Python ≥3.11, OCR-Backend
   (Tesseract oder vergleichbar), PDF-Library (pdfplumber/PyMuPDF). Bei
   Sanexio-Engine: `cortex-rename --check-engine`.
4. **Vendor-Patterns + OCR-Korrekturen aktuell?** Tenant-Files
   (`VENDOR_PATTERNS_TENANT.md`, `OCR_CORRECTIONS_TENANT.md`) reviewen,
   ggf. um neue Patterns aus dem letzten Batch erweitern.

## Während des Batches

1. **Textextraktion** für alle PDFs (native Text-Layer zuerst,
   OCR-Fallback bei leerem Ergebnis — R-001/R-002).
2. **Vendor-Erkennung** via `build_rules()` durchlaufen, alle
   Tenant-Vendor-Patterns prüfen.
3. **Kategorie-Klassifikation** PRX/PRV/SNX über Schlüsselwort-Sets
   und Adress-Hinweise.
4. **Datumsextraktion** mit hierarchischer 11-Pattern-Prüfung (R-003).
5. **Cloud-Drive-Lock-Check** vor dem Kopieren der Quell-Dateien (R-011).
6. **OCR-Korrekturen** anwenden (Tenant-Mapping aus
   `OCR_CORRECTIONS_TENANT.md`).
7. **Duplikat-Handling** (R-008 + Duplikat-Suffix-Konvention).
8. **`sanitize_filename`** auf jedes Ergebnis (R-005).
9. **Schreiben nach OUT** (batch-weise bei >500 Dateien — R-007).

## Nach dem Batch

1. **IN/OUT-Parität** prüfen (R-013) — Anzahl muss identisch sein.
2. **0-Byte-Check** auf alle OUT-Dateien (R-012) — keine leeren Dateien.
3. **Stichproben-Kontrolle** — 20-30 Dateien visuell prüfen
   (Vendor korrekt, Datum plausibel, Kategorie passt).
4. **Systematische Anti-Pattern-Checks**:
   - Keine `000000`-Datumsteile (Datum nicht erkannt → Tenant-Fehlerprotokoll)
   - Keine Vendor-Dopplungen (`KV_KV_…`)
   - Keine Versicherungs-Fehlklassifikationen (PRV vs PRX)
   - Keine doppelten Unterstriche an nicht-Duplikat-Stellen
5. **Wissens-Rückfluss** (R-010) — IMMER:
   - Neue Vendors → Engine `build_rules()` + ggf. `VENDOR_PATTERNS_TENANT.md`
   - Neue Datums-Muster → Engine `extract_date_hierarchical()`
   - Neue OCR-Fehler → `OCR_CORRECTIONS_TENANT.md`
   - Neue Fehler-Klassen → `FEHLERPROTOKOLL_TENANT.md`
6. **Archivierung** — alte IN/-Dateien zu einem datierten Ordner
   verschieben (`IN/_archive/YYYY-MM-DD-batch-N/`), neue Quell-Dateien
   können kommen.

## Empfohlene Frequenz

- **Tägliche Mini-Batches** (5-20 Dateien): per Skill-Aufruf, ~2 Min
- **Wöchentlicher Hauptbatch** (50-200 Dateien): geplanter Slot, ~30 Min
- **Aufräum-Batch** (>500 Dateien aus Backlog): in Wochenend-Block,
  Batches à 300 mit Verifikation zwischen jedem Batch.

## Notfall: IN-Ordner mit Fehl-Erkennung

Wenn nach dem Batch mehrere Dateien systematisch falsch benannt sind
(z.B. neue Vendor-Klasse nicht erkannt):

1. **NICHT die Engine in Panic-Modus debuggen.** Erst die letzten 10
   Fehl-Erkennungen sammeln, Pattern identifizieren.
2. Pattern in `VENDOR_PATTERNS_TENANT.md` (Tenant) oder zentral in
   Engine `build_rules()` (OSS) eintragen.
3. Betroffene Dateien aus OUT zurück nach IN moven (oder ein
   `RE-IN/`-Ordner anlegen), Batch erneut auf diese Untermenge fahren.
4. Verifikation: jetzt korrekt erkannt? Wenn ja, Pattern committen.
   Wenn nein, in Tenant-Fehlerprotokoll dokumentieren und manuell
   nachpflegen.
