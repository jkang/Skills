"""Rebrand an unpacked PPTX: replace logos and company name text.

Usage: python rebrand.py <unpacked_dir> [options]

Examples:
    python rebrand.py unpacked/
    python rebrand.py unpacked/ --old-name "Thoughtworks" --new-name "Inspire"
    python rebrand.py unpacked/ --templates-dir assets/

This script:
- Replaces logo images (detected by aspect ratio) with Inspire logos
- Replaces company name text in all XML files (slides, layouts, masters, themes)
- Chooses white or dark logo variant based on the original image analysis
"""

import argparse
import json
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None


# Logo detection: images with aspect ratio > 3:1 and height < 500px
LOGO_MIN_ASPECT_RATIO = 3.0
LOGO_MAX_HEIGHT = 500


def detect_logo_images(unpacked_dir: Path) -> list[Path]:
    """Find media files that look like logos based on aspect ratio."""
    media_dir = unpacked_dir / "ppt" / "media"
    if not media_dir.exists():
        return []

    if Image is None:
        print("Warning: Pillow not installed, skipping logo detection", file=sys.stderr)
        return []

    logos = []
    for img_file in sorted(media_dir.iterdir()):
        if not img_file.is_file():
            continue
        try:
            with Image.open(img_file) as im:
                w, h = im.size
                if h > 0 and w / h >= LOGO_MIN_ASPECT_RATIO and h < LOGO_MAX_HEIGHT:
                    logos.append(img_file)
        except Exception:
            continue

    return logos


def is_white_logo(img_path: Path) -> bool:
    """Detect if an image is a white-on-transparent logo (for dark backgrounds)."""
    if Image is None:
        return False
    try:
        with Image.open(img_path) as im:
            im = im.convert("RGBA")
            # Sample non-transparent pixels
            pixels = list(im.getdata())
            opaque = [(r, g, b) for r, g, b, a in pixels if a > 128]
            if not opaque:
                return False
            # If average brightness > 200, it's a white/light logo
            avg_brightness = sum(
                (r * 0.299 + g * 0.587 + b * 0.114) for r, g, b in opaque
            ) / len(opaque)
            return avg_brightness > 200
    except Exception:
        return False


def replace_logos(
    unpacked_dir: Path,
    logo_dark: Path,
    logo_white: Path,
) -> list[str]:
    """Replace detected logo images with Inspire logos."""
    logos = detect_logo_images(unpacked_dir)
    replaced = []

    for logo_path in logos:
        white = is_white_logo(logo_path)
        source = logo_white if white else logo_dark

        if not source.exists():
            print(f"Warning: Logo source {source} not found, skipping {logo_path.name}", file=sys.stderr)
            continue

        # Resize Inspire logo to match original dimensions
        try:
            with Image.open(logo_path) as orig:
                orig_size = orig.size

            with Image.open(source) as new_logo:
                # Convert to RGBA to avoid palette destruction during resize
                new_logo = new_logo.convert("RGBA")
                resized = new_logo.resize(orig_size, Image.LANCZOS)
                
                # Preserve color profile if it exists
                icc_profile = new_logo.info.get('icc_profile')
                if icc_profile:
                    resized.save(logo_path, format="PNG", icc_profile=icc_profile)
                else:
                    resized.save(logo_path, format="PNG")

            variant = "white" if white else "dark"
            replaced.append(f"{logo_path.name} ({orig_size[0]}x{orig_size[1]}, {variant})")
        except Exception as e:
            print(f"Warning: Failed to replace {logo_path.name}: {e}", file=sys.stderr)

    return replaced


