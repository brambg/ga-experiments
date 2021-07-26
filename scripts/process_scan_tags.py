#!/usr/bin/env python3

import csv
import json

SCAN_TAGS_CSV = '../golden-agents-htr/experiments/na_scans20210720.csv'
SCAN_TAGS_JSON = 'data/scan_tags.json'


def main():
    print(f"< reading {SCAN_TAGS_CSV}")
    with open(SCAN_TAGS_CSV) as f:
        reader = csv.DictReader(f, )
        data = [row for row in reader]
    print(f"  {len(data)} lines read. ")
    scan_tags = {}
    for i, r in enumerate(data):
        scan_name = r['scanNaam']
        tag = r['eventTypeLabel']
        if scan_name in scan_tags:
            scan_tags[scan_name].append(tag)
        else:
            scan_tags[scan_name] = [tag]

    print(f"> writing {len(scan_tags)} records to {SCAN_TAGS_JSON}")
    with open(SCAN_TAGS_JSON, 'w') as f:
        f.write(json.dumps(scan_tags, indent=4))


if __name__ == '__main__':
    main()
