import argparse
import os
import re
import sys
import copy
import zipfile
import shutil
import traceback
import io
import tempfile
from pathlib import Path

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.dml.color import RGBColor

# --- Color Scheme Definition ---
COLORS = {
    "primary": "#1B2B47",     # 极致海蓝
    "secondary": "#4A9FD8",   # 创想蓝
    "tertiary": "#64748B",    # 科技灰
    "bg_light": "#FFFFFF",    # 纯白
    "bg_warm": "#FFFDF5"      # 温暖米白
}

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return RGBColor(int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))

COLOR_VALS = [hex_to_rgb(v) for v in COLORS.values()]

# Template Slide Mapping (0-indexed based on InspireTemplate.pptx)
TEMPLATE_MAP = {
    "cover": 1,        # Slide 2: Inspire PPT Template Cover
    "agenda": 4,       # Slide 5: Agenda
    "section": 5,      # Slide 6: Section Separator (No Image)
    "ending": 10       # Slide 11: Ending
}

def classify_source_slide(slide, idx: int, total: int) -> str:
    if idx == 0: return "cover"
    if idx == total - 1: return "ending"

    txt_content = ""
    for s in slide.shapes:
        if s.has_text_frame: txt_content += s.text_frame.text.lower()
        
    if "agenda" in txt_content or "议程" in txt_content or "目录" in txt_content:
        return "agenda"
        
    # Section covers usually have very little text and might contain 'part' or '第'
    txt_stripped = txt_content.replace(' ', '').replace('\n', '')
    if len(txt_stripped) < 30 and ("part" in txt_stripped or "第" in txt_stripped):
        return "section"

    if "🎯" in txt_content or "共创" in txt_content or "练习" in txt_content:
        return "interactive"

    return "content"

def extract_texts_by_size(slide) -> list:
    shapes = []
    for shape in slide.shapes:
        if not shape.has_text_frame: continue
        txt = shape.text_frame.text.strip()
        if not txt: continue
        
        max_sz = 14
        for p in shape.text_frame.paragraphs:
            for r in p.runs:
                if r.font and r.font.size:
                    max_sz = max(max_sz, r.font.size.pt)
        shapes.append((max_sz, txt))
        
    shapes.sort(key=lambda x: x[0], reverse=True)
    return [txt for _, txt in shapes]

def inject_texts(slide, texts: list):
    """Inject texts into the copied template placeholder shapes by size hierarchy."""
    shapes = []
    for shape in slide.shapes:
        if not shape.has_text_frame: continue
        txt = shape.text_frame.text.strip()
        if not txt: continue
        max_sz = 14
        for p in shape.text_frame.paragraphs:
            for r in p.runs:
                if r.font and r.font.size:
                    max_sz = max(max_sz, r.font.size.pt)
        shapes.append((max_sz, shape))
    shapes.sort(key=lambda x: x[0], reverse=True)

    for i, (_, shape) in enumerate(shapes):
        if i >= len(texts): break
        new_val = texts[i]
        tf = shape.text_frame
        set_done = False
        for p in tf.paragraphs:
            if p.runs and not set_done:
                p.runs[0].text = new_val
                for r in p.runs[1:]: r.text = ''
                set_done = True
            elif set_done:
                for r in p.runs: r.text = ''

def apply_color_to_text_frame(text_frame, primary_rgb):
    for p in text_frame.paragraphs:
        for r in p.runs:
            if r.font:
                r.font.name = "Microsoft YaHei"
                # If explicit color is set, override it to primary unless it's white or another theme color
                if hasattr(r.font, 'color') and hasattr(r.font.color, 'rgb') and r.font.color.rgb:
                    if r.font.color.rgb not in COLOR_VALS:
                        r.font.color.rgb = primary_rgb

import colorsys

# Full diverse palette mapping based on Inspire specifications
INSPIRE_PALETTE = {
    "secondary": "#4A9FD8",
    "amethyst": "#7B6B9E",
    "myrtle": "#2F5B56",
    "cerulean": "#8FBCD4",
    "sakura": "#E8B4B4",
}
INSPIRE_RGB = {k: hex_to_rgb(v) for k, v in INSPIRE_PALETTE.items()}
INSPIRE_HSL = {}
for k, rgb in INSPIRE_RGB.items():
    r, g, b = rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    INSPIRE_HSL[k] = (h, l, s)

