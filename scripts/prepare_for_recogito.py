#!/usr/bin/env python3

import argparse
import json
from dataclasses import dataclass

import pagexml.parser as px
from dataclasses_json import dataclass_json

import golden_agents.tools as ga


@dataclass_json
@dataclass
class LineInfo:
    text: str
    id: str
    offset: int


def main():
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
                li = LineInfo(id=l.id, text=l.text, offset=offset)
                line_infos.append(li)
                offset += len(l.text) + 1
        if len(lines) > 0:
            with open(text_file, 'w') as f:
                f.write("\n".join(lines))
            with open(metadata_file, 'w', encoding='utf8') as f:
                json.dump([li.to_dict() for li in line_infos], f, indent=4)
    print()


if __name__ == '__main__':
    main()
