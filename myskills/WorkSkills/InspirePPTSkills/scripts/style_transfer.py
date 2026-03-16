import os
import sys
import argparse
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.dml.color import RGBColor
import traceback

class StyleTransfer:
    def __init__(self, template_path):
        self.template_path = template_path
        self.template_prs = Presentation(template_path)
        self.extract_template_styles()

    def extract_template_styles(self):
        """Extracts key styles from the template."""
        # Extract fonts from the first slide's first title if available, or use defaults
        self.heading_font = "Poppins" 
        self.body_font = "Lato"
        
        # Try to find theme fonts from master
        try:
            master = self.template_prs.slide_masters[0]
            # In a real scenario, we'd dig deeper into theme XML, 
            # but for now we'll use these high-quality defaults mentioned in the plan
        except Exception:
            pass

    def apply_style_to_shape(self, shape):
        """Recursively applies styles to a shape and its children (if any)."""
        try:
            if shape.has_text_frame:
                self.apply_text_style(shape.text_frame)

            if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
                for child_shape in shape.shapes:
                    self.apply_style_to_shape(child_shape)
            
            elif shape.shape_type == MSO_SHAPE_TYPE.TABLE:
                for row in shape.table.rows:
                    for cell in row.cells:
                        self.apply_text_style(cell.text_frame)
            
            # Note: We skip complex elements like SmartArt or Charts for now to avoid breaking them
        except Exception as e:
            print(f"Warning: Could not restyle shape {shape.name}: {e}")

    def apply_text_style(self, text_frame):
        """Applies font styles to a text frame while preserving content."""
        for paragraph in text_frame.paragraphs:
            for run in paragraph.runs:
                # Apply theme fonts
                # Heuristic: If it looks like a title (large font), use heading font
                if run.font.size and run.font.size > 24:
                    run.font.name = self.heading_font
                else:
                    run.font.name = self.body_font
                
                # Colors: We could map colors here, but let's start with fonts
                # to ensure high stability as requested.

    def transform(self, target_path):
        """Transforms the target presentation."""
        print(f"Transforming {target_path}...")
        target_prs = Presentation(target_path)
        
        # 1. Slide Master alignment (Simpler version: just iterate slides)
        for slide in target_prs.slides:
            for shape in slide.shapes:
                self.apply_style_to_shape(shape)
            
            # Apply slide background if possible
            # (Skipped for now for maximum stability)

        output_path = os.path.splitext(target_path)[0] + "_inspired.pptx"
        target_prs.save(output_path)
        print(f"Successfully saved to {output_path}")
        return output_path

def main():
    parser = argparse.ArgumentParser(description="Apply InspireTemplate styles to a PPT.")
    parser.add_argument("target_ppt", help="Path to the target PPT file.")
    parser.add_argument("--template", default=os.path.join(os.path.dirname(__file__), "..", "InspireTemplate.pptx"),
                        help="Path to the InspireTemplate.pptx file.")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.target_ppt):
        print(f"Error: Target file {args.target_ppt} not found.")
        sys.exit(1)
        
    if not os.path.exists(args.template):
        print(f"Error: Template file {args.template} not found.")
        sys.exit(1)

    try:
        transformer = StyleTransfer(args.template)
        transformer.transform(args.target_ppt)
    except Exception as e:
        print(f"An error occurred during transformation:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
