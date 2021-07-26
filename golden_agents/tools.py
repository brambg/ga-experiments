import csv
import glob
import json
from dataclasses import dataclass

from dataclasses_json import dataclass_json

DATA_DIR = '../../pagexml'
SCANS_FILE = '../data/scans_20210403.csv'
INVENTORY_FILE = '../data/werkvoorraad.csv'
TAGS_FILE = '../data/scan_tags.json'


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
    inventoryNumber: int
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

    wdl = [WorkData(*wd) for wd in data[1:]]
    return wdl


def read_scan_tags():
    with open(TAGS_FILE) as f:
        return json.load(f)

def extract_writer_index(work_data_list):
    return {t[0]: Writer(*t) for t in set([(wd.rubric, wd.writer) for wd in work_data_list])}


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
