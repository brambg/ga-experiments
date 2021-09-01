from collections import Counter, defaultdict

from elasticsearch import Elasticsearch
from icecream import ic

import golden_agents.tools as ga

es_host = "https://es_goldenagents.tt.di.huc.knaw.nl"
archive_idx = 'archives'
scan_idx = 'scans'


def main():
    es = Elasticsearch(hosts=es_host, http_compress=True)
    # delete_indexes(es)
    index_archives(es)
    index_scans(es)


def delete_indexes(es):
    es.indices.delete(index=archive_idx)
    es.indices.delete(index=scan_idx)


def index_archives(es):
    sd = ga.read_scan_data()
    idx = {d.title: d.id for d in sd}
    werkvoorraad = ga.read_werkvoorraad()
    sanity_check(werkvoorraad)
    print(f"- uploading to {es_host}/{archive_idx}:")
    bar = ga.default_progress_bar(len(werkvoorraad))
    unmatched_titles = set()
    for i, a in enumerate(werkvoorraad):
        bar.update(i)
        id = a.title
        data = a.__dict__
        if id in idx:
            data['archive_id'] = idx[id]
        else:
            unmatched_titles.add(id)
        r = es.index(index=archive_idx, id=id, body=data)
    es.indices.refresh(index=archive_idx)
    ic(unmatched_titles)


def index_scans(es):
    sd = ga.read_scan_data()
    idx = {d.title: d.id for d in sd}
    paths = ga.all_page_xml_file_paths()
    scan_tags = ga.read_scan_tags()
    filenames = defaultdict(list)
    for p in paths:
        (a, s) = p.split('/')
        filenames[a].append(s)
    titles_without_directories = set()
    titles_with_insufficient_files = set()
    max_value = len(sd)
    print(f"- uploading to {es_host}/{scan_idx}:")
    bar = ga.default_progress_bar(max_value)
    for i, d in enumerate(sd):
        bar.update(i)
        if d.title not in filenames:
            # print(f"no files found for {d.title}")
            titles_without_directories.add(d.title)
        else:
            n = int(d.number)
            fn = filenames[d.title]
            if len(fn) < n:
                # print(f"{d.title} has just {len(fn)} files, number {n} not found")
                titles_with_insufficient_files.add(d.title)
            else:
                filename = fn[n - 1]
                id = filename.replace('.xml', '').upper()
                archive_id = idx[d.title]
                data = {
                    "archive_title": d.title,
                    "n": n,
                    "iiif_base_url": d.previewImage.replace('/full/128,/0/default.jpg', ''),
                    "transkribus_url": ga.transkribus_url(archive_id=archive_id, page_index=n),
                    "filename": filename
                }
                if id in scan_tags:
                    data["tags"] = scan_tags[id]
                r = es.index(index=scan_idx, id=id, body=data)
    print()
    ic(titles_without_directories)
    ic(titles_with_insufficient_files)
    es.indices.refresh(index=scan_idx)



def sanity_check(werkvoorraad):
    ids = [a.title for a in werkvoorraad]
    c = Counter(ids)
    ic(c.most_common(10))
    dup = [a for a in werkvoorraad if a.title == '12788_NOTI01181']
    ic(dup)


if __name__ == '__main__':
    main()
