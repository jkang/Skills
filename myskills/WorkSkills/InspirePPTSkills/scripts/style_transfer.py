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
        if self.style_config:
            typo = self.style_config.get("typography", {})
            self.heading_font = typo.get("chinese_fonts", {}).get("heading", "Source Han Sans CN").split('(')[0].strip()
            self.body_font = typo.get("chinese_fonts", {}).get("body", "Source Han Sans CN").split('(')[0].strip()
            colors = self.style_config.get("color_system", {})
            self.primary_color_hex = colors.get("brand_primary", {}).get("starry_blues", {}).get("hex", "#1B2B47")
            self.accent_color_hex = colors.get("brand_primary", {}).get("creative_blue", {}).get("hex", "#4A9FD8")
            self.neutral_bg_hex = colors.get("brand_primary", {}).get("tech_gray", {}).get("hex", "#F5F7FA")
            self.white_hex = colors.get("brand_secondary", {}).get("white", {}).get("hex", "#FFFFFF")
            self.text_primary_hex = colors.get("functional", {}).get("text_primary", {}).get("hex", "#1B2B47")
            self.text_secondary_hex = colors.get("functional", {}).get("text_secondary", {}).get("hex", "#64748B")
            self.border_hex = colors.get("functional", {}).get("border", {}).get("hex", "#E2E8F0")
        else:
            self.heading_font = "Poppins"
            self.body_font = "Lato"
            self.primary_color_hex = "#1B2B47"
            self.accent_color_hex = "#4A9FD8"
            self.neutral_bg_hex = "#F5F7FA"
            self.white_hex = "#FFFFFF"
            self.text_primary_hex = "#1B2B47"
            self.text_secondary_hex = "#64748B"
            self.border_hex = "#E2E8F0"

    def shape_text_length(self, shape):
        if not shape.has_text_frame:
            return 0
        total = 0
        for paragraph in shape.text_frame.paragraphs:
            for run in paragraph.runs:
                total += len(run.text.strip())
        return total

    def is_title_shape(self, shape):
        if not shape.has_text_frame:
            return False
        tf = shape.text_frame
        for paragraph in tf.paragraphs:
            for run in paragraph.runs:
                if run.font.size and run.font.size.pt >= 26:
                    return True
                if run.font.bold and len(run.text.strip()) <= 40:
                    return True
        if shape.top is not None and shape.height is not None:
            return shape.top < 1700000 and shape.height > 500000
        return False

    def apply_shape_fill(self, shape, is_cover):
        if not hasattr(shape, "fill"):
            return
        if shape.fill.type is None:
            return
        text_len = self.shape_text_length(shape)
        shape.fill.solid()
        if is_cover:
            if text_len > 0:
                shape.fill.fore_color.rgb = hex_to_rgb(self.primary_color_hex)
            else:
                shape.fill.fore_color.rgb = hex_to_rgb(self.accent_color_hex)
            return
        if text_len > 0:
            shape.fill.fore_color.rgb = hex_to_rgb(self.white_hex)
        else:
            shape.fill.fore_color.rgb = hex_to_rgb(self.neutral_bg_hex)

    def apply_shape_line(self, shape):
        if not hasattr(shape, "line"):
            return
        if shape.line is None:
            return
        try:
            shape.line.color.rgb = hex_to_rgb(self.border_hex)
            shape.line.width = Pt(1)
        except Exception:
            return

    def apply_style_to_shape(self, shape, is_cover=False):
        try:
            if shape.has_text_frame:
                self.apply_text_style(shape.text_frame, is_cover=is_cover, is_title=self.is_title_shape(shape))

            if shape.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE:
                self.apply_shape_fill(shape, is_cover=is_cover)
                self.apply_shape_line(shape)

            if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
                for child_shape in shape.shapes:
                    self.apply_style_to_shape(child_shape, is_cover=is_cover)
            
            elif shape.shape_type == MSO_SHAPE_TYPE.TABLE:
                for row in shape.table.rows:
                    for cell_index, cell in enumerate(row.cells):
                        if row == shape.table.rows[0]:
                            cell.fill.solid()
                            cell.fill.fore_color.rgb = hex_to_rgb(self.primary_color_hex)
                            self.apply_text_style(cell.text_frame, is_cover=False, is_title=True, force_color=self.white_hex)
                        else:
                            cell.fill.solid()
                            cell.fill.fore_color.rgb = hex_to_rgb(self.white_hex)
                            self.apply_text_style(cell.text_frame, is_cover=False, is_title=cell_index == 0, force_color=self.text_primary_hex)
            
        except Exception as e:
            print(f"Warning: Could not restyle shape {shape.name}: {e}")

    def apply_text_style(self, text_frame, is_cover=False, is_title=False, force_color=None):
        for paragraph in text_frame.paragraphs:
            for run in paragraph.runs:
                try:
                    is_heading = is_title or (run.font.size and run.font.size.pt > 24) or run.font.bold
                    target_font = self.heading_font if is_heading else self.body_font
                    run.font.name = target_font
                    if run.font.size is None:
                        run.font.size = Pt(30) if is_heading else Pt(14)
                    elif is_heading and run.font.size.pt < 24:
                        run.font.size = Pt(24)
                    if is_heading:
                        run.font.bold = True
                    if force_color:
                        run.font.color.rgb = hex_to_rgb(force_color)
                    elif is_cover:
                        run.font.color.rgb = hex_to_rgb(self.white_hex)
                    elif is_heading:
                        run.font.color.rgb = hex_to_rgb(self.primary_color_hex)
                    else:
                        run.font.color.rgb = hex_to_rgb(self.text_primary_hex)
                except Exception:
                    pass

    def apply_slide_background(self, slide, index):
        background = slide.background
        background.fill.solid()
        if index == 0:
            background.fill.fore_color.rgb = hex_to_rgb(self.primary_color_hex)
        else:
            background.fill.fore_color.rgb = hex_to_rgb(self.neutral_bg_hex)

    def transform(self, target_path):
        print(f"Transforming {target_path} using JSON-defined styles...")
        target_prs = Presentation(target_path)
        
        for index, slide in enumerate(target_prs.slides):
            is_cover = index == 0
            self.apply_slide_background(slide, index)
            for shape in slide.shapes:
                self.apply_style_to_shape(shape, is_cover=is_cover)

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
