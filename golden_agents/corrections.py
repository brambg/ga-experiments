# from analiticcl import VariantModel, Weights, SearchParameters
from nltk import ngrams


class Corrector():

    def __init__(self, corrections: dict):
        self.corrections = corrections
        self.max_ngram = max(k.count(' ') for k in corrections.keys()) + 1

    def correct(self, raw_str: str) -> str:
        words = raw_str.split(' ')
        corrected = ' '.join([self.corrections.get(o, o) for o in words])
        for n in range(2, self.max_ngram + 1):
            words = corrected.split(' ')
            ngram_corrections = {}
            for i, t in enumerate(ngrams(words, n)):
                orig = " ".join(t)
                if (orig in self.corrections):
                    ngram_corrections[i] = self.corrections[orig]
            if (len(ngram_corrections) > 0):
                corrected_terms = []
                i = 0
                while (i < len(words)):
                    if (i in ngram_corrections):
                        corrected_terms.append(ngram_corrections[i])
                        i += n
                    else:
                        corrected_terms.append(words[i])
                        i += 1
                corrected = ' '.join(corrected_terms)

        return corrected
