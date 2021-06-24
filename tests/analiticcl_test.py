import json
import unittest

from analiticcl import VariantModel, Weights, SearchParameters


class AnaliticclTestCase1(unittest.TestCase):

    def test_example(self):
        model = VariantModel("../analiticcl/examples/simple.alphabet.tsv", Weights(), debug=False)
        model.read_lexicon("../analiticcl/examples/eng.aspell.lexicon")
        model.build()
        result = model.find_variants("udnerstand", SearchParameters(max_edit_distance=3))
        print(json.dumps(result, ensure_ascii=False, indent=4))
        print()
        results = model.find_all_matches("I do not udnerstand the probleem",
                                         SearchParameters(max_edit_distance=3, max_ngram=1))
        print(json.dumps(results, ensure_ascii=False, indent=4))

    def test_ga_example(self):
        model = VariantModel("../analiticcl/examples/simple.alphabet.tsv", Weights(), debug=True)
        model.read_lexicon("../golden-agents-htr/experiments/groundtruth.tok.lexicon.tsv")
        model.read_lexicon("../golden-agents-htr/experiments/htr.tok.lexicon.tsv")
        model.build()
        result = model.find_variants("udnerstand", SearchParameters(max_edit_distance=3))
        print(json.dumps(result, ensure_ascii=False, indent=4))
        print()
        results = model.find_all_matches("Tien stuckx kleijn linnen",
                                         SearchParameters(max_edit_distance=3, max_ngram=1))
        print(json.dumps(results, ensure_ascii=False, indent=2))

    def this_is_not_a_test(self):
        assert False


if __name__ == '__main__':
    unittest.main()
