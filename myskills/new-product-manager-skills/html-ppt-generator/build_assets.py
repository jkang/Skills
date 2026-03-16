import os

base_dir = "/Users/superkkk/MyCoding/Skills/myskills/new-product-manager-skills/html-ppt-generator"
scripts_dir = os.path.join(base_dir, "scripts")
os.makedirs(scripts_dir, exist_ok=True)

# Extract original CSS
sample_path = os.path.join(base_dir, "sample.html")
with open(sample_path, "r", encoding="utf-8") as f:
    sample_lines = f.readlines()

in_style = False
css_lines = []
for line in sample_lines:
    if "<style>" in line:
        in_style = True
        continue
    if "</style>" in line:
        break
    if in_style:
        css_lines.append(line)

base_css = "".join(css_lines)

# Append new PPT and layout CSS
ppt_css = """
/* --- PPT Mode CSS overrides --- */
body {
    padding: 0;
    overflow: hidden;
    margin: 0;
}
.slide-container {
    display: none !important;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    opacity: 0;
    transition: opacity 0.4s ease-in-out;
}
.slide-container.active {
    display: flex !important;
    opacity: 1;
}
.slide-container.bleed-image-layout.active {
    display: grid !important;
}

/* --- Added Layouts --- */

/* Agenda Layout */
.agenda-layout {
    width: 100%;
    margin: 0 auto;
}
.agenda-layout ol {
    counter-reset: agenda-counter;
    list-style: none;
    padding: 0;
    margin: 0;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 20px;
}
.agenda-layout li {
    position: relative;
    padding-left: 60px;
    font-size: 24px;
    color: #334155;
    background: #f8fafc;
    border-radius: 12px;
    padding: 20px 20px 20px 80px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    transition: transform 0.2s ease;
}
.agenda-layout li:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}
.agenda-layout li::before {
    counter-increment: agenda-counter;
    content: "0" counter(agenda-counter);
    position: absolute;
    left: 20px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 32px;
    font-weight: 700;
    color: #0284c7;
    font-family: 'Poppins', sans-serif;
}
.agenda-layout li p {
    font-size: 16px;
    color: #64748b;
    margin-top: 10px;
    margin-bottom: 0;
}

/* Chapter Layout */
.chapter-layout {
    text-align: center;
}
.chapter-layout .chapter-number {
    font-size: 24px;
    color: #0284c7;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 20px;
    display: inline-block;
    background: rgba(2, 132, 199, 0.1);
    padding: 8px 20px;
    border-radius: 50px;
}
.chapter-layout h2 {
    font-size: 64px;
    margin-bottom: 20px;
    color: #0f172a;
}
.chapter-layout p.subtitle {
    font-size: 24px;
    color: #475569;
    max-width: 800px;
    margin: 0 auto;
}

/* --- Controls Panel --- */
#ppt-controls {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(226, 232, 240, 0.8);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    border-radius: 50px;
    padding: 10px 25px;
    display: flex;
    align-items: center;
    gap: 20px;
    z-index: 9999;
    font-family: 'Poppins', sans-serif;
    transition: opacity 0.3s ease;
}
body:hover #ppt-controls {
    opacity: 1;
}
#ppt-controls button {
    background: transparent;
    border: none;
    cursor: pointer;
    font-size: 18px;
    color: #0f172a;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    transition: background 0.2s, color 0.2s;
}
#ppt-controls button:hover:not(:disabled) {
    background: #0284c7;
    color: #fff;
}
#ppt-controls button:disabled {
    color: #cbd5e1;
    cursor: not-allowed;
}
#ppt-controls .page-info {
    font-size: 16px;
    font-weight: 500;
    color: #334155;
    display: flex;
    align-items: center;
    gap: 8px;
}
#ppt-controls input {
    width: 48px;
    height: 30px;
    text-align: center;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    font-size: 16px;
    outline: none;
    font-family: 'Poppins', sans-serif;
}
#ppt-controls input:focus {
    border-color: #0284c7;
    box-shadow: 0 0 0 2px rgba(2, 132, 199, 0.2);
}
"""

with open(os.path.join(scripts_dir, "template.css"), "w", encoding="utf-8") as f:
    f.write(base_css + ppt_css)


