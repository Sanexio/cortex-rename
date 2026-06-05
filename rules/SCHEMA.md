# Namensschema — kanonische Datei-Benennung

## Format

```
YYMMDD_<Kategorie>_<Absender>_<Dokumenttyp>[_<Detail>].pdf
```

| Feld | Format | Beispiel |
|---|---|---|
| `YYMMDD` | 6-stelliges Datum (Jahr, Monat, Tag) | `260410` (2026-04-10) |
| `Kategorie` | 3-Buchstaben-Kürzel (PRX/PRV/SNX) | `PRX` |
| `Absender` | Identifikator des absendenden Vendors | `KV_Hessen` |
| `Dokumenttyp` | Art des Dokuments | `Schreiben`, `Laborbefund`, `Rechnung`, … |
| `Detail` *(optional)* | Zusätzliche Spezifikation | `Quartal-Q1`, `Mahnung-2` |

Trenner: Unterstrich `_`. **Doppelter Unterstrich `__`** ist reserviert für
Duplikat-Suffix (siehe Duplikat-Konvention unten).

## Kategorien

- **PRX — Praxisbezogen**
  Schreiben von Krankenkassen, Kassenärztlichen Vereinigungen,
  Laboren, Lieferanten, Behörden mit Bezug zur Praxis-Tätigkeit,
  Rechnungen von Dienstleistern, Personalakten-Korrespondenz.
- **PRV — Privat**
  Persönliche Versicherungen (Leben, Rente, Risiko), Steuerbescheide,
  Privat-Korrespondenz des Inhabers, persönliche Bankunterlagen.
- **SNX — Sanexio (Konzern-Hülle)**
  Gesellschafterbeschlüsse, Sanexio-spezifische Verträge, Konzern-
  Buchhaltung. Nur relevant, wenn die Praxis in eine Sanexio-/Holding-
  Struktur eingebunden ist; andernfalls weglassen.

## Beispiele

```
260410_PRX_KV_Hessen_Schreiben.pdf
260410_PRX_KV_Hessen_Schreiben_Mahnung-1.pdf
260305_PRX_PSEUDO-Labor_Laborbefund.pdf
260101_PRX_BZA_Amtsanfrage.pdf
260201_PRV_PSEUDO-Versicherung_Lebensversicherung.pdf
260601_PRV_Finanzamt_Einkommensteuerbescheid.pdf
260315_SNX_Gesellschafterbeschluss_Q1.pdf
```

## Duplikat-Konvention

Wenn mehrere Quell-Dateien denselben Ziel-Dateinamen erzeugen:

```
260410_PRX_KV_Hessen_Schreiben.pdf       (Original)
260410_PRX_KV_Hessen_Schreiben__1.pdf    (zweites Vorkommen)
260410_PRX_KV_Hessen_Schreiben__2.pdf    (drittes Vorkommen)
```

**Regel:** Doppel-Unterstrich `__` vor der laufenden Nummer, NICHT
einfacher Unterstrich. Das verhindert Verwechslung mit dem Detail-Feld.

## Datumsextraktion (Reihenfolge)

Die Engine sucht das Dokument-Datum in dieser Priorität (siehe
`CORE_RULES.md` R-003):

1. Strukturierter „Datum:"-Hinweis im Text (`Datum: DD.MM.YYYY`).
2. „Ausstellungsdatum:"-Variante (`Ausstellungsdatum: YYYY-MM-DD`).
3. „Erstellt am"-Variante (deutsch oder englisch).
4. PDF-Metadaten (Erstellt/Modifiziert) — nur als Fallback.
5. Datum im Dateinamen der Quell-Datei (z.B. `2026_04_10_scan.pdf`).
6. Reine Jahreszahl als allerletzter Notnagel — **niemals als
   vollständiges Datum verwenden**, sondern Tag/Monat als `0000` markieren
   und manuell nachpflegen.

## Anti-Pattern (häufige Fehler)

- ❌ `KV_KV_Hessen_Schreiben.pdf` — Absender-Dopplung (`KV` Prefix +
  `KV_Hessen` Detail). Korrekt: `KV_Hessen_Schreiben.pdf`. Engine muss
  `KV_` aus dem Rest entfernen, bevor sie es als Prefix setzt.
- ❌ `Laborgemeinschaft_Laborgemeinschaft_Befund.pdf` — gleicher Fall.
- ❌ `Schreiben.pdf` ohne Datum — Datums-Extraktion gescheitert, Engine
  muss `000000` markieren und eskalieren.
- ❌ Direktes Unterstrich `_1` statt `__1` für Duplikate.
- ❌ Mehrfache Bindestriche oder Leerzeichen im Dateinamen.

## Zeichensatz

- Nur **ASCII-sicher**: a-z, A-Z, 0-9, `_`, `-`, `.`
- Umlaute werden transliteriert: `ä→ae`, `ö→oe`, `ü→ue`, `ß→ss`.
- Leerzeichen werden zu `_`.
