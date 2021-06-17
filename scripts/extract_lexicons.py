#!/bin/env python
import csv

THESAURI_DIR = '../golden-agents-thesauri/'
LOCATIONS_FILE = THESAURI_DIR + 'locations/observations.csv'
OCCUPATIONS_FILE = THESAURI_DIR + 'occupations/observations.csv'
RELATIONS_FILE = THESAURI_DIR + 'relations/observations.csv'
LOCATIONS_LEXICON_FILE = 'data/lexicons/locations.tsv'
OCCUPATIONS_LEXICON_FILE = 'data/lexicons/occupations.tsv'
RELATIONS_LEXICON_FILE = 'data/lexicons/relations.tsv'


def extract_lexicon_from_thesaurus(thesaurus_file: str, lexicon_file: str):
    print(f"< reading from {thesaurus_file} ...")
    with open(thesaurus_file) as f:
        reader = csv.DictReader(f)
        data = [row for row in reader if row]
    print(f'  {len(data)} records read')
    lexicon_items = sorted(list({d['label'] for d in data if len(d['label']) > 0}))
    print(f"> writing {len(lexicon_items)} unique lexicon terms to {lexicon_file}")
    with open(lexicon_file, 'w') as tsv:
        writer = csv.writer(tsv, delimiter='\t')
        for item in lexicon_items:
            writer.writerow([item])


extract_lexicon_from_thesaurus(LOCATIONS_FILE, LOCATIONS_LEXICON_FILE)
extract_lexicon_from_thesaurus(OCCUPATIONS_FILE, OCCUPATIONS_LEXICON_FILE)
extract_lexicon_from_thesaurus(RELATIONS_FILE, RELATIONS_LEXICON_FILE)
