import os
import sys
import argparse
import json
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.dml.color import RGBColor
from pptx.util import Pt
import traceback

def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    return RGBColor(int(hex_code[0:2], 16), int(hex_code[2:4], 16), int(hex_code[4:6], 16))

class StyleTransfer:
    def __init__(self, template_path, style_config_path=None):
        self.template_path = template_path
        self.template_prs = Presentation(template_path)
        self.style_config = None
        
        if style_config_path and os.path.exists(style_config_path):
            with open(style_config_path, 'r', encoding='utf-8') as f:
                self.style_config = json.load(f)
        
        self.load_styles()

    def load_styles(self):
        """Loads styles from JSON config or fallback to template extraction."""
        if self.style_config:
            # Typography from JSON
            typo = self.style_config.get("typography", {})
            self.heading_font = typo.get("chinese_fonts", {}).get("heading", "Source Han Sans CN").split('(')[0].strip()
            self.body_font = typo.get("chinese_fonts", {}).get("body", "Source Han Sans CN").split('(')[0].strip()
            
            # Colors from JSON
            colors = self.style_config.get("color_system", {})
            self.primary_color_hex = colors.get("brand_primary", {}).get("starry_blues", {}).get("hex", "#1B2B47")
            self.accent_color_hex = colors.get("brand_primary", {}).get("creative_blue", {}).get("hex", "#4A9FD8")
            self.text_primary_hex = colors.get("functional", {}).get("text_primary", {}).get("hex", "#1B2B47")
        else:
            # Fallback to previous extraction logic
            self.heading_font = "Poppins"
            self.body_font = "Lato"
            self.primary_color_hex = "#1B2B47"
            self.accent_color_hex = "#4A9FD8"
            self.text_primary_hex = "#1B2B47"

    def apply_style_to_shape(self, shape):
        """Recursively applies styles to a shape."""
        try:
            if shape.has_text_frame:
                self.apply_text_style(shape.text_frame)

            # Apply colors to solid fills for AutoShapes
            if shape.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE:
                if hasattr(shape, "fill") and shape.fill.type == 1: # Solid fill
                    # Simple heuristic: if it was some kind of blue/dark color, map to brand primary
                    # Otherwise keep it or map to accent if it was bright.
                    # For now, let's just force the primary text color or similar for stability.
                    pass

            if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
                for child_shape in shape.shapes:
                    self.apply_style_to_shape(child_shape)
            
            elif shape.shape_type == MSO_SHAPE_TYPE.TABLE:
                for row in shape.table.rows:
                    for cell in row.cells:
                        self.apply_text_style(cell.text_frame)
            
        except Exception as e:
            print(f"Warning: Could not restyle shape {shape.name}: {e}")

    def apply_text_style(self, text_frame):
        """Applies font styles and colors to a text frame."""
        for paragraph in text_frame.paragraphs:
            for run in paragraph.runs:
                try:
                    # Font Name
                    is_heading = False
                    if run.font.size and run.font.size.pt > 24:
                        is_heading = True
                    elif run.font.bold:
                        is_heading = True
                    
                    target_font = self.heading_font if is_heading else self.body_font
                    run.font.name = target_font
                    
                    # Font Size Defaults
                    if run.font.size is None:
                        run.font.size = Pt(28) if is_heading else Pt(14)
                    
                    # Font Color
                    run.font.color.rgb = hex_to_rgb(self.text_primary_hex)
                    
                except Exception:
                    pass

    def transform(self, target_path):
        """Transforms the target presentation."""
        print(f"Transforming {target_path} using JSON-defined styles...")
        target_prs = Presentation(target_path)
        
        for slide in target_prs.slides:
            for shape in slide.shapes:
                self.apply_style_to_shape(shape)

        output_path = os.path.splitext(target_path)[0] + "_inspired.pptx"
        target_prs.save(output_path)
        print(f"Successfully saved to {output_path}")
        return output_path

def main():
    parser = argparse.ArgumentParser(description="Apply InspireTemplate styles (JSON-driven) to a PPT.")
    parser.add_argument("target_ppt", help="Path to the target PPT file.")
    parser.add_argument("--template", default=os.path.join(os.path.dirname(__file__), "..", "InspireTemplate.pptx"),
                        help="Path to the InspireTemplate.pptx file.")
    parser.add_argument("--style", default=os.path.join(os.path.dirname(__file__), "..", "pptstyle.json"),
                        help="Path to the pptstyle.json file.")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.target_ppt):
        print(f"Error: Target file {args.target_ppt} not found.")
        sys.exit(1)

    try:
        transformer = StyleTransfer(args.template, args.style)
        transformer.transform(args.target_ppt)
    except Exception as e:
        print(f"An error occurred during transformation:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
