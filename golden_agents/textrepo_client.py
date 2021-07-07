import uuid
from dataclasses import dataclass, field
from datetime import datetime
from http import HTTPStatus
from typing import List

import requests
from dataclasses_json import dataclass_json, config
from dateutil.parser import isoparse
from marshmallow import fields
from requests import Response


@dataclass
class DocumentIdentifier:
    id: uuid
    externalId: str
    createdAt: datetime


@dataclass
class DocumentsPage:
    items: list
    page_limit: int
    page_offset: int
    total: int


@dataclass
class FileIdentifier:
    id: uuid
    docId: uuid
    typeId: int
    url: str


@dataclass_json
@dataclass
class VersionIdentifier:
    id: uuid
    fileId: uuid
    createdAt: datetime = field(
        metadata=config(
            encoder=datetime.isoformat,
            decoder=datetime.fromisoformat,
            mm_field=fields.DateTime(format='iso')
        ))
    contentsSha: str


@dataclass_json
@dataclass
class FileType:
    id: int
    name: str
    mimetype: str


class TextRepoClient():

    def __init__(self, base_uri: str):
        self.base_uri = base_uri.strip('/')
        self.raise_exception = True

    def __str__(self):
        return (f"TextRepoClient({self.base_uri})")

    def __repr__(self):
        return self.__str__()

    def get_about(self) -> dict:
        url = f'{self.base_uri}/'
        response = requests.get(url=url)
        return self.__handle_response(response, {HTTPStatus.OK: lambda r: r.json()})

    def read_documents(self,
                       externalId: str = None,
                       createdAfter: datetime = None,
                       limit: int = None,
                       offset: int = None
                       ) -> DocumentsPage:
        url = f'{self.base_uri}/rest/documents'
        params = {}
        if (externalId):
            params['externalId'] = externalId
        if (createdAfter):
            params['createdAfter'] = createdAfter.isoformat(timespec='seconds')
        if (limit):
            params['limit'] = limit
        if (offset):
            params['offset'] = offset
        response = requests.get(url=url, params=params)
        return self.__handle_response(response, {HTTPStatus.OK: to_documents_page})

    def create_document(self, externalId: str) -> DocumentIdentifier:
        url = f'{self.base_uri}/rest/documents'
        response = requests.post(url=url, json={"externalId": externalId})
        return self.__handle_response(response, {HTTPStatus.CREATED: to_document_identifier})

    def update_document_externalId(self, documentId: DocumentIdentifier, externalId: str) -> DocumentIdentifier:
        url = f'{self.base_uri}/rest/documents/{documentId.id}'
        response = requests.put(url=url, json={"externalId": externalId})
        return self.__handle_response(response, {HTTPStatus.OK: to_document_identifier})

    def read_document(self, documentIdentifier: DocumentIdentifier) -> DocumentIdentifier:
        """Retrieve document"""
        url = f'{self.base_uri}/rest/documents/{documentIdentifier.id}'
        response = requests.get(url=url)
        return self.__handle_response(response, {HTTPStatus.OK: to_document_identifier})

    def delete_document(self, documentId: DocumentIdentifier) -> bool:
        """Delete document"""
        url = f'{self.base_uri}/rest/documents/{documentId.id}'
        response = requests.delete(url=url)
        return self.__handle_response(response, {HTTPStatus.OK: lambda r: True})

    def purge_document(self, externalId: str) -> bool:
        """
        Delete a document including its metadata, files, versions and contents. Contents are only deleted when not referenced by any other versions.

        :param externalId: the external Id
        :type externalId: str
        :return: whether the purge succeeded
        :rtype: bool
        """
        url = f'{self.base_uri}/task/delete/documents/{externalId}'
        response = requests.delete(url=url)
        return self.__handle_response(response, {HTTPStatus.OK: lambda r: True})

    def set_document_metadata(self, documentIdentifier: DocumentIdentifier, key: str, value: str) -> dict:
        url = f'{self.base_uri}/rest/documents/{documentIdentifier.id}/metadata/{key}'
        response = requests.put(url=url, data=value)
        return self.__handle_response(response, {HTTPStatus.OK: lambda r: r.json()})

    def read_document_metadata(self, documentIdentifier: DocumentIdentifier) -> dict:
        url = f'{self.base_uri}/rest/documents/{documentIdentifier.id}/metadata'
        response = requests.get(url=url)
        return self.__handle_response(response, {HTTPStatus.OK: lambda r: r.json()})

    def delete_document_metadata(self, documentIdentifier: DocumentIdentifier, key: str) -> bool:
        url = f'{self.base_uri}/rest/documents/{documentIdentifier.id}/metadata/{key}'
        response = requests.delete(url=url)
        return self.__handle_response(response, {HTTPStatus.OK: lambda r: True})

    def create_document_file(self, documentIdentifier: DocumentIdentifier, typeId: int) -> FileIdentifier:
        url = f'{self.base_uri}/rest/files'
        response = requests.post(url=url, json={'docId': documentIdentifier.id, 'typeId': typeId})
        return self.__handle_response(response, {HTTPStatus.CREATED: to_file_identifier})

    def read_file(self, fileIdentifier: FileIdentifier) -> FileIdentifier:
        url = f'{self.base_uri}/rest/files/{fileIdentifier.id}'
        response = requests.get(url=url)
        return self.__handle_response(response, {HTTPStatus.OK: to_file_identifier})

    def update_document_file(self, documentIdentifier: DocumentIdentifier, typeId: int) -> FileIdentifier:
        url = f'{self.base_uri}/rest/files'
        response = requests.put(url=url, data={'docId': documentIdentifier.id, 'typeId': typeId})
        return self.__handle_response(response, {HTTPStatus.OK: to_file_identifier})

    def delete_file(self, fileIdentifier: FileIdentifier) -> bool:
        url = f'{self.base_uri}/rest/files/{fileIdentifier.id}'
        response = requests.delete(url=url)
        return self.__handle_response(response, {HTTPStatus.OK: lambda r: True})

    def read_document_files(self, documentIdentifier: DocumentIdentifier, limit: int = None,
                            offset: int = None) -> dict:
        url = f'{self.base_uri}/rest/documents/{documentIdentifier.id}/files'
        params = {}
        if (limit):
            params['limit'] = limit
        if (offset):
            params['offset'] = offset
        response = requests.get(url=url, params=params)
        return self.__handle_response(response, {HTTPStatus.OK: lambda r: r.json()})

    def read_file_metadata(self, fileIdentifier: FileIdentifier) -> dict:
        url = f'{self.base_uri}/rest/files/{fileIdentifier.id}/metadata'
        response = requests.get(url=url)
        return self.__handle_response(response, {HTTPStatus.OK: lambda r: r.json()})

    def set_file_metadata(self, fileIdentifier: FileIdentifier, key: str, value: str) -> bool:
        """Create or update file metadata entry"""
        url = f'{self.base_uri}/rest/files/{fileIdentifier.id}/metadata/{key}'
        response = requests.put(url=url, data=value)
        return self.__handle_response(response, {HTTPStatus.OK: lambda r: True})

    def delete_file_metadata(self, fileIdentifier: FileIdentifier, key: str) -> bool:
        """Delete file metadata entry"""
        url = f'{self.base_uri}/rest/files/{fileIdentifier.id}/metadata/{key}'
        response = requests.delete(url=url)
        return self.__handle_response(response, {HTTPStatus.OK: lambda r: True})

    def read_file_versions(self,
                           fileIdentifier: FileIdentifier,
                           limit: int = None,
                           offset: int = None,
                           createdAfter: datetime = None
                           ) -> List[FileIdentifier]:
        url = f'{self.base_uri}/rest/files/{fileIdentifier.id}/versions'
        params = {}
        if (createdAfter):
            params['createdAfter'] = createdAfter.isoformat(timespec='seconds')
        if (limit):
            params['limit'] = limit
        if (offset):
            params['offset'] = offset
        response = requests.get(url=url, params=params)
        return self.__handle_response(response,
                                      {HTTPStatus.OK: lambda r: [VersionIdentifier.from_dict(d) for d in
                                                                 r.json()["items"]]})

    def create_version(self, fileIdentifier: FileIdentifier, file) -> VersionIdentifier:
        url = f'{self.base_uri}/rest/versions'
        files = {'contents': file}
        data = {'fileId': fileIdentifier.id}
        response = requests.post(url=url, files=files, data=data)
        return self.__handle_response(response, {HTTPStatus.CREATED: to_version_identifier})

    def read_file_types(self) -> List[FileType]:
        url = f'{self.base_uri}/rest/types'
        response = requests.get(url=url)
        return self.__handle_response(response, {HTTPStatus.OK: lambda r: [FileType.from_dict(d) for d in r.json()]})

    def create_file_type(self, name: str, mimetype: str) -> FileType:
        url = f'{self.base_uri}/rest/types'
        response = requests.post(url=url, json={"name": name, "mimetype": mimetype})
        return self.__handle_response(response, {HTTPStatus.CREATED: to_file_type})

    def read_file_type(self, id: int) -> FileType:
        url = f'{self.base_uri}/rest/types/{id}'
        response = requests.get(url=url)
        return self.__handle_response(response, {HTTPStatus.OK: to_file_type})

    def update_file_type(self, id: int, name: str, mimetype: str) -> FileType:
        url = f'{self.base_uri}/rest/types/{id}'
        response = requests.put(url=url, json={"name": name, "mimetype": mimetype})
        return self.__handle_response(response, {HTTPStatus.OK: to_file_type})

    def delete_file_type(self, id: int):
        url = f'{self.base_uri}/rest/types/{id}'
        response = requests.delete(url=url)
        return self.__handle_response(response, {HTTPStatus.OK: lambda r: True})

    def __handle_response(self, response: Response, result_producers: dict):
        if (response.status_code in result_producers.keys()):
            result = result_producers[response.status_code](response)
            # if (self.raise_exceptions):
            return result
        # else:
        #     return Success(response, result)
        else:
            # if (self.raise_exceptions):
            raise Exception(
                f'{response.request.method} {response.request.url} returned {response.status_code} : {response.text}')


# else:
#     return Failure(response)

def to_document_identifier(response: Response) -> DocumentIdentifier:
    json = response.json()
    return DocumentIdentifier(id=json['id'],
                              externalId=json['externalId'],
                              createdAt=isoparse(json['createdAt']))


def to_file_identifier(response: Response) -> FileIdentifier:
    json = response.json()
    return FileIdentifier(id=json['id'],
                          docId=json['docId'],
                          typeId=json['typeId'],
                          url=response.headers['location'])


def to_version_identifier(response: Response) -> VersionIdentifier:
    return VersionIdentifier.from_dict(response.json())


def to_documents_page(response: Response) -> DocumentsPage:
    json = response.json()
    items = [DocumentIdentifier(id=j['id'],
                                externalId=j['externalId'],
                                createdAt=isoparse(j['createdAt']))
             for j in json['items']]
    return DocumentsPage(items=items,
                         page_limit=json['page']['limit'],
                         page_offset=json['page']['offset'],
                         total=json['total'])


def to_file_type(response: Response) -> FileType:
    return FileType.from_dict(response.json())
