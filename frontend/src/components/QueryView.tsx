import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Brain, User, Loader2, Sparkles, RotateCcw, ClipboardCopy, BookmarkPlus } from "lucide-react";
import { askQuestion, createNote, getDocuments, getNotes, Note, QueryRequest, updateNote } from "../lib/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  sources?: Array<Record<string, unknown>>;
}

const welcomeSuggestions = [
  "Summarize my latest uploaded document",
  "What are the key findings in the research paper?",
  "Compare revenue figures across Q3 and Q4",
  "List all action items from meeting notes",
];

const QueryView = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [docs, setDocs] = useState<Document[]>([]);
  const [notes, setNotes] = useState<Note[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<number | null>(null);
  const [selectedNoteId, setSelectedNoteId] = useState<number | null>(null);
  const [newNoteName, setNewNoteName] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadDocuments();
    loadNotes();
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  const loadDocuments = async () => {
    try {
      const documents = await getDocuments();
      setDocs(documents);
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  };

  const loadNotes = async () => {
    try {
      const list = await getNotes();
      setNotes(list);
      if (!selectedNoteId && list.length > 0) {
        setSelectedNoteId(list[0].id);
      }
    } catch (error) {
      console.error('Failed to load notes:', error);
    }
  };

  const handleCreateNote = async () => {
    if (!newNoteName.trim()) {
      alert('Please enter a note title.');
      return;
    }

    try {
      const note = await createNote({ title: newNoteName.trim(), content: '' });
      setNotes((prev) => [note, ...prev]);
      setSelectedNoteId(note.id);
      setNewNoteName('');
    } catch (error) {
      console.error('Create note failed:', error);
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      alert('Copied to clipboard.');
    } catch (error) {
      console.error('Copy failed:', error);
      alert('Unable to copy text.');
    }
  };

  const saveTextToNote = async (text: string) => {
    let noteId = selectedNoteId;
    if (!noteId) {
      const title = window.prompt('Enter a note title to save this content:');
      if (!title?.trim()) {
        return;
      }
      const note = await createNote({ title: title.trim(), content: text });
      setNotes((prev) => [note, ...prev]);
      setSelectedNoteId(note.id);
      alert('Saved to new note.');
      return;
    }

    try {
      const note = notes.find((item) => item.id === noteId);
      if (!note) return;
      const updated = await updateNote(noteId, {
        title: note.title,
        content: `${note.content || ''}\n\n${text}`,
      });
      setNotes((prev) => prev.map((item) => (item.id === noteId ? updated : item)));
      alert('Saved to note.');
    } catch (error) {
      console.error('Save to note failed:', error);
      alert('Unable to save to note.');
    }
  };

  const sendMessage = async (text: string) => {
    if (!text.trim() || loading) return;
    const userMsg: Message = { id: Date.now().toString(), role: "user", content: text, timestamp: new Date() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const response = await askQuestion({ query: text, doc_id: selectedDocId ?? undefined });
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.answer,
        timestamp: new Date(),
        sources: response.sources,
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (error) {
      console.error('Query failed:', error);
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Sorry, I couldn't process your query. Please try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-6rem)]">
      <div className="mb-4">
        <h1 className="font-heading text-2xl font-bold text-foreground">AI Query</h1>
        <p className="text-sm text-muted-foreground mt-1">Ask questions about your documents</p>
        <div className="mt-4 flex flex-col gap-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div className="text-sm text-muted-foreground">Document scope:</div>
            <select
              value={selectedDocId ?? "all"}
              onChange={(e) => setSelectedDocId(e.target.value === "all" ? null : Number(e.target.value))}
              className="rounded-lg bg-secondary/50 border border-border/50 text-foreground px-3 py-2 text-sm"
            >
              <option value="all">All documents</option>
              {docs.map((doc) => (
                <option key={doc.id} value={doc.id}>{doc.file_name}</option>
              ))}
            </select>
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div className="text-sm text-muted-foreground">Save query / response to note:</div>
            <div className="flex flex-wrap items-center gap-2">
              <select
                value={selectedNoteId ?? ""}
                onChange={(e) => setSelectedNoteId(e.target.value ? Number(e.target.value) : null)}
                className="rounded-lg bg-secondary/50 border border-border/50 text-foreground px-3 py-2 text-sm"
              >
                <option value="">Select note</option>
                {notes.map((note) => (
                  <option key={note.id} value={note.id}>{note.title}</option>
                ))}
              </select>
              <input
                type="text"
                placeholder="New note title"
                value={newNoteName}
                onChange={(e) => setNewNoteName(e.target.value)}
                className="rounded-lg bg-secondary/50 border border-border/50 px-3 py-2 text-sm text-foreground focus:outline-none"
              />
              <button
                onClick={handleCreateNote}
                className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors"
              >
                Add note
              </button>
            </div>
          </div>
        </div>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto space-y-4 pr-2 scrollbar-thin">
        {messages.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center justify-center h-full text-center"
          >
            <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mb-4">
              <Sparkles className="w-8 h-8 text-primary animate-pulse-glow" />
            </div>
            <h2 className="font-heading text-lg font-semibold text-foreground mb-2">Ask anything about your documents</h2>
            <p className="text-sm text-muted-foreground mb-6 max-w-md">
              DocuMind uses RAG-powered AI to search and analyze your uploaded documents.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-w-lg w-full">
              {welcomeSuggestions.map((s) => (
                <button
                  key={s}
                  onClick={() => sendMessage(s)}
                  className="text-left p-3 rounded-lg bg-secondary/40 border border-border/30 text-sm text-muted-foreground hover:text-foreground hover:bg-secondary/60 hover:border-primary/20 transition-all"
                >
                  {s}
                </button>
              ))}
            </div>
          </motion.div>
        )}

        <AnimatePresence>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}
            >
              {msg.role === "assistant" && (
                <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0 mt-1">
                  <Brain className="w-4 h-4 text-primary" />
                </div>
              )}
              <div className={`max-w-[75%] ${msg.role === "user" ? "bg-primary/15 border border-primary/20" : "glass-panel"} rounded-xl p-4`}>
                <div className="text-sm text-foreground whitespace-pre-wrap">{msg.content}</div>
                <div className="mt-3 flex flex-wrap items-center gap-2">
                  <button
                    type="button"
                    onClick={() => copyToClipboard(msg.content)}
                    className="inline-flex items-center gap-1 rounded-lg bg-secondary/40 px-3 py-1 text-xs text-muted-foreground hover:bg-secondary/70 transition-colors"
                  >
                    <ClipboardCopy className="w-3.5 h-3.5" /> Copy
                  </button>
                  <button
                    type="button"
                    onClick={() => saveTextToNote(msg.content)}
                    className="inline-flex items-center gap-1 rounded-lg bg-primary/10 px-3 py-1 text-xs text-primary hover:bg-primary/20 transition-colors"
                  >
                    <BookmarkPlus className="w-3.5 h-3.5" /> Save to note
                  </button>
                </div>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-border/30">
                    <div className="text-xs text-muted-foreground mb-1">Sources:</div>
                    <div className="flex flex-wrap gap-1">
                      {msg.sources.map((source, index) => (
                        <span key={index} className="text-xs px-2 py-0.5 rounded bg-secondary/50 text-muted-foreground">
                          {typeof source === 'string' ? source : JSON.stringify(source)}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
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
              <Brain className="w-4 h-4 text-primary animate-pulse" />
            </div>
            <div className="glass-panel rounded-xl p-4 flex items-center gap-2">
              <Loader2 className="w-4 h-4 text-primary animate-spin" />
              <span className="text-sm text-muted-foreground">Searching documents...</span>
            </div>
          </motion.div>
        )}
      </div>

      <div className="mt-4">
        {messages.length > 0 && (
          <div className="flex justify-center mb-2">
            <button
              onClick={() => setMessages([])}
              className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
            >
              <RotateCcw className="w-3 h-3" /> New conversation
            </button>
          </div>
        )}
        <form
          onSubmit={(e) => { e.preventDefault(); sendMessage(input); }}
          className="glass-panel p-2 flex items-center gap-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your documents..."
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
      </div>
    </div>
  );
};

export default QueryView;
