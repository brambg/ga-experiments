import unittest

from elucidate.client import ElucidateClient, split_annotation
from icecream import ic
from pagexml.parser import parse_pagexml_file

from golden_agents.ner import NER


def create_scan_id(file) -> str:
    path_parts = file.split('/')
    archive_id = path_parts[-2]
    scan_id = path_parts[-1].replace('.xml', '')
    return f"urn:golden-agents:{archive_id}:scan={scan_id}"


class NERAnnotatorCase(unittest.TestCase):
    def test_annotator(self):
        file = '../pagexml/2408_A16098/a16098000013.xml'
        scan = parse_pagexml_file(file)
        if not scan.id:
            scan.id = create_scan_id(file)
        scan.transkribus_uri = "https://files.transkribus.eu/iiif/2/MOQMINPXXPUTISCRFIRKIOIX/full/max/0/default.jpg"
        ner = NER()
        annotations = ner.create_web_annnotations(scan, "http://localhost:8080/textrepo/versions/x")
        self.assertIsNotNone(annotations)
        ec = ElucidateClient("http://localhost:18080/annotation", verbose=True)
        container_id = ec.create_container('Golden Agents NER annotations')
        ic(container_id)
        for a in annotations:
            (body, target, custom) = split_annotation(a)
            annotation_id = ec.create_annotation(container_id=container_id, body=body, target=target, custom=custom)
            ic(annotation_id)


if __name__ == '__main__':
    unittest.main()