def get_closest_inspire_color_rgb(r, g, b):
    # Map an original RGB to the closest Inspire Palette semantic color
    h, l, s = colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)
    
    # If the original color is red/orange/pink -> sakura
    if h < 0.05 or h > 0.85: return INSPIRE_RGB["sakura"]
    # If original is Yellow/Green -> myrtle or cerulean depending on lightness/sat
    if 0.05 <= h < 0.45: return INSPIRE_RGB["myrtle"]
    # If original is Blue/Cyan -> secondary or cerulean
    if 0.45 <= h < 0.65: return INSPIRE_RGB["secondary"] if s > 0.5 else INSPIRE_RGB["cerulean"]
    # If original is Purple/Violet -> amethyst
    if 0.65 <= h <= 0.85: return INSPIRE_RGB["amethyst"]
    
    return INSPIRE_RGB["secondary"] # Fallback

def wash_shapes_recursive(shapes, primary_rgb, secondary_rgb, bg_light_rgb):
    for shape in shapes:
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            wash_shapes_recursive(shape.shapes, primary_rgb, secondary_rgb, bg_light_rgb)
            continue
            
        if shape.has_text_frame:
            apply_color_to_text_frame(shape.text_frame, primary_rgb)
            
        # Wash Solid Fills intelligently
        if hasattr(shape, "fill") and shape.fill.type == 1:
            if hasattr(shape.fill.fore_color, 'rgb') and shape.fill.fore_color.rgb:
                original_rgb = shape.fill.fore_color.rgb
                if original_rgb != bg_light_rgb and original_rgb != hex_to_rgb(COLORS["bg_light"]):
                    new_rgb = get_closest_inspire_color_rgb(*original_rgb)
                    shape.fill.fore_color.rgb = new_rgb
        # Do NO harm to theme colors! Native zip-replaced theme handles theme_colors perfectly.

def wash_shape_tree(slide):
    """Enforce Inspire style onto the existing shapes of a content slide."""
    primary = hex_to_rgb(COLORS["primary"])
    secondary = hex_to_rgb(COLORS["secondary"])
    bg_light = hex_to_rgb(COLORS["bg_light"])
    
    # 1. Background
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = bg_light
    
    # 2. Texts and Fills (Recursive)
    wash_shapes_recursive(slide.shapes, primary, secondary, bg_light)

def replace_zip_file(zip_path, file_to_replace, new_content):
    """Safely replace a file inside a ZIP archive."""
    temp_zip = zip_path + ".temp"
    with zipfile.ZipFile(zip_path, 'r') as zin, zipfile.ZipFile(temp_zip, 'w') as zout:
        for item in zin.infolist():
            if item.filename == file_to_replace:
                zout.writestr(item, new_content)
            else:
                zout.writestr(item, zin.read(item.filename))
    os.replace(temp_zip, zip_path)

def flatten_template_slide_to_target(target_slide, template_slide):
    """Deep copy background and shape tree from template (including layout) to target."""
    # 1. Clear target slide shapes entirely
    for s in list(target_slide.shapes):
        s._element.getparent().remove(s._element)
    
    # 2. Copy background <p:bg> (Check slide, then layout)
    bg_element = None
    if template_slide._element.xpath('./p:bg'):
        bg_element = template_slide._element.xpath('./p:bg')[0]
    elif template_slide.slide_layout._element.xpath('./p:bg'):
        bg_element = template_slide.slide_layout._element.xpath('./p:bg')[0]

    if bg_element is not None:
        target_bg_xpath = target_slide._element.xpath('./p:bg')
        if target_bg_xpath:
            target_slide._element.remove(target_bg_xpath[0])
        target_slide._element.insert(0, copy.deepcopy(bg_element))

    # 3. Copy Layout shapes (skip placeholders, extract pictures)
    layout = template_slide.slide_layout
    for shape in layout.shapes:
        if shape.is_placeholder:
            continue
        if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
            blob = shape.image.blob
            target_slide.shapes.add_picture(io.BytesIO(blob), shape.left, shape.top, shape.width, shape.height)
        else:
            # Safe deepcopy for vector shapes
            target_slide._element.spTree.append(copy.deepcopy(shape._element))

    # 4. Copy Slide shapes (extract pictures)
    for shape in template_slide.shapes:
        if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
            blob = shape.image.blob
            target_slide.shapes.add_picture(io.BytesIO(blob), shape.left, shape.top, shape.width, shape.height)
        else:
            target_slide._element.spTree.append(copy.deepcopy(shape._element))

