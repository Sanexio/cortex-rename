# Engine-Integration — wie ein Tenant eine Renaming-Engine anbindet

> Dieses Repo enthält **nur das Regelwerk**, nicht die Engine selbst.
> Tenants haben drei Optionen.

## Option 1: Sanexio-Engine lizenzieren (empfohlen, wenn Sanexio-Tenant)

Wer Sanexio-Tenant ist (eine Praxis im Sanexio-Distributionsnetzwerk),
bekommt die Sanexio-Engine als Teil des Tenant-Pakets. Die Engine läuft
auf einem Sanexio-Nexus-Knoten lokal in der Praxis und konsumiert dieses
Regelwerk + die tenant-eigene `VENDOR_PATTERNS_TENANT.md`.

Aufruf-Schema (geplant, Phase 3 der Cortex-Plattform-Roadmap):

```bash
# Engine über Cortex-CLI ansprechen
cortex rename --in ./IN --out ./OUT --rules-from ./rules
```

Status 2026-06-05: Die Cortex-CLI ist ausgeliefert; `cortex rename` ist
noch nicht enthalten. Bis dahin betreibt Sanexio die Engine als Teil des
Tenant-Pakets.

## Option 2: Eigene Engine bauen nach diesem Regelwerk

Wer keinen Sanexio-Vertrag hat, kann eine eigene Engine implementieren.
Das Regelwerk in `rules/` ist die normative Spezifikation. Empfohlener
Stack:

| Schicht | Library/Tool | Zweck |
|---|---|---|
| PDF-Textextraktion (nativ) | `pdfplumber` (Python) oder `PyMuPDF` | Text-Layer auslesen |
| OCR-Fallback | `tesseract` + `pytesseract` | Gescannte PDFs |
| Bildverarbeitung für OCR | `Pillow` | Pre-Processing |
| pdftotext-Fallback | `poppler` | Native CLI-Fallback |
| Sprache | Python ≥3.11 | Vorgabe der Regeln R-007 (Batch-Performance) |

Architektur-Skelett (Pseudo-Code):

```python
def rename_batch(in_dir, out_dir):
    rules = load_rules('rules/CORE_RULES.md')
    tenant_vendors = load_tenant('rules/VENDOR_PATTERNS_TENANT.md')
    ocr_corrections = load_tenant('rules/OCR_CORRECTIONS_TENANT.md')

    for src_file in glob(in_dir + '/*.pdf'):
        text = extract_text(src_file)  # native → OCR-fallback (R-001)
        text = apply_ocr_corrections(text, ocr_corrections)  # R-006

        vendor = match_vendor(text, tenant_vendors)  # R-009
        category = classify_category(vendor, text)  # PRX/PRV/SNX
        date = extract_date_hierarchical(text, src_file)  # R-003
        doctype = extract_doctype(text, vendor)

        new_name = format_filename(date, category, vendor, doctype)
        new_name = sanitize(new_name)  # R-005
        new_name = handle_duplicate(new_name, out_dir)  # R-008

        copy_with_lock_check(src_file, out_dir + '/' + new_name)  # R-011

    assert input_output_parity(in_dir, out_dir)  # R-013
    assert no_zero_byte_files(out_dir)  # R-012
```

## Option 3: Manuelles Verfahren ohne Engine

Wer nur 1-10 Dateien pro Woche umbenennt, kann das Schema auch manuell
anwenden (siehe `rules/SCHEMA.md`). In dem Fall ist das Repo
hauptsächlich eine Wissens-Quelle.

## Sanexio-Engine-Lizenzierung (optional)

Wenn Tenants die Sanexio-Engine als Teil ihrer Plattform-Anbindung
nutzen wollen, gilt der Standard-Sanexio-Tenant-Vertrag. Für
Open-Source-Implementierungen ist dieses Regelwerk **frei nutzbar
unter Apache 2.0**.

Sanexio garantiert nicht, dass die eigene Engine in jeder Praxis-
Umgebung lauffähig ist — das ist Teil des Tenant-Vertrags. Wer auf
sich selbst gestellt eine Engine bauen will, hat hier die normative
Spec — das genügt für eine eigene robuste Implementierung.

## Lizenz-Flow (Sanexio-Engine)

Die Sanexio-Engine prüft beim Start die lokale Lizenzdatei
`~/.cortex/license.json`. Diese Datei wird durch
`cortex init --license <token>` angelegt und enthält den Tenant-Token für
die Engine-Freischaltung.

Beim Start revalidiert die Engine den Token gegen:

```text
POST https://cortex.sanexio.de/api/v1/license/verify
```

Die Antwort enthält mindestens `valid` und `reason`. `valid=true`
schaltet den Lauf frei. Bei `valid=false` entscheidet `reason` über die
Fehlerklasse, z.B. `revoked`, `expired` oder `unknown_token`.

Erfolgreiche Validierungen dürfen für 24 Stunden lokal gecacht werden.
Wenn der Lizenzserver offline ist und der Cache noch gültig ist, darf die
Engine weiterlaufen. Ist der Cache abgelaufen, gilt fail-closed.

Exit-Codes:

| Code | Bedeutung |
|---:|---|
| 0 | Lizenz ok |
| 4 | Keine lokale Lizenz vorhanden |
| 5 | Lizenz abgelehnt (`revoked`, `expired`, `unknown_token`) |
| 6 | Offline und Lizenz-Cache abgelaufen |
