import { motion } from "framer-motion";
import { FileText, Scale, AlertTriangle, BookOpen, Clock, Shield, Gavel, FileSearch } from "lucide-react";
import { useEffect, useState } from "react";
import { getDocuments, getNotes, type Document, type Note } from "../lib/api";

const QUICK_ACTIONS = [
  { label: "Ask a Legal Question", desc: "Query your documents with AI", icon: Scale, color: "text-primary", bg: "bg-primary/10", view: "query" },
  { label: "Extract a Clause", desc: "Pull specific clauses instantly", icon: FileSearch, color: "text-blue-500", bg: "bg-blue-500/10", view: "query" },
  { label: "Risk Analysis", desc: "Identify legal risks in a document", icon: AlertTriangle, color: "text-amber-500", bg: "bg-amber-500/10", view: "query" },
  { label: "Legal Notes", desc: "Organize your legal research", icon: BookOpen, color: "text-green-500", bg: "bg-green-500/10", view: "notes" },
];

const DOC_TYPE_LABELS: Record<string, string> = {
  "application/pdf": "PDF",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "DOCX",
  "text/plain": "TXT",
};

interface DashboardViewProps {
  onNavigate?: (view: string) => void;
}

const DashboardView = ({ onNavigate }: DashboardViewProps) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [docsData, notesData] = await Promise.all([getDocuments(), getNotes()]);
        setDocuments(docsData || []);
        setNotes(notesData || []);
      } catch (e) {
        console.error("Dashboard load error:", e);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const readyDocs = documents.filter(d => d.status === "ready").length;
  const processingDocs = documents.filter(d => d.status === "processing").length;

  const stats = [
    { label: "Legal Documents", value: documents.length.toString(), icon: FileText, sub: `${readyDocs} ready` },
    { label: "Research Notes", value: notes.length.toString(), icon: BookOpen, sub: `${notes.length} created` },
    { label: "AI Analyses", value: "—", icon: Gavel, sub: "Track queries" },
    { label: "Risk Flags", value: processingDocs > 0 ? `${processingDocs} pending` : "—", icon: Shield, sub: "Run analysis" },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
          <Scale className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h1 className="font-heading text-2xl font-bold text-foreground">Legal Assistant Dashboard</h1>
          <p className="text-sm text-muted-foreground">AI-powered legal document analysis and research</p>
        </div>
      </div>

      {/* Disclaimer banner */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-start gap-3 p-4 rounded-xl bg-amber-500/10 border border-amber-500/20"
      >
        <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
        <p className="text-xs text-amber-700">
          <strong>Legal Disclaimer:</strong> This AI Legal Assistant provides information for research purposes only.
          It does not constitute legal advice. Always verify with a qualified legal professional before making legal decisions.
        </p>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="glass-panel p-5"
          >
            <div className="flex items-center justify-between mb-3">
              <stat.icon className="w-5 h-5 text-primary" />
              <span className="text-xs text-muted-foreground">{stat.sub}</span>
            </div>
            <div className="font-heading text-2xl font-bold text-foreground">{stat.value}</div>
            <div className="text-xs text-muted-foreground mt-1">{stat.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="font-heading font-semibold text-foreground mb-3 text-sm uppercase tracking-wide text-muted-foreground">
          Quick Actions
        </h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          {QUICK_ACTIONS.map((action, i) => (
            <motion.button
              key={action.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + i * 0.1 }}
              onClick={() => onNavigate?.(action.view)}
              className="glass-panel-hover p-4 text-left flex flex-col gap-2"
            >
              <div className={`w-9 h-9 rounded-lg ${action.bg} flex items-center justify-center`}>
                <action.icon className={`w-4 h-4 ${action.color}`} />
              </div>
              <div>
                <div className="text-sm font-semibold text-foreground">{action.label}</div>
                <div className="text-xs text-muted-foreground mt-0.5">{action.desc}</div>
              </div>
            </motion.button>
          ))}
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Recent Documents */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="glass-panel p-6"
        >
          <h2 className="font-heading font-semibold text-foreground mb-4 flex items-center gap-2">
            <FileText className="w-4 h-4 text-primary" />
            Recent Legal Documents
          </h2>
          <div className="space-y-2">
            {loading ? (
              <p className="text-sm text-muted-foreground py-4 text-center">Loading...</p>
            ) : documents.length === 0 ? (
              <div className="py-8 text-center">
                <FileText className="w-8 h-8 text-muted-foreground/30 mx-auto mb-2" />
                <p className="text-sm text-muted-foreground">No documents uploaded yet</p>
                <p className="text-xs text-muted-foreground mt-1">Upload contracts, agreements, or case files to get started</p>
              </div>
            ) : (
              documents.slice(0, 6).map(doc => (
                <div key={doc.id} className="flex items-center gap-3 p-3 rounded-lg bg-secondary/30 hover:bg-secondary/50 transition-colors">
                  <div className="w-8 h-8 rounded-md bg-primary/10 flex items-center justify-center shrink-0">
                    <FileText className="w-4 h-4 text-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-foreground truncate">{doc.file_name}</div>
                    <div className="text-xs text-muted-foreground flex items-center gap-1 mt-0.5">
                      <Clock className="w-3 h-3" />
                      {new Date(doc.upload_date).toLocaleDateString()}
                      <span className="ml-1 px-1.5 py-0.5 rounded text-xs bg-secondary">
                        {DOC_TYPE_LABELS[doc.file_type] || doc.file_type}
                      </span>
                    </div>
                  </div>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${
                    doc.status === "ready"
                      ? "bg-green-500/10 text-green-600"
                      : doc.status === "processing"
                      ? "bg-amber-500/10 text-amber-600"
                      : "bg-red-500/10 text-red-600"
                  }`}>
                    {doc.status}
                  </span>
                </div>
              ))
            )}
          </div>
        </motion.div>

        {/* Recent Notes */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="glass-panel p-6"
        >
          <h2 className="font-heading font-semibold text-foreground mb-4 flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-primary" />
            Legal Research Notes
          </h2>
          <div className="space-y-2">
            {loading ? (
              <p className="text-sm text-muted-foreground py-4 text-center">Loading...</p>
            ) : notes.length === 0 ? (
              <div className="py-8 text-center">
                <BookOpen className="w-8 h-8 text-muted-foreground/30 mx-auto mb-2" />
                <p className="text-sm text-muted-foreground">No research notes yet</p>
                <p className="text-xs text-muted-foreground mt-1">Save AI responses and analysis to notes</p>
              </div>
            ) : (
              notes.slice(0, 6).map(note => (
                <div key={note.id} className="p-3 rounded-lg bg-secondary/30 hover:bg-secondary/50 transition-colors cursor-pointer">
                  <div className="text-sm font-medium text-foreground truncate">{note.title}</div>
                  <div className="text-xs text-muted-foreground mt-0.5 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    Updated {new Date(note.updated_at).toLocaleDateString()}
                  </div>
                </div>
              ))
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default DashboardView;