generator_script = '''import os
import sys
import json

def load_template_css():
    css_path = os.path.join(os.path.dirname(__file__), 'template.css')
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading CSS: {e}")
        return ""

def build_html(slides_data, css_content):
    html = ["""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>""" + slides_data.get('title', 'Presentation') + """</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Lato:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
""" + css_content + """
    </style>
</head>
<body>
"""]

    slides = slides_data.get('slides', [])
    for i, slide in enumerate(slides):
        slide_type = slide.get('type')
        active_class = " active" if i == 0 else ""
        
        if slide_type == 'cover':
            html.append(f"""
    <div class="slide-container{active_class}" id="slide{i}">
        <div class="title-layout">
            <h1>{slide.get('title', '')}</h1>
            <p class="subtitle">{slide.get('subtitle', '')}</p>
            <p style="margin-top:20px; color:#94a3b8;"><i class="fa-solid fa-pen-nib"></i> {slide.get('author', '')} &nbsp;&nbsp;|&nbsp;&nbsp; {slide.get('date', '')}</p>
        </div>
    </div>""")
            
        elif slide_type == 'agenda':
            items_html = "\\n".join([f"<li><strong>{item.get('title', '')}</strong><p>{item.get('subtitle', '')}</p></li>" for item in slide.get('items', [])])
            html.append(f"""
    <div class="slide-container{active_class}" id="slide{i}">
        <h2 class="slide-title">{slide.get('title', 'Agenda')}</h2>
        <div class="content-area">
            <div class="agenda-layout">
                <ol>
                    {items_html}
                </ol>
            </div>
        </div>
    </div>""")
            
        elif slide_type == 'chapter':
            bg_image = slide.get('bg_image')
            if bg_image:
                html.append(f"""
    <div class="slide-container full-bg-image{active_class}" id="slide{i}" style="background-image: linear-gradient(rgba(241, 245, 249, 0.7), rgba(241, 245, 249, 0.9)), url('{bg_image}');">
        <div class="content-overlay">
            <span class="chapter-number">{slide.get('chapter_label', 'Chapter')}</span>
            <h2>{slide.get('title', '')}</h2>
            <p style="font-size: 24px; color: #475569;">{slide.get('subtitle', '')}</p>
        </div>
    </div>""")
            else:
                html.append(f"""
    <div class="slide-container{active_class}" id="slide{i}">
        <div class="chapter-layout">
            <span class="chapter-number">{slide.get('chapter_label', 'Chapter')}</span>
            <h2>{slide.get('title', '')}</h2>
            <p class="subtitle">{slide.get('subtitle', '')}</p>
        </div>
    </div>""")

        elif slide_type == 'content_bleed_image':
            html.append(f"""
    <div class="slide-container bleed-image-layout{active_class}" id="slide{i}">
        <div class="content-container">
            <h2 class="slide-title">{slide.get('title', '')}</h2>
            <div class="content-area">
                <div class="bleed-text-side">
                    {slide.get('content', '')}
                </div>
            </div>
        </div>
        <div class="image-container">
            <img class="bleed-image-side" src="{slide.get('image', '')}" alt="{slide.get('title', '')}">
        </div>
    </div>""")

        elif slide_type == 'content_two_column':
            html.append(f"""
    <div class="slide-container{active_class}" id="slide{i}">
        <h2 class="slide-title">{slide.get('title', '')}</h2>
        <div class="content-area">
            <div class="two-column tiled">
                <div>{slide.get('col1', '')}</div>
                <div>{slide.get('col2', '')}</div>
            </div>
        </div>
    </div>""")

        elif slide_type == 'content_tiled':
            tiles_html = []
            for t in slide.get('tiles', []):
                icon = t.get('icon', 'fa-star')
                if not icon.startswith('fa-'): icon = 'fa-' + icon
                tiles_html.append(f"""
                <div class="tile">
                    <div class="icon"><i class="fa-solid {icon}"></i></div>
                    <h3 style="color:#0f172a; font-size: 22px; margin-bottom:10px;">{t.get('title','')}</h3>
                    <p>{t.get('content','')}</p>
                </div>""")
            html.append(f"""
    <div class="slide-container{active_class}" id="slide{i}">
        <h2 class="slide-title">{slide.get('title', '')}</h2>
        <div class="content-area">
            <div class="tiled-content">
                {"".join(tiles_html)}
            </div>
            {slide.get('bottom_content', '')}
        </div>
    </div>""")

        elif slide_type == 'content_timeline':
            steps_html = []
            colors = ['text-cyan', 'text-emerald', 'text-purple', 'text-rose']
            for idx, s in enumerate(slide.get('steps', [])):
                color = colors[idx % len(colors)]
                steps_html.append(f"""
                <div class="timeline-item">
                    <div class="content-wrapper">
                        <h3 class="{color}">{s.get('title','')}</h3>
                        <p>{s.get('content','')}</p>
                    </div>
                </div>""")
            html.append(f"""
    <div class="slide-container{active_class}" id="slide{i}">
        <h2 class="slide-title">{slide.get('title', '')}</h2>
        <div class="content-area">
            <div class="timeline-layout">
                <div class="timeline-line"></div>
                {"".join(steps_html)}
            </div>
        </div>
    </div>""")

        elif slide_type == 'content_rounded_image':
            html.append(f"""
    <div class="slide-container{active_class}" id="slide{i}">
        <h2 class="slide-title">{slide.get('title', '')}</h2>
        <div class="content-area">
            <div class="two-column rounded-image-layout">
                <div>
                    <div class="image-wrapper">
                        <img src="{slide.get('image', '')}" alt="Rounded Image">
                    </div>
                </div>
                <div>
                    <h3>{slide.get('subtitle', '')}</h3>
                    {slide.get('content', '')}
                </div>
            </div>
        </div>
    </div>""")

        elif slide_type == 'qa':
            html.append(f"""
    <div class="slide-container{active_class}" id="slide{i}">
        <div class="qa-layout">
            <h2>{slide.get('title', 'Q&A')}</h2>
            <p>{slide.get('subtitle', 'Any questions?')}</p>
        </div>
    </div>""")

    js_script = """
    <!-- Controls Panel -->
    <div id="ppt-controls">
        <button id="btn-prev" onclick="prevSlide()" title="上一页"><i class="fa-solid fa-chevron-left"></i></button>
        <div class="page-info">
            <span id="current-page">1</span> / <span id="total-pages">""" + str(len(slides)) + """</span>
        </div>
        <button id="btn-next" onclick="nextSlide()" title="下一页"><i class="fa-solid fa-chevron-right"></i></button>
        <div style="height: 24px; width: 1px; background: #cbd5e1; margin: 0 10px;"></div>
        <div style="display:flex; align-items:center; gap:5px;">
            <input type="number" id="jump-input" min="1" max=\"""" + str(len(slides)) + """\" placeholder="页">
            <button onclick="jumpSlide()" title="跳转" style="font-size: 14px; width: auto; padding: 0 10px; border-radius: 12px; background: #0284c7; color: white;">Go</button>
        </div>
    </div>

    <script>
        const slides = document.querySelectorAll('.slide-container');
        const prevBtn = document.getElementById('btn-prev');
        const nextBtn = document.getElementById('btn-next');
        const currentPageEl = document.getElementById('current-page');
        const jumpInput = document.getElementById('jump-input');
        
        document.getElementById('total-pages').innerText = slides.length;
        jumpInput.max = slides.length;

        let currentSlide = 0;

        function updateUI() {
            slides.forEach((slide, index) => {
                if (index === currentSlide) {
                    slide.classList.add('active');
                } else {
                    slide.classList.remove('active');
                }
            });

            currentPageEl.innerText = currentSlide + 1;
            prevBtn.disabled = currentSlide === 0;
            nextBtn.disabled = currentSlide === slides.length - 1;
        }

        function prevSlide() {
            if (currentSlide > 0) { currentSlide--; updateUI(); }
        }

        function nextSlide() {
            if (currentSlide < slides.length - 1) { currentSlide++; updateUI(); }
        }

        function jumpSlide() {
            let targetSlide = parseInt(jumpInput.value) - 1;
            if (!isNaN(targetSlide) && targetSlide >= 0 && targetSlide < slides.length) {
                currentSlide = targetSlide;
                updateUI();
            } else {
                alert('请输入有效的页码（1-' + slides.length + '）');
            }
        }

        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') {
                nextSlide();
            } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
                prevSlide();
            }
        });

        updateUI();
    </script>
</body>
</html>
"""
    html.append(js_script)
    return "\\n".join(html)

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 generate_ppt.py <input.json> <output.html>")
        sys.exit(1)

    input_json = sys.argv[1]
    output_html = sys.argv[2]

    try:
        with open(input_json, 'r', encoding='utf-8') as f:
            slides_data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON: {e}")
        sys.exit(1)

    css_content = load_template_css()
    final_html = build_html(slides_data, css_content)

    try:
        with open(output_html, 'w', encoding='utf-8') as f:
            f.write(final_html)
        print(f"✅ Presentation compiled successfully: {output_html}")
    except Exception as e:
        print(f"Error writing HTML: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

with open(os.path.join(scripts_dir, "generate_ppt.py"), "w", encoding="utf-8") as f:
    f.write(generator_script)

print("Builder assets created successfully.")
