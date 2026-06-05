# cortex-rename — Regelwerk für intelligente Praxis-Dokumenten-Umbenennung

> **Cortex-Layer-Projekt** im Sanexio-Plattform-Modell (Aware-Health-/Aniva-
> Style): generisches Regelwerk für die kanonische Umbenennung von
> Praxis-Dokumenten (PDFs aus Krankenkassen, Laboren, Behörden, …)
> nach einem einheitlichen Schema.
>
> **Status 2026-06-05:** Regelwerk vollständig (Phase B abgeschlossen),
> Repo für den OSS-Launch vorbereitet.

## Was ist hier drin

- **`rules/`** — kuratiertes Regelwerk + Namensschema + Beispiele.
- **`docs/ENGINE_INTEGRATION.md`** — wie Tenants eine Engine anbinden.

## Was hier explizit NICHT drin ist

- **Die Engine selbst** (Python-Module für PDF-Textextraktion, OCR-Fallback,
  Vendor-Pattern-Matching) — diese bleibt **proprietäre Sanexio-Hoheit**.
  Andere Tenants haben zwei Optionen:
  1. **Eigene Engine bauen** nach diesem Regelwerk (Open-Source-Distribution).
  2. **Sanexio-Engine lizenzieren** als Teil eines Sanexio-Tenant-Pakets.
- **Tenant-spezifische Vendor-Listen** (z.B. die konkreten Krankenkassen,
  Labore und Behörden einer einzelnen Praxis) — diese leben im
  jeweiligen privaten Tenant-Repo.
- **Konkrete OCR-Korrektur-Mappings** für praxis-spezifische
  Scan-Artefakte — ebenfalls Tenant-Hoheit.

Das ist die Cortex-Plattform-Framework/Tenant-Split-Architektur
(Doku: https://sanexio.github.io/cortex/docs/).

## Namensschema (Auszug aus `rules/SCHEMA.md`)

```
YYMMDD_<Kategorie>_<Absender>_<Dokumenttyp>[_<Detail>].pdf
```

Kategorie:
- **PRX** — Praxisbezogen (Krankenkassen-Schreiben, KV-Mitteilungen, Lieferanten-Rechnungen, …)
- **PRV** — Privat (private Versicherungen, Steuerbescheide, Privat-Korrespondenz)
- **SNX** — Sanexio (Gesellschafterbeschlüsse, Sanexio-Verträge)

Beispiele:
```
260410_PRX_KV_Hessen_Schreiben.pdf
260305_PRX_Laborgemeinschaft_Laborbefund.pdf
260101_PRX_BZA_Amtsanfrage.pdf
260201_PRV_Allianz_Lebensversicherung.pdf
```

## Quickstart für andere Praxen

```bash
# 1. Repo klonen
git clone https://github.com/Sanexio/cortex-rename.git

# 2. Tenant-eigene Vendor-Liste anlegen (gitignored, sicher gegen
#    versehentliches Commit ins OSS-Repo)
cp rules/VENDOR_PATTERNS_EXAMPLE.md rules/VENDOR_PATTERNS_TENANT.md
nano rules/VENDOR_PATTERNS_TENANT.md
# Eure konkreten Krankenkassen, Labore, Behörden eintragen.

# 3. Eigene Engine anbinden — siehe docs/ENGINE_INTEGRATION.md
#    (Python/Tesseract/pdfplumber-Stack als Referenz; eigene Sprache möglich)

# 4. Pipeline: IN/ → Engine → OUT/ mit Schema-konformen Namen
```

## Beitrags-Modell

Pull-Requests willkommen. Bevor du eine PR aufmachst:
- README + `docs/ENGINE_INTEGRATION.md` lesen
- Schema-Erweiterungen (neue Kategorien, neue Dokumenttypen) bitte
  zuerst als Issue diskutieren
- Tenant-spezifische Vendor-Listen sind **nicht** Teil dieses Repos
  (siehe oben „Was hier explizit NICHT drin ist")

Maintenance: Dr. Stracke (Sanexio GmbH) — 2-Personen-Approval bei PRs
mit Schema-Impact (Cortex-Plattform §10.8).

## Querverweise

- Sanexio-Cortex-Plattform: https://sanexio.github.io/cortex/docs/
- Sister-Repos im Cortex Layer (in Vorbereitung): `cortex-desk`, `cortex-qm`,
  sowie das Cortex-Web-Praxisseiten-Theme (Tenant-spezifischer Theme-Name
  bleibt im jeweiligen Tenant-Repo).

## Lizenz

Apache License 2.0 — siehe `LICENSE`.
