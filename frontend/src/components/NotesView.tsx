import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { BookOpen, Plus, Save, Trash2, Download, Bold, Italic, List, Wand2, Loader, ChevronDown } from "lucide-react";
import { createNote, deleteNote, getNotes, updateNote, restructureNote, Note } from "../lib/api";
import { StructureEditor } from "./StructureEditor";
import html2pdf from "html2pdf.js";

const NotesView = () => {
  const [notes, setNotes] = useState<Note[]>([]);
  const [selectedNoteId, setSelectedNoteId] = useState<number | null>(null);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("<p>Start writing your note here...</p>");
  const [loading, setLoading] = useState(false);
  const [newNoteName, setNewNoteName] = useState("");
  const [showStructureSettings, setShowStructureSettings] = useState(false);
  const [showStructureEditor, setShowStructureEditor] = useState(false);
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [structureType, setStructureType] = useState("summary");
  const [customSections, setCustomSections] = useState("");
  const [style, setStyle] = useState("headings");
  const [previewContent, setPreviewContent] = useState<string | null>(null);
  const [isPreviewMode, setIsPreviewMode] = useState(false);
  const editorRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadNotes();
  }, []);

  useEffect(() => {
    if (selectedNoteId) {
      // Cancel preview mode if switching notes
      if (isPreviewMode) {
        setIsPreviewMode(false);
        setPreviewContent(null);
      }
      const note = notes.find((item) => item.id === selectedNoteId);
      if (note) {
        setTitle(note.title);
        setContent(note.content || "<p></p>");
      }
    }
  }, [selectedNoteId, notes]);

  // Close export menu when clicking elsewhere
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target.closest('[data-export-menu]')) {
        setShowExportMenu(false);
      }
    };

    if (showExportMenu) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [showExportMenu]);

  const loadNotes = async () => {
    try {
      const loaded = await getNotes();
      setNotes(loaded);
      if (!selectedNoteId && loaded.length > 0) {
        setSelectedNoteId(loaded[0].id);
      }
    } catch (error) {
      console.error("Failed to load notes:", error);
    }
  };

  const handleCreateNote = async () => {
    const label = newNoteName.trim() || "Untitled Note";
    try {
      setLoading(true);
      const note = await createNote({ title: label, content: "<p></p>" });
      setNotes((prev) => [note, ...prev]);
      setSelectedNoteId(note.id);
      setNewNoteName("");
    } catch (error) {
      console.error("Create note failed:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveNote = async () => {
    if (!selectedNoteId) return;
    try {
      setLoading(true);
      const updated = await updateNote(selectedNoteId, { title, content });
      setNotes((prev) => prev.map((note) => (note.id === updated.id ? updated : note)));
      alert("Note saved successfully.");
    } catch (error) {
      console.error("Save note failed:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleRestructureNote = async () => {
    if (!selectedNoteId) return;
    try {
      setLoading(true);
      // Store original content for preview mode
      setPreviewContent(content);
      setIsPreviewMode(true);
      
      const options = {
        structure_type: structureType,
        custom_prompt: customSections,
        custom_sections: "",
        style: "headings"
      };
      const updated = await restructureNote(selectedNoteId, options);
      // Show restructured content as preview (don't save yet)
      setContent(updated.content);
      setShowStructureSettings(false);
    } catch (error) {
      console.error("Restructure note failed:", error);
      alert("Failed to restructure note. Check console for details.");
      setIsPreviewMode(false);
      setPreviewContent(null);
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptRestructure = async () => {
    if (!selectedNoteId) return;
    try {
      setLoading(true);
      // Save the restructured content
      await updateNote(selectedNoteId, { title, content });
      setNotes((prev) =>
        prev.map((note) =>
          note.id === selectedNoteId ? { ...note, content } : note
        )
      );
      setIsPreviewMode(false);
      setPreviewContent(null);
      alert("Restructure saved successfully.");
    } catch (error) {
      console.error("Save restructure failed:", error);
      alert("Failed to save restructure. Check console for details.");
    } finally {
      setLoading(false);
    }
  };

  const handleDiscardRestructure = () => {
    // Revert to original content
    if (previewContent !== null) {
      setContent(previewContent);
      setIsPreviewMode(false);
      setPreviewContent(null);
    }
  };

  const handleDeleteNote = async () => {
    if (!selectedNoteId) return;
    if (!window.confirm("Delete this note permanently?")) return;
    try {
      setLoading(true);
      await deleteNote(selectedNoteId);
      
      // Update notes list and select next note
      const updatedNotes = notes.filter((note) => note.id !== selectedNoteId);
      setNotes(updatedNotes);
      
      // Select next note or clear if no notes left
      if (updatedNotes.length > 0) {
        setSelectedNoteId(updatedNotes[0].id);
      } else {
        setSelectedNoteId(null);
        setTitle("");
        setContent("<p></p>");
      }
    } catch (error) {
      console.error("Delete note failed:", error);
    } finally {
      setLoading(false);
    }
  };

  const applyFormat = (command: string) => {
    if (!editorRef.current) return;
    
    const editor = editorRef.current;
    editor.focus();
    
    try {
      document.execCommand(command, false, "");
      setContent(editor.innerHTML);
    } catch (error) {
      console.error(`Failed to execute command: ${command}`, error);
    }
  };

  const downloadFile = (filename: string, content: string, mimeType: string) => {
    const blob = new Blob([content], { type: mimeType });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  const handleExportPdf = () => {
    const note = notes.find((item) => item.id === selectedNoteId);
    if (!note) return;

    const element = document.createElement("div");
    element.innerHTML = `
      <div style="padding: 28px; font-family: Arial, sans-serif;">
        <h1 style="font-size: 24px; margin-bottom: 18px;">${note.title}</h1>
        <div style="line-height: 1.6;">
          ${content}
        </div>
      </div>
    `;

    const options = {
      margin: 10,
      filename: `${note.title}.pdf`,
      image: { type: "jpeg", quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { orientation: "portrait", unit: "mm", format: "a4" }
    };

    html2pdf()
      .set(options)
      .from(element)
      .save()
      .then(() => {
        setShowExportMenu(false);
      });
  };

  const handleExportWord = () => {
    const note = notes.find((item) => item.id === selectedNoteId);
    if (!note) return;

    const htmlContent = `
      <html xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word">
        <head>
          <meta charset="UTF-8">
          <title>${note.title}</title>
          <style>
            body { font-family: 'Calibri', sans-serif; line-height: 1.5; padding: 20px; }
            h1 { font-size: 28px; margin: 20px 0; font-weight: bold; }
            p { margin: 10px 0; }
          </style>
        </head>
        <body>
          <h1>${note.title}</h1>
          ${content}
        </body>
      </html>
    `;

    downloadFile(`${note.title}.docx`, htmlContent, "application/vnd.openxmlformats-officedocument.wordprocessingml.document");
    setShowExportMenu(false);
  };

  const handleExportText = () => {
    const note = notes.find((item) => item.id === selectedNoteId);
    if (!note) return;

    const plainText = content.replace(/<[^>]*>/g, "").replace(/&nbsp;/g, " ").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
    const text = `${note.title}\n${'='.repeat(note.title.length)}\n\n${plainText}`;

    downloadFile(`${note.title}.txt`, text, "text/plain");
    setShowExportMenu(false);
  };

  const handleExportHtml = () => {
    const note = notes.find((item) => item.id === selectedNoteId);
    if (!note) return;

    const html = `
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>${note.title}</title>
    <style>
      body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 40px; max-width: 800px; margin: 0 auto; line-height: 1.6; }
      h1 { color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }
      h2 { color: #555; margin-top: 20px; }
      h3 { color: #777; }
      p { color: #666; }
      ul, ol { margin: 10px 0; }
      li { margin: 5px 0; }
      pre { background: #f4f4f4; padding: 10px; border-radius: 4px; overflow-x: auto; }
      code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; }
    </style>
  </head>
  <body>
    <h1>${note.title}</h1>
    ${content}
  </body>
</html>
    `;

    downloadFile(`${note.title}.html`, html, "text/html");
    setShowExportMenu(false);
  };

  const activeNote = selectedNoteId ? notes.find((note) => note.id === selectedNoteId) : null;

  return (
    <div className="grid lg:grid-cols-[280px_1fr] gap-6 h-[calc(100vh-6rem)]">
      <div className="glass-panel p-5 flex flex-col gap-4 overflow-hidden">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h1 className="font-heading text-xl font-bold text-foreground">Notes</h1>
            <p className="text-sm text-muted-foreground">Create, edit, and export your notes.</p>
          </div>
          <BookOpen className="w-6 h-6 text-primary" />
        </div>

        <div className="flex gap-2">
          <input
            type="text"
            value={newNoteName}
            onChange={(e) => setNewNoteName(e.target.value)}
            placeholder="New note title"
            className="flex-1 rounded-lg bg-secondary/50 border border-border/50 px-3 py-2 text-sm text-foreground focus:outline-none"
          />
          <button
            onClick={handleCreateNote}
            disabled={loading}
            className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            <Plus className="w-4 h-4 mr-1 inline" /> Create
          </button>
        </div>

        <div className="overflow-y-auto space-y-2 pr-1 flex-1" style={{ maxHeight: "calc(100vh - 240px)" }}>
          {notes && notes.length > 0 ? (
            notes.map((note) => (
              <div
                key={note.id}
                className="group relative"
              >
                <button
                  onClick={() => {
                    setSelectedNoteId(note.id);
                  }}
                  className={`w-full text-left rounded-2xl p-3 transition-all ${
                    note.id === selectedNoteId
                      ? "bg-primary/10 border border-primary"
                      : "bg-secondary/40 hover:bg-secondary/60"
                  }`}
                >
                  <div className="font-medium text-foreground truncate">{note.title}</div>
                  <div className="text-xs text-muted-foreground mt-1">
                    Updated {new Date(note.updated_at).toLocaleDateString()}
                  </div>
                </button>
                {/* Delete button on hover */}
                <button
                  onClick={async (e) => {
                    e.stopPropagation();
                    if (window.confirm("Delete this note permanently?")) {
                      try {
                        setLoading(true);
                        await deleteNote(note.id);

                        const updatedNotes = notes.filter((n) => n.id !== note.id);
                        setNotes(updatedNotes);

                        // Clear selection if deleted note was selected
                        if (selectedNoteId === note.id) {
                          if (updatedNotes.length > 0) {
                            setSelectedNoteId(updatedNotes[0].id);
                          } else {
                            setSelectedNoteId(null);
                            setTitle("");
                            setContent("<p></p>");
                          }
                        }
                      } catch (error) {
                        console.error("Delete note failed:", error);
                      } finally {
                        setLoading(false);
                      }
                    }
                  }}
                  className="absolute right-2 top-2 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg bg-destructive/80 hover:bg-destructive p-2 text-destructive-foreground z-10"
                  title="Delete note"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <p>No notes yet. Create one to get started!</p>
            </div>
          )}
        </div>
      </div>

      <div className="glass-panel p-5 flex flex-col h-full">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
          <div>
            <h1 className="font-heading text-xl font-bold text-foreground">{activeNote ? activeNote.title : "Create or select a note"}</h1>
            {!activeNote && <p className="text-sm text-muted-foreground">Choose an existing note or create a new one to start writing.</p>}
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <button 
              onClick={() => applyFormat("bold")} 
              disabled={!activeNote}
              className="rounded-lg bg-secondary px-3 py-2 text-sm hover:bg-secondary/80 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Bold className="w-4 h-4 inline" /> Bold
            </button>
            <button 
              onClick={() => applyFormat("italic")} 
              disabled={!activeNote}
              className="rounded-lg bg-secondary px-3 py-2 text-sm hover:bg-secondary/80 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Italic className="w-4 h-4 inline" /> Italic
            </button>
          </div>
        </div>

        <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Note title"
            className="flex-1 rounded-lg bg-secondary/50 border border-border/50 px-3 py-2 text-sm text-foreground focus:outline-none"
            disabled={!activeNote}
          />
          <div className="flex gap-2 items-center flex-wrap">
            <button
              onClick={handleSaveNote}
              disabled={!activeNote || loading}
              className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Save className="w-4 h-4 mr-1 inline" /> Save
            </button>
            <button
              onClick={() => setShowStructureSettings(!showStructureSettings)}
              disabled={!activeNote || loading}
              className="rounded-lg bg-secondary px-4 py-2 text-sm font-semibold text-foreground hover:bg-secondary/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Wand2 className="w-4 h-4 mr-1 inline" /> Auto-Structure
            </button>
            
            {/* Export dropdown menu */}
            <div className="relative" data-export-menu>
              <button
                onClick={() => setShowExportMenu(!showExportMenu)}
                disabled={!activeNote || loading}
                className="rounded-lg bg-secondary px-4 py-2 text-sm font-semibold text-foreground hover:bg-secondary/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
              >
                <Download className="w-4 h-4" /> Export <ChevronDown className="w-3 h-3" />
              </button>
              
              {showExportMenu && activeNote && (
                <div className="absolute right-0 top-full mt-2 min-w-max bg-secondary border border-border/50 rounded-lg shadow-lg z-50">
                  <button
                    onClick={handleExportPdf}
                    className="w-full px-4 py-2 text-left text-sm hover:bg-secondary/80 transition-colors flex items-center gap-2 border-b border-border/50"
                  >
                    <Download className="w-4 h-4" /> Export as PDF
                  </button>
                  <button
                    onClick={handleExportWord}
                    className="w-full px-4 py-2 text-left text-sm hover:bg-secondary/80 transition-colors flex items-center gap-2 border-b border-border/50"
                  >
                    <Download className="w-4 h-4" /> Export as Word (.docx)
                  </button>
                  <button
                    onClick={handleExportText}
                    className="w-full px-4 py-2 text-left text-sm hover:bg-secondary/80 transition-colors flex items-center gap-2 border-b border-border/50"
                  >
                    <Download className="w-4 h-4" /> Export as Text (.txt)
                  </button>
                  <button
                    onClick={handleExportHtml}
                    className="w-full px-4 py-2 text-left text-sm hover:bg-secondary/80 transition-colors flex items-center gap-2"
                  >
                    <Download className="w-4 h-4" /> Export as HTML
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {showStructureSettings && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-4 p-4 rounded-lg bg-secondary/20 border border-border/50 max-h-96 overflow-y-auto"
          >
            <h3 className="text-sm font-semibold mb-3">Choose Structure Type</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2 mb-4">
              {[
                { value: "summary", label: "Summary", desc: "Quick summary + key points" },
                { value: "tasks", label: "Action Items", desc: "Tasks & deadlines" },
                { value: "meeting_notes", label: "Meeting Notes", desc: "Professional notes" },
                { value: "timeline", label: "Timeline", desc: "Chronological events" },
                { value: "checklist", label: "Checklist", desc: "Actionable checklist" },
                { value: "report", label: "Formal Report", desc: "Professional report" },
                { value: "comparison", label: "Comparison", desc: "Pros & cons" },
                { value: "faq", label: "FAQ", desc: "Q&A format" },
                { value: "json", label: "Structured Data", desc: "JSON format" },
              ].map((option) => (
                <button
                  key={option.value}
                  onClick={() => setStructureType(option.value)}
                  className={`p-2 rounded-lg border-2 text-left transition-all text-xs ${
                    structureType === option.value
                      ? "border-primary bg-primary/10"
                      : "border-border/50 hover:border-border"
                  }`}
                >
                  <div className="font-semibold text-xs">{option.label}</div>
                  <div className="text-xs text-muted-foreground">{option.desc}</div>
                </button>
              ))}
            </div>

            {/* Custom prompt section */}
            <div className="mb-4 p-3 rounded-lg bg-secondary/30 border border-border/30">
              <label className="block text-xs font-semibold mb-2">Custom Prompt (Optional)</label>
              <textarea
                placeholder="Enter your custom restructuring instructions..."
                value={customSections}
                onChange={(e) => setCustomSections(e.target.value)}
                className="w-full rounded-lg bg-secondary/50 border border-border/50 px-3 py-2 text-xs focus:outline-none h-16 resize-none"
              />
              <p className="text-xs text-muted-foreground mt-1">Leave empty to use selected structure type</p>
            </div>

            <div className="flex gap-2">
              <button
                onClick={handleRestructureNote}
                disabled={loading}
                className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <motion.span
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      className="inline-block"
                    >
                      <Loader className="w-4 h-4 mr-1 inline" />
                    </motion.span>
                    Restructuring...
                  </>
                ) : (
                  <>
                    <Wand2 className="w-4 h-4 mr-1 inline" /> Apply
                  </>
                )}
              </button>
              <button
                onClick={() => setShowStructureSettings(false)}
                className="rounded-lg bg-secondary px-4 py-2 text-sm font-semibold text-foreground hover:bg-secondary/80 transition-colors"
              >
                Cancel
              </button>
            </div>
          </motion.div>
        )}

        {isPreviewMode && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-4 p-4 rounded-lg bg-yellow-500/10 border-2 border-yellow-500/50 flex items-center justify-between gap-3"
          >
            <div>
              <p className="text-sm font-semibold text-yellow-700">Preview Mode</p>
              <p className="text-xs text-yellow-700/70">This is a preview of the restructured content. Save to apply or discard to keep the original.</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleAcceptRestructure}
                disabled={loading}
                className="rounded-lg bg-green-600 px-4 py-2 text-sm font-semibold text-white hover:bg-green-700 transition-colors disabled:opacity-50"
              >
                Save Structure
              </button>
              <button
                onClick={handleDiscardRestructure}
                disabled={loading}
                className="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700 transition-colors disabled:opacity-50"
              >
                Discard
              </button>
            </div>
          </motion.div>
        )}

        <div className="flex-1 overflow-hidden rounded-3xl border border-border/50 bg-background p-4">
          <div
            ref={editorRef}
            contentEditable={!!activeNote}
            suppressContentEditableWarning
            onInput={(e) => setContent((e.target as HTMLDivElement).innerHTML)}
            className={`min-h-[420px] outline-none text-sm ${activeNote ? "" : "opacity-50 cursor-not-allowed"}`}
            dangerouslySetInnerHTML={{ __html: content }}
          />
        </div>
      </div>

      {showStructureEditor && selectedNoteId && (
        <StructureEditor
          noteId={selectedNoteId}
          onClose={() => setShowStructureEditor(false)}
          onApply={(sections) => {
            setContent(`<p>Structure updated with ${sections.length} sections</p>`);
            loadNotes();
          }}
        />
      )}
    </div>
  );
};

export default NotesView;
