import struct
import os


FILENAME = "test_download.bin"

def hex_dump(data, start_addr, length=128):
    for i in range(0, length, 16):
        chunk = data[i:i+16]
        hex_str = " ".join(f"{b:02X}" for b in chunk)
        ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        print(f"{start_addr+i:06X}  {hex_str:<48}  {ascii_str}")

def analyze():
    if not os.path.exists(FILENAME):
        print(f"File {FILENAME} not found.")
        return

    with open(FILENAME, "rb") as f:
        data = f.read()

    print(f"File size: {len(data)}")

    # Offsets from visual_editor.py
    offsets = [
        (92549, "Manual"),
        (295672, "Program"),
        (294104, "Aperture Priority"),
        (294152, "U1"),
        (294132, "U2"),
        (294108, "U3")
    ]





def scan_for_value(data, target_val):
    print(f"\nScanning for value {target_val} (Set Picture Control) in potential i-menu slots...")
    
    # We are looking for a sequence of 12 values, spaced by 4 bytes.
    # One of them should be target_val.
    
    # Let's iterate through the file 4 bytes at a time?
    # Or just iterate every byte and check if it could be the start of an i-menu containing target_val.
    
    candidates = []
    
    for i in range(0, len(data) - 48, 4):
        # Check if this position could be the start of an i-menu (slot 1)
        # OR if this position is slot X and contains target_val
        
        # Let's simplify: check if we find target_val at i
        if data[i] == target_val:
            # Assume this is slot S (0-11).
            # Check if the surrounding structure looks like an i-menu.
            
            # Try all 12 possible slot positions for this value
            for slot in range(12):
                start_offset = i - (slot * 4)
                if start_offset < 0 or start_offset + 48 > len(data):
                    continue
                
                # Check if all 12 slots have valid values (e.g. < 100)
                # And check if they are 0-padded (e.g. data[start_offset+1] == 0, etc if 32-bit integers)
                # The file seems to use 32-bit integers for menu items? 
                # Previous dump showed: 01 00 00 00 ... so yes, little endian 32-bit.
                
                is_valid = True
                values = []
                for k in range(12):
                    val_offset = start_offset + k*4
                    val = data[val_offset]
                    # Check padding bytes
                    if data[val_offset+1] != 0 or data[val_offset+2] != 0 or data[val_offset+3] != 0:
                        is_valid = False
                        break
                    if val > 100: # Arbitrary max ID
                        is_valid = False
                        break
                    values.append(val)
                
                if is_valid:
                    # We found a valid-looking i-menu containing our target value!
                    # Now let's see if we can find a Mode ID associated with it.
                    # Assuming i-menu is at offset +924 relative to section start.
                    section_start = start_offset - 924
                    mode_id = -1
                    if section_start >= 0 and section_start + 1240 < len(data):
                        mode_id = data[section_start + 1240]
                    
                    candidates.append({
                        'imenu_start': start_offset,
                        'section_start': section_start,
                        'mode_id': mode_id,
                        'values': values,
                        'found_at_slot': slot + 1
                    })

    print(f"Found {len(candidates)} candidates containing value {target_val}.")
    for c in candidates:
        print(f"i-menu at {c['imenu_start']} (Section {c['section_start']}): Mode ID {c['mode_id']}, Slot {c['found_at_slot']}, Values: {c['values']}")

def analyze():
    if not os.path.exists(FILENAME):
        print(f"File {FILENAME} not found.")
        return

    with open(FILENAME, "rb") as f:
        data = f.read()

    print(f"File size: {len(data)}")
    
    # Search for "Set Picture Control" (31)
    scan_for_value(data, 31)

if __name__ == "__main__":
    analyze()