def replace_text_in_xml(
    unpacked_dir: Path,
    old_name: str,
    new_name: str,
    new_year: str | None = None,
) -> list[str]:
    """Replace company name and year in XML files (excluding .rels to avoid corrupting targets)."""
    modified = []

    # STRICT FIX: Exclude .rels files. Replacing raw strings in .rels files where Target attributes 
    # might match the old company name (e.g., Target="media/image_thoughtworks.png") 
    # will break the packaging relationships since we don't rename the physical media files.
    xml_files = list(unpacked_dir.rglob("*.xml"))

    # Regex for year replacement: 
    # Must follow a copyright symbol/word OR be followed by the company name
    # We use a negative lookbehind as a simple check to avoid URLs
    year_pattern = re.compile(
        r"(?<!http://schemas\.openxmlformats\.org/package/)"  # Avoid namespaces
        r"(?<!http://schemas\.openxmlformats\.org/officeDocument/)" # Avoid more namespaces
        r"((?:\u00a9|Copyright|版权所有)\s*)?" # Optional copyright indicator
        r"(20\d{2})"                            # The year
        r"(\s*" + re.escape(old_name) + r")?",  # Optional company name
        re.IGNORECASE
    )

    for xml_file in xml_files:
        try:
            content = xml_file.read_text(encoding="utf-8")
        except Exception:
            continue

        new_content = content

        # 1. Replace Year (if provided)
        if new_year:
            def year_repl(match):
                # Only replace if there's a copyright indicator OR the company name follows
                # Group 1 is indicator, Group 2 is year, Group 3 is company
                indicator = match.group(1)
                year = match.group(2)
                company = match.group(3)
                
                if indicator or company:
                    return f"{indicator or ''}{new_year}{company or ''}"
                return match.group(0) # No change if it's just a random '2025'
            
            new_content = year_pattern.sub(year_repl, new_content)

        # 2. Replace company name
        if old_name in new_content:
            new_content = new_content.replace(old_name, new_name)

        # Also try common case variants
        for variant in [old_name.lower(), old_name.upper(), old_name.capitalize()]:
            if variant in new_content and variant != new_name:
                new_content = new_content.replace(variant, new_name)

        if new_content != content:
            xml_file.write_text(new_content, encoding="utf-8")
            rel_path = xml_file.relative_to(unpacked_dir)
            count = content.count(old_name)
            # Count all case variants
            for variant in [old_name.lower(), old_name.upper(), old_name.capitalize()]:
                if variant != old_name:
                    count += content.count(variant)
            modified.append(f"{rel_path} ({count} replacement(s))")

    return modified


def replace_theme_styles(
    unpacked_dir: Path,
    style_json_path: Path | None = None,
) -> list[str]:
    """Replace theme colors and fonts based on pptstyle.json."""
    if style_json_path is None or not style_json_path.exists():
        # Look for default assets/pptstyle.json
        style_json_path = Path(__file__).resolve().parent.parent / "assets" / "pptstyle.json"

    if not style_json_path.exists():
        print(f"Warning: style JSON {style_json_path} not found", file=sys.stderr)
        return []

    try:
        with open(style_json_path, "r", encoding="utf-8") as f:
            style = json.load(f)
    except Exception as e:
        print(f"Error loading style JSON: {e}", file=sys.stderr)
        return []

    # Map pptstyle.json to PPT theme slots
    # Note: we use HEX codes without # for XML
    colors_map = {
        "dk1": style["color_system"]["functional"]["text_primary"]["hex"].replace("#", ""),
        "lt1": "FFFFFF", # Background 1
        "dk2": style["color_system"]["functional"]["text_secondary"]["hex"].replace("#", ""),
        "lt2": style["color_system"]["brand_primary"]["tech_gray"]["hex"].replace("#", ""),
        "accent1": style["color_system"]["brand_primary"]["starry_blues"]["hex"].replace("#", ""),
        "accent2": style["color_system"]["brand_primary"]["creative_blue"]["hex"].replace("#", ""),
        "accent3": style["color_system"]["brand_secondary"]["amethyst"]["hex"].replace("#", ""),
        "accent4": style["color_system"]["brand_secondary"]["myrtle_deep_green"]["hex"].replace("#", ""),
        "accent5": style["color_system"]["brand_secondary"]["cerulean_frost"]["hex"].replace("#", ""),
        "accent6": style["color_system"]["brand_secondary"]["sakura_pink"]["hex"].replace("#", ""),
    }

    fonts = {
        "major": {
            "latin": "Montserrat Bold",
            "ea": style["typography"]["chinese_fonts"]["heading"],
        },
        "minor": {
            "latin": "Inter",
            "ea": style["typography"]["chinese_fonts"]["body"],
        }
    }

    modified = []
    ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
    # Register namespaces to preserve them on save
    for prefix, uri in ns.items():
        ET.register_namespace(prefix, uri)

    theme_dir = unpacked_dir / "ppt" / "theme"
    if not theme_dir.exists():
        return []

    for theme_file in theme_dir.glob("theme*.xml"):
        tree = ET.parse(theme_file)
        root = tree.getroot()

        changed = False

        # 1. Replace Colors
        clr_scheme = root.find(".//a:clrScheme", ns)
        if clr_scheme is not None:
            clr_scheme.set("name", "Inspire Theme")
            for slot, hex_val in colors_map.items():
                slot_el = clr_scheme.find(f"a:{slot}", ns)
                if slot_el is not None:
                    # Look for srgbClr
                    srgb = slot_el.find("a:srgbClr", ns)
                    if srgb is not None:
                        srgb.set("val", hex_val)
                        changed = True
                    # Also look for sysClr (like in dk1/lt1)
                    sys_clr = slot_el.find("a:sysClr", ns)
                    if sys_clr is not None:
                        # Convert sysClr to srgbClr to force our brand color
                        slot_el.remove(sys_clr)
                        new_srgb = ET.SubElement(slot_el, "{http://schemas.openxmlformats.org/drawingml/2006/main}srgbClr")
                        new_srgb.set("val", hex_val)
                        changed = True

        # 2. Replace Fonts
        font_scheme = root.find(".//a:fontScheme", ns)
        if font_scheme is not None:
            font_scheme.set("name", "Inspire Fonts")
            for type_slot in ["major", "minor"]:
                slot_el = font_scheme.find(f"a:{type_slot}Font", ns)
                if slot_el is not None:
                    # Replace latin
                    latin = slot_el.find("a:latin", ns)
                    if latin is not None:
                        latin.set("typeface", fonts[type_slot]["latin"])
                    # Replace EA
                    ea = slot_el.find("a:ea", ns)
                    if ea is not None:
                        ea.set("typeface", fonts[type_slot]["ea"])
                    # Replace CS
                    cs = slot_el.find("a:cs", ns)
                    if cs is not None:
                        cs.set("typeface", fonts[type_slot]["latin"])
                    changed = True

        if changed:
            tree.write(theme_file, encoding="utf-8", xml_declaration=True)
            modified.append(theme_file.name)

    return modified


