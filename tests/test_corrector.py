import json
import unittest

from golden_agents.corrections import Corrector

HTR_CORRECTIONS_FILE = 'data/htr_corrections.json'

with open(HTR_CORRECTIONS_FILE) as f:
    corrections_json = f.read()
corrections = json.loads(corrections_json)
htr_corrector = Corrector(corrections)


class CorrectorTestCase(unittest.TestCase):
    def test_max_ngram_3(self):
        corrections = {"term1": "term2", 'a short sentence': 'corrected sentence'}
        c = Corrector(corrections)
        self.assertEqual(3, c.max_ngram)

    def test_max_ngram_4(self):
        corrections = {"term1": "term2", 'a somewhat longer sentence': 'corrected long sentence'}
        c = Corrector(corrections)
        self.assertEqual(4, c.max_ngram)

    def test_corrector_with_bigrams(self):
        corrections = {"term1": "term2", 'cor rect': 'correct'}
        c = Corrector(corrections)
        orig = "I say this is cor rect for now"
        expected = "I say this is correct for now"
        self.assertEqual(expected, c.correct(orig))

    def test_corrector_with_trigrams(self):
        corrections = {'amo': 'anno', 'als me de': 'alsmede'}
        c = Corrector(corrections)
        orig = "proloog als me de epiloog, amo 2021"
        expected = "proloog alsmede epiloog, anno 2021"
        self.assertEqual(expected, c.correct(orig))

    def test_htr_corrections_1(self):
        orig = "d'langstlevenden Abrahan aelites aftestaen"
        expected = "d' langstlevenden Abraham ad lites af te staen"
        self.assert_htr_corrections(orig, expected)

    def test_htr_corrections_2(self):
        orig = 'This is already correct'
        expected = 'This is already correct'
        self.assert_htr_corrections(orig, expected)

    def test_htr_corrections_with_bigram(self):
        orig = 'Alsook de biteur en de biteuren heden'
        expected = 'Alsook debiteur en debiteuren heden'
        self.assert_htr_corrections(orig, expected)

    def assert_htr_corrections(self, orig, expected):
        self.assertEqual(2, htr_corrector.max_ngram)
        self.assertEqual(expected, htr_corrector.correct(orig))


if __name__ == '__main__':
    unittest.main()
