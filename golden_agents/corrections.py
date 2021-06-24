# from analiticcl import VariantModel, Weights, SearchParameters

class Corrector():

    def __init__(self, corrections: dict):
        self.corrections = corrections
        self.max_ngram = max(k.count(' ') for k in corrections.keys()) + 1

    def correct(self, raw_str: str) -> str:
        words = raw_str.split(' ')
        corrected = ' '.join([self.corrections.get(o, o) for o in words])
        return corrected
