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


def detect_text_regions(pagexmlfile):
    htr_corrector = load_corrector()
    scan = parse_pagexml_file(pagexmlfile)
    text_regions = []
    scan.set_text_regions_in_reader_order()
    lines = scan.get_lines()
    lines.sort(key=lambda l: l.coords.y)
    for line in lines:
        if not text_regions:
            tr = [line]
            text_regions.append(tr)
        else:
            matching_text_region = None
            for tr in text_regions:
                last_line = tr[-1]
                if line.is_below(last_line):
                    matching_text_region = tr
                    break
            if matching_text_region:
                matching_text_region.append(line)
            else:
                new_text_region = [line]
                text_regions.append(new_text_region)

    text_regions.sort(key=lambda tr: tr[0].coords.x)
    return text_regions


def main():
    parser = argparse.ArgumentParser(
        description="Detect text regions from pagexml",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("pagexmlfile",
                        help="The PageXML file to extract xywh table from",
                        type=str)
    args = parser.parse_args()
    pagexmlfile = args.pagexmlfile
    if pagexmlfile:
        print(pagexmlfile)
        text_regions = detect_text_regions(pagexmlfile)
        for i, tr in enumerate(text_regions):
            print(f"TextRegion {i + 1}")
            print("---------------")
            for line in tr:
                if line.text:
                    print(line.text)
            print()
            print()


if __name__ == '__main__':
    main()
