import json
import unittest
import uuid
from datetime import datetime, timezone
from io import StringIO

import lxml.etree
from icecream import ic

from golden_agents.corrections import Corrector
from golden_agents.textrepo_client import TextRepoClient

TR = TextRepoClient('http://localhost:8080/textrepo/')


class TextRepoTestCase(unittest.TestCase):

    def test_textrepo_base_url(self):
        tr1 = TextRepoClient('http://localhost:8080/textrepo/')
        self.assertEqual('http://localhost:8080/textrepo', tr1.base_uri)
        tr2 = TextRepoClient('http://localhost:8080/textrepo')
        self.assertEqual('http://localhost:8080/textrepo', tr2.base_uri)

    def test_about(self):
        ic(TR)
        about = TR.get_about()
        ic(about)
        self.assertIsNotNone(about)

    def test_read_documents(self):
        documentsPage = TR.read_documents()
        ic(documentsPage)
        self.assertIsNotNone(documentsPage)
        self.assertEqual(10, documentsPage.page_limit)
        self.assertEqual(0, documentsPage.page_offset)

    def test_read_documents_with_limit_and_offset(self):
        documentsPage = TR.read_documents(limit=100, offset=201)
        ic(documentsPage)
        self.assertIsNotNone(documentsPage)
        self.assertEqual(100, documentsPage.page_limit)
        self.assertEqual(201, documentsPage.page_offset)

    def test_read_documents_with_externalId(self):
        documentsPage = TR.read_documents(external_id='ga:xyz')
        ic(documentsPage)
        self.assertIsNotNone(documentsPage)

    def test_read_documents_created_after(self):
        documentsPage = TR.read_documents(created_after=datetime.today())
        ic(documentsPage)
        self.assertIsNotNone(documentsPage)
        self.assertEqual(0, documentsPage.total)

    def test_file_type_crud(self):
        self.purge_file_types()

        type = TR.create_file_type("httml", "application/text+html")
        ic(type)
        self.assertEqual("httml", type.name)
        self.assertEqual("application/text+html", type.mimetype)

        updated_type = TR.update_file_type(type.id, "html", "text/html")
        self.assertEqual("html", updated_type.name)
        self.assertEqual("text/html", updated_type.mimetype)
        self.assertEqual(type.id, updated_type.id)

        types = TR.read_file_types()
        self.assertEqual(1, len(types))
        self.assertEqual(updated_type, types[0])

        ok = TR.delete_file_type(type.id)
        assert ok

        types = TR.read_file_types()
        self.assertEqual(0, len(types))

    def test_document_crud(self):
        self.purge_all_documents()
        self.purge_file_types()

        external_id = f'ga:annotationId:{uuid.uuid4()}'
        document_id = TR.create_document(external_id)
        ic(document_id)
        self.assertIsNotNone(document_id)

        readId = TR.read_document(document_id)
        ic(readId)
        self.assertEqual(document_id, readId)

        files = TR.read_document_files(document_id)
        ic(files)

        result = TR.set_document_metadata(document_id.id, "field", "value")
        ic(result)

        metadata = TR.read_document_metadata(document_id)
        ic(metadata)
        self.assertEqual({"field": "value"}, metadata)

        xmlType = TR.create_file_type("xml", "text/xml")
        ic(xmlType)

        fileId = TR.create_document_file(document_id, xmlType.id)
        ic(fileId)

        ok = TR.set_file_metadata(fileId, "creator", "ga-ner-tool")
        assert (ok)

        metadata = TR.read_file_metadata(fileId)
        ic(metadata)
        self.assertEqual("ga-ner-tool", metadata["creator"])

        versions = TR.read_file_versions(fileId)
        ic(versions)

        file = StringIO('<xml>the contents of this version<</xml>')
        ic(type(file))
        versionId = TR.create_version(fileId, file)
        ic(versionId)

        ok = TR.delete_file(fileId)
        assert (ok)

        ok = TR.delete_document_metadata(document_id, "field")
        assert (ok)

        ok = TR.delete_file_type(xmlType.id)
        assert (ok)

        docId = TR.update_document_externalId(document_id, "new_external_id")
        ic(docId)
        self.assertEqual("new_external_id", docId.externalId)

        ok = TR.delete_document(readId)
        assert (ok)

    def test_version_import(self):
        external_id = f'ga:annotationId:{uuid.uuid4()}'
        type_name = 'pagexml'
        get_pagexml_type_id(TR)
        contents = StringIO('<xml>Hello, World!</xml>')
        version_info = TR.import_version(external_id=external_id, type_name=type_name, contents=contents,
                                         allow_new_document=True, as_latest_version=True)
        ic(version_info)
        ok = TR.index_type(type_name)
        assert ok

    def test_document_purge(self):
        external_id = f'ga:annotationId:{uuid.uuid4()}'
        document_id = TR.create_document(external_id)
        ic(document_id)
        self.assertIsNotNone(document_id)

        ok = TR.purge_document(external_id)
        assert ok

    def purge_file_types(self):
        if ('localhost' not in TR.base_uri):
            print("no purging on external textrepo's!!")
            exit(-1)
        else:
            for type in TR.read_file_types():
                TR.delete_file_type(type.id)

    def purge_all_documents(self):
        if ('localhost' not in TR.base_uri):
            print("no purging on external textrepo's!!")
            exit(-1)
        else:
            docPage = TR.read_documents()
            for document in docPage.items:
                try:
                    TR.purge_document(document.externalId)
                except Exception:
                    print(f"{TR.base_uri}/rest/documents/{document.id}")


