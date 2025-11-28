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

def find_text_patterns(data):
    """Find interesting text patterns in the file"""
    print("\n=== Text Patterns Found ===")
    
    # Look for common camera settings text
    patterns = [
        b"DSC", b"NIKON", b"AUTO", b"MANUAL", b"PROGRAM", 
        b"APERTURE", b"SHUTTER", b"ISO", b"WB", b"AF"
    ]
    
    for pattern in patterns:
        pos = 0
        while True:
            pos = data.find(pattern, pos)
            if pos == -1:
                break
            print(f"'{pattern.decode('ascii')}' found at offset {pos} (0x{pos:x})")
            pos += 1

def analyze_config_section(data, offset, section_name):
    """Analyze a configuration section and detect if it contains valid data"""
    print(f"\n=== {section_name} Analysis ===")
    
    if offset + 6628 > len(data):
        print("Section extends beyond file size")
        return False
    
    # Check if section contains mostly zeros
    section_data = data[offset:offset+6628]
    zero_count = section_data.count(0)
    data_density = (len(section_data) - zero_count) / len(section_data)
    
    print(f"Data density: {data_density:.2%} (lower = more zeros)")
    
    if data_density < 0.01:  # Less than 1% non-zero data
        print("Section appears to be mostly empty/zeros")
        return False
    
    # Mode ID analysis
    mode_offset = offset + 1240
    if mode_offset < len(data):
        mode_id = data[mode_offset]
        mode_names = {29: "Program", 30: "Shutter Priority", 31: "Aperture Priority", 
                     32: "Manual", 33: "Auto"}
        mode_name = mode_names.get(mode_id, f"Unknown ({mode_id})")
        print(f"Mode: {mode_name}")
        
        # Show surrounding bytes for context
        start = max(0, mode_offset - 8)
        end = min(len(data), mode_offset + 8)
        context = data[start:end]
        print(f"Mode area context: {' '.join(f'{b:02x}' for b in context)}")
    
    # i-menu analysis
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
    
    valid_entries = 0
    for i in range(12):
        pos = imenu_offset + i * 4
        if pos < len(data):
            item_id = data[pos]
            item_name = imenu_names.get(item_id, f"Unknown/Invalid ({item_id})")
            print(f"  Slot {i+1}: {item_name}")
            if item_id in imenu_names:
                valid_entries += 1
    
    print(f"Valid i-menu entries: {valid_entries}/12")
    
    # File prefix
    prefix_offset = offset + 1540
    if prefix_offset + 10 < len(data):
        prefix_bytes = data[prefix_offset:prefix_offset+10]
        null_pos = prefix_bytes.find(0)
        if null_pos >= 0:
            prefix_bytes = prefix_bytes[:null_pos]
        try:
            prefix = prefix_bytes.decode('ascii')
            print(f"File prefix: '{prefix}'")
        except UnicodeDecodeError:
            print(f"File prefix (hex): {prefix_bytes.hex()}")
    
    return True

def scan_for_configs(data):
    """Scan the entire file for potential configuration sections"""
    print("\n=== Scanning for Configuration Patterns ===")
    
    # Look for the specific byte pattern that indicates mode IDs
    mode_patterns = [29, 30, 31, 32, 33]  # Valid mode IDs
    
    for mode_id in mode_patterns:
        pos = 0
        while True:
            pos = data.find(bytes([mode_id]), pos)
            if pos == -1:
                break
            
            # Check if this could be a mode ID at offset 1240 from section start
            potential_section_start = pos - 1240
            if potential_section_start >= 0:
                mode_names = {29: "Program", 30: "Shutter Priority", 31: "Aperture Priority", 
                             32: "Manual", 33: "Auto"}
                print(f"Potential {mode_names[mode_id]} mode found at offset {pos} (0x{pos:x})")
                print(f"  Implied section start: {potential_section_start} (0x{potential_section_start:x})")
            
            pos += 1

def enhanced_dump_file(filename):
    """Enhanced dump with better analysis and detection"""
    try:
        with open(filename, "rb") as file:
            data = file.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    print(f"=== Enhanced Nikon Z Camera Settings Analysis: {filename} ===")
    print(f"File size: {len(data)} bytes")
    
    # Basic file info
    if len(data) > 10:
        model_bytes = data[0:11]
        null_pos = model_bytes.find(0)
        if null_pos >= 0:
            model_bytes = model_bytes[:null_pos]
        try:
            camera_model = model_bytes.decode('ascii')
            print(f"Camera model: {camera_model}")
        except UnicodeDecodeError:
            print(f"Camera model (hex): {model_bytes.hex()}")
    
    if len(data) > 28:
        fw_bytes = data[24:29]
        null_pos = fw_bytes.find(0)
        if null_pos >= 0:
            fw_bytes = fw_bytes[:null_pos]
        try:
            firmware = fw_bytes.decode('ascii')
            print(f"Firmware version: {firmware}")
        except UnicodeDecodeError:
            print(f"Firmware version (hex): {fw_bytes.hex()}")
    
    if len(data) >= 2:
        crc_bytes = data[-2:]
        crc_value = struct.unpack('>H', crc_bytes)[0]
        print(f"CRC checksum: 0x{crc_value:04X}")
    
    # Find text patterns
    find_text_patterns(data)
    
    # Scan for potential config sections
    scan_for_configs(data)
    
    # Analyze standard sections
    sections = [
        (250612, "M/A/S/P Settings (Main)"),
        (272312, "M/A/S/P Settings (Backup)"),
        (294012, "U1"),
        (315712, "U2"),
        (337412, "U3")
    ]
    
    for offset, name in sections:
        analyze_config_section(data, offset, name)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python enhanced_dump.py <filename.BIN>")
        print("Example: python enhanced_dump.py G:\\NCSET006.BIN")
        sys.exit(1)
    
    enhanced_dump_file(sys.argv[1])
