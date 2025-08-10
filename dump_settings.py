import sys
import struct

def hex_dump(data, offset, length, label=""):
    """Display a hex dump of data for debugging"""
    if label:
        print(f"\n--- {label} ---")
    
    for i in range(0, min(length, len(data) - offset), 16):
        hex_line = " ".join(f"{data[offset + i + j]:02x}" if offset + i + j < len(data) else "  " 
                           for j in range(16))
        ascii_line = "".join(chr(data[offset + i + j]) if offset + i + j < len(data) and 32 <= data[offset + i + j] <= 126 else "."
                            for j in range(16))
        print(f"{offset + i:08x}: {hex_line:<48} |{ascii_line}|")

def dump_config_section(data, offset, section_name, debug=False):
    """Dump a configuration section with known offsets"""
    print(f"\n=== {section_name} Configuration ===")
    
    if debug:
        print(f"Section starts at offset: {offset} (0x{offset:x})")
        hex_dump(data, offset, 64, f"{section_name} section start")
    
    # Mode ID (offset 1240 from section start)
    mode_offset = offset + 1240
    if mode_offset < len(data):
        mode_id = data[mode_offset]
        mode_names = {29: "Program", 30: "Shutter Priority", 31: "Aperture Priority", 
                     32: "Manual", 33: "Auto"}
        mode_name = mode_names.get(mode_id, f"Unknown ({mode_id})")
        print(f"Mode: {mode_name}")
        
        if debug:
            hex_dump(data, mode_offset - 8, 16, f"Mode ID area (offset {mode_offset})")
    
    # i-menu configuration (offset 924, 12 items spaced 4 bytes apart)
    imenu_offset = offset + 924
    print("i-menu configuration:")
    imenu_names = {
        0: "Active D-Lighting", 1: "AF area mode", 3: "Auto bracketing",
        4: "Bluetooth connection", 5: "Monitor/viewfinder brightness", 6: "Color space",
        7: "Choose image area", 8: "Custom controls", 9: "Shutter type",
        11: "Exposure compensation", 12: "Exposure delay mode", 13: "Flash compensation",
        15: "Focus Mode", 17: "HDR", 19: "High ISO NR", 21: "Image Quality",
        22: "Image Size", 24: "ISO sensitivity settings", 25: "Long exposure NR",
        26: "Apply settings to live view", 27: "Metering", 29: "Multiple Exposure",
        30: "Peaking Highlights", 31: "Set Picture Control", 32: "Release Mode",
        33: "Silent Photography", 34: "Split-screen display zoom (Disable)",
        35: "Vibration Reduction", 36: "White Balance", 38: "Wifi connection",
        39: "View memory card info", 40: "Interval timer shooting", 41: "Time-lapse movie",
        42: "Focus shift shooting", 51: "Group flash options"
    }
    
    if debug:
        hex_dump(data, imenu_offset, 48, f"i-menu area (offset {imenu_offset})")
    
    for i in range(12):
        pos = imenu_offset + i * 4
        if pos < len(data):
            item_id = data[pos]
            item_name = imenu_names.get(item_id, f"Unknown/Invalid ({item_id})")
            print(f"  Slot {i+1}: {item_name}")
            if debug and item_id not in imenu_names:
                print(f"    Raw value at offset {pos}: {item_id}")
    
    # File prefix (offset 1540)
    prefix_offset = offset + 1540
    if prefix_offset + 10 < len(data):  # Read up to 10 chars
        prefix_bytes = data[prefix_offset:prefix_offset+10]
        # Find null terminator
        null_pos = prefix_bytes.find(0)
        if null_pos >= 0:
            prefix_bytes = prefix_bytes[:null_pos]
        try:
            prefix = prefix_bytes.decode('ascii')
            print(f"File prefix: '{prefix}'")
        except UnicodeDecodeError:
            print(f"File prefix: {prefix_bytes.hex()}")
            
        if debug:
            hex_dump(data, prefix_offset, 16, f"File prefix area (offset {prefix_offset})")

def dump_bin_file(filename, debug=False):
    """Main function to dump all settings from a .BIN file"""
    try:
        with open(filename, "rb") as file:
            data = file.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    print(f"=== Nikon Z Camera Settings Dump: {filename} ===")
    print(f"File size: {len(data)} bytes")
    
    # Camera model (bytes 0-10)
    if len(data) > 10:
        model_bytes = data[0:11]
        null_pos = model_bytes.find(0)
        if null_pos >= 0:
            model_bytes = model_bytes[:null_pos]
        try:
            camera_model = model_bytes.decode('ascii')
            print(f"Camera model: {camera_model}")
        except UnicodeDecodeError:
            print(f"Camera model: {model_bytes.hex()}")
    
    # Firmware version (bytes 24-28)
    if len(data) > 28:
        fw_bytes = data[24:29]
        null_pos = fw_bytes.find(0)
        if null_pos >= 0:
            fw_bytes = fw_bytes[:null_pos]
        try:
            firmware = fw_bytes.decode('ascii')
            print(f"Firmware version: {firmware}")
        except UnicodeDecodeError:
            print(f"Firmware version: {fw_bytes.hex()}")
    
    # CRC at end of file
    if len(data) >= 2:
        crc_bytes = data[-2:]
        crc_value = struct.unpack('>H', crc_bytes)[0]  # Big-endian 16-bit
        print(f"CRC checksum: 0x{crc_value:04X}")
    
    # Configuration sections
    sections = [
        (169824, "Primary M/A/S/P/Auto"),
        (176452, "Secondary M/A/S/P/Auto"),
        (183080, "U1"),
        (189708, "U2"),
        (196336, "U3")
    ]
    
    for offset, name in sections:
        if offset + 6628 <= len(data):  # Config section is 6628 bytes
            dump_config_section(data, offset, name, debug)
        else:
            print(f"\n=== {name} Configuration ===")
            print("Section extends beyond file size - incomplete data")

if __name__ == "__main__":
    debug_mode = False
    filename = None
    
    if len(sys.argv) < 2:
        print("Usage: python dump_settings.py <filename.BIN> [--debug]")
        print("Example: python dump_settings.py G:\\NCSET006.BIN")
        print("  --debug: Show hex dumps for debugging")
        sys.exit(1)
    
    # Parse arguments
    for arg in sys.argv[1:]:
        if arg == "--debug":
            debug_mode = True
        else:
            filename = arg
    
    if not filename:
        print("Error: No filename provided")
        sys.exit(1)
    
    dump_bin_file(filename, debug_mode)