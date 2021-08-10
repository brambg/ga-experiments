import json
from datetime import datetime, timezone
from io import StringIO
from typing import Dict

import lxml.etree

from golden_agents.corrections import Corrector
from golden_agents.textrepo_client import TextRepoClient
from golden_agents.tools import read_werkvoorraad, read_scan_tags


class PageXMLUploader:
    def __init__(self, text_repo_client: TextRepoClient, pagexml_base_path: str):
        # scandata = read_scan_data()
        werkvoorraad = read_werkvoorraad()
        self.scan_tags = read_scan_tags()
        self.wv_idx = {wv.title: wv for wv in werkvoorraad}
        self.tr = text_repo_client
        self.pagexml_base_path = pagexml_base_path
        get_pagexml_type_id(text_repo_client)
        HTR_CORRECTIONS_FILE = '../data/htr_corrections.json'
        with open(HTR_CORRECTIONS_FILE) as f:
            corrections_json = f.read()
        self.htr_corrector = Corrector(json.loads(corrections_json))

    def upload(self, file_path: str) -> Dict[str, str]:
        filename = f'{self.pagexml_base_path}/{file_path}'
        parts = filename.split('/')
        archive = parts[-2]
        file = parts[-1]
        scan_name = file.removesuffix('.xml')
        tr = self.tr
        (corrected, xml) = correct_htr(self.htr_corrector, filename)
        type_name = 'pagexml'
        external_id = f'golden_agents:{archive}:{scan_name}'
        version_info = tr.import_version(external_id=external_id, type_name=type_name,
                                         contents=StringIO(xml), allow_new_document=True, as_latest_version=True)
        document_id = version_info.documentId
        file_id = version_info.fileId
        version_id = version_info.versionId
        ok = tr.set_document_metadata(document_id, 'project', 'Golden Agents')
        ok = tr.set_document_metadata(document_id, 'archive', archive)
        ok = tr.set_document_metadata(document_id, 'file', file)
        archive_data = self.wv_idx.get(archive)
        if archive_data:
            ok = tr.set_document_metadata(document_id, 'writer', archive_data.writer)
            ok = tr.set_document_metadata(document_id, 'status', archive_data.status)
        ok = tr.set_file_metadata(file_id, 'filename', file)
        ok = tr.set_version_metadata(version_id, 'corrected', str(corrected))
        tags = self.scan_tags.get(scan_name)
        if tags:
            for tag in tags:
                ok = tr.set_document_metadata(document_id, f'tag_{tag}', 'True')
        base_uri = tr.base_uri
        upload_info = {
            'external_id': external_id,
            'document': f'{base_uri}/rest/documents/{document_id}',
            'document_metadata': f'{base_uri}/rest/documents/{document_id}/metadata',
            'document_files': f'{base_uri}/rest/documents/{document_id}/files',
            'file': f'{base_uri}/rest/files/{file_id}',
            'file_metadata': f'{base_uri}/rest/files/{file_id}/metadata',
            'file_versions': f'{base_uri}/rest/files/{file_id}/versions',
            'version': f'{base_uri}/rest/versions/{version_id}',
            'version_metadata': f'{base_uri}/rest/versions/{version_id}/metadata',
            'version_contents': f'{base_uri}/rest/versions/{version_id}/contents'
        }
        return upload_info


def get_pagexml_type_id(textrepo: TextRepoClient) -> int:
    existing_types = textrepo.read_file_types()
    type_id_index = {t.name: t.id for t in existing_types}
    pagexml = 'pagexml'
    if pagexml not in type_id_index.keys():
        type = textrepo.create_file_type(pagexml, 'application/vnd.prima.page+xml')
        return type.id
    else:
        return type_id_index[pagexml]


def correct_htr(htr_corrector: Corrector, filename: str):
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
            if corrected != original:
                corrections[original] = corrected
    corrected_xml = original_xml
    is_corrected = False
    if len(corrections) > 0:
        is_corrected = True
        original_last_change = doc.xpath("//pagexml:Metadata/pagexml:LastChange", namespaces={
            'pagexml': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})[0].text
        new_last_change = datetime.now(timezone.utc).astimezone().isoformat(timespec='milliseconds')
        corrections[f'<LastChange>{original_last_change}</LastChange>'] = f'<LastChange>{new_last_change}</LastChange>'
        for o, c in corrections.items():
            corrected_xml = corrected_xml.replace(o, c)
    return is_corrected, corrected_xml
