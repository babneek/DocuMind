import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Send, Brain, User, Loader2, Sparkles, RotateCcw,
  ClipboardCopy, BookmarkPlus, Scale, AlertTriangle,
  FileSearch, GitCompare, ChevronDown
} from "lucide-react";
import {
  askLegalQuestion, createNote, getDocuments, getNotes,
  updateNote, extractClause, analyzeRisks, compareDocuments,
  type Note, type Document, type LegalSource
} from "../lib/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  sources?: LegalSource[];
  context_used?: boolean;
  mode?: string;
}

const LEGAL_SUGGESTIONS = [
  "What is the termination clause in this agreement?",
  "Summarize the obligations of each party",
  "Does this contract allow early termination?",
  "What are the liability limitations in this document?",
  "Identify any risks or red flags in this contract",
  "What does this indemnity clause mean?",
  "What is the governing law and jurisdiction?",
  "Are there any missing clauses I should be aware of?",
];

const CLAUSE_TYPES = [
  "Termination Clause",
  "Indemnity Clause",
  "Liability Clause",
  "Confidentiality / NDA Clause",
  "Dispute Resolution Clause",
  "Payment Terms",
  "Force Majeure Clause",
  "Intellectual Property Clause",
  "Non-Compete Clause",
  "Warranty Clause",
];

type ActiveTool = "ask" | "clause" | "risk" | "compare";

