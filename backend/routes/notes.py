from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import sys
from pathlib import Path
import re
import hashlib
import logging
import time

# Add parent directory to path so we can import from root-level modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.postgres import get_db
from models.note import Note
from models.user import User
from .auth import get_current_user
from services.llm_service import LLMService
from services.cache_service import CacheManager

logger = logging.getLogger("documind")
cache_manager = CacheManager()

router = APIRouter(prefix="/api/notes", tags=["Notes"])

def strip_html_tags(html_content):
    """Remove HTML tags and decode entities from content"""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', html_content)
    # Decode common HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&amp;', '&')
    text = text.replace('&quot;', '"')
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text.strip()

def extract_sections_from_html(html_content):
    """Extract sections from HTML content based on headings and paragraphs"""
    sections = []
    section_id = 0
    
    # Split by h2/h3 tags or multiple paragraphs
    # Match h2, h3 tags with content
    pattern = r'<h[23][^>]*>([^<]+)</h[23]>'
    matches = list(re.finditer(pattern, html_content))
    
    if not matches:
        # No headings found, treat whole content as one section
        plain = strip_html_tags(html_content)
        if plain:
            sections.append(Section(id=f"sec_{section_id}", title="Content", content=plain, order=0))
        return sections
    
    # Extract sections between headings
    for i, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(html_content)
        
        section_content = html_content[start:end]
        plain_content = strip_html_tags(section_content)
        
        if plain_content:
            sections.append(Section(
                id=f"sec_{section_id}",
                title=title,
                content=plain_content,
                order=section_id
            ))
            section_id += 1
    
    return sections

class NoteCreateRequest(BaseModel):
    title: str
    content: str = ""

class NoteUpdateRequest(BaseModel):
    title: str
    content: str


def get_user_note(note_id: int, user_id: int, db: Session):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found or access denied")
    return note

@router.get("/")
def list_notes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    notes = db.query(Note).filter(Note.user_id == current_user.id).order_by(Note.updated_at.desc()).all()
    return notes

