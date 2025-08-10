import sys
import struct

def find_best_config_sections(data):
    """Find the best quality configuration sections for each mode"""
    mode_patterns = {
        29: "Program",
        30: "Shutter Priority", 
        31: "Aperture Priority",
        32: "Manual",
        33: "Auto",
        34: "U1 (User Setting 1)",
        35: "U2 (User Setting 2)", 
        36: "U3 (User Setting 3)"
    }
    
    # Updated i-menu names based on Nikon Z5 Mark 2 Reference Guide
    imenu_names = {
        0: "Active D-Lighting", 1: "AF area mode", 2: "AF tracking sensitivity", 
        3: "Auto bracketing", 4: "Bluetooth connection", 5: "Monitor/viewfinder brightness", 
        6: "Color space", 7: "Choose image area", 8: "Custom controls", 
        9: "Shutter type", 10: "Electronic front-curtain shutter", 11: "Exposure compensation", 
        12: "Exposure delay mode", 13: "Flash compensation", 14: "Flash mode", 
        15: "Focus Mode", 16: "Focus peaking", 17: "HDR", 18: "Highlight-weighted metering",
        19: "High ISO NR", 20: "Image review", 21: "Image Quality", 22: "Image Size", 
        23: "ISO display", 24: "ISO sensitivity settings", 25: "Long exposure NR", 
        26: "Apply settings to live view", 27: "Metering", 28: "Matrix metering", 
        29: "Multiple Exposure", 30: "Peaking Highlights", 31: "Set Picture Control", 
        32: "Release Mode", 33: "Silent Photography", 34: "Split-screen display zoom", 
        35: "Vibration Reduction", 36: "White Balance", 37: "White balance fine-tuning",
        38: "Wifi connection", 39: "View memory card info", 40: "Interval timer shooting", 
        41: "Time-lapse movie", 42: "Focus shift shooting", 43: "Wind noise reduction",
        44: "Zebras", 45: "Movie quality", 46: "Movie frame size/frame rate",
        47: "Movie microphone", 48: "Movie wind noise reduction", 49: "HDMI output resolution",
        50: "Copyright information", 51: "Group flash options", 52: "FV lock",
        53: "BKT button assignment", 54: "Fn1 button assignment", 55: "Fn2 button assignment",
        56: "AF-assist illuminator", 57: "Beep options", 58: "Touch controls",
        59: "Eye-Detection AF", 60: "Animal-Detection AF", 61: "Subject tracking",
        62: "Wide-area AF (L)", 63: "Wide-area AF (S)", 64: "Auto-area AF",
        65: "Pinpoint AF", 66: "Single-point AF", 67: "Dynamic-area AF",
        68: "3D-tracking", 69: "Group-area AF", 70: "Auto ISO sensitivity control",
        71: "Spot metering", 72: "Center-weighted metering", 73: "Flash sync speed",
        74: "Flash control mode", 75: "Wireless flash control", 76: "Built-in flash mode",
        77: "Commander mode", 78: "Remote flash control", 79: "TTL flash mode",
        80: "Manual flash mode"
    }
    
    best_sections = {}
    
    for mode_id, mode_name in mode_patterns.items():
        candidates = []
        pos = 0
        
        while True:
            pos = data.find(bytes([mode_id]), pos)
            if pos == -1:
                break
            
            # Check if this could be a mode ID at offset 1240 from section start
            potential_section_start = pos - 1240
            if potential_section_start >= 0 and potential_section_start + 6628 <= len(data):
                # Calculate data density
                section_data = data[potential_section_start:potential_section_start+6628]
                zero_count = section_data.count(0)
                data_density = (len(section_data) - zero_count) / len(section_data)
                
                if data_density >= 0.01:  # At least 1% non-zero data
                    # Count valid i-menu entries
                    imenu_offset = potential_section_start + 924
                    valid_entries = 0
                    for i in range(12):
                        menu_pos = imenu_offset + i * 4
                        if menu_pos < len(data):
                            item_id = data[menu_pos]
                            if item_id in imenu_names:
                                valid_entries += 1
                    
                    # Score this section (higher is better)
                    score = (data_density * 50) + (valid_entries * 5)
                    
                    candidates.append({
                        'offset': potential_section_start,
                        'score': score,
                        'density': data_density,
                        'valid_imenu': valid_entries,
                        'mode_name': mode_name
                    })
            
            pos += 1
        
        # Keep only the best candidate for each mode
        if candidates:
            best = max(candidates, key=lambda x: x['score'])
            best_sections[mode_name] = best
    
    return best_sections

