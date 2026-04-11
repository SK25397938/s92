import faiss
import pickle

VECTOR_PATH = "backend/ai_agent/vector.index"
TEXT_PATH = "backend/ai_agent/texts.pkl"
META_PATH = "backend/ai_agent/metadata.pkl"
TOKEN_PATH = "backend/ai_agent/tokens.pkl"


def save_vector_store(index, texts, metadata, tokenized_texts):
    faiss.write_index(index, VECTOR_PATH)

    with open(TEXT_PATH, "wb") as f:
        pickle.dump(texts, f)

    with open(META_PATH, "wb") as f:
        pickle.dump(metadata, f)

    with open(TOKEN_PATH, "wb") as f:
        pickle.dump(tokenized_texts, f)


def load_vector_store():
    index = faiss.read_index(VECTOR_PATH)

    with open(TEXT_PATH, "rb") as f:
        texts = pickle.load(f)

    with open(META_PATH, "rb") as f:
        metadata = pickle.load(f)

    with open(TOKEN_PATH, "rb") as f:
        tokenized_texts = pickle.load(f)

    return index, texts, metadata, tokenized_texts