@router.post("/")
def create_note(request: NoteCreateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note = Note(user_id=current_user.id, title=request.title.strip() or "Untitled Note", content=request.content or "")
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

@router.put("/{note_id}")
def update_note(note_id: int, request: NoteUpdateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note = get_user_note(note_id, current_user.id, db)
    note.title = request.title.strip() or note.title
    note.content = request.content
    db.commit()
    db.refresh(note)
    return note

class Section(BaseModel):
    id: str
    title: str
    content: str
    order: int

class NoteRestructureRequest(BaseModel):
    structure_type: str = "general"
    custom_sections: str = ""
    style: str = "headings"


def convert_text_to_html(text: str) -> str:
    """Convert plain text with markdown-like formatting to proper HTML"""
    lines = text.split('\n')
    html_parts = []
    in_list = False
    in_numbered_list = False
    in_code_block = False
    
    def apply_inline_formatting(text: str) -> str:
        """Convert inline markdown to HTML (bold, italic, etc.)"""
        # Handle ***bold+italic*** (must come first)
        text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
        # Handle **bold**
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        # Handle *italic* or _italic_
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
        return text
    
    for line in lines:
        stripped = line.strip()
        
        # Handle code blocks
        if stripped.startswith('```'):
            if in_code_block:
                html_parts.append('</code></pre>')
                in_code_block = False
            else:
                html_parts.append('<pre><code>')
                in_code_block = True
            continue
        
        if in_code_block:
            html_parts.append(line + '\n')
            continue
        
        # Handle headings
        if stripped.startswith('### '):
            if in_list:
                html_parts.append('</ul>')
                in_list = False
            if in_numbered_list:
                html_parts.append('</ol>')
                in_numbered_list = False
            heading_text = apply_inline_formatting(stripped[4:].strip())
            html_parts.append(f'<h3>{heading_text}</h3>')
        elif stripped.startswith('## '):
            if in_list:
                html_parts.append('</ul>')
                in_list = False
            if in_numbered_list:
                html_parts.append('</ol>')
                in_numbered_list = False
            heading_text = apply_inline_formatting(stripped[3:].strip())
            html_parts.append(f'<h2>{heading_text}</h2>')
        elif stripped.startswith('# '):
            if in_list:
                html_parts.append('</ul>')
                in_list = False
            if in_numbered_list:
                html_parts.append('</ol>')
                in_numbered_list = False
            heading_text = apply_inline_formatting(stripped[2:].strip())
            html_parts.append(f'<h1>{heading_text}</h1>')
        
        # Handle bullet points
        elif stripped.startswith(('- ', '* ', '• ')):
            if in_numbered_list:
                html_parts.append('</ol>')
                in_numbered_list = False
            if not in_list:
                html_parts.append('<ul>')
                in_list = True
            bullet_text = re.sub(r'^[-*•]\s+', '', stripped)
            bullet_text = apply_inline_formatting(bullet_text)
            html_parts.append(f'<li>{bullet_text}</li>')
        
        # Handle numbered lists (1., 2., etc.)
        elif re.match(r'^\d+\.\s', stripped):
            if in_list:
                html_parts.append('</ul>')
                in_list = False
            if not in_numbered_list:
                html_parts.append('<ol>')
                in_numbered_list = True
            numbered_text = re.sub(r'^\d+\.\s+', '', stripped)
            numbered_text = apply_inline_formatting(numbered_text)
            html_parts.append(f'<li>{numbered_text}</li>')
        
        # Regular text paragraphs
        elif stripped:
            if in_list:
                html_parts.append('</ul>')
                in_list = False
            if in_numbered_list:
                html_parts.append('</ol>')
                in_numbered_list = False
            para_text = apply_inline_formatting(stripped)
            html_parts.append(f'<p>{para_text}</p>')
    
    # Close any open lists or code blocks
    if in_list:
        html_parts.append('</ul>')
    if in_numbered_list:
        html_parts.append('</ol>')
    if in_code_block:
        html_parts.append('</code></pre>')
    
    result = '\n'.join(html_parts)
    return result


class NoteRestructureRequest(BaseModel):
    structure_type: str = "summary"
    custom_prompt: str = ""
    custom_sections: str = ""
    style: str = "headings"

class ExtractStructureResponse(BaseModel):
    sections: list[Section]

class RebuildNoteRequest(BaseModel):
    sections: list[Section]

@router.post("/{note_id}/restructure")
def restructure_note(note_id: int, request: NoteRestructureRequest = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if request is None:
        request = NoteRestructureRequest()
    
    note = get_user_note(note_id, current_user.id, db)
    if not note.content:
        raise HTTPException(status_code=400, detail="Note has no content to restructure")
    
    # Strip HTML tags to get plain text for LLM
    plain_text_content = strip_html_tags(note.content)
    if not plain_text_content:
        raise HTTPException(status_code=400, detail="Note content appears to be empty after parsing")
    
    # Build dynamic prompt based on structure type
    if request.custom_prompt:
        base_prompt = request.custom_prompt
    elif request.structure_type == "summary":
        base_prompt = """Analyze the following content and create a clean summary structure.

Output format:
## Summary
[2-3 sentence summary of main point]

## Key Points
- [First key point]
- [Second key point]
- [Additional points]

## Status
[Current status or conclusions]"""
    
    elif request.structure_type == "tasks":
        base_prompt = """Extract all actionable tasks, deadlines, and responsibilities.

Output format:
## Tasks
1. [Task 1] - [Deadline if mentioned] - [Owner if mentioned]
2. [Task 2] - [Deadline if mentioned] - [Owner if mentioned]
3. [Continue for all tasks]

## Priority
[High/Medium/Low based on context]

## Timeline
[Overall project timeline]"""
    
    elif request.structure_type == "meeting_notes":
        base_prompt = """Structure the content as professional meeting notes.

Output format:
## Meeting Summary
[Brief overview of meeting]

## Attendees
- [Person 1]
- [Person 2]

## Discussion Points
- [Point 1]
- [Point 2]

## Action Items
- [Item 1] - Owner: [Name]
- [Item 2] - Owner: [Name]

## Next Steps
[Timeline and next meeting details]"""
    
    elif request.structure_type == "timeline":
        base_prompt = """Create a chronological timeline of events and milestones.

Output format:
## Timeline

### [Period/Date 1]
[What happened]

### [Period/Date 2]
[What happened]

### [Period/Date 3]
[What happened]

## Key Milestones
- [Milestone 1]
- [Milestone 2]"""
    
    elif request.structure_type == "checklist":
        base_prompt = """Convert content into an actionable checklist format.

Output format:
## Checklist

### [Category 1]
- [ ] [Item 1]
- [ ] [Item 2]
- [ ] [Item 3]

### [Category 2]
- [ ] [Item 1]
- [ ] [Item 2]

## Notes
[Any important notes or context]"""
    
    elif request.structure_type == "report":
        base_prompt = """Analyze and structure as a formal report.

Output format:
## Executive Summary
[Concise 2-3 sentence overview]

## Background
[Context and relevant history]

## Analysis
[Key findings and observations]

## Risks & Issues
- [Risk or issue 1]
- [Risk or issue 2]

## Recommendations
- [Recommendation 1]
- [Recommendation 2]

## Conclusion
[Final summary and next steps]"""
    
    elif request.structure_type == "comparison":
        base_prompt = """Create a comparison or pros/cons structure.

Output format:
## Comparison

### Option 1 / Pros
- [Pro 1]
- [Pro 2]
- [Pro 3]

### Option 2 / Cons
- [Con 1]
- [Con 2]
- [Con 3]

## Summary
[Overall assessment or recommendation]"""
    
    elif request.structure_type == "faq":
        base_prompt = """Convert content into a FAQ (Frequently Asked Questions) format.

Output format:
## FAQ

### Q: [Question 1]
A: [Answer]

### Q: [Question 2]
A: [Answer]

### Q: [Question 3]
A: [Answer]"""
    
    elif request.structure_type == "json":
        base_prompt = """Extract and structure as machine-readable JSON data.

Output ONLY the JSON, no other text:
```json
{
  "title": "main topic",
  "summary": "brief overview",
  "key_items": ["item1", "item2", "item3"],
  "tasks": [{"task": "task name", "owner": "person", "deadline": "date"}],
  "status": "status value",
  "metadata": {
    "priority": "high/medium/low",
    "created": "date if mentioned",
    "deadline": "date if mentioned"
  }
}
```"""
    
    else:  # Default to summary
        base_prompt = """Analyze and create a clean summary structure.

Output format:
## Summary
[Summary of main point]

## Key Points
- [Key point 1]
- [Key point 2]

## Status
[Current status]"""
    
    if not request.custom_prompt:
        base_prompt += "\n\nPreserve all important information but improve clarity and organization."
    
    prompt = f"""{base_prompt}

Original content:
{plain_text_content}

Restructured content:
"""
    
    # Create cache key based on content + structure settings
    cache_key = f"restructure_{note_id}_{hashlib.md5((plain_text_content + request.structure_type + request.custom_sections + request.style).encode()).hexdigest()}"
    
    # Check if we have a cached restructure result
    cached_result = cache_manager.get_response(cache_key)
    if cached_result:
        logger.info(f"[Restructure] Cache hit for note {note_id}")
        note.content = convert_text_to_html(cached_result)
        db.commit()
        db.refresh(note)
        return note
    
    # Use Groq API for faster restructuring
    logger.info(f"[Restructure] Starting restructure for note {note_id} with {request.structure_type} type")
    start_time = time.time()
    
    groq_client, groq_model = LLMService.get_groq_client()
    if not groq_client:
        raise HTTPException(status_code=500, detail="Groq API not configured. Please set GROQ_API_KEY in .env")
    
    try:
        logger.info(f"[Restructure] Calling Groq API with model {groq_model}")
        request_args = {
            "model": groq_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 1200,
            "timeout": 30.0,  # 30 second timeout
        }

        response = groq_client.chat.completions.create(**request_args)
        restructured_content = response.choices[0].message.content.strip()
        
        elapsed = time.time() - start_time
        logger.info(f"[Restructure] Completed in {elapsed:.2f}s for note {note_id}")
        
        # Cache the result for future use
        cache_manager.set_response(cache_key, restructured_content)
        
        # Update the note with restructured content (convert to proper HTML)
        note.content = convert_text_to_html(restructured_content)
        db.commit()
        db.refresh(note)
        return note
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"[Restructure] Failed after {elapsed:.2f}s: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to restructure note: {str(e)}")

@router.delete("/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note = get_user_note(note_id, current_user.id, db)
    db.delete(note)
    db.commit()
    return {"message": "Note deleted successfully"}

@router.get("/{note_id}/structure")
def extract_structure(note_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note = get_user_note(note_id, current_user.id, db)
    sections = extract_sections_from_html(note.content)
    return {"sections": sections}

@router.post("/{note_id}/rebuild")
def rebuild_note(note_id: int, request: RebuildNoteRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note = get_user_note(note_id, current_user.id, db)
    
    # Sort sections by order
    sorted_sections = sorted(request.sections, key=lambda x: x.order)
    
    # Rebuild HTML content from sections
    html_parts = []
    for section in sorted_sections:
        html_parts.append(f"<h2>{section.title}</h2>")
        html_parts.append(f"<p>{section.content}</p>")
    
    note.content = "\n".join(html_parts)
    db.commit()
    db.refresh(note)
    return note
