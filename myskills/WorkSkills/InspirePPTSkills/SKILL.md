# InspirePPTSkills

A skill to transform existing PPT documents into the "InspireTemplate" style while strictly preserving all original content.

## Core Features
- **Style Analysis**: Deeply parses `InspireTemplate.pptx` to extract master layouts, theme fonts, and color palettes.
- **Content Preservation**: Ensures all text, data, and core slide elements remain intact during transformation.
- **Defensive Styling**: Skips or uses fallbacks for complex shapes (SmartArt, grouped objects) that are difficult to restyle without breaking.
- **Batch Transformation**: Can be extended to process multiple PPT files at once.

## Usage
1. Ensure your target PPT file is available.
2. The skill will use `InspireTemplate.pptx` located in the same directory as a style reference.
3. Run the style transfer script:
   ```bash
   python scripts/style_transfer.py <target_ppt_path>
   ```
4. The transformed file will be saved as `<original_name>_inspired.pptx`.

## Scripts
- `scripts/style_transfer.py`: The main engine for analyzing the template and applying styles to the target document.