const QueryView = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [docs, setDocs] = useState<Document[]>([]);
  const [notes, setNotes] = useState<Note[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<number | null>(null);
  const [selectedNoteId, setSelectedNoteId] = useState<number | null>(null);
  const [activeTool, setActiveTool] = useState<ActiveTool>("ask");
  const [clauseType, setClauseType] = useState(CLAUSE_TYPES[0]);
  const [compareDoc2, setCompareDoc2] = useState<number | null>(null);
  const [showClauseDropdown, setShowClauseDropdown] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => { loadDocuments(); loadNotes(); }, []);
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  const loadDocuments = async () => {
    try { setDocs(await getDocuments()); } catch (e) { console.error(e); }
  };
  const loadNotes = async () => {
    try {
      const list = await getNotes();
      setNotes(list);
      if (!selectedNoteId && list.length > 0) setSelectedNoteId(list[0].id);
    } catch (e) { console.error(e); }
  };

  const addMessage = (role: Message["role"], content: string, extra?: Partial<Message>) => {
    const msg: Message = { id: Date.now().toString(), role, content, timestamp: new Date(), ...extra };
    setMessages(prev => [...prev, msg]);
    return msg;
  };

  const copyToClipboard = async (text: string) => {
    try { await navigator.clipboard.writeText(text); } catch { /* silent */ }
  };

  const saveToNote = async (text: string) => {
    let noteId = selectedNoteId;
    if (!noteId) {
      const title = window.prompt("Enter a note title:");
      if (!title?.trim()) return;
      const note = await createNote({ title: title.trim(), content: text });
      setNotes(prev => [note, ...prev]);
      setSelectedNoteId(note.id);
      return;
    }
    const note = notes.find(n => n.id === noteId);
    if (!note) return;
    await updateNote(noteId, { title: note.title, content: `${note.content || ""}\n\n${text}` });
  };

  // ── Tool handlers ──────────────────────────────────────────────────────────

  const handleAsk = async (text: string) => {
    if (!text.trim() || loading) return;
    addMessage("user", text);
    setInput("");
    setLoading(true);
    try {
      const res = await askLegalQuestion({ query: text, doc_id: selectedDocId ?? undefined });
      addMessage("assistant", res.answer, { sources: res.sources, context_used: res.context_used, mode: "ask" });
    } catch {
      addMessage("assistant", "Sorry, I couldn't process your legal query. Please try again.");
    } finally { setLoading(false); }
  };

  const handleClauseExtract = async () => {
    if (!selectedDocId) { alert("Please select a document first."); return; }
    const docName = docs.find(d => d.id === selectedDocId)?.file_name || "Document";
    addMessage("user", `Extract: **${clauseType}** from *${docName}*`);
    setLoading(true);
    try {
      const { extractClause: extractClauseApi } = await import("../lib/api");
      const res = await extractClauseApi(selectedDocId, clauseType);
      addMessage("assistant", res.result, { mode: "clause" });
    } catch {
      addMessage("assistant", "Failed to extract clause. Please try again.");
    } finally { setLoading(false); }
  };

  const handleRiskAnalysis = async () => {
    if (!selectedDocId) { alert("Please select a document first."); return; }
    const docName = docs.find(d => d.id === selectedDocId)?.file_name || "Document";
    addMessage("user", `Analyze legal risks in: *${docName}*`);
    setLoading(true);
    try {
      const res = await analyzeRisks(selectedDocId);
      addMessage("assistant", res.analysis, { mode: "risk" });
    } catch {
      addMessage("assistant", "Failed to analyze risks. Please try again.");
    } finally { setLoading(false); }
  };

  const handleCompare = async () => {
    if (!selectedDocId || !compareDoc2) { alert("Please select two documents to compare."); return; }
    if (selectedDocId === compareDoc2) { alert("Please select two different documents."); return; }
    const name1 = docs.find(d => d.id === selectedDocId)?.file_name || "Document 1";
    const name2 = docs.find(d => d.id === compareDoc2)?.file_name || "Document 2";
    addMessage("user", `Compare: *${name1}* vs *${name2}*`);
    setLoading(true);
    try {
      const res = await compareDocuments(selectedDocId, compareDoc2);
      addMessage("assistant", res.comparison, { mode: "compare" });
    } catch {
      addMessage("assistant", "Failed to compare documents. Please try again.");
    } finally { setLoading(false); }
  };

  // ── Render helpers ─────────────────────────────────────────────────────────

  const renderSources = (sources?: LegalSource[]) => {
    if (!sources || sources.length === 0) return null;
    return (
      <div className="mt-3 pt-3 border-t border-border/30">
        <div className="text-xs font-semibold text-muted-foreground mb-1 flex items-center gap-1">
          <FileSearch className="w-3 h-3" /> Sources
        </div>
        <div className="flex flex-wrap gap-1">
          {sources.map((src, i) => (
            <span key={i} className={`text-xs px-2 py-0.5 rounded-full border ${
              src.type === "general_knowledge"
                ? "bg-amber-500/10 border-amber-500/30 text-amber-700"
                : "bg-primary/10 border-primary/20 text-primary"
            }`}>
              {src.type === "general_knowledge"
                ? "General Legal Knowledge"
                : `Doc #${src.doc_id} · ${src.mode} ${src.relevance_score ? `(${(src.relevance_score * 100).toFixed(0)}%)` : ""}`
              }
            </span>
          ))}
        </div>
      </div>
    );
  };

  const renderFormattedAnswer = (content: string) => {
    // Render markdown-like bold and line breaks
    const lines = content.split("\n");
    return (
      <div className="text-sm text-foreground space-y-1">
        {lines.map((line, i) => {
          if (!line.trim()) return <div key={i} className="h-1" />;
          // Bold headers like **Answer:**
          const formatted = line.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
          if (line.startsWith("**") && line.includes(":**")) {
            return <div key={i} className="font-semibold text-foreground mt-2" dangerouslySetInnerHTML={{ __html: formatted }} />;
          }
          if (line.startsWith("- ") || line.startsWith("• ")) {
            return <div key={i} className="pl-3 text-muted-foreground" dangerouslySetInnerHTML={{ __html: `• ${formatted.slice(2)}` }} />;
          }
          if (line.startsWith("*This information")) {
            return <div key={i} className="text-xs text-muted-foreground italic mt-2 pt-2 border-t border-border/20" dangerouslySetInnerHTML={{ __html: formatted }} />;
          }
          return <div key={i} dangerouslySetInnerHTML={{ __html: formatted }} />;
        })}
      </div>
    );
  };

  const toolTabs: { id: ActiveTool; label: string; icon: any }[] = [
    { id: "ask", label: "Ask", icon: Brain },
    { id: "clause", label: "Extract Clause", icon: FileSearch },
    { id: "risk", label: "Risk Analysis", icon: AlertTriangle },
    { id: "compare", label: "Compare", icon: GitCompare },
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-6rem)]">
      {/* Header */}
      <div className="mb-4">
        <div className="flex items-center gap-2 mb-1">
          <Scale className="w-5 h-5 text-primary" />
          <h1 className="font-heading text-2xl font-bold text-foreground">AI Legal Assistant</h1>
        </div>
        <p className="text-sm text-muted-foreground">Analyze contracts, extract clauses, assess risks, and get legal insights</p>

        {/* Tool tabs */}
        <div className="flex gap-1 mt-4 p-1 rounded-xl bg-secondary/40 w-fit">
          {toolTabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTool(tab.id)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTool === tab.id
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <tab.icon className="w-3.5 h-3.5" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tool controls */}
        <div className="mt-3 flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground">Document:</span>
            <select
              value={selectedDocId ?? "all"}
              onChange={e => setSelectedDocId(e.target.value === "all" ? null : Number(e.target.value))}
              className="rounded-lg bg-secondary/50 border border-border/50 text-foreground px-3 py-1.5 text-xs"
            >
              <option value="all">All documents</option>
              {docs.map(d => <option key={d.id} value={d.id}>{d.file_name}</option>)}
            </select>
          </div>

          {activeTool === "clause" && (
            <div className="relative">
              <button
                onClick={() => setShowClauseDropdown(!showClauseDropdown)}
                className="flex items-center gap-1 rounded-lg bg-secondary/50 border border-border/50 px-3 py-1.5 text-xs text-foreground"
              >
                {clauseType} <ChevronDown className="w-3 h-3" />
              </button>
              {showClauseDropdown && (
                <div className="absolute top-full mt-1 left-0 z-50 bg-background border border-border/50 rounded-lg shadow-lg min-w-[200px]">
                  {CLAUSE_TYPES.map(ct => (
                    <button
                      key={ct}
                      onClick={() => { setClauseType(ct); setShowClauseDropdown(false); }}
                      className="w-full text-left px-3 py-2 text-xs hover:bg-secondary/50 transition-colors"
                    >
                      {ct}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTool === "compare" && (
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground">vs:</span>
              <select
                value={compareDoc2 ?? ""}
                onChange={e => setCompareDoc2(e.target.value ? Number(e.target.value) : null)}
                className="rounded-lg bg-secondary/50 border border-border/50 text-foreground px-3 py-1.5 text-xs"
              >
                <option value="">Select second document</option>
                {docs.filter(d => d.id !== selectedDocId).map(d => (
                  <option key={d.id} value={d.id}>{d.file_name}</option>
                ))}
              </select>
            </div>
          )}

          {/* Save to note */}
          <div className="flex items-center gap-2 ml-auto">
            <span className="text-xs text-muted-foreground">Save to:</span>
            <select
              value={selectedNoteId ?? ""}
              onChange={e => setSelectedNoteId(e.target.value ? Number(e.target.value) : null)}
              className="rounded-lg bg-secondary/50 border border-border/50 text-foreground px-3 py-1.5 text-xs"
            >
              <option value="">Select note</option>
              {notes.map(n => <option key={n.id} value={n.id}>{n.title}</option>)}
            </select>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto space-y-4 pr-1">
        {messages.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center justify-center h-full text-center"
          >
            <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mb-4">
              <Scale className="w-8 h-8 text-primary" />
            </div>
            <h2 className="font-heading text-lg font-semibold text-foreground mb-2">
              AI Legal Assistant
            </h2>
            <p className="text-sm text-muted-foreground mb-6 max-w-md">
              Upload legal documents and ask questions. Get structured answers with citations, clause extraction, risk analysis, and document comparison.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-w-xl w-full">
              {LEGAL_SUGGESTIONS.slice(0, 6).map(s => (
                <button
                  key={s}
                  onClick={() => handleAsk(s)}
                  className="text-left p-3 rounded-lg bg-secondary/40 border border-border/30 text-xs text-muted-foreground hover:text-foreground hover:bg-secondary/60 hover:border-primary/20 transition-all"
                >
                  {s}
                </button>
              ))}
            </div>
          </motion.div>
        )}

        <AnimatePresence>
          {messages.map(msg => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}
            >
              {msg.role === "assistant" && (
                <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0 mt-1">
                  <Scale className="w-4 h-4 text-primary" />
                </div>
              )}
              <div className={`max-w-[80%] ${
                msg.role === "user"
                  ? "bg-primary/15 border border-primary/20"
                  : "glass-panel"
              } rounded-xl p-4`}>
                {msg.role === "assistant"
                  ? renderFormattedAnswer(msg.content)
                  : <div className="text-sm text-foreground whitespace-pre-wrap" dangerouslySetInnerHTML={{ __html: msg.content.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>').replace(/\*(.+?)\*/g, '<em>$1</em>') }} />
                }

                {msg.role === "assistant" && renderSources(msg.sources)}

                <div className="mt-3 flex items-center gap-2">
                  <button
                    onClick={() => copyToClipboard(msg.content)}
                    className="inline-flex items-center gap-1 rounded-lg bg-secondary/40 px-2 py-1 text-xs text-muted-foreground hover:bg-secondary/70 transition-colors"
                  >
                    <ClipboardCopy className="w-3 h-3" /> Copy
                  </button>
                  {msg.role === "assistant" && (
                    <button
                      onClick={() => saveToNote(msg.content)}
                      className="inline-flex items-center gap-1 rounded-lg bg-primary/10 px-2 py-1 text-xs text-primary hover:bg-primary/20 transition-colors"
                    >
                      <BookmarkPlus className="w-3 h-3" /> Save to note
                    </button>
                  )}
                </div>
              </div>
              {msg.role === "user" && (
                <div className="w-8 h-8 rounded-lg bg-secondary flex items-center justify-center shrink-0 mt-1">
                  <User className="w-4 h-4 text-muted-foreground" />
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {loading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-3">
            <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
              <Scale className="w-4 h-4 text-primary animate-pulse" />
            </div>
            <div className="glass-panel rounded-xl p-4 flex items-center gap-2">
              <Loader2 className="w-4 h-4 text-primary animate-spin" />
              <span className="text-sm text-muted-foreground">Analyzing legal document...</span>
            </div>
          </motion.div>
        )}
      </div>

      {/* Input area */}
      <div className="mt-4">
        {messages.length > 0 && (
          <div className="flex justify-center mb-2">
            <button
              onClick={() => setMessages([])}
              className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
            >
              <RotateCcw className="w-3 h-3" /> New session
            </button>
          </div>
        )}

        {activeTool === "ask" && (
          <form
            onSubmit={e => { e.preventDefault(); handleAsk(input); }}
            className="glass-panel p-2 flex items-center gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Ask a legal question about your documents..."
              className="flex-1 px-4 py-2.5 bg-transparent text-foreground placeholder:text-muted-foreground text-sm focus:outline-none"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="p-2.5 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-30"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        )}

        {activeTool === "clause" && (
          <div className="glass-panel p-3 flex items-center gap-3">
            <FileSearch className="w-4 h-4 text-primary shrink-0" />
            <span className="text-sm text-muted-foreground flex-1">
              Extract <strong className="text-foreground">{clauseType}</strong> from selected document
            </span>
            <button
              onClick={handleClauseExtract}
              disabled={loading || !selectedDocId}
              className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-semibold hover:bg-primary/90 transition-colors disabled:opacity-30"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Extract"}
            </button>
          </div>
        )}

        {activeTool === "risk" && (
          <div className="glass-panel p-3 flex items-center gap-3">
            <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0" />
            <span className="text-sm text-muted-foreground flex-1">
              Run legal risk analysis on selected document
            </span>
            <button
              onClick={handleRiskAnalysis}
              disabled={loading || !selectedDocId}
              className="px-4 py-2 rounded-lg bg-amber-500 text-white text-sm font-semibold hover:bg-amber-600 transition-colors disabled:opacity-30"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Analyze Risks"}
            </button>
          </div>
        )}

        {activeTool === "compare" && (
          <div className="glass-panel p-3 flex items-center gap-3">
            <GitCompare className="w-4 h-4 text-primary shrink-0" />
            <span className="text-sm text-muted-foreground flex-1">
              Compare selected documents side by side
            </span>
            <button
              onClick={handleCompare}
              disabled={loading || !selectedDocId || !compareDoc2}
              className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-semibold hover:bg-primary/90 transition-colors disabled:opacity-30"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Compare"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default QueryView;
