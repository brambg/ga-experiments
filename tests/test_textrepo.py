import unittest
from datetime import datetime

from icecream import ic

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
        documentsPage = TR.read_documents(externalId='ga:xyz')
        ic(documentsPage)
        self.assertIsNotNone(documentsPage)

    def test_read_documents_createdAfter(self):
        documentsPage = TR.read_documents(createdAfter=datetime.today())
        ic(documentsPage)
        self.assertIsNotNone(documentsPage)
        self.assertEqual(0, documentsPage.total)

    def test_create_document(self):
        externalId = 'ga:annotationId:pageId2'
        documentId = TR.create_document(externalId)
        ic(documentId)
        self.assertIsNotNone(documentId)

        readId = TR.read_document(documentId)
        ic(readId)
        success = TR.delete_document(readId)
        ic(success)


if __name__ == '__main__':
    unittest.main()
