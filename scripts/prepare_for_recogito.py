#!/usr/bin/env python3

import argparse
import json
import re
from dataclasses import dataclass

import pagexml.parser as px
from dataclasses_json import dataclass_json

import golden_agents.tools as ga


@dataclass_json
@dataclass
class LineInfo:
    text: str
    page_id: str
    line_id: str
    offset: int


def main1():
    parser = argparse.ArgumentParser(description="Extract text contents from Page XML",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("files", nargs='*', help="Files")
    args = parser.parse_args()
    bar = ga.default_progress_bar(len(args.files))
    for i, filename in enumerate(args.files):
        bar.update(i + 1)
        basename = filename.split('/')[-1].replace('.xml', '')
        scan = px.parse_pagexml_file(filename)
        text_file = f"out/{basename}.txt"
        metadata_file = f"out/{basename}.json"
        line_infos = []
        lines = []
        offset = 0
        for l in scan.get_lines():
            if l.text:
                lines.append(l.text)
                li = LineInfo(line_id=l.id, text=l.text, offset=offset, page_id=basename)
                line_infos.append(li)
                offset += len(l.text) + 1
        if lines:
            with open(text_file, 'w') as f:
                f.write("\n".join(lines))
            with open(metadata_file, 'w', encoding='utf8') as f:
                json.dump([li.to_dict() for li in line_infos], f, indent=4)
    print()


def main2():
    parser = argparse.ArgumentParser(description="Extract text contents from all Page XML in a directory",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("directories", nargs='*', help="Directories")
    args = parser.parse_args()
    bar1 = ga.default_progress_bar(len(args.directories))
    r = re.compile('.*/([^/]+)/?$')
    for i, directory in enumerate(args.directories):
        bar1.update(i + 1)
        basename = r.match(directory).group(1)
        scan_paths = ga.scan_paths(directory)
        text_file = f"out/{basename}.txt"
        metadata_file = f"out/{basename}.json"
        line_infos = []
        lines = []
        offset = 0
        bar2 = ga.default_progress_bar(len(scan_paths))
        for j, filename in enumerate(scan_paths):
            bar2.update(j)
            page_basename = filename.split('/')[-1].replace('.xml', '')
            scan = px.parse_pagexml_file(filename)
            for l in scan.get_lines():
                if l.text:
                    lines.append(l.text)
                    li = LineInfo(line_id=l.id, text=l.text, offset=offset, page_id=page_basename)
                    line_infos.append(li)
                    offset += len(l.text) + 1
        if lines:
            with open(text_file, 'w') as f:
                f.write("\n".join(lines))
            with open(metadata_file, 'w', encoding='utf8') as f:
                json.dump([li.to_dict() for li in line_infos], f, indent=4)
    print()


if __name__ == '__main__':
    main1()
    # main2()
