# Nikon Z Camera Menu Configuration Tools

Een complete toolkit voor het visueel bewerken en beheren van Nikon Z camera menu instellingen. Ondersteunt zowel Z5 Mark 1 als Mark 2 met automatische formaat detectie.

## ✨ Nieuwe Features

### 🖥️ Visual Editor (visual_editor.py)
Een complete GUI applicatie voor het visueel bewerken van camera menu's:
- **Visuele i-menu configuratie**: Sleep en wijzig alle 12 i-menu slots met een gebruiksvriendelijke interface
- **Camera mode selectie**: Bewerk instellingen voor Program, Manual, Aperture Priority, etc.
- **File prefix bewerking**: Stel de bestandsnaam prefix in (bijv. "DSC" voor DSC_0001.JPG)
- **Automatische format detectie**: Werkt met zowel Z5 Mark 1 als Mark 2 bestanden
- **CRC verificatie**: Automatische integriteits controle
- **Backup functionaliteit**: Maak automatisch backups van originele bestanden
- **Import/Export**: Sla instellingen op in JSON formaat

### 📤 Camera Uploader (camera_uploader.py)
Command-line tool voor het uploaden van menu bestanden naar de camera:
- **Automatische camera detectie**: Vindt verbonden camera geheugenkaarten automatisch
- **Veiligheids controles**: Verifieert bestanden voordat ze worden geüpload
- **Backup functionaliteit**: Maakt automatisch backups van bestaande menu bestanden
- **Upload verificatie**: Controleert of de upload succesvol was
- **Cross-platform**: Werkt op Windows, macOS en Linux

### 📋 Batch Manager (batch_manager.py)
Geavanceerd profiel beheer systeem:
- **Configuratie profielen**: Sla meerdere camera configuraties op met namen en beschrijvingen
- **Quick apply**: Pas snel verschillende configuraties toe
- **Backup management**: Automatische backups van huidige camera instellingen
- **Profiel vergelijking**: Vergelijk verschillen tussen configuraties
- **Import/Export**: Deel configuraties met anderen

### 🔍 Enhanced Analysis Tools
Verbeterde analyse tools voor verschillende bestandsformaten:
- **smart_dump.py**: Intelligente dump die automatisch de beste configuratie secties vindt
- **auto_detect_dump.py**: Gedetailleerde analyse van alle mogelijke configuraties
- **enhanced_dump.py**: Verbeterde versie met patroon detectie

## 🚀 Quick Start

### 1. Visual Editor starten
```bash
python visual_editor.py
```
- Open een .BIN bestand via File → Open Menu File
- Selecteer een camera mode in de linkerpaneel
- Bewerk i-menu instellingen in de rechterpaneel
- Sla op via File → Save

### 2. Menu bestand uploaden naar camera
```bash
# Automatische camera detectie
python camera_uploader.py upload mijn_menu.bin

# Specifieke drive opgeven
python camera_uploader.py upload mijn_menu.bin --drive E:\

# Camera drives bekijken
python camera_uploader.py list
```

### 3. Profiel management
```bash
# Maak een nieuw profiel
python batch_manager.py create "Studio_Setup" mijn_studio_config.bin --description "Instellingen voor studio fotografie"

# Bekijk alle profielen
python batch_manager.py list

# Pas een profiel toe
python batch_manager.py apply "Studio_Setup"

# Backup huidige camera instellingen
python batch_manager.py backup --name "Current_Backup"

# Vergelijk twee profielen
python batch_manager.py compare "Studio_Setup" "Current_Backup"
```

### 4. Bestand analyse
```bash
# Slimme analyse (aanbevolen voor Z5 Mark 2)
python smart_dump.py jouw_bestand.bin

# Gedetailleerde analyse
python auto_detect_dump.py jouw_bestand.bin

# Originele dump (voor Z5 Mark 1)
python dump_settings.py jouw_bestand.bin
```

## 📁 Bestandsstructuur

```
nzconfigtools/
├── visual_editor.py          # GUI editor applicatie
├── camera_uploader.py        # Upload tool
├── batch_manager.py          # Profiel management
├── smart_dump.py            # Intelligente analyse
├── auto_detect_dump.py      # Auto-detectie analyse
├── enhanced_dump.py         # Verbeterde analyse
├── dump_settings.py         # Originele dump tool
├── changemode.py            # Mode wijzigen
├── copyconfig.py            # Configuratie kopiëren
├── fixcrc.py               # CRC reparatie
├── README.md               # Deze handleiding
└── tests/                  # Test bestanden
    ├── S0.BIN
    └── S1.BIN
```

## 🎯 Use Cases

### Scenario 1: Studio Fotograaf
```bash
# 1. Maak studio profiel
python batch_manager.py create "Studio" studio_config.bin --description "Studio instellingen: Manual mode, specifieke ISO, aangepaste i-menu"

# 2. Maak outdoor profiel  
python batch_manager.py create "Outdoor" outdoor_config.bin --description "Outdoor instellingen: Aperture Priority, auto ISO, andere i-menu"

# 3. Wissel snel tussen profielen
python batch_manager.py apply "Studio"    # Voor studio sessie
python batch_manager.py apply "Outdoor"   # Voor outdoor shoot
```

### Scenario 2: Event Fotograaf
```bash
# 1. Backup huidige instellingen
python batch_manager.py backup --name "Voor_Event" --description "Backup voor event fotografie"

# 2. Pas event instellingen toe
python batch_manager.py apply "Event_Settings"

# 3. Na event, herstel originele instellingen
python batch_manager.py apply "Voor_Event"
```

### Scenario 3: Camera Setup Delen
```bash
# 1. Exporteer je configuratie
python batch_manager.py export "Mijn_Setup" gedeelde_config.bin

# 2. Iemand anders kan het importeren
python batch_manager.py import "Gedeelde_Setup" gedeelde_config.bin --description "Setup van collega"

# 3. Testen en vergelijken
python batch_manager.py compare "Mijn_Setup" "Gedeelde_Setup"
```

## 🔧 Camera Compatibility

### Nikon Z5 Mark 1
- Gebruikt standaard offsets (169824, 176452, etc.)
- Firmware 01.02 getest
- Bestandsgrootte: ~203KB

### Nikon Z5 Mark 2  
- Gebruikt nieuwe bestandsstructuur
- Firmware 01.00 getest  
- Bestandsgrootte: ~359KB
- Automatische detectie werkt

### Andere Nikon Z Camera's
De tools zijn ontworpen om flexibel te zijn en zouden moeten werken met andere Nikon Z modellen. De auto-detectie functionaliteit past zich aan aan verschillende bestandsformaten.

## ⚙️ Technical Details

### Bestandsformaat Detectie
De tools gebruiken een intelligente detectie methode:

1. **Probeer standaard offsets** (Z5 Mark 1 formaat)
2. **Als dat faalt, scan het gehele bestand** naar geldige configuratie secties
3. **Score elke gevonden sectie** op basis van data kwaliteit
4. **Selecteer de beste secties** voor elk camera mode

### i-menu Configuratie
De i-menu bestaat uit 12 slots, elk 4 bytes uit elkaar:
- Offset 924 + (slot_nummer × 4) binnen een configuratie sectie
- Elke slot bevat een ID die verwijst naar een camera functie
- ID 0 = leeg slot

### CRC Verificatie
Bestanden gebruiken CRC-16 (XMODEM variant):
- Laatste 2 bytes van het bestand
- Big-endian formaat
- Berekend over alle data behalve de CRC zelf

## 🛠️ Installation

### Requirements
- Python 3.7+
- tkinter (meestal meegeleverd met Python)
- Standard library modules alleen

### Setup
```bash
# Clone de repository
git clone https://github.com/jouw_username/nzconfigtools.git
cd nzconfigtools

# Direct gebruiken - geen extra installatie nodig!
python visual_editor.py
```

## 📋 Command Reference

### Visual Editor
```bash
python visual_editor.py
```
- GUI applicatie - geen command line argumenten

### Camera Uploader
```bash
# Upload bestand
python camera_uploader.py upload <bestand> [--drive <drive>] [--no-backup] [--no-safety-checks]

# Download bestand
python camera_uploader.py download [--drive <drive>] [--output <bestand>]

# List cameras
python camera_uploader.py list
```

### Batch Manager
```bash
# Profiel beheer
python batch_manager.py create <naam> <bestand> [--description <beschrijving>]
python batch_manager.py list
python batch_manager.py apply <naam> [--drive <drive>]
python batch_manager.py delete <naam>

# Backup en vergelijken
python batch_manager.py backup [--name <naam>] [--description <beschrijving>]
python batch_manager.py compare <profiel1> <profiel2>

# Import/Export
python batch_manager.py export <naam> <uitvoer_bestand>
python batch_manager.py import <naam> <bron_bestand> [--description <beschrijving>]
```

### Analysis Tools
```bash
# Slimme analyse (aanbevolen)
python smart_dump.py <bestand>

# Uitgebreide analyse
python auto_detect_dump.py <bestand>
python enhanced_dump.py <bestand>

# Debug informatie
python dump_settings.py <bestand> [--debug]
```

## 🤝 Contributing

Bijdragen zijn welkom! Vooral voor:
- Ondersteuning van andere Nikon Z modellen
- Nieuwe camera instellingen ontcijferen
- UI verbeteringen
- Bug fixes

## 📄 License

MIT License - zie LICENSE bestand voor details.

## ⚠️ Disclaimer

Deze tools zijn ontwikkeld voor educatieve doeleinden. Maak altijd een backup van je originele camera instellingen voordat je wijzigingen aanbrengt. De ontwikkelaars zijn niet verantwoordelijk voor eventuele schade aan je camera of verlies van instellingen.

## 🆘 Support

Heb je problemen of vragen?
1. Controleer eerst of je camera wordt gedetecteerd met `python camera_uploader.py list`
2. Test de analyse tools op je bestanden
3. Maak altijd backups voordat je wijzigingen aanbrengt
4. Open een issue op GitHub met details over je camera model en firmware versie

---

**Happy shooting! 📸**
