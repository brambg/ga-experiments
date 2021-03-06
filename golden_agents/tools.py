import csv
import glob
import json
from dataclasses import dataclass
from typing import List

import progressbar as progressbar
from dataclasses_json import dataclass_json

RELATIVE_PATH = ''
# RELATIVE_PATH = '../'
DATA_DIR = f'{RELATIVE_PATH}../pagexml'
SCANS_FILE = f'{RELATIVE_PATH}data/scans_20210403.csv'
INVENTORY_FILE = f'{RELATIVE_PATH}data/werkvoorraad.csv'
TAGS_FILE = f'{RELATIVE_PATH}data/scan_tags.json'
ALL_PAGEXML_LST = f'{RELATIVE_PATH}data/all-pagexml.lst'


@dataclass_json
@dataclass
class ScanData:
    """Simple class for scan data"""
    id: int
    title: str
    number: int
    previewImage: str
    xmlKey: str
    imageURL: str


@dataclass_json
@dataclass
class WorkData:
    """Data from werkvoorraad"""
    rubric: int
    inventoryNumber: str
    serialNumber: str
    title: str
    writer: str
    numberOfScans: int
    status: str


@dataclass_json
@dataclass
class Writer:
    id: str
    name: str


@dataclass_json
@dataclass
class Archive:
    inventoryNumber: int
    serialNumber: str
    title: str
    numberOfScans: int
    status: str
    writer_id: int


def read_scan_data():
    with open(SCANS_FILE) as f:
        reader = csv.reader(f)
        data = [tuple(row) for row in reader]
    return [ScanData(*sd) for sd in data[1:]]


def read_werkvoorraad():
    with open(INVENTORY_FILE) as f:
        reader = csv.reader(f, delimiter=';')
        data = [tuple(row) for row in reader]

    return [WorkData(*wd) for wd in data[1:]]


def read_scan_tags():
    with open(TAGS_FILE) as f:
        return json.load(f)


def extract_writer_index(work_data_list):
    return {
        t[0]: Writer(*t)
        for t in {(wd.rubric, wd.writer) for wd in work_data_list}
    }


def extract_archive_index(work_data_list):
    return {wd.inventoryNumber: Archive(wd.inventoryNumber, wd.serialNumber, wd.title, wd.numberOfScans, wd.status,
                                        wd.rubric) for wd in work_data_list}


def transkribus_url(archive_id: str, page_index: int) -> str:
    return f'https://transkribus.eu/r/amsterdam-city-archives/#/documents/{archive_id}/pages/{page_index}'


def scan_paths(scan_dir: str):
    return [x.replace('\\', '/') for x in glob.glob(f'{scan_dir}/*.xml')]


def get_xml_paths():
    archive_dirs = [x.replace('\\', '/') for x in glob.glob(f'{DATA_DIR}/*[0-9]')]
    return {dir.split('/')[-1]: scan_paths(dir) for dir in archive_dirs}


def file_url(scan_path: str):
    return f'file:///C:/workspaces/golden-agents/pagexml{scan_path.replace(DATA_DIR, "")}'


def all_page_xml_file_paths() -> List[str]:
    with open(ALL_PAGEXML_LST) as f:
        paths = f.readlines()
    return [p.strip() for p in paths]


def default_progress_bar(max_value):
    widgets = [' [',
               progressbar.Timer(format='elapsed time: %(elapsed)s'),
               '] ',
               progressbar.Bar('*'),
               ' (',
               progressbar.ETA(),
               ') ',
               ]
    return progressbar.ProgressBar(max_value=max_value,
                                   widgets=widgets).start()
