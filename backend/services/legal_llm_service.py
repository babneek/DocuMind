"""
Legal-aware LLM Service for AI Legal Assistant.
Wraps LLMService with legal-specific prompts, structured output, and citation formatting.
"""

import os
import json
from backend.services.llm_service import LLMService


LEGAL_SYSTEM_PROMPT = """You are an advanced AI Legal Assistant designed to help lawyers efficiently analyze, search, and understand legal documents.

Your role is to provide legally cautious, professional, and traceable answers by combining:
1. Uploaded legal documents (contracts, agreements, judgments, petitions, evidence)
2. General legal knowledge (laws, statutes, regulations, case law)
3. Logical legal reasoning

STRICT RULES:
- Never fabricate legal facts, citations, or case references
- Always indicate uncertainty when information is missing
- Never give final legal advice — present information as assistance only
- Always reference the source of your information
- Be legally cautious and professionally precise

OUTPUT FORMAT — Always structure your response EXACTLY like this:

**Answer:** [Clear, direct answer to the question]

**Explanation:** [Detailed legal reasoning, referencing relevant clauses, sections, or principles]

**Sources:**
- [Source 1: document name / law / general knowledge]
- [Source 2: ...]

**Confidence:** [High / Medium / Low] — [brief reason]

---
*This information is based on the available documents and general legal knowledge. Please verify with a qualified legal professional.*"""


LEGAL_SUMMARY_PROMPT = """You are a legal document analyst. Provide a structured legal summary of the following document.

Your summary must include:
1. **Document Type** — (Contract / Agreement / Judgment / Petition / Other)
2. **Parties Involved** — Names and roles of all parties
3. **Key Obligations** — What each party must do
4. **Important Dates & Deadlines** — Effective dates, expiry, milestones
5. **Key Clauses** — Termination, liability, indemnity, confidentiality, dispute resolution
6. **Risks & Red Flags** — Unusual or potentially problematic clauses
7. **Governing Law & Jurisdiction** — Applicable law and courts

Be precise, professional, and legally cautious."""


CLAUSE_EXTRACTION_PROMPT = """You are a legal clause extraction specialist. Extract and analyze the requested clause(s) from the document.

For each clause found, provide:
- **Clause Title/Type**
- **Exact Location** (section number if available)
- **Summary** of what the clause says
- **Legal Implications** — what this means practically
- **Risk Level** — Low / Medium / High
- **Recommendation** — any concerns or suggestions

If the clause is not found, clearly state it is absent and note the legal implications of its absence."""


RISK_ANALYSIS_PROMPT = """You are a legal risk analyst. Analyze the provided document for legal risks and issues.

Identify and categorize:
1. **High Risk** — Clauses or omissions that could cause significant legal or financial harm
2. **Medium Risk** — Clauses that need attention or negotiation
3. **Low Risk** — Minor issues or standard clauses worth noting
4. **Missing Clauses** — Important protections that are absent
5. **Compliance Issues** — Potential regulatory or statutory violations

For each risk, provide:
- Description of the risk
- Relevant clause or section
- Potential consequence
- Recommended action"""


COMPARISON_PROMPT = """You are a legal document comparison specialist. Compare the provided documents and highlight:

1. **Key Differences** — Material differences in terms, obligations, rights
2. **Similarities** — Common clauses and shared terms
3. **Favorable Terms** — Which document has better terms for each party
4. **Missing Provisions** — Clauses present in one but absent in another
5. **Risk Comparison** — Which document carries more legal risk and why
6. **Recommendation** — Which document is preferable and why

Be objective, precise, and legally thorough."""


class LegalLLMService:
    def __init__(self):
        self.llm = LLMService()

    def _call(self, system_msg: str, user_msg: str, max_tokens: int = 2000, temperature: float = 0.2) -> str:
        if not self.llm.client:
            return "[Error] No LLM provider configured. Please set API keys in .env"
        try:
            request_args = {
                "model": self.llm.model_name,
                "messages": [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if self.llm.extra_body:
                request_args["extra_body"] = self.llm.extra_body
            response = self.llm.client.chat.completions.create(**request_args)
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[Error] LLM call failed: {e}"

    def answer_legal_question(self, question: str, context: str, doc_names: list[str] = None) -> str:
        """Answer a legal question using document context with structured legal output."""
        source_hint = ""
        if doc_names:
            source_hint = f"\n\nDocument(s) in context: {', '.join(doc_names)}"

        user_msg = f"""Document Context:
---
{context}
---
{source_hint}

Legal Question: {question}

Provide a structured legal answer following the required output format."""
        return self._call(LEGAL_SYSTEM_PROMPT, user_msg, max_tokens=2000)

    def summarize_legal_document(self, text: str, doc_name: str = "Document") -> str:
        """Generate a structured legal summary of a document."""
        user_msg = f"""Document Name: {doc_name}

Document Content:
---
{text[:12000]}
---

Provide a comprehensive legal summary following the required structure."""
        return self._call(LEGAL_SUMMARY_PROMPT, user_msg, max_tokens=1800, temperature=0.3)

    def extract_clause(self, text: str, clause_type: str, doc_name: str = "Document") -> str:
        """Extract and analyze a specific clause from a document."""
        user_msg = f"""Document Name: {doc_name}

Clause to Extract: {clause_type}

Document Content:
---
{text[:12000]}
---

Extract and analyze the requested clause."""
        return self._call(CLAUSE_EXTRACTION_PROMPT, user_msg, max_tokens=1500)

    def analyze_risks(self, text: str, doc_name: str = "Document") -> str:
        """Perform a legal risk analysis on a document."""
        user_msg = f"""Document Name: {doc_name}

Document Content:
---
{text[:12000]}
---

Perform a comprehensive legal risk analysis."""
        return self._call(RISK_ANALYSIS_PROMPT, user_msg, max_tokens=2000, temperature=0.3)

    def compare_documents(self, text1: str, name1: str, text2: str, name2: str) -> str:
        """Compare two legal documents."""
        user_msg = f"""Document 1: {name1}
---
{text1[:6000]}
---

Document 2: {name2}
---
{text2[:6000]}
---

Compare these two legal documents comprehensively."""
        return self._call(COMPARISON_PROMPT, user_msg, max_tokens=2000, temperature=0.3)

    def answer_general_legal_question(self, question: str) -> str:
        """Answer a general legal knowledge question (no document context)."""
        system_msg = LEGAL_SYSTEM_PROMPT
        user_msg = f"""Legal Question (General Knowledge): {question}

Note: No specific document has been provided. Answer based on general legal knowledge and principles.
Clearly indicate this is general legal information and not advice specific to any document."""
        return self._call(system_msg, user_msg, max_tokens=1500)

    def extract_parties_and_dates(self, text: str) -> dict:
        """Extract parties, dates, and key metadata from a legal document."""
        system_msg = "You are a legal metadata extraction specialist. Extract structured information and return ONLY valid JSON."
        user_msg = f"""Extract the following from this legal document and return as JSON only:
{{
  "document_type": "contract/agreement/judgment/petition/other",
  "parties": [{{"name": "", "role": ""}}],
  "effective_date": "",
  "expiry_date": "",
  "governing_law": "",
  "jurisdiction": "",
  "key_obligations": [""],
  "document_summary": ""
}}

Document:
---
{text[:8000]}
---

Return ONLY the JSON object, no other text."""
        result = self._call(system_msg, user_msg, max_tokens=1000, temperature=0)
        try:
            # Strip markdown code blocks if present
            clean = result.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            return json.loads(clean.strip())
        except Exception:
            return {"raw": result}
