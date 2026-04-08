import { motion } from "framer-motion";
import { FileText, Brain, Search, TrendingUp, Clock } from "lucide-react";
import { useEffect, useState } from "react";
import { getDocuments, getNotes, type Document, type Note } from "../lib/api";

const DashboardView = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [docsData, notesData] = await Promise.all([
          getDocuments(),
          getNotes(),
        ]);
        setDocuments(docsData || []);
        setNotes(notesData || []);
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const stats = [
    { label: "Documents", value: documents.length.toString(), icon: FileText, change: `${documents.length} uploaded` },
    { label: "Notes", value: notes.length.toString(), icon: Brain, change: `${notes.length} created` },
    { label: "Searches", value: "—", icon: Search, change: "History" },
    { label: "Insights", value: "—", icon: TrendingUp, change: "Coming soon" },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-heading text-2xl font-bold text-foreground">Dashboard</h1>
        <p className="text-sm text-muted-foreground mt-1">Your document intelligence overview</p>
      </div>

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
              <span className="text-xs text-muted-foreground">{stat.change}</span>
            </div>
            <div className="font-heading text-2xl font-bold text-foreground">{stat.value}</div>
            <div className="text-xs text-muted-foreground mt-1">{stat.label}</div>
          </motion.div>
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Recent documents */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-panel p-6"
        >
          <h2 className="font-heading font-semibold text-foreground mb-4 flex items-center gap-2">
            <FileText className="w-4 h-4 text-primary" />
            Recent Documents
          </h2>
          <div className="space-y-3">
            {loading ? (
              <div className="flex items-center justify-center py-8 text-muted-foreground">
                <p className="text-sm">Loading...</p>
              </div>
            ) : documents.length === 0 ? (
              <div className="flex items-center justify-center py-8 text-muted-foreground">
                <p className="text-sm">No documents uploaded yet</p>
              </div>
            ) : (
              documents.slice(0, 5).map((doc) => (
                <div key={doc.id} className="flex items-center justify-between p-3 rounded-lg bg-secondary/30 hover:bg-secondary/50 transition-colors cursor-pointer">
                  <div>
                    <div className="text-sm font-medium text-foreground">{doc.file_name}</div>
                    <div className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                      <Clock className="w-3 h-3" /> {new Date(doc.upload_date).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </motion.div>

        {/* Recent queries */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="glass-panel p-6"
        >
          <h2 className="font-heading font-semibold text-foreground mb-4 flex items-center gap-2">
            <Brain className="w-4 h-4 text-primary" />
            Recent AI Queries
          </h2>
          <div className="space-y-3">
            {loading ? (
              <div className="flex items-center justify-center py-8 text-muted-foreground">
                <p className="text-sm">Loading...</p>
              </div>
            ) : notes.length === 0 ? (
              <div className="flex items-center justify-center py-8 text-muted-foreground">
                <p className="text-sm">No queries yet</p>
              </div>
            ) : (
              notes.slice(0, 5).map((note) => (
                <div key={note.id} className="p-3 rounded-lg bg-secondary/30 hover:bg-secondary/50 transition-colors cursor-pointer">
                  <div className="text-sm text-foreground truncate">{note.title}</div>
                  <div className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                    <Clock className="w-3 h-3" /> {new Date(note.created_at).toLocaleDateString()}
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
