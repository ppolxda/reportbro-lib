import glob
import os
import re
from collections import defaultdict
from dataclasses import asdict
from dataclasses import dataclass
from itertools import chain
from typing import List


FILE_PATH = os.path.abspath(os.path.dirname(__file__))
FONT_PATH = os.path.join(FILE_PATH, "data", "fonts")
FONT_TYPES = {
    "bold": "bold_filename",
    "bolder": "bold_filename",
    "b": "bold_filename",
    "light": "light_filename",
    "lighter": "light_filename",
    "l": "light_filename",
    "normal": "filename",
    "regular": "filename",
    "r": "filename",
    "n": "filename",
}


@dataclass
class ReportFonts(object):
    """ReportFonts."""

    value: str = ""
    filename: str = ""
    bold_filename: str = ""
    light_filename: str = ""

    def to_jinja2(self):
        """to_jinja2."""
        if self.filename:
            self.filename = self.filename

        return {
            "name": self.value,
            "href": os.path.basename(self.filename),
        }


class ReportFontsLoader(object):
    """ReportFontsLoader."""

    LOAD_FMT_REGIX = re.compile(
        r"^(?:[0-9].*?-)*(.*?)(?:-[0-9]*?)*-"
        r"(bold|bolder|lighter|light|normal|medium|regular|N|M|R|L|B)\.(otf|ttf)$",
        re.MULTILINE | re.IGNORECASE,
    )

    def __init__(self, font_path: str):
        """__init__."""
        self.fonts_cls: List[ReportFonts] = []
        self.fonts: List[dict] = []
        self.font_path = font_path
        self.load()

    def load(self):
        """Load fonts in path."""
        path_list = defaultdict(list)
        for path in chain(
            glob.glob(self.font_path + "/*.ttf"), glob.glob(self.font_path + "/*.otf")
        ):
            dirname = os.path.basename(path)
            names = self.LOAD_FMT_REGIX.match(dirname)
            if not names:
                continue

            names = names.groups()
            path_list[names[0]].append((path, names))

        fonts = []
        for name, paths in path_list.items():
            paths_map = {"value": name}
            for i in paths:
                key = FONT_TYPES.get(i[1][1].lower(), None)
                if not key:
                    continue

                paths_map[key] = i[0]

                if "filename" not in paths_map:
                    paths_map["filename"] = i[0]

            if len(paths_map) > 1:
                fonts.append(ReportFonts(**paths_map))

        self.fonts_cls = fonts
        self.fonts_jinja = [i.to_jinja2() for i in fonts]
        self.fonts = [asdict(i) for i in fonts]


DEFAULT_FONTS = ReportFontsLoader(FONT_PATH)
