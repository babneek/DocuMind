import os
import sys
import time

# Support for older sqlite systems (like Render/Linux)
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
    print("[VectorDB] Swapped sqlite3 for pysqlite3-binary")
except ImportError:
    pass

# Add parent directory to path
sys.path.insert(0, str(__file__).replace('\\', '/').rsplit('/', 2)[0])

try:
    from backend.services.cache_service import get_cache_manager
    cache_manager = get_cache_manager()
except:
    cache_manager = None

class VectorDB:
    def __init__(self, persist_directory=None):
        if persist_directory is None:
            # Use absolute path relative to backend/ directory
            persist_directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_data")
        self.persist_directory = persist_directory
        # Lazy-init: don't create chromadb client until first use
        self._client = None
        self._collection = None
        self.collection_name = "documind_collection"

        self.model_name = os.getenv("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2")
        self.embedder = None
        self.embeddings_available = False
        self._embedder_loaded = False

    @property
    def client(self):
        """Lazy-load ChromaDB client on first access."""
        if self._client is None:
            import chromadb
            print("[VectorDB] Initializing ChromaDB client...")
            self._client = chromadb.PersistentClient(path=self.persist_directory)
        return self._client

    @property
    def collection(self):
        """Lazy-load ChromaDB collection on first access."""
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(name=self.collection_name)
        return self._collection

    def _ensure_embedder(self):
        if self._embedder_loaded:
            return

        self._embedder_loaded = True
        try:
            from sentence_transformers import SentenceTransformer
            self.embedder = SentenceTransformer(self.model_name)
            self.embeddings_available = True
            print(f"[VectorDB] Loaded embedding model: {self.model_name}")
        except Exception as e:
            self.embedder = None
            self.embeddings_available = False
            print(f"Warning: Sentence transformers not available: {e}")

    def add_documents(self, documents, metadatas, ids):
        """
        Add documents to the vector database with caching.
        """
        self._ensure_embedder()
        if not self.embeddings_available:
            print("Embeddings not available - skipping storage")
            return

        try:
            embeddings = []
            for doc in documents:
                # Check cache first
                cached_emb = cache_manager.get_embedding(doc) if cache_manager else None
                if cached_emb:
                    embeddings.append(cached_emb)
                else:
                    # Generate embedding and cache it
                    new_emb = self.embedder.encode([doc]).tolist()[0]
                    embeddings.append(new_emb)
                    if cache_manager:
                        cache_manager.set_embedding(doc, new_emb)
            
            self.collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
        except Exception as e:
            print(f"[VectorDB] Error storing documents: {e}")

    def query(self, query_text: str, top_k: int = 5, filter_metadata: dict = None):
        """
        Query the vector database with caching.
        """
        self._ensure_embedder()
        if not self.embeddings_available:
            print("Embeddings not available - return empty results")
            return []
            
        try:
            # Check cache for embedding
            cached_emb = cache_manager.get_embedding(query_text) if cache_manager else None
            if cached_emb:
                query_emb = cached_emb
            else:
                query_emb = self.embedder.encode([query_text]).tolist()[0]
                if cache_manager:
                    cache_manager.set_embedding(query_text, query_emb)
            
            results = self.collection.query(
                query_embeddings=[query_emb],
                n_results=top_k,
                where=filter_metadata
            )
            
            hits = []
            if results["documents"]:
                for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
                    hits.append({
                        "content": doc,
                        "metadata": meta,
                        "distance": dist
                    })
            return hits
        except Exception as e:
            print(f"[VectorDB] Error in query: {e}")
            return []

    def delete_by_metadata(self, filter_metadata: dict):
        """
        Delete documents matching the metadata filter.
        """
        try:
            self.collection.delete(where=filter_metadata)
        except Exception as e:
            print(f"[VectorDB] Error in deletion: {e}")
