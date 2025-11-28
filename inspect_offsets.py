import struct

def print_imenu_at_offset(data, offset, label):
    print(f"--- {label} at offset {offset} (0x{offset:x}) ---")
    if offset < 0 or offset >= len(data):
        print("Offset out of bounds")
        return

    # i-menu is usually at offset + 924 in the section
    # But we found the match directly. The match IS the i-menu start.
    # So we print 12 items starting at offset.
    
    vals = []
    for i in range(12):
        pos = offset + i*4
        if pos < len(data):
            val = data[pos]
            vals.append(val)
    print(f"Values: {vals}")

def main():
    filename = "NCSET016_downloaded_20251125.BIN"
    try:
        with open(filename, "rb") as f:
            data = f.read()
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return

    u1_offsets = [294936, 316636, 338336]
    stride = 21700
    
    # Print found U1s
    for off in u1_offsets:
        print_imenu_at_offset(data, off, "Found U1 Match")

    # Predict M offsets
    # Assuming M is before U1.
    # U1 is usually bank 3 or 4?
    # Z5 Mk1: M/A/S/P (Primary), M/A/S/P (Secondary), U1, U2, U3
    # If U1 is at 294936, maybe:
    # U2 at 316636?
    # U3 at 338336?
    # That fits the stride exactly!
    
    # So M (or P/S/A/M bank) might be before U1.
    # Bank 1: 294936 - 2*21700 = 251536
    # Bank 2: 294936 - 1*21700 = 273236
    
    potential_offsets = [251536, 273236]
    for off in potential_offsets:
        print_imenu_at_offset(data, off, "Potential M/P/S/A Bank")

    # Also check if there's a header offset difference.
    # In Z5 Mk1, i-menu is at section_start + 924.
    # If our found match is the i-menu itself, then section start is match - 924.
    # Let's check if there's a mode ID at match - 924 + 1240 = match + 316.
    
    for off in u1_offsets + potential_offsets:
        mode_id_off = off + 316
        if mode_id_off < len(data):
            mode_id = data[mode_id_off]
            print(f"  Mode ID at offset+316: {mode_id}")

if __name__ == "__main__":
    main()
