import { useState } from "react";
import AuthScreen from "../components/AuthScreen";
import NavShell from "../components/NavShell";
import DashboardView from "../components/DashboardView";
import DocumentsView from "../components/DocumentsView";
import QueryView from "../components/QueryView";
import NotesView from "../components/NotesView";

const Index = () => {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'));
  const [currentView, setCurrentView] = useState("dashboard");

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  if (!token) {
    return <AuthScreen onLogin={(token) => { localStorage.setItem('token', token); setToken(token); }} />;
  }

  return (
    <NavShell currentView={currentView} onNavigate={setCurrentView} onLogout={handleLogout}>
      {currentView === "dashboard" && <DashboardView />}
      {currentView === "documents" && <DocumentsView />}
      {currentView === "query" && <QueryView />}
      {currentView === "notes" && <NotesView />}
    </NavShell>
  );
};

export default Index;
