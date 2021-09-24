#!/usr/bin/env python3
import argparse
import json

import yaml


def main():
    parser = argparse.ArgumentParser(
        description="Convert a json file to yaml.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("jsonfile",
                        help="The json file to convert",
                        type=str)
    args = parser.parse_args()

    with open(args.jsonfile, "r", encoding='utf-8') as f:
        obj = json.load(f)
    print(yaml.dump(obj, encoding='utf-8').decode(encoding='utf-8'))


if __name__ == '__main__':
    main()
