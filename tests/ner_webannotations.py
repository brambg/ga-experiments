import json
import uuid
from datetime import datetime

from analiticcl import VariantModel, Weights, SearchParameters
from pagexml.parser import parse_pagexml_file, PageXMLTextLine

OBJECT_LEXICON = "../data/lexicons/objects.tsv"
LOCATION_LEXICON = "../data/lexicons/locations.tsv"
OCCUPATION_LEXICON = "../data/lexicons/occupations.tsv"
ner_category = {
    OBJECT_LEXICON: "object",
    LOCATION_LEXICON: "location",
    OCCUPATION_LEXICON: "occupation"
}

model = VariantModel("../../analiticcl/examples/simple.alphabet.tsv", Weights(), debug=False)
model.read_lexicon(OBJECT_LEXICON)
model.read_corpus(LOCATION_LEXICON)
model.read_corpus(OCCUPATION_LEXICON)
model.build()

FILE = '../../pagexml/1285_KLAB05520/KLAB05520000004.xml'

scan = parse_pagexml_file(FILE)
if (not scan.id):
    path_parts = FILE.split('/')
    archive_id = path_parts[-2]
    scan_id = path_parts[-1].replace('.xml', '')
    scan.id = f"urn:golden-agents:{archive_id}:scan={scan_id}"


def text_line_urn(archive_id: str, scan_id: str, textline_id: str):
    return f"urn:golden-agents:{archive_id}:scan={scan_id}:textline={textline_id}"


def do_ner_on_line(text_line: PageXMLTextLine, model: VariantModel):
    return model.find_all_matches(text_line.text, SearchParameters(max_edit_distance=3, max_ngram=1))


def create_web_annotation(scan_urn: str, text_line: PageXMLTextLine, ner_result):
    top_variant = ner_result['variants'][0]

    return {
        "@context": "http://www.w3.org/ns/anno.jsonld",
        "id": str(uuid.uuid4()),
        "type": "Annotation",
        "motivation": "classifying",
        "created": datetime.today().isoformat(),
        "generator": {
            "id": "https://github.com/knaw-huc/golden-agents-tool",
            "type": "Software",
            "name": "GoldenAgentsNER"
        },
        "target": {
            "source": f'{scan_urn}:textline={text_line.id}',
            "selector": {
                "type": "TextPositionSelector",
                "start": ner_result['offset']['begin'],
                "end": ner_result['offset']['end']
            }
        },
        "body": [
            {
                "type": "TextualBody",
                "purpose": "classifying",
                "value": ner_category[top_variant['lexicon']]
            },
            {
                "type": "Dataset",
                "value": {
                    "match_phrase": ner_result['input'],
                    "match_variant": top_variant['text'],
                    "match_score": top_variant['score'],
                    "category": ner_category[top_variant['lexicon']]
                }
            }]
    }


for tl in [l for l in scan.get_lines() if l.text]:
    ner_results = do_ner_on_line(tl, model)
    for result in ner_results:
        if len(result['variants']) > 0:
            if (result['variants'][0]['score'] > 0.8):
                print(tl.text)
                print((result['input'], result['variants'][0]))
                wa = create_web_annotation(scan.id, tl, result)
                print(json.dumps(wa, indent=4))
                print()
