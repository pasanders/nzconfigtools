# Quick Start Guide - Nikon Z Visual Menu Editor

## Wat heb je nu?

✅ **Visual Editor** - Complete GUI voor menu bewerking
✅ **Camera Uploader** - Upload direct naar je camera  
✅ **Profile Manager** - Beheer verschillende configuraties
✅ **Smart Analysis** - Automatische bestand detectie

## Direct starten in 3 stappen:

### Stap 1: Test de Visual Editor
```bash
python visual_editor.py
```
- Klik "Open Menu File" en kies je .BIN bestand
- Selecteer een camera mode (Program, Manual, etc.)
- Bewerk de i-menu instellingen rechts
- Sla op met "Save"

### Stap 2: Test Camera Connectie
```bash
python camera_uploader.py list
```
Dit toont je verbonden camera drives.

### Stap 3: Upload naar Camera
```bash
python camera_uploader.py upload jouw_bewerkte_bestand.bin
```

## Belangrijke bestanden:

- **visual_editor.py** = Hoofdprogramma met GUI
- **camera_uploader.py** = Upload tool
- **batch_manager.py** = Profile management
- **smart_dump.py** = Bestand analyse (voor Z5 Mark 2)

## Voor Z5 Mark 2 gebruikers:

Je oude `dump_settings.py` toonde alleen nullen omdat de bestandsstructuur anders is.
Gebruik nu `smart_dump.py`:

```bash
python smart_dump.py jouw_bestand.bin
```

Dit vindt automatisch de juiste configuratie secties!

## Tips:

1. **Maak altijd backups** - De tools doen dit automatisch
2. **Test eerst met kopieën** - Niet direct op originele bestanden
3. **Gebruik profielen** - Sla verschillende configuraties op
4. **Controleer CRC** - Tools doen automatische verificatie

## Hulp nodig?

- Bekijk `README_VISUAL_TOOLS.md` voor complete documentatie
- Test eerst met de meegeleverde S0.BIN en S1.BIN bestanden
- Camera niet gevonden? Controleer of geheugenkaart in USB mode staat

**Je kunt nu visueel je camera menu's bewerken zonder op het kleine schermpje te hoeven kijken! 📸**
