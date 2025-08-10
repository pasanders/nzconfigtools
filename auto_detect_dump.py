import sys
import struct

def analyze_potential_section(data, section_start, mode_id, mode_name):
    """Analyze a potential configuration section"""
    print(f"\n=== Potential {mode_name} Configuration at offset {section_start} ===")
    
    # Check if we have enough data
    if section_start + 6628 > len(data):
        print("Section would extend beyond file size")
        return False
    
    # Check data density
    section_data = data[section_start:section_start+6628]
    zero_count = section_data.count(0)
    data_density = (len(section_data) - zero_count) / len(section_data)
    
    if data_density < 0.01:  # Less than 1% non-zero data
        print(f"Data density too low: {data_density:.2%}")
        return False
    
    print(f"Data density: {data_density:.2%}")
    
    # Verify mode ID at expected offset
    mode_offset = section_start + 1240
    if mode_offset < len(data) and data[mode_offset] == mode_id:
        print(f"✓ Mode ID confirmed: {mode_name}")
        
        # Analyze i-menu
        imenu_offset = section_start + 924
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
        prefix_offset = section_start + 1540
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
        
        # Additional settings analysis
        analyze_additional_settings(data, section_start)
        
        return True
    else:
        actual_mode = data[mode_offset] if mode_offset < len(data) else "N/A"
        print(f"✗ Mode ID mismatch: expected {mode_id}, found {actual_mode}")
        return False

def analyze_additional_settings(data, section_start):
    """Analyze additional settings in a configuration section"""
    print("Additional settings:")
    
    # Look for common camera settings patterns
    settings_map = {
        # These are educated guesses based on common camera settings
        100: "ISO Auto control",
        200: "Focus tracking", 
        300: "Auto ISO minimum shutter speed",
        400: "Flash mode",
        500: "White balance fine-tuning",
        600: "Picture Control settings",
        700: "VR settings",
        800: "Custom functions",
        900: "Button assignments",
        1000: "Display settings",
        1100: "Playback settings",
        1200: "Video settings"
    }
    
    for offset, description in settings_map.items():
        pos = section_start + offset
        if pos + 4 <= len(data):
            value = struct.unpack('<I', data[pos:pos+4])[0]  # Little-endian 32-bit
            if value != 0:  # Only show non-zero values
                print(f"  {description} (offset {offset}): {value}")

def auto_detect_dump_file(filename):
    """Automatically detect and dump all configuration sections"""
    try:
        with open(filename, "rb") as file:
            data = file.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    print(f"=== Auto-Detecting Nikon Z Camera Settings: {filename} ===")
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
    
    # Auto-detect configuration sections
    mode_patterns = {
        29: "Program",
        30: "Shutter Priority", 
        31: "Aperture Priority",
        32: "Manual",
        33: "Auto"
    }
    
    found_sections = []
    
    for mode_id, mode_name in mode_patterns.items():
        pos = 0
        while True:
            pos = data.find(bytes([mode_id]), pos)
            if pos == -1:
                break
            
            # Check if this could be a mode ID at offset 1240 from section start
            potential_section_start = pos - 1240
            if potential_section_start >= 0:
                # Avoid duplicates (same section start)
                if not any(abs(section[0] - potential_section_start) < 100 for section in found_sections):
                    if analyze_potential_section(data, potential_section_start, mode_id, mode_name):
                        found_sections.append((potential_section_start, mode_name))
            
            pos += 1
    
    # Summary
    print(f"\n=== Summary ===")
    print(f"Found {len(found_sections)} valid configuration section(s):")
    for section_start, name in found_sections:
        print(f"  {name} at offset {section_start} (0x{section_start:x})")
    
    if not found_sections:
        print("No valid configuration sections detected.")
        print("This might indicate:")
        print("- Different camera model with different format")
        print("- Corrupted configuration file")
        print("- New firmware version with changed format")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python auto_detect_dump.py <filename.BIN>")
        print("Example: python auto_detect_dump.py G:\\NCSET006.BIN")
        print()
        print("This tool automatically detects configuration sections in Nikon Z")
        print("camera settings files, regardless of file format changes.")
        sys.exit(1)
    
    auto_detect_dump_file(sys.argv[1])
