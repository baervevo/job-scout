from abc import ABC

import spacy
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
from torch import Tensor


class Processor(ABC):
    def __init__(self, nlp_model_name="en_core_web_sm",
                 kw_model_name="all-MiniLM-L6-v2",
                 embed_model_name="all-MiniLM-L6-v2"):
        self.nlp_spacy = spacy.load(nlp_model_name)
        self.kw_model = KeyBERT(model=kw_model_name)
        self.embed_model = SentenceTransformer(embed_model_name)

    def preprocess(self, text: str) -> str:
        doc = self.nlp_spacy(text)
        tokens = [
            token.lemma_.lower()
            for token in doc
            if not token.is_stop and not token.is_punct and not token.is_space
        ]
        return " ".join(tokens)

    def extract_keywords(self, text: str, top_n: int = 5, nr_candidates: int = 15, ngram_min: int = 1,
                         ngram_max: int = 2, use_maxsum: bool = False, stop_words: str = 'english') -> list[str]:
        keyword_tuples = self.kw_model.extract_keywords(
            text,
            keyphrase_ngram_range=(ngram_min, ngram_max),
            stop_words=stop_words,
            use_maxsum=use_maxsum,
            nr_candidates=nr_candidates,
            top_n=top_n
        )
        keywords = [kw for kw, score in keyword_tuples]
        return keywords

    def embed_text(self, text: str) -> Tensor:
        return self.embed_model.encode(text)
