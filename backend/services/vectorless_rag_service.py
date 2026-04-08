import os

class VectorlessRAGService:
    def __init__(self):
        self.pageindex_service = None

    def _get_pageindex_service(self):
        if self.pageindex_service is None:
            from backend.services.pageindex_service import PageIndexService
            self.pageindex_service = PageIndexService()
        return self.pageindex_service

    def retrieve_context(self, doc_id: str, query: str):
        """Retrieve context using PageIndex tree-based document indexing."""
        try:
            service = self._get_pageindex_service()
            return [service.retrieve_context(doc_id, query)]
        except Exception as e:
            print(f"[PageIndex] Retrieval failed: {e}")
            return []
