import struct

def find_sequence(data, sequence):
    matches = []
    stride = 4
    seq_len_bytes = len(sequence) * stride
    
    for i in range(0, len(data) - seq_len_bytes, 4):
        match = True
        for j, val in enumerate(sequence):
            if val is not None:
                if data[i + j*stride] != val:
                    match = False
                    break
        if match:
            matches.append(i)
    return matches

def main():
    filename = "NCSET016_downloaded_20251125.BIN"
    try:
        with open(filename, "rb") as f:
            data = f.read()
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return

    # M Sequence partials
    # Top row: Set Picture Control (31), Image quality (21), Image size (22), Iso sensitivity settings (24), AF-area mode (1), Focus mode (15)
    m_part1 = [31, 21, 22, 24, 1, 15]
    
    print("Searching for M partial 1 (Top row):")
    print(m_part1)
    matches1 = find_sequence(data, m_part1)
    for m in matches1:
        print(f"Found M partial 1 at offset {m} (0x{m:x})")
        # Check if the rest matches roughly
        # We expect 12 items total. This is the start (index 0).
        # Check index 7 (Tone mode), 8 (VR), 9 (Custom), 10 (Metering), 11 (Peaking), 12 (Card info)
        # Indices: 0..5 found. 6=?, 7=35, 8=8, 9=27, 10=16, 11=39
        
        # Check index 7 (8th item) -> 35
        val_7 = data[m + 7*4]
        val_8 = data[m + 8*4]
        val_9 = data[m + 9*4]
        val_10 = data[m + 10*4]
        val_11 = data[m + 11*4]
        
        print(f"  Next values: [?, {val_7}, {val_8}, {val_9}, {val_10}, {val_11}]")
        
    # Bottom row: Tone mode (?), Vibration reduction (35), Custom controls (8), Metering (27), Focus peaking (16), View memory card info (39)
    # Search for [35, 8, 27, 16, 39] which corresponds to indices 7, 8, 9, 10, 11
    m_part2 = [35, 8, 27, 16, 39]
    print("\nSearching for M partial 2 (Bottom row part):")
    print(m_part2)
    matches2 = find_sequence(data, m_part2)
    for m in matches2:
        # m is the offset of item 7 (Vibration reduction)
        # Start of imenu would be m - 7*4
        start = m - 7*4
        print(f"Found M partial 2 at offset {m} (0x{m:x}) -> Start approx {start} (0x{start:x})")
        
        # Check the first part
        if start >= 0:
            vals = []
            for k in range(6):
                vals.append(data[start + k*4])
            print(f"  Preceding values: {vals}")
            # Check Tone mode (index 6)
            tone_val = data[start + 6*4]
            print(f"  Tone mode value: {tone_val}")

if __name__ == "__main__":
    main()
