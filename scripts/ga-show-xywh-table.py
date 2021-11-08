#!/usr/bin/env python3

import argparse
import json

from pagexml.parser import parse_pagexml_file
from prettytable import PrettyTable

from golden_agents.corrections import Corrector


def load_corrector():
    HTR_CORRECTIONS_FILE = 'data/htr_corrections.json'
    with open(HTR_CORRECTIONS_FILE) as f:
        corrections_json = f.read()
    return Corrector(json.loads(corrections_json))


def xywh(line):
    coords = line.coords
    return f"({coords.x},{coords.y},{coords.w},{coords.h})"


def xywh_table(pagexmlfile: str):
    htr_corrector = load_corrector()

    scan = parse_pagexml_file(pagexmlfile)
    t = PrettyTable(['X', 'Y', 'W', 'H', 'Text', 'Corrections'])
    t.align = "l"
    for i in ['X', 'Y', 'W', 'H']:
        t.align[i] = "r"
    # t.sort_by="Y"
    for line in scan.get_lines():
        if line.text:
            corrected = htr_corrector.correct(line.text)
            empty_if_same = '' if corrected == line.text else corrected
            c = line.coords
            t.add_row([c.x, c.y, c.w, c.h, line.text, empty_if_same])
    return t


def main():
    parser = argparse.ArgumentParser(
        description="Show extracted text from pagexml + its xywh in a table",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("pagexmlfile",
                        help="The PageXML file to extract xywh table from",
                        type=str)
    args = parser.parse_args()
    pagexmlfile = args.pagexmlfile
    if pagexmlfile:
        print(pagexmlfile)
        print(xywh_table(pagexmlfile))


if __name__ == '__main__':
    main()
