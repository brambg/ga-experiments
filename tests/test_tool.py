import json
import random
import unittest

from icecream import ic

from golden_agents.tools import read_werkvoorraad, extract_writer_index, extract_archive_index, DATA_DIR, scan_paths, \
    transkribus_url, read_scan_data, get_xml_paths, all_page_xml_file_paths, read_scan_tags


class ToolTestCase1(unittest.TestCase):
    def test_writers(self):
        write_writers_page()
        write_archive_page()
        write_scan_pages()


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
    with open(f'{DATA_DIR}/writers.html', 'w+') as f:
        f.write(f'<html><body>')
        for w in sorted(writer_idx.values(), key=lambda w: w.name):
            print(f"- writer: {w.name}")
            f.write(f'<h2>{w.name}</h2>')
            f.write(f'<table border="1">')
            f.write(
                f'<tr><th>inventory number</th><th>serial number</th><th>title</th><th>number of scans</th><th>status</th></tr>')
            wa = [a for a in archive_idx.values() if a.writer_id == w.id]
            for a in wa:
                f.write(
                    f'<tr><td>{a.inventoryNumber}</td><td>{a.serialNumber}</td><td><a href="{a.title}/index.html">{a.title}</a></td><td>{a.numberOfScans}</td><td>{a.status}</td></tr>')
            f.write(f'</table>')
        f.write(f'</body></html>')


def write_archive_page():
    wdl = read_werkvoorraad()
    writer_idx = extract_writer_index(wdl)
    archive_idx = extract_archive_index(wdl)
    sd = read_scan_data()
    file_paths = all_page_xml_file_paths()
    scan_tags = read_scan_tags()
    for a in archive_idx.values():
        archive_title = a.title
        archive_file_paths = [p for p in file_paths if p.startswith(a.title)]
        writer = writer_idx[a.writer_id].name
        # ids = {scan_data.id for scan_data in sd if scan_data.title == archive_title}
        table_rows = []
        for (i, n) in enumerate(archive_file_paths):
            basename = n.split('/')[-1].replace('.xml', '')
            tags = scan_tags.get(basename, [])
            tags.sort()
            tagStr = ", ".join(tags)
            table_rows.append(
                f'<tr><td>{i + 1}</td><td><a href="{basename}.html">{basename}</a></td><td>{tagStr}</td></tr>')
        table_body = "\n".join(table_rows)
        html = f"""<html>
    <body>
        Writer: <a href="../writers.html">{writer}</a><br/>
        Archive: {archive_title}<br/>
        Status: {a.status}<br/>
        <table border=1>
        <tr><th>n</th><th>id</th><th>tags</th></tr>
        {table_body}
        </table>
    </body>
</html>"""
        out_file_name = f'{DATA_DIR}/{archive_title}/index.html'
        print(f'writing to {out_file_name}')
        with open(out_file_name, 'w+') as f:
            f.write(html)


def write_scan_pages():
    wdl = read_werkvoorraad()
    writer_idx = extract_writer_index(wdl)
    archive_idx = extract_archive_index(wdl)
    sd = read_scan_data()
    unknown_archive_titles = []
    for a in archive_idx.values():
        archive_title = a.title
        print(f"- {archive_title}")
        writer = writer_idx[a.writer_id].name
        ids = {scan_data.id for scan_data in sd if scan_data.title == archive_title}
        if len(ids) == 1:
            archive_id = list(ids)[0]
            for (i, p) in enumerate(scan_paths(f'{DATA_DIR}/{archive_title}')):
                write_scan_page(archive_title, archive_id, writer, a.status, p.replace('\\', '/'), i + 1)
        else:
            print(f"! unknown archive_title: {archive_title}")
            unknown_archive_titles.append(archive_title)
    ic(unknown_archive_titles)


def write_scan_page(archive_title: str, archive_id: str, writer: str, archive_status: str, xml_path: str,
                    page_index: int):
    file_name = xml_path.split('/')[-1]
    prev_page = f'{archive_title}_{(page_index - 1):04d}.html'
    this_page = f'{archive_title}_{page_index:04d}.html'
    next_page = f'{archive_title}_{(page_index + 1):04d}.html'
    html = f"""<html>
    <body>
        Writer: <a href="../writers.html">{writer}</a><br/>
        Archive: {archive_title}<br/>
        Status: {archive_status}<br/>
        Page: <a href="{prev_page}"><button>&lt;</button></a> {page_index} <a href="{next_page}"><button>&gt;</button></a><br/>
        <iframe src="{transkribus_url(archive_id, page_index)}" height="900" width="100%"></iframe>
        <iframe src="{file_name}" height="900" width="100%"></iframe>
    </body>
</html>"""
    out_file_name = f'{DATA_DIR}/{archive_title}/{this_page}'
    print(f'writing to {out_file_name}')
    with open(out_file_name, 'w+') as f:
        f.write(html)


if __name__ == '__main__':
    unittest.main()