def correct_htr(filename):
    HTR_CORRECTIONS_FILE = '../data/htr_corrections.json'
    with open(HTR_CORRECTIONS_FILE) as f:
        corrections_json = f.read()
    htr_corrector = Corrector(json.loads(corrections_json))
    with open(filename) as f:
        original_xml = f.read()
    doc = lxml.etree.parse(filename).getroot()
    corrections = {}
    for element in doc.xpath("//pagexml:TextRegion/pagexml:TextLine/pagexml:TextEquiv/pagexml:Unicode",
                             namespaces={
                                 'pagexml': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}):
        original = element.text
        if original:
            corrected = htr_corrector.correct(original)
            if (corrected != original):
                corrections[original] = corrected
    corrected_xml = original_xml
    if (len(corrections) > 0):
        original_last_change = doc.xpath("//pagexml:Metadata/pagexml:LastChange", namespaces={
            'pagexml': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0].text
        new_last_change = datetime.now(timezone.utc).astimezone().isoformat(timespec='milliseconds')
        corrections[
            f'<LastChange>{original_last_change}</LastChange>'] = f'<LastChange>{new_last_change}</LastChange>'
        for o, c in corrections.items():
            corrected_xml = corrected_xml.replace(o, c)
    return corrected_xml


def get_pagexml_type_id(textrepo: TextRepoClient) -> int:
    existing_types = textrepo.read_file_types()
    type_id_index = {t.name: t.id for t in existing_types}
    pagexml = 'pagexml'
    if pagexml not in type_id_index.keys():
        type = textrepo.create_file_type(pagexml, 'application/vnd.prima.page+xml')
        return type.id
    else:
        return type_id_index[pagexml]


class CorrectedPageXMLTestCase(unittest.TestCase):
    def test_upload_to_textrepo(self):
        filename = '../../pagexml/2417_NOTD00273/NOTD00273000216.xml'
        parts = filename.split('/')
        archive = parts[-2]
        file = parts[-1]
        file_base = file.removesuffix('xml')
        pageXmlId = get_pagexml_type_id(TR)
        xml = correct_htr(filename)
        ic(xml[0:500])
        version_info = TR.import_version(external_id=f'golden_agents:{archive}:{file_base}', type_name='pagexml',
                                         contents=StringIO(xml), allow_new_document=True, as_latest_version=True)
        # doc = TR.create_document(f'golden_agents:{archive}:{file_base}')
        ok = TR.set_document_metadata(version_info.documentId, 'project', 'Golden Agents')
        ok = TR.set_document_metadata(version_info.documentId, 'archive', archive)
        ok = TR.set_document_metadata(version_info.documentId, 'file', file)
        # file = TR.create_document_file(doc, pageXmlId)
        # version = TR.create_version(file, StringIO(xml))
        # ic(version)


if __name__ == '__main__':
    unittest.main()
