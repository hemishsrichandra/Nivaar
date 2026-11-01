# Bundled fonts

Noto Sans, Noto Sans Devanagari and Noto Sans Kannada were obtained from the official notofonts/noto-fonts repository, under the SIL Open Font License in LICENSE.txt.

NivaarUnicode.ttf is a merged derivative renamed **Nivaar Unicode**. It preserves Latin, Devanagari and Kannada glyph coverage in a single font so ReportLab/HarfBuzz can shape mixed-language paragraphs correctly. Regenerate with `python build_font.py` after installing fonttools. The original font files are retained for reproducibility and licensing.

Sources:
- https://github.com/notofonts/noto-fonts/tree/main/hinted/ttf/NotoSans
- https://github.com/notofonts/noto-fonts/tree/main/hinted/ttf/NotoSansDevanagari
- https://github.com/notofonts/noto-fonts/tree/main/hinted/ttf/NotoSansKannada
