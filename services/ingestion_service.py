import os
import requests
from bs4 import BeautifulSoup, Tag
from ebooklib import epub
try:
    import pypdf
except ImportError:
    pypdf = None
try:
    import docx
except ImportError:
    docx = None

class IngestionService:
    def __init__(self):
        pass

    def extract_text_from_pdf(self, file_path):
        if not pypdf:
            return "Error: pypdf not installed"
        text = ""
        try:
            reader = pypdf.PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            return f"Error extracting PDF: {e}"

    def extract_text_from_docx(self, file_path):
        if not docx:
            return "Error: python-docx not installed"
        try:
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            return f"Error extracting DOCX: {e}"

    def extract_text_from_epub(self, file_path):
        try:
            book = epub.read_epub(file_path)
            items = {item.get_name(): item for item in book.get_items() if item.get_type() == 9}
            chapter_texts = []

            def process_entry(entry):
                if isinstance(entry, tuple):
                    link = entry[0]
                    subs = entry[1]
                else:
                    link = entry
                    subs = []
                href = getattr(link, 'href', None)
                if href and href in items:
                    item = items[href]
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    text = soup.get_text(separator=' ', strip=True)
                    if len(text) > 50:
                        chapter_texts.append(text)
                for sub in subs:
                    process_entry(sub)

            for entry in book.toc:
                process_entry(entry)

            if not chapter_texts:
                for item in book.get_items():
                    if item.get_type() == 9:
                        soup = BeautifulSoup(item.get_content(), 'html.parser')
                        text = soup.get_text(separator=' ', strip=True)
                        if len(text) > 50:
                            chapter_texts.append(text)
            
            return "\n\n".join(chapter_texts) if chapter_texts else "No text found in EPUB"
        except Exception as e:
            return f"Error extracting EPUB: {e}"

    def extract_text_from_url(self, url):
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Try Wikisource specific content first
            main = soup.find('div', id='ws-content') or soup.find('div', class_='mw-parser-output') or soup.find('body')
            if not main:
                return "Error: Could not find main content on page"
            
            text = '\n'.join(p.get_text(separator=' ', strip=True) for p in main.find_all(['p', 'div', 'span', 'li']))
            return text
        except Exception as e:
            return f"Error scraping URL: {e}"

    def chunk_text(self, text, chunk_size=1000, chunk_overlap=200):
        chunks = []
        for i in range(0, len(text), chunk_size - chunk_overlap):
            chunks.append(text[i:i + chunk_size])
        return chunks

    def chunk_by_sections(self, text, chunk_size=1500, chunk_overlap=200):
        sections = [section.strip() for section in text.split('\n\n') if section.strip()]
        chunks = []
        current_chunk = ""

        for section in sections:
            if len(section) > chunk_size:
                for i in range(0, len(section), chunk_size - chunk_overlap):
                    chunk = section[i:i + chunk_size].strip()
                    if chunk:
                        chunks.append(chunk)
                continue

            if len(current_chunk) + len(section) + 2 <= chunk_size:
                current_chunk += section + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = section + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks
