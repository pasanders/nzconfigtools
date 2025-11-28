import struct

def is_valid_config_section(data, offset):
    if offset + 6628 > len(data):
        return False
    section_data = data[offset:offset+6628]
    zero_count = section_data.count(0)
    data_density = (len(section_data) - zero_count) / len(section_data)
    return data_density >= 0.01

def main():
    filename = "NCSET016_downloaded_20251125.BIN"
    try:
        with open(filename, "rb") as f:
            data = f.read()
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return

    # Z5 Mark 2 Standard Offsets (Corrected: Match - 924)
    standard_sections_mk2 = [
        (250612, "M/A/S/P Settings (Main)"),
        (272312, "M/A/S/P Settings (Backup)"),
        (294012, "U1"),
        (315712, "U2"),
        (337412, "U3")
    ]
    
    imenu_names = {
        66: "Airplane mode",
        70: "Tone mode",
        30: "Peaking Highlights",
        31: "Set Picture Control",
        36: "White Balance",
        11: "Exposure compensation",
        24: "ISO sensitivity settings",
        1: "AF-area mode",
        15: "Focus Mode",
        35: "Vibration Reduction",
        8: "Custom controls",
        27: "Metering",
        9: "Shutter type",
        21: "Image Quality",
        22: "Image Size",
        16: "Focus peaking",
        39: "View memory card info"
    }

    print("Verifying Z5 Mark 2 Sections:")
    for offset, name in standard_sections_mk2:
        valid = is_valid_config_section(data, offset)
        print(f"Section '{name}' at {offset}: {'Valid' if valid else 'Invalid'}")
        
        if valid:
            # Check Mode ID
            mode_id_offset = offset + 316
            mode_id = data[mode_id_offset] if mode_id_offset < len(data) else -1
            print(f"  Mode ID: {mode_id}")
            
            # Check i-menu
            print("  i-menu:")
            imenu_offset = offset + 924
            for i in range(12):
                pos = imenu_offset + i * 4
                val = data[pos]
                name_str = imenu_names.get(val, f"Unknown ({val})")
                print(f"    Slot {i+1}: {name_str}")

if __name__ == "__main__":
    main()
