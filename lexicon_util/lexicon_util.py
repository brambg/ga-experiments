import json
import os
import re
import sqlite3
import sys
from typing import List

import nltk
from IPython.display import Markdown, display


def _printmd(string):
    display(Markdown(string))


class LexiconUtil:

    def __init__(self, data_root_path: str):
        self.data_root_path = data_root_path

        self.db = f'{self.data_root_path}/galu.db'
        conn = sqlite3.connect(self.db)
        # conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        self.words = [x[0] for x in cur.execute('select word from words').fetchall() if len(x[0]) > 1]
        self.words.sort(key=lambda w: w.lower())
        conn.close()

    def find(self, regexp: str, limit: int = 10, ignore_case: bool = False):
        if ignore_case:
            r = re.compile(f"^{regexp}$", re.IGNORECASE)
        else:
            r = re.compile(f"^{regexp}$")
        matching_words = [w for w in self.words if r.match(w)]
        if matching_words:
            for word in matching_words:
                print(f"'{word}' found in: (limit={limit})\n")
                conn = sqlite3.connect(self.db)
                # conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                paths_json = cur.execute('select pagexml_paths from words where word=?', (word,)).fetchone()[0]
                conn.close()

                paths = sorted(json.loads(paths_json))
                for i, p in enumerate(paths[:limit]):
                    json_path = f'{self.data_root_path}/{p.replace("xml", "json")}'
                    if os.path.isfile(json_path):
                        print(f"{i + 1}] Stads Archief: " + self._transkribus_url_for_pagexml_path(p))
                        with open(json_path) as f:
                            word2iiif = json.load(f)
                        for url in word2iiif[word]:
                            print("Scan-uitsnede: " + url)
                        self._concordance(p, word)
                print('-' * 120)
                print()
        else:
            print(f"no words found matching '{regexp}'")
        print("")

    def words_like(self, regexp: str, ignore_case=False) -> List[str]:
        if ignore_case:
            r = re.compile(f"^{regexp}$", re.IGNORECASE)
        else:
            r = re.compile(f"^{regexp}$")
        return [w for w in self.words if r.match(w)]

    def _concordance(self, path: str, word: str):
        text_path = f"{self.data_root_path}/{path.replace('.xml', '.txt')}"
        with open(text_path) as f:
            text = nltk.Text(nltk.word_tokenize(f.read()))
        lines = [
            f"{cl.left_print} <u><b>{cl.query}</b></u> {cl.right_print}   "
            for cl in text.concordance_list(word)
        ]

        _printmd("Concordance:\n<pre>{0}</pre>".format("\n".join(lines)))

    def _transkribus_url_for_pagexml_path(self, path: str):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        result = cur.execute('select transkribus_url from pagexml where path=?', (path,)).fetchone()
        conn.close()
        if result:
            return result[0]
        print(f"no transkribus url found for {path}", file=sys.stderr)
        return ""


# nltk.download('punkt')
lu = LexiconUtil('/data/galu')


def find(regexp: str, limit: int = 10, ignore_case=False):
    lu.find(regexp, limit, ignore_case)


def words_like(regexp: str, ignore_case=False) -> List[str]:
    return lu.words_like(regexp, ignore_case)
