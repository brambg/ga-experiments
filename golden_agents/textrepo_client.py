import uuid
from datetime import datetime
from http import HTTPStatus

import requests
from dataclasses import dataclass
from dateutil.parser import isoparse
from icecream import ic
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


class TextRepoClient():

    def __init__(self, base_uri: str):
        self.base_uri = base_uri.strip('/')
        self.raise_exception = True

    def __str__(self):
        return (f"TextRepoClient({self.base_uri})")

    def __repr__(self):
        return self.__str__()

    def get_about(self):
        url = f'{self.base_uri}/'
        response = requests.get(url=url)
        return self.__handle_response(response, {HTTPStatus.OK: lambda r: r.json()})

    def read_documents(self,
                       externalId: str = None,
                       createdAfter: datetime = None,
                       limit: int = None,
                       offset: int = None):
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

    def create_document(self, externalId: str):
        url = f'{self.base_uri}/rest/documents'
        response = requests.post(url=url, json={"externalId": externalId})
        return self.__handle_response(response, {HTTPStatus.OK: to_document_identifier})

    def read_document(self, documentIdentifier: DocumentIdentifier):
        url = f'{self.base_uri}/rest/documents/{documentIdentifier.id}'
        response = requests.get(url=url)
        return self.__handle_response(response, {HTTPStatus.OK: to_document_identifier})

    def delete_document(self, documentId: DocumentIdentifier):
        url = f'{self.base_uri}/rest/documents/{documentId.id}'
        response = requests.delete(url=url)
        ic(response)
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
