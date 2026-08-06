# -*- coding: utf-8 -*-
"""
Convert the lattice figure from SVG to the formats a publisher accepts
======================================================================

The figure itself is drawn as SVG. Publishers want vector PDF or EPS with
fonts embedded, so this converts and then checks the result rather than
assuming it worked: page size, absence of Type 3 fonts, and font embedding
are all verified after writing.

The output stem follows the input, so the script can be pointed at a second
figure without writing over the lattice figure's PDF.

Usage
-----
    python convert_figure.py [input.svg]
"""
import os
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_IN = os.path.join(HERE, 'fig_lattice_K1_K3.svg')


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_IN
    if not os.path.exists(src):
        print('input not found: %s' % src)
        return 1
    stem = os.path.splitext(src)[0]

    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPDF, renderPM
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    # reportlab's built-in Helvetica is a base-14 font: referenced by name and
    # not embedded. Publishers ask for every font to be embedded, so a TrueType
    # face is registered and substituted. Arial is used in preference to any
    # other free face because its metrics match Helvetica closely enough that
    # the layout, which was measured against Helvetica, does not shift.
    # Registering a new name is not enough: the converter resolves the SVG's
    # font-family through its own table and lands on Helvetica regardless. The
    # base-14 names themselves are therefore rebound to the TrueType files, so
    # whatever the converter asks for is embedded.
    reg = r'C:\Windows\Fonts\arial.ttf'
    bold = r'C:\Windows\Fonts\arialbd.ttf'
    if os.path.exists(reg) and os.path.exists(bold):
        for name, path in (('Helvetica', reg), ('Helvetica-Bold', bold),
                           ('Times-Roman', reg), ('Times-Bold', bold)):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
            except Exception as exc:
                print('could not rebind %s (%s)' % (name, type(exc).__name__))
        pdfmetrics.registerFontFamily('Helvetica', normal='Helvetica',
                                      bold='Helvetica-Bold')
    else:
        print('Arial not found; the output will reference a non-embedded face')

    drawing = svg2rlg(src)
    if drawing is None:
        print('the SVG could not be parsed')
        return 1

    renderPDF.drawToFile(drawing, stem + '.pdf')
    try:
        renderPM.drawToFile(drawing, stem + '.png', fmt='PNG', dpi=600)
    except Exception as exc:
        print('PNG not written (%s); the vector output is what matters'
              % type(exc).__name__)

    # --- verify the PDF rather than trusting the converter -------------
    data = open(stem + '.pdf', 'rb').read()
    box = re.search(rb'/MediaBox\s*\[([^\]]*)\]', data)
    pts = [float(x) for x in box.group(1).split()] if box else [0, 0, 0, 0]
    w_mm = (pts[2] - pts[0]) / 72.0 * 25.4
    h_mm = (pts[3] - pts[1]) / 72.0 * 25.4

    type3 = len(re.findall(rb'/Type3', data))
    embedded = (len(re.findall(rb'/FontFile2', data))
                + len(re.findall(rb'/FontFile3', data))
                + len(re.findall(rb'/FontFile\b', data)))

    print('written : %s.pdf  (%d kB)' % (os.path.basename(stem), len(data) // 1024))
    print('page    : %.1f x %.1f mm' % (w_mm, h_mm))
    print('Type 3  : %d  %s' % (type3, 'OK' if type3 == 0 else '*** publishers reject these'))
    print('embedded fonts : %d %s' % (embedded,
          'OK' if embedded else '*** none embedded, check before submission'))
    if abs(w_mm - 190) > 2:
        print('*** width is not the 190 mm double-column measure')
    return 0


if __name__ == '__main__':
    sys.exit(main())
