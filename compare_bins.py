import sys
import struct

def main():
    if len(sys.argv) < 3:
        print("Usage: python compare_bins.py <file1.BIN> <file2.BIN>")
        return

    file1 = sys.argv[1]
    file2 = sys.argv[2]
    
    try:
        with open(file1, "rb") as f1, open(file2, "rb") as f2:
            data1 = f1.read()
            data2 = f2.read()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    if len(data1) != len(data2):
        print(f"Files have different sizes: {len(data1)} vs {len(data2)}")
        return

    print(f"Comparing {file1} and {file2}...")
    
    diffs = []
    for i in range(len(data1)):
        if data1[i] != data2[i]:
            diffs.append((i, data1[i], data2[i]))

    print(f"Found {len(diffs)} differences.")
    
    # Group differences
    # We expect a change in the i-menu area.
    # Also CRC at the end will change.
    
    for offset, v1, v2 in diffs:
        # Check if it's the CRC (last 2 bytes)
        if offset >= len(data1) - 2:
            print(f"Offset {offset} (CRC): {v1} -> {v2}")
            continue
            
        print(f"Offset {offset} (0x{offset:x}): {v1} -> {v2}")
        
        # Check if this offset falls into any known bank
        # Bank A: 250612 (0x3D2F4)
        # Bank B: 272312 (0x427B8)
        # U1: 294012 (0x47C7C)
        # U2: 315712 (0x4D140)
        # U3: 337412 (0x52604)
        
        banks = {
            "Bank A": 250612,
            "Bank B": 272312,
            "U1": 294012,
            "U2": 315712,
            "U3": 337412
        }
        
        for name, start in banks.items():
            end = start + 6628
            if start <= offset < end:
                rel_offset = offset - start
                print(f"  -> Inside {name} at relative offset {rel_offset}")
                
                # Check if it's in i-menu (924 to 924 + 12*4 = 972)
                if 924 <= rel_offset < 972:
                    slot = (rel_offset - 924) // 4
                    byte_in_slot = (rel_offset - 924) % 4
                    print(f"  -> In i-menu Slot {slot+1}, byte {byte_in_slot}")

if __name__ == "__main__":
    main()
