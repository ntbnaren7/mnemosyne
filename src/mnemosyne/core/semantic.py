import logging
import warnings
from typing import List, Optional

# Suppress warnings from libraries (e.g. huggingface tokenizers parallelism)
warnings.filterwarnings("ignore")

try:
    from sentence_transformers import SentenceTransformer
    from sentence_transformers.util import cos_sim
    HAS_SEMANTICS = True
except ImportError:
    HAS_SEMANTICS = False
    print("WARNING: 'sentence-transformers' not found. Semantic features disabled.")

class SemanticEngine:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SemanticEngine, cls).__new__(cls)
            cls._instance._initialize_model()
        return cls._instance

    def _initialize_model(self):
        """Loads the local embedding model."""
        if HAS_SEMANTICS and self._model is None:
            try:
                # 'all-MiniLM-L6-v2' is fast, efficient, and good for general semantic similarity
                self._model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                print(f"ERROR: Failed to load semantic model: {e}")
                self._model = None

    def encode(self, text: str) -> Optional[List[float]]:
        """Computes embedding for a given text."""
        if not self._model:
            return None
        try:
            embedding = self._model.encode(text, convert_to_tensor=True)
            return embedding.tolist()
        except Exception as e:
            print(f"ERROR: Encoding failed: {e}")
            return None

    def similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """Computes cosine similarity between two embeddings."""
        if not HAS_SEMANTICS or not emb1 or not emb2:
            return 0.0
        try:
            return float(cos_sim(emb1, emb2)[0][0])
        except Exception as e:
            print(f"ERROR: Similarity computation failed: {e}")
            return 0.0
