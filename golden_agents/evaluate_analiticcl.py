#!/bin/env python

from collections import defaultdict
from dataclasses import dataclass

import pagexml.parser as px
from dataclasses_json import dataclass_json
from icecream import ic

import golden_agents.tools as ga


@dataclass_json
@dataclass
class EvaluationFile:
    name: str
    htr_path: str
    gt_path: str


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
        ic(gt_scan.id)
        htr_file = f'../pagexml/{ef.htr_path}'
        htr_scan = px.parse_pagexml_file(htr_file)
        ic(htr_scan.id)


if __name__ == '__main__':
    main()
