import csv
import json
import os
import random
from collections import defaultdict
from dataclasses import dataclass

import pagexml.parser as px
from dataclasses_json import dataclass_json

import golden_agents.tools as ga

segment_file = "data/na_boedel_deeds_scans20210906.csv"
metadata_file = "data/na_boedel_deeds_inventory_minuut_20210917.csv"


@dataclass_json
@dataclass
class LineInfo:
    text: str
    page_id: str
    line_id: str
    offset: int


def load_present_deed_segments():
    present_paths = ga.all_page_xml_file_paths()
    basename_to_path = {}
    for p in present_paths:
        basename = p.split('/')[-1].replace('.xml', '').upper()
        basename_to_path[basename] = p
    with open(segment_file) as f:
        reader = csv.DictReader(f)
        segment_data = [r for r in reader]
    deed_segments = defaultdict(list)
    for sd in segment_data:
        scan_naam = sd['scanNaam']
        if scan_naam in basename_to_path:
            deed_segments[sd['akteIndex']].append(scan_naam)
    return deed_segments


def load_deed_metadata():
    with open(metadata_file) as f:
        reader = csv.DictReader(f)
        deed_data = [r for r in reader]
    return deed_data


def load_notaries():
    # scan_data = ga.read_scan_data()
    wdl = ga.read_werkvoorraad()
    ai = ga.extract_archive_index(wdl)
    wi = ga.extract_writer_index(wdl)
    return {a.inventoryNumber: wi[a.writer_id].name for a in ai.values()}


def load_deeds():
    deed_segments = load_present_deed_segments()
    with open(metadata_file) as f:
        reader = csv.DictReader(f)
        deed_data = [r for r in reader]
    notary_per_inventory_number = load_notaries()
    wdl = ga.read_werkvoorraad()
    rootpath_for_inventory_number = {wd.inventoryNumber: wd.title for wd in wdl}
    status_for_inventory_number = {wd.inventoryNumber: wd.status for wd in wdl}
    deeds = {}
    for deed in deed_data:
        key = deed['akteIndex']
        deed_inventory_number = deed['inventoryNumber']
        if key in deed_segments and deed_inventory_number in notary_per_inventory_number:
            if key in deeds and deed['minuutakte'] == '0':
                break
            deeds[key] = {}
            deeds[key].update(deed)
            deeds[key]['segments'] = deed_segments[key]
            deeds[key]['notary'] = notary_per_inventory_number[deed_inventory_number]
            deeds[key]['rootpath'] = rootpath_for_inventory_number[deed_inventory_number]
            deeds[key]['status'] = status_for_inventory_number[deed_inventory_number]
    return deeds


def make_selection(deeds):
    randomized_deeds = random.choices(list(deeds.values()), k=len(deeds))
    selected_dates = set()
    selected_notaries = defaultdict(lambda: 0)
    selected_notary_deed_type = {}
    selection = []
    selected_minutes = {'0': 0, '1': 0}
    for d in randomized_deeds:
        date = d['date']
        notary = d['notary']
        decade = date[0:4]
        minutes = d['minuutakte']
        if decade not in selected_dates \
                and selected_notary_deed_type.get(notary) != minutes \
                and selected_notaries[notary] < 2 \
                and selected_minutes[minutes] < 10 \
                and d['status'] == 'HTR':
            selected_dates.add(decade)
            selected_notaries[notary] += 1
            selected_minutes[minutes] += 1
            selected_notary_deed_type[notary] = minutes
            selection.append(d)
            print(f"{date} | {notary} | {minutes}")
            if len(selection) == 10:
                break
    return selection


def main():
    deeds = load_deeds()
    selection = make_selection(deeds)
    metadata = {}
    for d in selection:
        docname = f"GA_{d['date']}_{d['inventoryNumber']}"
        d["documentname"] = docname
        os.makedirs(f'recogito/{docname}', exist_ok=True)
        for s in d['segments']:
            pagexml_file_path = f"../pagexml/{d['rootpath']}/{s}.xml"
            text_file_path = f"recogito/{docname}/{s}.txt"
            scan = px.parse_pagexml_file(pagexml_file_path)
            line_infos = []
            lines = []
            offset = 0
            for l in scan.get_lines():
                if l.text:
                    lines.append(l.text)
                    li = LineInfo(line_id=l.id, text=l.text, offset=offset, page_id=s)
                    line_infos.append(li.to_dict())
                    offset += len(l.text) + 1
            if lines:
                with open(text_file_path, 'w') as f:
                    f.write("\n".join(lines))
                metadata[s] = line_infos

    with open('out/recogito_selection.json', 'w', encoding='utf8') as f:
        json.dump(fp=f, obj=selection)
    with open('out/recogito_selection_metadata.json', 'w', encoding='utf8') as f:
        json.dump(fp=f, obj=metadata)


if __name__ == '__main__':
    main()
