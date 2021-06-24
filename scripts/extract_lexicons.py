#!/usr/bin/env python3

import csv

THESAURI_DIR = '../golden-agents-thesauri/'
LOCATIONS_FILE = THESAURI_DIR + 'locations/observations.csv'
OCCUPATIONS_FILE = THESAURI_DIR + 'occupations/observations.csv'
RELATIONS_FILE = THESAURI_DIR + 'relations/observations.csv'
OBJECTS_FILE = '../golden-agents-htr/resources/objects.csv'
LOCATIONS_LEXICON_FILE = 'data/lexicons/locations.tsv'
OCCUPATIONS_LEXICON_FILE = 'data/lexicons/occupations.tsv'
RELATIONS_LEXICON_FILE = 'data/lexicons/relations.tsv'
OBJECTS_LEXICON_FILE = 'data/lexicons/objects.tsv'


def extract_lexicon_from_csv(thesaurus_file: str, lexicon_file: str, column: str):
    print(f"< reading from {thesaurus_file} ...")
    with open(thesaurus_file) as f:
        reader = csv.DictReader(f)
        data = [row for row in reader if row]
    print(f'  {len(data)} records read')
    lexicon_items = sorted(list({d[column] for d in data if len(d[column]) > 0}),key=str.casefold)
    print(f"> writing {len(lexicon_items)} unique lexicon terms to {lexicon_file}")
    with open(lexicon_file, 'w') as tsv:
        writer = csv.writer(tsv, delimiter='\t')
        for item in [li for li in lexicon_items if li.count(' ')<3]: # since analiticcl only accepts lexicon terms of up to 3 words
            writer.writerow([item])


def extract_lexicon_from_thesaurus(thesaurus_file: str, lexicon_file: str):
    extract_lexicon_from_csv(thesaurus_file, lexicon_file, 'label')


def extract_objects():
    extract_lexicon_from_csv(OBJECTS_FILE, OBJECTS_LEXICON_FILE, 'object')


extract_lexicon_from_thesaurus(LOCATIONS_FILE, LOCATIONS_LEXICON_FILE)
extract_lexicon_from_thesaurus(OCCUPATIONS_FILE, OCCUPATIONS_LEXICON_FILE)
extract_lexicon_from_thesaurus(RELATIONS_FILE, RELATIONS_LEXICON_FILE)
extract_objects()