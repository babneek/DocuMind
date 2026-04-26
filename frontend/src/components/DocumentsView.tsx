import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FileText, Upload, Trash2, Eye, Search, Clock, CheckCircle, Loader2, RotateCcw } from "lucide-react";
import { getDocuments, deleteDocument, uploadDocument, summarizeDocument, Document } from "../lib/api";

const DocumentsView = () => {
  const [docs, setDocs] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      if (docs.some((doc) => doc.status.toLowerCase().includes("processing"))) {
        loadDocuments();
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [docs]);

  const loadDocuments = async () => {
    try {
      console.log('[DocumentsView] Loading documents...');
      const documents = await getDocuments();
      console.log('[DocumentsView] Loaded documents:', documents);
      setDocs(documents);
    } catch (error) {
      console.error('[DocumentsView] Failed to load documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const filtered = docs.filter((d) => d.file_name.toLowerCase().includes(searchQuery.toLowerCase()));

  const handleFileSelect = (files: FileList | null) => {
    if (files && files[0]) {
      console.log('[DocumentsView] File selected:', files[0].name, 'Size:', files[0].size);
      handleUpload(files[0]);
    }
  };

  const handleUpload = async (file: File) => {
    setUploading(true);
    try {
      console.log('[DocumentsView] Starting upload for file:', file.name);
      const response = await uploadDocument(file);
      console.log('[DocumentsView] Upload successful:', response);
      alert(`✅ File "${file.name}" uploaded successfully!\nStatus: ${response.status}`);
      
      console.log('[DocumentsView] Reloading documents after upload...');
      await loadDocuments();
    } catch (error: any) {
      console.error('[DocumentsView] Upload failed:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Upload failed';
      alert(`❌ Error uploading file: ${errorMsg}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleUpload(files[0]);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteDocument(id);
      setDocs((prev) => prev.filter((d) => d.id !== id));
    } catch (error) {
      console.error('Delete failed:', error);
    }
  };

  const handleSummarize = async (id: number) => {
    try {
      const result = await summarizeDocument(id);
      window.alert(`Summary:\n\n${result.summary}`);
    } catch (error) {
      console.error('Summary failed:', error);
      window.alert('Failed to fetch summary.');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-heading text-2xl font-bold text-foreground">Legal Documents</h1>
          <p className="text-sm text-muted-foreground mt-1">{docs.length} documents uploaded</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={loadDocuments}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-secondary text-foreground font-medium text-sm hover:bg-secondary/80 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
            Refresh
          </button>
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-primary text-primary-foreground font-heading font-semibold text-sm hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <Upload className="w-4 h-4" />
                Upload Document
              </>
            )}
          </button>
        </div>
      </div>

      <motion.div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
          dragOver ? "border-primary bg-primary/5" : "border-border/50"
        }`}
      >
        <Upload className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
        <p className="text-sm text-muted-foreground">
          Drag & drop files here, or{" "}
          <button onClick={() => fileInputRef.current?.click()} className="text-primary hover:underline">
            browse
          </button>
        </p>
        <p className="text-xs text-muted-foreground mt-1">PDF, DOCX, TXT — Contracts, Agreements, Judgments, Petitions</p>
        <input ref={fileInputRef} type="file" className="hidden" accept=".pdf,.docx,.txt,.md" onChange={(e) => handleFileSelect(e.target.files)} />
      </motion.div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search documents..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-secondary/50 border border-border/50 text-foreground placeholder:text-muted-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
        />
      </div>

      <div className="space-y-2">
        <AnimatePresence>
          {filtered.map((doc, i) => (
            <motion.div
              key={doc.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ delay: i * 0.05 }}
              className="glass-panel-hover p-4 flex items-center gap-4"
            >
              <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                <FileText className="w-5 h-5 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-foreground truncate">{doc.file_name}</div>
                <div className="text-xs text-muted-foreground flex items-center gap-2 mt-0.5">
                  <Clock className="w-3 h-3" /> {new Date(doc.upload_date).toLocaleDateString()}
                </div>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                {doc.status === "processing" ? (
                  <span className="flex items-center gap-1 text-xs text-accent">
                    <Loader2 className="w-3 h-3 animate-spin" /> Processing
                  </span>
                ) : doc.status === "ready" ? (
                  <span className="flex items-center gap-1 text-xs text-primary">
                    <CheckCircle className="w-3 h-3" /> Ready
                  </span>
                ) : doc.status?.toLowerCase().startsWith("error") ? (
                  <span className="flex items-center gap-1 text-xs text-destructive">
                    Error
                  </span>
                ) : (
                  <span className="flex items-center gap-1 text-xs text-muted-foreground">
                    {doc.status}
                  </span>
                )}
                <button
                  onClick={() => handleSummarize(doc.id)}
                  className="p-1.5 rounded-md hover:bg-secondary transition-colors text-muted-foreground hover:text-foreground"
                >
                  <Eye className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleDelete(doc.id)}
                  className="p-1.5 rounded-md hover:bg-destructive/10 transition-colors text-muted-foreground hover:text-destructive"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default DocumentsView;
