import struct

def main():
    filename = "NCSET016_downloaded_20251125.BIN"
    try:
        with open(filename, "rb") as f:
            data = f.read()
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return

    # Check 228912 (250612 - 21700)
    off = 228912
    print(f"--- Inspecting offset {off} (0x{off:x}) ---")
    imenu_off = off + 924
    vals = []
    for i in range(12):
        pos = imenu_off + i*4
        if pos < len(data):
            vals.append(data[pos])
    print(f"  Values: {vals}")

if __name__ == "__main__":
    main()
