#!/usr/bin/env python3

import argparse
import json
from datetime import datetime

import lxml.etree

from golden_agents.corrections import Corrector

parser = argparse.ArgumentParser(description="Correct text contents from Page XML",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("files", nargs='*', help="Files")
args = parser.parse_args()

HTR_CORRECTIONS_FILE = 'data/htr_corrections.json'

with open(HTR_CORRECTIONS_FILE) as f:
    corrections_json = f.read()
htr_corrector = Corrector(json.loads(corrections_json))

for filename in args.files:
    print(f"< reading {filename}")
    with open(filename) as f:
        original_xml = f.read()
    doc = lxml.etree.parse(filename).getroot()

    corrections = {}
    for element in doc.xpath("//pagexml:TextRegion/pagexml:TextLine/pagexml:TextEquiv/pagexml:Unicode",
                             namespaces={'pagexml': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}):
        original = element.text
        if original:
            corrected = htr_corrector.correct(original)
            if corrected != original:
                corrections[original] = corrected
                print(f'original:  {original}')
                print(f'corrected: {corrected}')
                print()
    if corrections:
        corrected_xml = original_xml
        original_last_change = doc.xpath("//pagexml:Metadata/pagexml:LastChange", namespaces={
            'pagexml': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0].text
        new_last_change = datetime.today().isoformat()
        corrections[f'<LastChange>{original_last_change}</LastChange>'] = f'<LastChange>{new_last_change}</LastChange>'
        for o, c in corrections.items():
            corrected_xml = corrected_xml.replace(o, c)
        corrected_filename = filename.replace('.xml', '.corrected.xml')
        print(f"> writing corrections to {corrected_filename}")
        with (open(corrected_filename, 'w')) as f:
            f.write(corrected_xml)
    print()