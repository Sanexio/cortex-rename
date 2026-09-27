# Namensschema — kanonische Datei-Benennung

Alle Anbieter und Referenznummern in den Beispielen sind synthetische
Demodaten ohne Bezug zu tatsächlichen Vorgängen.

## Format

```
YYMMDD_<Kategorie>_<Absender>_<Dokumenttyp>[_<Detail>].pdf
```

| Feld | Format | Pflicht | Beispiel |
|---|---|---|---|
| `YYMMDD` | 6-stelliges **Dokument**datum (nicht Scan-/Mail-Datum) | ja | `260410` (2026-04-10) |
| `Kategorie` | exakt eines aus {`PRX`,`PRV`,`SNX`} | ja | `PRX` |
| `Absender` | Vendor vom **Briefkopf** (nicht Betreff/Sachbearbeiter) | ja | `PSEUDO-Kasse` |
| `Dokumenttyp` | Art des Dokuments, aus kontrolliertem Vokabular | **ja** | `Rechnung`, `Angebot`, `Auftragsbestaetigung` |
| `Detail` *(optional)* | Betreff-Stichwort und/oder gelabelte Referenz | nein | `Umbau-Theke`, `DEMO-2025-00001` |

Trenner: Unterstrich `_`. **Doppelter Unterstrich `__`** ist reserviert für
Duplikat-Suffix (siehe Duplikat-Konvention unten).

> **Geändert mit dem Legibility-Batch (R-014..R-021):** `Dokumenttyp` ist jetzt
> **Pflichtfeld**, `Kategorie` ist auf {PRX,PRV,SNX} hart begrenzt (kein `APO`
> o.ä.), und `Detail` fasst Betreff + Referenz zusammen. Grund: ein Dateiname
> ohne Dokumenttyp ist nicht inhalts-lesbar. Siehe `CORE_RULES.md` R-014..R-019.

## Dokumenttyp (Pflichtfeld, kontrolliertes Vokabular)

Der Dokumenttyp ist der **inhalts-tragendste** Token und steht fast immer
wörtlich im Dokument (Briefkopf-Überschrift, Betreffzeile). Er MUSS gesetzt
werden. Kanonisches Vokabular (transliteriert, keine Umlaute):

```
Rechnung            Stornorechnung        Mahnung            Zahlungserinnerung
Angebot             Auftragsbestaetigung  Auftrag            Bestellblatt
Lieferschein        Vertrag               Nachtrag           Kuendigung
Antrag              Versicherungsschein   Beitragsbescheinigung
Kontoauszug         Rechnungsabschluss    Depotauszug        Zahlungsbeleg
Schreiben           Infobrief             Anschreiben        Bescheid
Reservierungsbestaetigung   Buchungsbestaetigung   Reiseunterlagen
Verbrauchsinformation       Vertragsinformation    Laborbefund
PIN-PUK                     SIM-Kartenbrief
```

Regeln:
- **Mapping aus dem Volltext**, nicht raten: deutsche/englische Überschrift →
  kanonischer Typ (`Auftragsbestätigung`→`Auftragsbestaetigung`,
  `Receipt`→`Zahlungsbeleg`, `Invoice`→`Rechnung`).
