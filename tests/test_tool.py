import json
import os
import random
import unittest

from icecream import ic

from golden_agents.tools import read_werkvoorraad, extract_writer_index, extract_archive_index, DATA_DIR, scan_paths, \
    transkribus_url, read_scan_data, get_xml_paths, all_page_xml_file_paths, read_scan_tags


def write_tag_page():
    pass


class ToolTestCase1(unittest.TestCase):
    def test_writers(self):
        write_writers_page()
        write_archive_page()
        write_scan_pages()
        write_tag_page()


class ToolTestCase2(unittest.TestCase):
    def test_textregion(self):
        scan_data = read_scan_data()
        wdl = read_werkvoorraad()
        writer_idx = extract_writer_index(wdl)
        with open('writer_idx.json', 'w') as f:
            json.dump(writer_idx, f)
        archive_idx = extract_archive_index(wdl)
        with open('archive_idx.json', 'w') as f:
            json.dump(archive_idx, f)
        archives = list(archive_idx.values())
        a = random.choice(archives)
        scans_per_archive = get_xml_paths()
        with open('scans_per_archive.json', 'w') as f:
            json.dump(scans_per_archive, f)
        scans = scans_per_archive[a.title]
        ic(scans)


def write_writers_page():
    wdl = read_werkvoorraad()
    writer_idx = extract_writer_index(wdl)
    archive_idx = extract_archive_index(wdl)
    head = """
    <head>
        <style>
        table {
          border-spacing: 0;
          border: 2px solid #ddd;
        }
        th, td {
          text-align: left;
          padding: 16px;
        }
        th {
          position: sticky;
          top: 0;
          background-color: #999999;
        }
        tr:nth-child(even) {
          background-color: #f2f2f2;
        }
        </style>
        <script src="https://www.kryogenix.org/code/browser/sorttable/sorttable.js"></script>
    </head>
    """
    with open(f'{DATA_DIR}/writers.html', 'w+') as f:
        f.write(f'<html>{head}<body>')
        f.write(f'<table class="sortable" border="1">')
        f.write(
            f'<tr><th>writer</th><th>inventory number</th><th>serial number</th><th>title</th><th>number of scans</th><th>status</th></tr>')
        for w in sorted(writer_idx.values(), key=lambda w: w.name):
            wa = [a for a in archive_idx.values() if a.writer_id == w.id]
            for a in wa:
                f.write(
                    f'<tr><td>{w.name}</td><td>{a.inventoryNumber}</td><td>{a.serialNumber}</td><td><a href="{a.title}/index.html">{a.title}</a></td><td>{a.numberOfScans}</td><td>{a.status}</td></tr>')
        f.write(f'</table>')
        f.write(f'</body></html>')


def write_archive_page():
    wdl = read_werkvoorraad()
    writer_idx = extract_writer_index(wdl)
    archive_idx = extract_archive_index(wdl)
    sd = read_scan_data()
    file_paths = all_page_xml_file_paths()
    scan_tags = scan_tags_index()
    for a in archive_idx.values():
        archive_title = a.title
        archive_file_paths = [p for p in file_paths if p.startswith(a.title)]
        writer = writer_idx[a.writer_id].name
        # ids = {scan_data.id for scan_data in sd if scan_data.title == archive_title}
        table_rows = []
        for (i, n) in enumerate(archive_file_paths):
            basename = n.split('/')[-1].replace('.xml', '')
            tags = sorted(scan_tags.get(basename.lower(), []))
            tags.sort()
            tagStr = ", ".join(tags)
            filename = f'{archive_title}_{i + 1:04d}.html'
            table_rows.append(
                f'<tr><td>{i + 1}</td><td><a href="{filename}">{basename.upper()}</a></td><td>{tagStr}</td></tr>')
        table_body = "\n".join(table_rows)
        style = """
        <style>
        table {
          border-spacing: 0;
          border: 2px solid #ddd;
        }
        
        th, td {
          text-align: left;
          padding: 16px;
        }
        th {
          position: sticky;
          top: 0;
          background-color: #999999;
        }
        tr:nth-child(even) {
          background-color: #f2f2f2;
        }
        </style>
        """
        html = f"""<html>
    <head>
        <script src="https://www.kryogenix.org/code/browser/sorttable/sorttable.js"></script>
        {style}
    </head>
    <body>
        <b>Writer</b>: <a href="../writers.html">{writer}</a><br/>
        <b>Archive</b>: {archive_title}<br/>
        <b>Status</b>: {a.status}<br/>
        <table class="sortable" border="1">
        <tr><th>n</th><th>id</th><th>tags</th></tr>
        {table_body}
        </table>
    </body>
</html>"""
        out_file_name = f'{DATA_DIR}/{archive_title}/index.html'
        os.makedirs(f'{DATA_DIR}/{archive_title}', exist_ok=True)
        print(f'writing to {out_file_name}')
        with open(out_file_name, 'w+') as f:
            f.write(html)


def scan_tags_index():
    scan_tags = {k.lower(): v for (k, v) in read_scan_tags().items()}
    return scan_tags


def write_scan_pages():
    wdl = read_werkvoorraad()
    writer_idx = extract_writer_index(wdl)
    archive_idx = extract_archive_index(wdl)
    sd = read_scan_data()
    scan_tags = scan_tags_index()
    unknown_archive_titles = []
    for a in archive_idx.values():
        archive_title = a.title
        print(f"- {archive_title}")
        writer = writer_idx[a.writer_id].name
        ids = {scan_data.id for scan_data in sd if scan_data.title == archive_title}
        if len(ids) == 1:
            archive_id = list(ids)[0]
            for (i, p) in enumerate(scan_paths(f'{DATA_DIR}/{archive_title}')):
                basename = os.path.basename(p)
                scan_id = os.path.splitext(basename)[0]
                path = p.replace('\\', '/')
                tags = sorted(scan_tags.get(scan_id.lower(), []))
                write_scan_page(archive_title, archive_id, writer, a.status, path, i + 1, tags=tags)
        else:
            print(f"! unknown archive_title: {archive_title}")
            unknown_archive_titles.append(archive_title)
    ic(unknown_archive_titles)


def write_scan_page(archive_title: str, archive_id: str, writer: str, archive_status: str, xml_path: str,
                    page_index: int, tags=[]):
    file_name = xml_path.split('/')[-1]
    prev_page = f'{archive_title}_{(page_index - 1):04d}.html'
    this_page = f'{archive_title}_{page_index:04d}.html'
    next_page = f'{archive_title}_{(page_index + 1):04d}.html'
    html = f"""<html>
    <body>
        <b>Writer</b>: <a href="../writers.html">{writer}</a><br/>
        <b>Archive</b>: <a href="index.html">{archive_title}</a><br/>
        <b>Status</b>: {archive_status}<br/>
        <b>Tags</b>: {", ".join(tags)}<br/>
        <b>Page</b>: <a href="{prev_page}"><button>&lt;</button></a> {page_index} <a href="{next_page}"><button>&gt;</button></a><br/>
        <br/>
        <iframe src="{transkribus_url(archive_id, page_index)}" height="900" width="100%"></iframe>
        <iframe src="{file_name}" height="900" width="100%"></iframe>
    </body>
</html>"""
    out_file_name = f'{DATA_DIR}/{archive_title}/{this_page}'
    print(f'writing to {out_file_name}', end='\r')
    with open(out_file_name, 'w+') as f:
        f.write(html)


if __name__ == '__main__':
    unittest.main()
