import random
import time
import unittest
from multiprocessing import Pool

from icecream import ic
from textrepo.client import TextRepoClient

from golden_agents.pagexml_uploader import PageXMLUploader
from golden_agents.tools import all_page_xml_file_paths

TR = TextRepoClient(base_uri='http://localhost:8080/textrepo/', verbose=True)


class PageXMLUploaderTestCase(unittest.TestCase):
    def test_upload_to_textrepo(self):
        uploader = PageXMLUploader(TR, '../../pagexml')
        paths = all_page_xml_file_paths()
        random_path = random.choice(paths)
        upload_info = uploader.upload(random_path)
        ic(upload_info)


class UploadAllPageXMLTestCase(unittest.TestCase):
    def test_upload_all_to_textrepo(self):
        print("purging all documents...")
        startTime = time.time()
        purge_all_documents()
        print(f'  done in {round(time.time() - startTime)} seconds')

        uploader = PageXMLUploader(TR, '../../pagexml')
        paths = all_page_xml_file_paths()
        print(f"uploading {len(paths)} documents...")
        startTime = time.time()
        with Pool(5) as p:
            p.map(uploader.upload, paths)
        # for path in paths:
        #     upload_info = uploader.upload(path)
        print(f'  done in {round(time.time() - startTime)} seconds')

        print("indexing the documents...")
        startTime = time.time()
        TR.index_type('pagexml')
        print(f'  done in {round(time.time() - startTime)} seconds')


class Upload2408PageXMLTestCase(unittest.TestCase):
    def test_upload_some_to_textrepo(self):
        uploader = PageXMLUploader(TR, '../../pagexml')
        paths = [p for p in all_page_xml_file_paths() if '2408' in p]
        print(f"uploading {len(paths)} documents...")
        startTime = time.time()
        with Pool(5) as p:
            p.map(uploader.upload, paths)
        # for path in paths:
        #     upload_info = uploader.upload(path)
        print(f'  done in {round(time.time() - startTime)} seconds')

        print("indexing the documents...")
        startTime = time.time()
        TR.index_type('pagexml')
        print(f'  done in {round(time.time() - startTime)} seconds')


def purge_file_types():
    if 'localhost' not in TR.base_uri:
        print("no purging on external textrepo's!!")
        exit(-1)
    else:
        for type in TR.read_file_types():
            TR.delete_file_type(type.id)


def purge_all_documents():
    if 'localhost' not in TR.base_uri:
        print("no purging on external textrepo's!!")
        exit(-1)
    else:
        docPage = TR.read_documents()
        total = docPage.total
        docPage = TR.read_documents(limit=total)
        with Pool(5) as p:
            p.map(TR.purge_document, [document.externalId for document in docPage.items])

        # for document in docPage.items:
        #     try:
        #         TR.purge_document(document.externalId)
        #     except Exception:
        #         print(f"{TR.base_uri}/rest/documents/{document.id}")


if __name__ == '__main__':
    unittest.main()
