# Kern-Regeln R-001 bis R-013

> Generische Regeln für jede Engine-Implementierung. Tenant-spezifische
> Erweiterungen gehören in `VENDOR_PATTERNS_TENANT.md` (gitignored) bzw.
> ins jeweilige Tenant-Repo.

Alle Beispiele, Referenznummern und Kartenkennungen sind synthetische
Demodaten. Mailadressen verwenden reservierte `.example`-Domains.

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
- `PSEUDO-Kasse_PSEUDO-Kasse`, `PSEUDO-Labor_PSEUDO-Labor` (Absender-Dopplung)
- Doppel-Unterstrich `__` nur an reservierter Stelle (Duplikat-Suffix)
- Bindestriche/Leerzeichen-Reste aus unsauberen Quell-Namen

## R-006: OCR-Korrupt-Mapping pflegen

OCR-Engines erzeugen reproduzierbare Fehler bei bestimmten Schriftarten/
Scan-Qualitäten. Tenants pflegen ein Mapping in
`OCR_CORRECTIONS_TENANT.md`:

```
Beispiel (generische Pattern-Struktur):
  "PSEUDO-Kassc" → "PSEUDO-Kasse"        (c statt e als synthetischer OCR-Fehler)
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

---

> **Regeln R-014..R-021 — Inhalts-Lesbarkeit des Dateinamens**
> Ergänzt nach einem Audit des ToSort-Bestands. Befund: zu viele Namen waren
> nicht inhalts-lesbar (Vendor + Nummer, ohne Dokumenttyp; Betreff oder
> Sachbearbeiter statt Absender; verschluckte Umlaute). Diese Regeln
> adressieren jede beobachtete Fehlerklasse; die Belege liegen im internen
> Fehlerprotokoll der Betreiber-Instanz. **R-018 ist bewusst nicht Teil des
> öffentlichen Regelwerks** — es enthält die hausinterne Kategorie-Heuristik
> der Betreiber-Instanz und bleibt dort.

## R-014: Dokumenttyp ist Pflicht

Jeder Zielname MUSS einen Dokumenttyp aus dem kontrollierten Vokabular
(`SCHEMA.md` → „Dokumenttyp") enthalten, gesetzt **aus dem Volltext** (Briefkopf-
Überschrift / Betreffzeile), nicht geraten. Engine-Ablauf:

1. Kandidaten suchen: erste Überschrift in Großschreibung (`RECHNUNG`,
   `AUFTRAGSBESTÄTIGUNG`, `ANGEBOT`, `RESERVIERUNGSBESTÄTIGUNG`, …) bzw.
   englische Pendants (`Invoice` / `Receipt` / `Order confirmation`).
2. Auf kanonischen Typ mappen (transliteriert).
3. Kein sicherer Treffer → `Schreiben` + Eintrag im Fehlerprotokoll.

Verboten: eine Referenznummer als Dokumenttyp-Ersatz (`_AB3606XY.pdf`).

## R-015: Referenznummer-Demotion

Rechnungs-/Auftrags-/Kunden-/Buchungs-/Vertragsnummern dürfen nie das Absender-
oder Dokumenttyp-Feld besetzen. Sie landen als **letztes** `Detail`-Token hinter
dem Dokumenttyp. Auswahl: fachlich sprechende Nummer bevorzugen (Rechnungs-/
Angebots-Nr. > Kunden-/Konto-Nr.). Mehrteilige Nummern intern mit `-` verbinden,
damit sie ein Feld bleiben. Aussagelose Order-/Konto-IDs dürfen entfallen.

## R-016: Absender vom Briefkopf, nicht aus Betreff/Sachbearbeiter

Der Absender wird aus der **Briefkopf-Identität** (Firmenname, Logo-Zeile,
Impressum, Absender-Postzeile) bestimmt — nicht aus:
- der E-Mail-Betreffzeile (`ihre_reiseunterlagen` / `Reservations` /
  `leserservice`),
- dem Namen einer Sachbearbeiterin oder eines Vermittlers (`Vorname_Nachname`
  aus der Signatur ist nicht der Vendor),
- einem Fax-/Transport-Header (`@@NMR <FAXKENNUNG>@@` ist eine Faxkennung der
  Übertragungsstrecke, nicht der Vendorname).

Heuristik: Absender-Kandidat aus Volltext gewinnt gegen Dateinamen-Fragment.
Bei Verrechnungsstellen den **wirtschaftlich Verantwortlichen** mitführen
(`Verrechnungsstelle-Kanzlei`: Verrechnungsstelle V für Kanzlei K).

## R-017: Umlaut-Transliteration erzwingen + nachprüfen

Vor dem Schreiben Umlaute zwingend transliterieren (`ä→ae` usw.). Anschließend
in `sanitize_filename` per Regex auf **verschluckte Umlaute** prüfen
(`sta_tig` / `fu_r` / `Zubeho_r` / `Fru_h` / `beho_r` / `besta_`). Treffer werden
korrigiert (`besta_tigung→bestaetigung`) und als Klasse im Fehlerprotokoll
geführt, bis die Extraktions-/Transliterations-Stufe nachweislich sauber ist.

## R-019: Quell-Metadaten-Rauschen entfernen

Vor der Namensbildung aus Quell-Dateinamen und Volltext entfernen:
- **Scanner-Timestamps** (`_YYYYMMDDhhmmss`, z.B. `_20251208110142`),
- **Fax-/Transport-Header** (`@@…@@`),
- **Marketing-/Preis-Fluff** aus Mail-Betreffs
  (`Max_Plan_5x_107_16EUR` / `Angebot_fuer_Ihren_privaten_Anschluss`),
- **Satzfragmente** aus OCR (`_des` / `_ab_September`), die kein Detail tragen.

Ergebnis: `Detail` enthält nur sinntragende Stichworte (Betreff) und/oder genau
eine gelabelte Referenz.

## R-020: Mail-Metadaten als primäre Inhaltsquelle bei generischem/irreführendem Briefkopf

Ein Quell-Dateiname kann der **E-Mail-Local-Part**
einer Sammel-Adresse (`info@` / `service@` / `support@` / `kontakt@` /
`noreply@`) sein — als „Absender" wertlos und teils irreführend.
Synthetische Gegenbeispiele: `info_Rechnung` für eine Vereins-Einladung
oder `membership_Rechnung` für eine Spendenbescheinigung.

Regeln:
1. **Generische Mailbox erkannt** → Absender NICHT aus dem Local-Part, sondern
   aus der **Domain** ableiten (`info@sportverein.example`→
   `Sportverein-Beispiel`, `service@hausverwaltung.example`→
   `Hausverwaltung-Beispiel`) bzw. aus dem Briefkopf.
2. **Attachment-Dateiname + Betreff sind die verlässlichste Inhaltsquelle**,
   wenn das PDF gescannt/bildbasiert ist oder der Briefkopf nicht zum Inhalt
   passt. Diese Metadaten beim Mail-Import mitführen und persistieren.
3. **Privat-Person als Absender** (`@gmail` / `@gmx` / `@me.com` / `@icloud`):
   kein Personenname als Vendor; stattdessen Vorgang/Dokumenttyp benennen
   (`Bewerbung_MFA_<Name>` / `Mietvertrag_<Objekt>_<Name>` / `Kaufvertrag_…`).
4. **Doctype ≠ "Rechnung" als Default.** Bei diesen Quellen ist der echte Typ
   oft Vertrag / Antrag / Plan oder Grundriss / Spendenbescheinigung /
   Reisebestätigung / Lohnauswertung / Datenblatt — aus Betreff/Attachment
   bestimmen (R-014).

## R-021: Zugangsmittel-Dokumente (PIN/PUK/SIM) — Karten-Identifikator in den Namen, Geheimnisse NICHT

Für Dokumente, die Zugangsmittel ausliefern (SIM-PIN/PUK-Briefe, SIM-Kartenbriefe):

1. **Dokumenttyp** `PIN-PUK` bzw. `SIM-Kartenbrief` (R-014).
2. **Karten-Identifikator ins Detail-Feld**: die SIM-/Karten-/Profilnummer
   (ICCID, Format `8-949xx-xxxxx-xxxxxxxx-x`) gehört in den Namen, damit das
   Dokument der physischen Karte zuordenbar ist. Ziffern/Bindestriche
   kompakt als ein Token (`SIM-89490200001234567890`). Optional zusätzlich die
   Mobilfunk-Rufnummer (MSISDN) als zweites Detail.
3. **Geheimnisse niemals in den Dateinamen**: die eigentlichen PIN-, PUK-,
   Super-PIN- oder Passwort-**Werte** dürfen NIE im Namen erscheinen — nur der
   nicht-geheime Karten-Identifikator. (Der Dateiname ist der am wenigsten
   geschützte Teil einer Datei: sichtbar in jedem Verzeichnislisting, jedem
   Backup, jedem Suchergebnis, jedem Sync-Log.)
4. **Erkennung MUSS auf OCR-Text laufen (R-001), nicht nur auf der nativen
   Textebene.** SIM-Kartenbriefe sind fast immer abfotografierte/gescannte
   Plastik-Kartenträger **ohne** Text-Layer — eine reine `pdftotext`-Suche nach
   `PIN`/`PUK`/`SIM` findet sie nicht. Bei leerer Textebene zwingend OCR ziehen,
   dann SIM-Nummer extrahieren. Die ICCID per OCR ist fehleranfällig: gegen die
   Anbieter-IIN plausibilisieren (`89490x`=Telekom, `89492x`=Vodafone,
   `89493x`=Telefónica/o2) und im Zweifel zur Verifikation gegen die physische
   Karte markieren.

Schema:
```
YYMMDD_<KAT>_<Anbieter>_PIN-PUK_SIM-<ICCID>[_Rufnummer-<MSISDN>].pdf
Beispiel: 260515_PRX_PSEUDO-Mobilfunk_PIN-PUK_SIM-89490200001234567890.pdf
```

Abgrenzung: Verträge und Rechnungen, in denen SIM/PUK nur als Klausel oder
Sammel-Liste vorkommen, sind **kein** `PIN-PUK`-Dokument (kein einzelner
Karten-Identifikator → normaler Vertrags-/Rechnungs-Name).
