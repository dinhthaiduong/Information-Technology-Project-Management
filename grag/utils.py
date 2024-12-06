from enum import Enum
from typing import Any
from nltk import sent_tokenize, word_tokenize, pos_tag
from nltk.stem import WordNetLemmatizer
import numpy as np

class RagMode(Enum):
    Create = "create"
    QUERY = "query"


def split_text_into_chunks(text: str, max_length=12000) -> list[str]:
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_length:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = ""

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


lemmatizer = WordNetLemmatizer()
def extract_verbs(sentence: str) -> str:
    tokens = word_tokenize(sentence)
    tagged = pos_tag(tokens)
    verbs = [lemmatizer.lemmatize(word, pos='v').upper() for word, tag in tagged if tag.startswith("VB")]
    if len(verbs) == 0:
        return "RELATED"

    return "_".join(verbs)


def get_index_or(array: list[Any], idx: int, default: Any) -> Any:
    try:
        return array[idx]
    except:
        return default

def get_index(array: list[Any], idx: int) -> Any | None:
    try:
        return array[idx]
    except:
        return None


def cosine_similarity(v1: np.ndarray, v2: np.ndarray):
    dot_product = np.dot(v1, v2)
    magnitude_v1 = np.linalg.norm(v1)
    magnitude_v2 = np.linalg.norm(v2)

    if not magnitude_v1 or not magnitude_v2:
        return 0.0
    return dot_product / (magnitude_v1 * magnitude_v2)
