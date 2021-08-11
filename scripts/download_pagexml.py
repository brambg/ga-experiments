#!/usr/bin/env python3

import csv
import difflib
import json
import os
import re
import time
from os.path import exists

import requests

ARCHIVE_INFO_CSV = "data/HTR aanvulling 202108.csv"
PAGE_INFO_JSON = "data/page_info.json"
PAGEXML_BASE_DIR = "out/pagexml"
DOWNLOADED_ARCHIVES_JSON = "out/downloaded_archives.json"


def read_document_page_info(document_id: str, number_of_scans: int):
    url = f"https://transkribus.eu/r/search-read/documents/{document_id}/pages"
    headers = {"Content-Type": "application/json"}
    body = {"offset": 0, "limit": number_of_scans}
    result = requests.post(url=url, headers=headers, json=body)
    if result.ok:
        return result.json()['items']
    else:
        print(result.status_code)
        print(result.content)


def download_pagexml(url: str, destination_dir: str):
    r = requests.get(url=url)
    if r.ok:
        d = r.headers['content-disposition']
        fname = re.findall('filename="(.+)"', d)[0]
        path = f"{destination_dir}/{fname}"
        with open(path, 'wb') as f:
            f.write(r.content)
        return path
    else:
        print(r.status_code)
        print(r.content)


def sanitize_titles(items, new_htr_archives):
    new_htr_titles = set([a['TITLE'] for a in new_htr_archives])
    transkribus_titles = set([t['title'] for t in items])
    unmatched_aanvulling_titles = new_htr_titles - transkribus_titles
    if len(unmatched_aanvulling_titles) > 0:
        print(
            f"! {len(unmatched_aanvulling_titles)} mismatched found in document titles, using closest match from {ARCHIVE_INFO_CSV}")
        unmatched_transkribus_titles = transkribus_titles - new_htr_titles
        transkribus_title_fixes = {}
        for at in unmatched_aanvulling_titles:
            tt = difflib.get_close_matches(at, unmatched_transkribus_titles, n=1)[0]
            transkribus_title_fixes[tt] = at
        corrected_items = []
        for i in items:
            transkribus_archive_title = i['title']
            if transkribus_archive_title in transkribus_title_fixes:
                fixed_title = transkribus_title_fixes[transkribus_archive_title]
                print(f"    replacing transkribus document title '{transkribus_archive_title}' with '{fixed_title}'")
                i['title'] = fixed_title
            corrected_items.append(i)
        items = corrected_items
    return items


def main():
    print("> downloading relevant document info:")
    url = "https://transkribus.eu/r/search-read/documents"
    print(f"> GET {url}")
    headers = {"Content-Type": "application/json"}
    body = {"collections": [85448], "offset": 0, "limit": 1024}
    result = requests.post(url=url, headers=headers, json=body).json()
    items = result['items']
    print(f"< {len(items)} documents found")

    print(f"> reading {ARCHIVE_INFO_CSV}: ", end='')
    with open(ARCHIVE_INFO_CSV) as f:
        reader = csv.DictReader(f)
        new_htr_archives = [l for l in reader]
    number_of_new_htr_archives = len(new_htr_archives)
    print(f"{number_of_new_htr_archives} newly htr-ed archives")

    items = sanitize_titles(items, new_htr_archives)

    title2id = {item['title']: item['id'] for item in items}

    downloaded_archives = []
    if exists(DOWNLOADED_ARCHIVES_JSON):
        with open(DOWNLOADED_ARCHIVES_JSON) as f:
            downloaded_archives = json.load(f)

    print(f"> processing archives:")
    pages_data = []
    for (i, a) in enumerate(new_htr_archives):
        title = a['TITLE']
        xml_dir = f"{PAGEXML_BASE_DIR}/{title}"
        os.makedirs(xml_dir, exist_ok=True)
        print(f"    archive {title} ({i + 1}/{number_of_new_htr_archives}): ", end='')
        if title in downloaded_archives:
            print("already downloaded")
        else:
            pages_info = read_document_page_info(title2id[title], a['AANTAL SCANS'])
            total_pages = len(pages_info)
            print(f"{total_pages} pages")
            for page_info in pages_info:
                scan_number = page_info['number']
                print(f">       downloading page {scan_number}/{total_pages}:", end='')
                iiif_url = page_info['previewImage']
                xml_url = page_info['xmlKey']

                file_path = download_pagexml(xml_url, xml_dir)
                print(f" {file_path}", end='\r')

                pages_data.append({
                    "archive_title": title,
                    "scan_number": scan_number,
                    "file_path": file_path,
                    "iiif_url": iiif_url,
                })
                time.sleep(1)
            print()
            downloaded_archives.append(title)
            with open(DOWNLOADED_ARCHIVES_JSON, 'w') as f:
                json.dump(downloaded_archives, f)

    print(f"> writing {PAGE_INFO_JSON}")
    with open(PAGE_INFO_JSON, 'w') as f:
        json.dump(pages_data, fp=f)
    print("done!")


if __name__ == '__main__':
    main()
