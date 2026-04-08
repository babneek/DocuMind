import json
import os
import re
import sys
from pathlib import Path

from backend.services.llm_service import LLMService

PAGEINDEX_REPO_PATH = Path(__file__).resolve().parents[1] / "pageindex_repo"
if str(PAGEINDEX_REPO_PATH) not in sys.path:
    sys.path.insert(0, str(PAGEINDEX_REPO_PATH))

try:
    from pageindex import PageIndexClient
except ImportError as exc:
    raise ImportError(
        "Could not import PageIndex from local pageindex_repo. "
        "Make sure pageindex_repo is present and its dependencies are installed."
    ) from exc


class PageIndexService:
    def __init__(self):
        root_dir = Path(__file__).resolve().parents[1]
        default_workspace = root_dir / "pageindex_workspace"
        self.workspace = os.getenv("PAGEINDEX_WORKSPACE", str(default_workspace))
        self.model = os.getenv("PAGEINDEX_MODEL", "gpt-4o-2024-11-20")
        self.client = PageIndexClient(workspace=self.workspace, model=self.model)
        self.llm_service = LLMService()

    def index_document(self, file_path: str) -> str:
        return self.client.index(file_path)

    def get_document_structure(self, doc_id: str) -> dict:
        return json.loads(self.client.get_document_structure(doc_id))

    def get_page_content(self, doc_id: str, pages: str) -> list[dict]:
        return json.loads(self.client.get_page_content(doc_id, pages))

    def _flatten_structure(self, structure: list | dict) -> list[dict]:
        entries = []
        if isinstance(structure, dict):
            structure = [structure]

        for node in structure:
            if not isinstance(node, dict):
                continue
            page = node.get("physical_index") or node.get("start_index") or node.get("page")
            title = node.get("title") or node.get("name")
            if title and page:
                entries.append({"title": title, "page": page})
            if node.get("nodes"):
                entries.extend(self._flatten_structure(node["nodes"]))
        return entries

    def _format_structure_for_selection(self, structure: list | dict) -> str:
        flattened = self._flatten_structure(structure)
        lines = []
        for i, item in enumerate(flattened, start=1):
            lines.append(f"{i}. {item['title']} (page {item['page']})")
        return "\n".join(lines)

    def _parse_page_ranges(self, text: str) -> str:
        if not text:
            return ""
        matches = re.findall(r"\d+\s*(?:-\s*\d+)?", text)
        ranges = []
        for match in matches:
            match = match.replace(" ", "")
            if "-" in match:
                start, end = map(int, match.split("-"))
                if start > end:
                    start, end = end, start
                ranges.append((start, end))
            else:
                page = int(match)
                ranges.append((page, page))

        normalized = []
        seen = set()
        for start, end in sorted(ranges):
            if (start, end) in seen:
                continue
            seen.add((start, end))
            normalized.append((start, end))

        if not normalized:
            return ""

        formatted = []
        for start, end in normalized:
            if start == end:
                formatted.append(str(start))
            else:
                formatted.append(f"{start}-{end}")
        return ", ".join(formatted)

    def select_page_ranges(self, doc_id: str, question: str) -> str:
        structure = self.get_document_structure(doc_id)
        structure_summary = self._format_structure_for_selection(structure)
        if not structure_summary:
            return ""

        prompt = (
            "You are a document retrieval assistant. Given a document structure with section titles and page numbers, "
            "choose the smallest set of page ranges most likely to answer the question. "
            "Return only page ranges in the form '5-7, 12, 16-18' and nothing else."
        )
        query = f"Question: {question}\n\nStructure:\n{structure_summary}"
        page_ranges = self.llm_service.answer_question(prompt, query)
        return self._parse_page_ranges(page_ranges)

    def retrieve_context(self, doc_id: str, question: str) -> str:
        page_ranges = self.select_page_ranges(doc_id, question)
        if not page_ranges:
            page_ranges = "1-3"

        pages = self.get_page_content(doc_id, page_ranges)
        page_texts = []
        for entry in pages:
            if isinstance(entry, dict):
                page_texts.append(f"Page {entry.get('page')}: {entry.get('content', '')}")
        return "\n\n".join(page_texts)
