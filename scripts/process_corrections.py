#!/bin/env python
import csv
import json

HTR_CORRECTIONS_TSV = '../golden-agents-htr/experiments/htr_verbeterd_1.tsv'
HTR_CORRECTIONS_JSON = 'data/htr_corrections.json'


def main():
    print(f"< reading {HTR_CORRECTIONS_TSV}")
    with open(HTR_CORRECTIONS_TSV) as f:
        reader = csv.reader(f, delimiter='\t')
        data = [tuple(row) for row in reader]
    print(f"  {len(data)} lines read. ")
    corrections = {}
    for i, t in enumerate(data):
        if len(t) != 3:
            original_line = "\t".join(t)
            print(
                f'{HTR_CORRECTIONS_TSV}:{i} : unexpected input ({len(t)} fields instead of the expected 3) : {original_line}')
        else:
            if t[0] in corrections:
                print(f'{HTR_CORRECTIONS_TSV}:{i} : duplicate term {t[0]}')
            else:
                corrections[t[0]] = t[2].replace('’', "'")

    print(f"> writing {len(corrections)} records to {HTR_CORRECTIONS_JSON}")
    with open(HTR_CORRECTIONS_JSON, 'w') as f:
        f.write(json.dumps(corrections, indent=4))


if __name__ == '__main__':
    main()