- Ist kein Typ sicher bestimmbar: `Schreiben` als neutraler Fallback **und**
  Eintrag ins Fehlerprotokoll (nicht still eine Referenznummer als „Typ" setzen).
- Neue Typen werden hier ergänzt, bevor sie verwendet werden.

## Referenznummer-Regel

Rechnungs-, Auftrags-, Kunden-, Buchungs- oder Vertragsnummern sind **niemals**
der Absender oder der Dokumenttyp. Sie gehören ins optionale `Detail`-Feld,
**hinter** den Dokumenttyp:

```
❌ 250804_PRX_478912_10023.pdf                 (nur Nummern — Inhalt unlesbar)
✅ 250804_PRX_Werbetechnik-Beispiel_Angebot_478912.pdf

❌ 240311_PRX_AB3606XY.pdf                      (Auftragsnr. als ganzer Name)
✅ 240311_PRX_Moebelhaus-Beispiel_Auftragsbestaetigung_AB3606XY.pdf
```

- Bevorzuge die **fachlich sprechende** Nummer (Rechnungs-/Angebots-Nr.),
  nicht Kunden-/Konto-Nr.
- Mehrteilige Nummern mit `-` zusammenziehen
  (`DEMO_2025_00001`→`DEMO-2025-00001`, `DEMO_RE_202605_00001`→`DEMO-RE-202605-00001`).
- Reine Order-/Konto-IDs ohne Aussagewert dürfen entfallen, wenn Absender +
  Dokumenttyp + Datum schon eindeutig sind.

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
260410_PRX_PSEUDO-Kasse_Schreiben.pdf
260410_PRX_PSEUDO-Kasse_Schreiben_Mahnung-1.pdf
260305_PRX_PSEUDO-Labor_Laborbefund.pdf
260101_PRX_PSEUDO-Behoerde_Amtsanfrage.pdf
260201_PRV_PSEUDO-Versicherung_Lebensversicherung.pdf
260601_PRV_Finanzamt_Einkommensteuerbescheid.pdf
260315_SNX_Gesellschafterbeschluss_Q1.pdf
```

## Duplikat-Konvention

Wenn mehrere Quell-Dateien denselben Ziel-Dateinamen erzeugen:

```
260410_PRX_PSEUDO-Kasse_Schreiben.pdf       (Original)
260410_PRX_PSEUDO-Kasse_Schreiben__1.pdf    (zweites Vorkommen)
260410_PRX_PSEUDO-Kasse_Schreiben__2.pdf    (drittes Vorkommen)
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

- ❌ `PSEUDO-Kasse_PSEUDO-Kasse_Schreiben.pdf` — Absender-Dopplung.
  Korrekt: `PSEUDO-Kasse_Schreiben.pdf`; identische Absender nur einmal setzen.
- ❌ `PSEUDO-Labor_PSEUDO-Labor_Befund.pdf` — gleicher Fall.
- ❌ `Schreiben.pdf` ohne Datum — Datums-Extraktion gescheitert, Engine
  muss `000000` markieren und eskalieren.
- ❌ Direktes Unterstrich `_1` statt `__1` für Duplikate.
- ❌ Mehrfache Bindestriche oder Leerzeichen im Dateinamen.
- ❌ **Umlaut als `_` verschluckt**: `Auftragsbesta_tigung`, `Fru_hbetreuung`,
  `Zubeho_r`, `fu_r`. Ursache: Umlaut-Byte gelöscht statt transliteriert.
  Korrekt: `Auftragsbestaetigung`, `Fruehbetreuung`, `Zubehoer`, `fuer`.
- ❌ **Kategorie ungleich PRX/PRV/SNX** (z.B. `APO`). Muss auf eine der drei
  abgebildet werden (Geschäftskonto→PRX, Privatkonto→PRV).
- ❌ **Referenznummer/Auftragsnr. als Absender** (`AB3606XY`, `478912_10023`).
- ❌ **E-Mail-Betreff oder Sachbearbeiter-Name als Absender**
  (`ihre_reiseunterlagen`, `Vorname_Nachname`, `leserservice`).
- ❌ **Scanner-Timestamp / Faxheader im Namen** (`_20251208110142`, `@@NMR …@@`).
- ❌ **Dokumenttyp fehlt** — Name trägt nur Vendor + Nummer.

## Zeichensatz

- Nur **ASCII-sicher**: a-z, A-Z, 0-9, `_`, `-`, `.`
- Umlaute werden **transliteriert** (zwingend, nicht löschen):
  `ä→ae`, `ö→oe`, `ü→ue`, `Ä→Ae`, `Ö→Oe`, `Ü→Ue`, `ß→ss`.
- Leerzeichen werden zu `_`.
- **Pflicht-Nachprüfung in `sanitize_filename`:** Regex auf das Muster
  `<Konsonant>_<Konsonant|Wortende>` an Stellen, wo ein verschluckter Umlaut
  wahrscheinlich ist (`sta_tig`, `fu_r`, `Zubeho_r`, `Fru_h`, `besta_`). Treffer
  → als Transliterations-Fehler markieren und korrigieren (siehe CORE_RULES
  R-017).
