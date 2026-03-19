import zipfile, os

def replace_zip_file(zip_path, file_to_replace, new_content):
    temp_zip = zip_path + ".temp"
    with zipfile.ZipFile(zip_path, 'r') as zin, zipfile.ZipFile(temp_zip, 'w') as zout:
        for item in zin.infolist():
            if item.filename == file_to_replace:
                zout.writestr(item, new_content)
            else:
                zout.writestr(item, zin.read(item.filename))
    os.replace(temp_zip, zip_path)

out_file = 'AI 2.0 替换主题后.pptx'
import shutil
shutil.copy('AI 2.0 产品流程和实践.pptx', out_file)

with zipfile.ZipFile('InspireTemplate.pptx', 'r') as tz:
    theme_xml = tz.read('ppt/theme/theme1.xml')

replace_zip_file(out_file, 'ppt/theme/theme1.xml', theme_xml)

print("Theme replaced. Checking if python-pptx can open it...")
from pptx import Presentation
prs = Presentation(out_file)
print("Success! Number of slides:", len(prs.slides))
