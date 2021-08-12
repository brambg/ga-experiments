#!/usr/bin/env python3

from textrepo.client import TextRepoClient


def main():
    TR = TextRepoClient('http://localhost:8080/textrepo/')
    type1 = TR.create_file_type("xml", "application/xml")
    type2 = TR.create_file_type("txt", "text/plain")
    types = TR.read_file_types()
    print(types)


if __name__ == '__main__':
    main()
