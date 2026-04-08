import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, ChevronUp, Plus, Trash2, X } from "lucide-react";
import { extractStructure, rebuildNote } from "../lib/api";

interface Section {
  id: string;
  title: string;
  content: string;
  order: number;
}

interface StructureEditorProps {
  noteId: number;
  onClose: () => void;
  onApply: (sections: Section[]) => void;
}

export const StructureEditor = ({ noteId, onClose, onApply }: StructureEditorProps) => {
  const [sections, setSections] = useState<Section[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [applying, setApplying] = useState(false);

  useEffect(() => {
    loadStructure();
  }, [noteId]);

  const loadStructure = async () => {
    try {
      setLoading(true);
      const data = await extractStructure(noteId);
      setSections(data.sections || []);
    } catch (error) {
      console.error("Failed to extract structure:", error);
    } finally {
      setLoading(false);
    }
  };

  const moveSection = (index: number, direction: "up" | "down") => {
    const newSections = [...sections];
    const newIndex = direction === "up" ? index - 1 : index + 1;

    if (newIndex < 0 || newIndex >= newSections.length) return;

    [newSections[index], newSections[newIndex]] = [newSections[newIndex], newSections[index]];

    newSections.forEach((s, i) => (s.order = i));
    setSections(newSections);
  };

  const updateSection = (id: string, field: "title" | "content", value: string) => {
    setSections(
      sections.map((s) => (s.id === id ? { ...s, [field]: value } : s))
    );
  };

  const addSection = () => {
    const newId = `sec_${Date.now()}`;
    const newSection: Section = {
      id: newId,
      title: "New Section",
      content: "Add content here...",
      order: sections.length,
    };
    setSections([...sections, newSection]);
    setEditingId(newId);
  };

  const deleteSection = (id: string) => {
    const filtered = sections.filter((s) => s.id !== id);
    filtered.forEach((s, i) => (s.order = i));
    setSections(filtered);
  };

  const handleApply = async () => {
    try {
      setApplying(true);
      await rebuildNote(noteId, sections);
      onApply(sections);
      onClose();
    } catch (error) {
      console.error("Failed to rebuild note:", error);
    } finally {
      setApplying(false);
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-background rounded-lg p-8 max-w-2xl w-full mx-4">
          <p className="text-muted-foreground">Loading structure...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="bg-background rounded-lg shadow-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto"
      >
        {/* Header */}
        <div className="sticky top-0 bg-background border-b border-border/50 p-4 flex justify-between items-center">
          <h2 className="text-lg font-bold">Structure Editor</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-secondary rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Sections List */}
        <div className="p-4">
          <AnimatePresence>
            {sections.map((section, index) => (
              <motion.div
                key={section.id}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="mb-4 p-4 bg-secondary/50 rounded-lg border border-border/50"
              >
                {/* Title */}
                <div className="flex gap-2 items-start mb-3">
                  <div className="flex flex-col gap-1">
                    <button
                      onClick={() => moveSection(index, "up")}
                      disabled={index === 0}
                      className="p-1 hover:bg-secondary rounded disabled:opacity-30 transition-colors"
                    >
                      <ChevronUp className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => moveSection(index, "down")}
                      disabled={index === sections.length - 1}
                      className="p-1 hover:bg-secondary rounded disabled:opacity-30 transition-colors"
                    >
                      <ChevronDown className="w-4 h-4" />
                    </button>
                  </div>

                  <input
                    type="text"
                    value={section.title}
                    onChange={(e) => updateSection(section.id, "title", e.target.value)}
                    onFocus={() => setEditingId(section.id)}
                    onBlur={() => setEditingId(null)}
                    className="flex-1 font-semibold bg-background border border-border/50 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                  />

                  <button
                    onClick={() => deleteSection(section.id)}
                    className="p-2 hover:bg-red-500/20 text-red-500 rounded transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                {/* Content */}
                <textarea
                  value={section.content}
                  onChange={(e) => updateSection(section.id, "content", e.target.value)}
                  onFocus={() => setEditingId(section.id)}
                  onBlur={() => setEditingId(null)}
                  rows={3}
                  className="w-full bg-background border border-border/50 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                  placeholder="Edit section content..."
                />
              </motion.div>
            ))}
          </AnimatePresence>

          {sections.length === 0 && (
            <p className="text-muted-foreground text-center py-8">
              No sections found. Your note might be unstructured.
            </p>
          )}
        </div>

        {/* Add Section Button */}
        <div className="px-4 py-2 border-t border-border/50">
          <button
            onClick={addSection}
            className="w-full flex items-center justify-center gap-2 py-2 px-4 rounded-lg bg-secondary hover:bg-secondary/80 transition-colors text-foreground font-medium"
          >
            <Plus className="w-4 h-4" /> Add Section
          </button>
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-background border-t border-border/50 p-4 flex gap-2 justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-secondary hover:bg-secondary/80 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleApply}
            disabled={applying}
            className="px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50 font-medium flex items-center gap-2"
          >
            {applying ? "Applying..." : "Apply Changes"}
          </button>
        </div>
      </motion.div>
    </div>
  );
};
