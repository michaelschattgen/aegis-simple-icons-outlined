import io
import json
import os
import re
import secrets
import unicodedata
from collections import OrderedDict

import xmltodict
from lxml import etree
from reportlab.graphics import renderPM
from reportlab.graphics.shapes import Drawing
from svglib.svglib import svg2rlg, SvgRenderer

# source: https://github.com/simple-icons/simple-icons/blob/e5b3b29f1b12974c59db524a272f6cd929545991/scripts/utils.js
def icon_title_to_name(title):
    title = title.lower()

    expr = [
        (r'\+', 'plus'),
        (r'\.', 'dot'),
        (r'&', 'and'),
        ('đ', 'd'),
        ('ħ', 'h'),
        ('ı', 'i'),
        ('ĸ', 'k'),
        ('ŀ', 'l'),
        ('ł', 'l'),
        ('ß', 'ss'),
        ('ŧ'  't')
    ]

    for e in expr:
        title = re.sub(e[0], e[1], title)

    return title.replace(" ", "")

class Icon:
    def __init__(self, title, filename, svg):
        self.title = title
        self.filename = filename
        self.svg = svg

    def get_xml(self):
        return xmltodict.unparse(self.svg, pretty=True)

    def render_png(self, width=800, height=800):
        # svglib expects an lxml structure internally
        parser = etree.XMLParser(remove_comments=True, recover=True)
        svg = etree.fromstring(self.get_xml().encode("utf-8"), parser=parser)

        # render the SVG to a PNG
        renderer = SvgRenderer(None)
        drawing = renderer.render(svg)
        scale_x = width / drawing.width
        scale_y = height / drawing.height
        drawing.width = width
        drawing.height = height
        drawing.scale(scale_x, scale_y)
        return renderPM.drawToString(drawing, fmt="PNG")

class IconGenerator:
    def __init__(self, path):
        self._icon_dir = os.path.join(path)

        with io.open(os.path.join(self._icon_dir, "_data", "simple-icons.json"), "r", encoding='utf-8') as f:
            self._icons = json.load(f)

    def generate(self, icon, square=False):
        title = icon["title"]
        name = icon_title_to_name(title)
        name = re.sub(r"[^a-zA-Z0-9  ]", "", self._remove_accents(name))
        filename = (icon["slug"] if "slug" in icon else name) + ".svg"
        full_filename = os.path.join(self._icon_dir, "icons", filename)
        with io.open(full_filename, "r", encoding='utf-8') as f:
            xml = xmltodict.parse(f.read())

        svg = OrderedDict()
        for key, val in xml["svg"].items():
            if key == "path":
                val["@transform"] = "translate(4.8, 4.8) scale(0.6)"
                val["@fill"] = "#" + icon["hex"]
            svg[key] = val

        xml["svg"] = svg
        return Icon(title, filename, xml)

    def generate_random(self):
        return self.generate(secrets.choice(self._icons))

    def generate_all(self, square=False):
        for icon in self._icons:
            yield self.generate(icon, square)

    @staticmethod
    def _remove_accents(s):
        norm = unicodedata.normalize("NFKD", s)
        return u"".join([c for c in norm if not unicodedata.combining(c)])
