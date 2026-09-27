# Examples

Dieses Verzeichnis zeigt, wie das Regelwerk aus `rules/CORE_RULES.md`,
`rules/SCHEMA.md` und `rules/VENDOR_PATTERNS_EXAMPLE.md` auf fiktive
Dateinamen angewendet werden kann.

Die Demo ist eine kleine Nachbildung mit `python3`-Standardbibliothek.
Sie ist keine lauffaehige Sanexio-Engine und verarbeitet keine echten
PDF-Inhalte. Die lizenzpflichtige Sanexio-Engine ist Teil der
Tenant-Schicht; Details stehen in `docs/ENGINE_INTEGRATION.md`.

Start:

```bash
bash examples/run-demo.sh
```

Der Lauf erzeugt `examples/rename-demo/out/ergebnis.md` und validiert die
generierten Namen gegen das Schema. Ein absichtlich ungueltiger Name wird
separat geprueft, damit der FAIL-Pfad sichtbar ist, ohne den gesamten
Demo-Lauf scheitern zu lassen.