def rebrand(
    unpacked_dir: Path,
    old_name: str = "Thoughtworks",
    new_name: str = "Inspire",
    new_year: str | None = None,
    style_json: Path | None = None,
    templates_dir: Path | None = None,
) -> dict:
    """Run full rebranding: logos + text + styles."""
    results = {"logos": [], "text": [], "styles": []}

    # Determine template paths
    if templates_dir is None:
        # Try to find templates relative to script location
        script_dir = Path(__file__).resolve().parent.parent / "assets"
        if script_dir.exists():
            templates_dir = script_dir
        else:
            templates_dir = Path("assets")

    logo_dark = templates_dir / "Inspire logo.png"
    logo_white = templates_dir / "Inspire logo white.png"

    # Step 1: Replace logos
    if logo_dark.exists() or logo_white.exists():
        results["logos"] = replace_logos(unpacked_dir, logo_dark, logo_white)
    else:
        print(f"Warning: No Inspire logos found in {templates_dir}", file=sys.stderr)

    # Step 2: Replace text and year
    results["text"] = replace_text_in_xml(unpacked_dir, old_name, new_name, new_year)

    # Step 3: Replace theme styles
    results["styles"] = replace_theme_styles(unpacked_dir, style_json)

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Rebrand an unpacked PPTX: replace logos and company name text"
    )
    parser.add_argument("unpacked_dir", help="Path to unpacked PPTX directory")
    parser.add_argument(
        "--old-name",
        default="Thoughtworks",
        help="Company name to replace (default: Thoughtworks)",
    )
    parser.add_argument(
        "--new-name",
        default="Inspire",
        help="New company name (default: Inspire)",
    )
    parser.add_argument(
        "--year",
        default="2026",
        help="New copyright year (default: 2026)",
    )
    parser.add_argument(
        "--style-json",
        type=Path,
        default=None,
        help="Path to pptstyle.json for style transfer",
    )
    parser.add_argument(
        "--templates-dir",
        type=Path,
        default=None,
        help="Path to templates directory containing Inspire logos",
    )
    args = parser.parse_args()

    unpacked_dir = Path(args.unpacked_dir)
    if not unpacked_dir.exists():
        print(f"Error: {unpacked_dir} not found", file=sys.stderr)
        sys.exit(1)

    results = rebrand(
        unpacked_dir,
        old_name=args.old_name,
        new_name=args.new_name,
        new_year=args.year,
        style_json=args.style_json,
        templates_dir=args.templates_dir,
    )

    if results["logos"]:
        print(f"Replaced {len(results['logos'])} logo(s):")
        for logo in results["logos"]:
            print(f"  {logo}")
    else:
        print("No logos detected for replacement")

    if results["styles"]:
        print(f"\nUpdated theme styles in {len(results['styles'])} file(s):")
        for s in results["styles"]:
            print(f"  {s}")

    if results["text"]:
        print(f"\nUpdated text in {len(results['text'])} file(s):")
        for f in results["text"]:
            print(f"  {f}")
    else:
        print(f"\nNo '{args.old_name}' text found")
