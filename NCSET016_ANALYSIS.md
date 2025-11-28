# Analysis of NCSET016.BIN (Nikon Z5 mk2)

## File Overview
- **Filename**: `NCSET016_downloaded_20250810_162802.BIN`
- **Size**: 358,606 bytes (approx 350KB)
- **Header**: Starts with `NIKON...Z5_2`, confirming it is for the Nikon Z5 Mark 2.
- **Firmware Version**: 01.00

## Menu Storage Structure
The file appears to use a similar "Configuration Section" structure to the Z5, but the sections are located at different offsets.

### Identified Configuration Sections
The analysis tool identified the following potential configuration sections. Each section seems to follow the pattern where the **i-menu** starts at offset +924 and the **Mode ID** is at offset +1240 relative to the section start.

| Mode | Section Offset (Decimal) | Section Offset (Hex) | Confidence |
|------|--------------------------|----------------------|------------|
| **Manual** | 92,549 | 0x16985 | High (Score: 74.9) |
| **Program** | 295,672 | 0x482F8 | High (Score: 71.9) |
| **Aperture**| 294,104 | 0x47CD8 | Medium (Overlaps with User modes) |
| **User (U1/U2/U3)** | ~294,100 | ~0x47D00 | Medium (Clustered) |

### Observations
1. **Manual Mode**: A distinct section was found at offset **92,549**. The i-menu configuration in this section contains valid entries like "Active D-Lighting" and "Color space", but also some unknown values, suggesting the menu ID table might differ slightly for the Z5 mk2.
2. **Program Mode**: Found at offset **295,672**, significantly further in the file.
3. **User Modes**: The tool found multiple potential starts for U1, U2, and U3 clustered tightly around offset **294,100**. This suggests these settings might be stored contiguously or the tool is detecting echoes of the same data.

### i-Menu Structure
The i-menu appears to still be stored as a sequence of bytes spaced 4 bytes apart, starting at offset +924 from the section start.
- **Spacing**: 4 bytes
- **Values**: Byte values correspond to menu item IDs (e.g., 0 = Active D-Lighting, 6 = Color Space).
- **Unknown IDs**: Several slots contained IDs (e.g., 69, 79, 77) that are not in the Z5 mapping table, indicating the Z5 mk2 has new or remapped menu items.

## Conclusion
The menus are stored in "Configuration Blocks" similar to the Z5, but placed at new memory addresses. To fully parse this file, the `smart_dump.py` tool's offset detection is working, but the specific menu item IDs need to be updated for the Z5 mk2.
