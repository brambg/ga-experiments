#!/usr/bin/env python3
import argparse
import json

import yaml


def main():
    parser = argparse.ArgumentParser(
        description="Convert a yaml file to json.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("yamlfile",
                        help="The yaml file to convert",
                        type=str)
    args = parser.parse_args()

    with open(args.yamlfile, "r", encoding='utf-8') as f:
        obj = yaml.safe_load(f)
    print(json.dumps(obj, indent=4))


if __name__ == '__main__':
    main()
