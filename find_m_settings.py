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

    # User M Sequence:
    # 31 (Set Picture Control)
    # 21 (Image Quality)
    # 22 (Image Size)
    # 24 (Iso sensitivity)
    # 1 (AF-area)
    # 15 (Focus mode)
    
    # Search for just [31, 21, 22]
    seq = [31, 21, 22]
    print(f"Searching for {seq}...")
    matches = find_sequence(data, seq)
    
    for m in matches:
        print(f"Found match at {m} (0x{m:x})")
        # Print context (12 items)
        vals = []
        for k in range(12):
            pos = m + k*4
            if pos < len(data):
                vals.append(data[pos])
        print(f"  Context: {vals}")
        
        # Check if this could be the start of i-menu
        # If so, section start is m - 924
        section_start = m - 924
        print(f"  Potential Section Start: {section_start} (0x{section_start:x})")

if __name__ == "__main__":
    main()
