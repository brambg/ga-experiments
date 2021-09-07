#!/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict
from dataclasses import dataclass

import pagexml.parser as px
from dataclasses_json import dataclass_json
from shapely.geometry import Polygon

import golden_agents.tools as ga


@dataclass_json
@dataclass
class EvaluationFile:
    name: str
    htr_path: str
    gt_path: str


@dataclass
class LineInfo:
    id: str
    text: str
    polygon: Polygon


def main():
    paths = ga.all_page_xml_file_paths()
    rpaths = [p for p in paths if 'NOTI01181' in p]
    by_file = defaultdict(list)
    for p in rpaths:
        parts = p.split('/')
        dir = parts[0]
        file = parts[1]
        by_file[file].append(dir)
    evaluation_files = []
    for k, v in by_file.items():
        if len(v) == 2:
            name = k.replace('.xml', '')
            htr_path = f"{v[1]}/{k}"
            gt_path = f"{v[0]}/{k}"
            evaluation_files.append(EvaluationFile(name=name, htr_path=htr_path, gt_path=gt_path))
    for ef in evaluation_files:
        gt_file = f'../pagexml/{ef.gt_path}'
        gt_scan = px.parse_pagexml_file(gt_file)
        gt_line_info = []
        for l in gt_scan.get_lines():
            if l.text:
                gt_line_info.append(LineInfo(
                    id=l.id,
                    text=l.text,
                    polygon=(Polygon(l.coords.points))
                ))
        htr_file = f'../pagexml/{ef.htr_path}'
        htr_scan = px.parse_pagexml_file(htr_file)
        htr_line_info = []
        for l in htr_scan.get_lines():
            if l.text:
                htr_line_info.append(LineInfo(
                    id=l.id,
                    text=l.text,
                    polygon=(Polygon(l.coords.points))
                ))
        for li in gt_line_info:
            if not li.polygon.is_valid:
                print(li)
                break
            htr_match = htr_line_info[0]
            largest_overlap = 0
            for htr_li in htr_line_info:
                if not htr_li.polygon.is_valid:
                    print(htr_li)
                    break
                overlap = li.polygon.intersection(htr_li.polygon).area
                if overlap > largest_overlap:
                    largest_overlap = overlap
                    htr_match = htr_li
            if li.text != htr_match.text:
                # print(f"GT line {li.id}<{li.text}> matches with HTR line {htr_match.id}<{htr_match.text}>")
                htr_id = f"{ef.htr_path}#{htr_match.id}"
                gt_id = f"{ef.gt_path}#{li.id}"
                print(f"HTR: {htr_id.ljust(42)} | {htr_match.text}")
                print(f"GT : {gt_id.ljust(42)} | {li.text}")
                print()


if __name__ == '__main__':
    main()
