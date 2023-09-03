import argparse
import json
import os
import pathlib
import zipfile
from collections import namedtuple
from urllib.parse import urlencode, quote as urlquote

from icons import IconGenerator


def _do_icons(args):
    gen = IconGenerator(path=args.simple_icons)
    for icon in gen.generate_all():
        with open(os.path.join(args.output, icon.filename), "w", encoding="utf-8") as f:
            f.write(icon.get_xml())


def _do_icon_pack(args):
    pack = {
        "uuid": "c41b931d-8757-49f4-b32b-dd896a431bf9",
        "name": "Aegis Simple Icons - Outlined",
        "version": args.version,
        "icons": [],
    }

    with zipfile.ZipFile(args.output, "w", zipfile.ZIP_DEFLATED) as zipf:
        count = 0
        for icon in IconGenerator(path=args.simple_icons).generate_all():
            basename = os.path.basename(icon.filename)
            filename_zip = os.path.join("SVG", basename)
            zipf.writestr(filename_zip, icon.get_xml())
            pack["icons"].append(
                {
                    "name": icon.title,
                    "filename": pathlib.Path(filename_zip).as_posix(),
                    "category": None,
                    "issuer": [icon.title],
                }
            )
            count += 1
        pack["icons"].sort(key=lambda icon: icon["filename"])
        zipf.writestr("pack.json", json.dumps(pack, indent=4).encode("utf-8"))
        print(f"generated pack with {count} icons")


def main():
    parser = argparse.ArgumentParser(
        description="A collection of developer tools for Aegis Authenticator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers()

    icon_parser = subparsers.add_parser(
        "gen-icons",
        help="Generate icons for Aegis based on simple-icons",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    icon_parser.add_argument(
        "--simple-icons",
        dest="simple_icons",
        required=True,
        help="path of the simple-icons repository checkout",
    )
    icon_parser.add_argument(
        "--output", dest="output", required=True, help="icon output folder"
    )
    icon_parser.set_defaults(func=_do_icons)

    icon_pack_parser = subparsers.add_parser(
        "gen-icon-pack",
        help="Generate an icon pack for Aegis based on simple-icons",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    icon_pack_parser.add_argument(
        "--simple-icons",
        dest="simple_icons",
        required=True,
        help="path of the simple-icons repository checkout",
    )
    icon_pack_parser.add_argument(
        "--version", dest="version", required=True, type=int, help="the version number"
    )
    icon_pack_parser.add_argument(
        "--output", dest="output", required=True, help="icon pack output filename"
    )
    icon_pack_parser.set_defaults(func=_do_icon_pack)

    args = parser.parse_args()
    if args.func:
        args.func(args)


main()
