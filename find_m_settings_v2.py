import struct

def main():
    filename = "NCSET016_downloaded_20251125.BIN"
    try:
        with open(filename, "rb") as f:
            data = f.read()
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return

    # U1 is at 294012 (0x47C7C)
    # Stride is 21700
    # Potential M banks:
    # Bank A: 250612 (0x3D2F4)
    # Bank B: 272312 (0x427B8)
    
    offsets = [250612, 272312]
    
    for off in offsets:
        print(f"--- Inspecting offset {off} (0x{off:x}) ---")
        imenu_off = off + 924
        vals = []
        for i in range(12):
            pos = imenu_off + i*4
            if pos < len(data):
                vals.append(data[pos])
        print(f"  Values: {vals}")
        
    # Also search for '21' (Image Quality) in the whole file, but filter for i-menu like structures
    # i-menu structure: 12 integers (4 bytes each).
    # We are looking for a sequence that contains 21.
    
    print("\nSearching for any sequence containing 21 (Image Quality) and 22 (Image Size):")
    # We look for 21 at index i, and 22 at index i+1 (4 bytes later)
    
    for i in range(0, len(data) - 8, 4):
        if data[i] == 21 and data[i+4] == 22:
            print(f"Found [21, 22] at offset {i} (0x{i:x})")
            # Print context
            start = i - 4 # Assuming 21 is second item? Or first?
            # Let's print -4 to +40
            vals = []
            for k in range(-1, 11):
                pos = i + k*4
                if pos >= 0 and pos < len(data):
                    vals.append(data[pos])
            print(f"  Context (-1 to +10): {vals}")

if __name__ == "__main__":
    main()