def process_presentation(source_path, template_path):
    print("\n🚀 InspireTransfer v6.0 (Source-Host + SamplePPT Structures)")
    print(f"   Source:   {os.path.basename(source_path)}")
    print(f"   Template: {os.path.basename(template_path)}")
    
    # We now also load SamplePPT for high-fidelity structural slide layouts
    sample_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'SamplePPT.pptx')
    sample_prs = Presentation(sample_path)
    
    STRUCTURAL_TEMPLATES = {
        "cover": sample_prs.slides[0],    # Slide 1
        "agenda": sample_prs.slides[1],   # Slide 2
        "section": sample_prs.slides[4],  # Slide 5
        "ending": sample_prs.slides[15]   # Slide 16
    }
    
    # 1. Build a Temporary Workspace
    with tempfile.TemporaryDirectory() as tmpdir:
        target_pptx_path = os.path.join(tmpdir, "target.pptx")
        shutil.copy2(source_path, target_pptx_path)
        
        # 2. Extract theme from template
        theme_bytes = None
        with zipfile.ZipFile(template_path, 'r') as zip_tpl:
            for file in zip_tpl.namelist():
                if file.endswith('theme1.xml'):
                    theme_bytes = zip_tpl.read(file)
                    break
                    
        # 3. Force inject theme into target PPT ZIP to globally update colors
        if theme_bytes:
            replace_zip_file(target_pptx_path, "ppt/theme/theme1.xml", theme_bytes)
            
        # 4. Open the theme-hacked target presentation for shape modifications
        target_prs = Presentation(target_pptx_path)
        tpl_prs = Presentation(template_path)
    total_slides = len(target_prs.slides)
    print(f"   Processing {total_slides} slides...")
    
    # 5. Master Page Cleanups (Remove old TW logos and Footers)
    inspire_logo = None
    for shape in tpl_prs.slide_layouts[0].shapes:
        if shape.shape_type == MSO_SHAPE_TYPE.PICTURE and shape.width.pt < 150 and shape.height.pt < 50:
            inspire_logo = shape
            break
            
    for master in target_prs.slide_masters:
        shapes = list(master.shapes)
        for s in shapes:
            if s.shape_type == MSO_SHAPE_TYPE.PICTURE and s.width.pt > 250:
                s._element.getparent().remove(s._element)
            if s.has_text_frame and ("©" in s.text_frame.text or "Thoughtworks" in s.text_frame.text):
                s._element.getparent().remove(s._element)
                
    for layout in target_prs.slide_layouts:
        shapes = list(layout.shapes)
        for s in shapes:
            if s.shape_type == MSO_SHAPE_TYPE.PICTURE and s.width.pt > 200 and s.width.pt < 450:
                s._element.getparent().remove(s._element)
            if s.has_text_frame and ("©" in s.text_frame.text or "Thoughtworks" in s.text_frame.text):
                s._element.getparent().remove(s._element)
    
    from pptx.util import Pt
    for i, slide in enumerate(target_prs.slides):
        stype = classify_source_slide(slide, i, total_slides)
        
        if stype in STRUCTURAL_TEMPLATES:
            # Extract texts before clearing
            texts = []
            for s in slide.shapes:
                if s.has_text_frame and s.text_frame.text.strip():
                    texts.append(s.text_frame.text.strip())
            
            txt_preview = ' '.join(texts).replace('\n', ' ')[:40]
            print(f"   [{i+1:02d}/{total_slides}] {stype:<12} | Cloning from SamplePPT -> {txt_preview}...")
            
            # Map structural template
            tpl_slide = STRUCTURAL_TEMPLATES[stype]
            flatten_template_slide_to_target(tpl_slide, slide)
            inject_texts(slide, texts)
        else:
            txt_preview = ""
            for s in slide.shapes:
                if s.has_text_frame: txt_preview += s.text_frame.text.replace('\n', ' ')
            desc_text = txt_preview[:40]
            print(f"   [{i+1:02d}/{total_slides}] {stype:<12} | Washing styles -> {desc_text}")
            
            wash_shape_tree(slide)
            
            # Inject Logo
            if inspire_logo:
                target_left = target_prs.slide_width - inspire_logo.width - 200000 
                slide.shapes.add_picture(io.BytesIO(inspire_logo.image.blob), target_left, inspire_logo.top, inspire_logo.width, inspire_logo.height)
                
            # Inject Footer
            tf = slide.shapes.add_textbox(300000, target_prs.slide_height - 300000 - 150000, 2500000, 300000)
            p = tf.text_frame.paragraphs[0]
            r = p.add_run()
            r.text = "© 2026 Inspire | Confidential"
            r.font.name = "Microsoft YaHei"
            r.font.size = Pt(10)
            r.font.color.rgb = hex_to_rgb(COLORS["secondary"])
            
    # Save the strictly mutated presentation safely
    out_path = os.path.splitext(source_path)[0] + "_inspired.pptx"
    print(f"\n✅ Saving: {out_path}")
    target_prs.save(out_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspire PPT Style Transfer (V5 Source-Host)")
    parser.add_argument("source", help="Path to source PPTX file")
    parser.add_argument("--template", default="InspireTemplate.pptx", help="Path to Inspire PPT template")
    
    args = parser.parse_args()
    if not os.path.exists(args.source):
        print(f"Error: Source file {args.source} not found.")
        sys.exit(1)
        
    try:
        process_presentation(args.source, args.template)
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        traceback.print_exc()