def dump_config_section_detailed(data, offset, section_info):
    """Dump a configuration section with detailed analysis"""
    print(f"\n=== {section_info['mode_name']} Configuration ===")
    print(f"Offset: {offset} (0x{offset:x})")
    print(f"Data density: {section_info['density']:.2%}")
    print(f"Quality score: {section_info['score']:.1f}")
    
    # Mode verification
    mode_offset = offset + 1240
    if mode_offset < len(data):
        mode_id = data[mode_offset]
        mode_names = {29: "Program", 30: "Shutter Priority", 31: "Aperture Priority", 
                     32: "Manual", 33: "Auto", 34: "U1 (User Setting 1)", 
                     35: "U2 (User Setting 2)", 36: "U3 (User Setting 3)"}
        print(f"Mode: {mode_names.get(mode_id, f'Unknown ({mode_id})')}")
    
    # i-menu configuration
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
    
    for i in range(12):
        pos = imenu_offset + i * 4
        if pos < len(data):
            item_id = data[pos]
            item_name = imenu_names.get(item_id, f"Unknown/Invalid ({item_id})")
            status = "[OK]" if item_id in imenu_names else "[X]"
            print(f"  Slot {i+1}: {status} {item_name}")
    
    # File prefix
    prefix_offset = offset + 1540
    if prefix_offset + 10 < len(data):
        prefix_bytes = data[prefix_offset:prefix_offset+10]
        null_pos = prefix_bytes.find(0)
        if null_pos >= 0:
            prefix_bytes = prefix_bytes[:null_pos]
        try:
            prefix = prefix_bytes.decode('ascii')
            if prefix:
                print(f"File prefix: '{prefix}'")
            else:
                print("File prefix: (empty)")
        except UnicodeDecodeError:
            print(f"File prefix (hex): {prefix_bytes.hex()}")
    
    # Additional useful settings (educated guesses based on common camera settings)
    print("Additional settings (non-zero values):")
    settings_to_check = [
        (0, "Unknown setting A"),
        (50, "Unknown setting B"), 
        (100, "ISO related"),
        (200, "Focus related"),
        (300, "Exposure related"),
        (400, "Flash related"),
        (500, "WB related"),
        (600, "Picture Control related"),
        (700, "VR related"),
        (800, "Custom functions"),
        (900, "Button assignments"),
        (1000, "Display related"),
        (1100, "Playback related"),
        (1200, "Video related")
    ]
    
    for rel_offset, description in settings_to_check:
        pos = offset + rel_offset
        if pos + 4 <= len(data):
            value = struct.unpack('<I', data[pos:pos+4])[0]
            if value != 0 and value < 1000000:  # Filter out obviously wrong values
                print(f"  {description} (offset {rel_offset}): {value}")

def smart_dump_file(filename):
    """Smart dump that finds the best configuration sections automatically"""
    try:
        with open(filename, "rb") as file:
            data = file.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    print(f"=== Smart Nikon Z Camera Settings Dump: {filename} ===")
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
    
    # Find best configuration sections
    print("\nSearching for configuration sections...")
    best_sections = find_best_config_sections(data)
    
    if not best_sections:
        print("No valid configuration sections found.")
        return
    
    print(f"Found {len(best_sections)} high-quality configuration section(s):")
    for mode_name, section_info in best_sections.items():
        print(f"  {mode_name}: offset {section_info['offset']} (score: {section_info['score']:.1f})")
    
    # Dump each section
    for mode_name, section_info in best_sections.items():
        dump_config_section_detailed(data, section_info['offset'], section_info)
    
    # Summary and recommendations
    print("\n=== Summary & Recommendations ===")
    print("This file appears to have a different structure than the documented format.")
    print("Possible reasons:")
    print("- Different camera model or firmware version")
    print("- Modified or extended file format")
    print("- Multiple configuration sets stored in one file")
    print()
    print("For tool compatibility, you may need to:")
    print("1. Update offset mappings for your camera model")
    print("2. Create model-specific configuration files")
    print("3. Add auto-detection to existing tools")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python smart_dump.py <filename.BIN>")
        print("Example: python smart_dump.py G:\\NCSET006.BIN")
        print()
        print("This tool intelligently finds and displays the best camera")
        print("configuration sections regardless of file format variations.")
        sys.exit(1)
    
    smart_dump_file(sys.argv[1])
