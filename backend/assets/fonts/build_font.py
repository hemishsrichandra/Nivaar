"""Regenerate the combined, renamed OFL font: pip install fonttools; python build_font.py."""
from pathlib import Path
from fontTools.merge import Merger
root=Path(__file__).resolve().parent
font=Merger().merge([str(root/n) for n in ('NotoSans-Regular.ttf','NotoSansDevanagari-Regular.ttf','NotoSansKannada-Regular.ttf')])
for record in font['name'].names:
    value={1:'Nivaar Unicode',2:'Regular',3:'NivaarUnicode-Regular-1.0',4:'Nivaar Unicode Regular',6:'NivaarUnicode-Regular'}.get(record.nameID)
    if value is not None:record.string=value.encode(record.getEncoding(),errors='replace')
font.save(root/'NivaarUnicode.ttf')
