# Vendor-Patterns — Beispiel-Set

> **Demo-Vendors**, nicht echte Praxis-Daten. Tenants legen eine eigene
> `VENDOR_PATTERNS_TENANT.md` an (gitignored) und tragen dort ihre
> konkreten Kassen, Labore und Behörden ein.

## Struktur eines Vendor-Patterns

```
### <VENDOR_KEY>
- match: <Suchbegriffe im Dokumenttext>
- prefix: <Absender-Kürzel im Dateinamen>
- category: PRX | PRV | SNX
- doctype_hints: <Pattern für Dokumenttyp-Erkennung>
- notes: <Tenant-Hinweise>
```

## Beispiele

### PSEUDO-LABOR
- match: `Pseudo-Labor GmbH`, `Befund Pseudo-Labor`
- prefix: `Pseudo-Labor`
- category: PRX
- doctype_hints: `Laborbefund`, `Befund`, `Probe`
- notes: Demo-Labor für Schema-Tests. Echte Labore werden im Tenant-File
  eingetragen.

### PSEUDO-KK
- match: `Pseudo-Krankenkasse`, `Pseudo-KK`
- prefix: `Pseudo-KK`
- category: PRX
- doctype_hints: `Mitgliederbescheinigung`, `Abrechnung`, `Schreiben`
- notes: Demo-Krankenkasse für Schema-Tests.

### PSEUDO-KV
- match: `Pseudo-Kassenärztliche Vereinigung`, `Pseudo-KV`
- prefix: `Pseudo-KV`
- category: PRX
- doctype_hints: `Schreiben`, `Mahnung`, `Quartalsabrechnung`
- notes: Demo-KV.

### PSEUDO-Amt
- match: `Pseudo-Amt`, `Behörde Pseudo`
- prefix: `Pseudo-Amt`
- category: PRX
- doctype_hints: `Amtsanfrage`, `Bescheid`, `Aufforderung`
- notes: Demo-Behörde.

### PSEUDO-Vers (Versicherer mit Sparten-Differenzierung)
- match: `Pseudo-Versicherung AG`
- prefix: `Pseudo-Vers`
- category: PRX oder PRV (sparten-abhängig — siehe R-004)
- doctype_hints:
  - Lebensversicherung / Rentenversicherung / Risikoversicherung → **PRV**
  - Berufshaftpflicht / Praxis-Inhaltsversicherung / Sach → **PRX**
- notes: Differenzierung kommt aus dem Dokumenttyp, nicht aus dem
  Vendor-Namen — eine Versicherung betreibt oft beide Sparten.

## Anti-Pattern: Was NICHT in dieses OSS-Repo gehört

❌ Konkrete Krankenkassen, deren genauer Name auf eine bestimmte Praxis
   schließen lässt (z.B. eine regional sehr seltene Sonder-Kasse).
❌ Konkrete Labor-Namen, die typischerweise eine Praxis nutzt.
❌ Konkrete Beratungs-/Steuer-/Anwalts-Kanzleien.
❌ Personennamen.
❌ Adressen.
❌ Telefon-Patterns, die auf eine bestimmte Region hinweisen.

All das gehört in die **`VENDOR_PATTERNS_TENANT.md`** (gitignored, lokal
beim Tenant) oder ins jeweilige Sanexio-Tenant-Repo.

## Vendor-Aufnahme-Verfahren

Wenn ein neuer Vendor in deinem Praxis-Alltag häufig vorkommt:

1. **Tenant-File zuerst**: in `VENDOR_PATTERNS_TENANT.md` eintragen.
2. **Engine-Code-Update**: wenn die Match-Logik komplex ist (Regex,
   mehrere Sprachen, OCR-anfällig), Engine-Code entsprechend erweitern.
3. **Schema-Erweiterung als PR** (nur wenn das Schema selbst betroffen
   ist — siehe README §Beitrags-Modell).

Pseudo-Vendors hier im Repo werden NICHT durch echte Vendors ersetzt —
sie bleiben als Schema-Demo erhalten.
