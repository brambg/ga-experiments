from nltk import ngrams


class Corrector:

    def __init__(self, corrections: dict):
        self.corrections = corrections
        self.max_ngram = max(k.count(' ') for k in corrections) + 1

    def correct(self, raw_str: str) -> str:
        corrected = raw_str
        for n in range(1, self.max_ngram + 1):
            words = corrected.split(' ')  # TODO: check the words have not already been corrected?
            ngram_corrections = {}
            for i, t in enumerate(ngrams(words, n)):
                orig = " ".join(t)
                if orig in self.corrections:
                    ngram_corrections[i] = self.corrections[orig]
            if ngram_corrections:
                corrected_terms = []
                i = 0
                while i < len(words):
                    if i in ngram_corrections:
                        corrected_terms.append(ngram_corrections[i])
                        i += n
                    else:
                        corrected_terms.append(words[i])
                        i += 1
                corrected = ' '.join(corrected_terms)

        return corrected
