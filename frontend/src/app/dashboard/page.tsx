"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { fetchAuthSession, signOut } from "aws-amplify/auth";
import ReactMarkdown from "react-markdown";
import {
  FiPlus,
  FiBook,
  FiArrowRight,
  FiBell,
  FiSun,
  FiMoon,
  FiMenu,
  FiX,
} from "react-icons/fi";

export default function ChatPage() {
  const router = useRouter();

  const [query, setQuery] = useState("");
  const [darkMode, setDarkMode] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [emailSent, setEmailSent] = useState(false);

  const [historyOpen, setHistoryOpen] = useState(false);
  const [history, setHistory] = useState<any[]>([]);

  const toggleTheme = () => setDarkMode(!darkMode);
  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);

  const handleLogout = async () => {
    await signOut();
    router.push("/");
  };

  const fetchHistory = async () => {
    const session = await fetchAuthSession();
    const token = session.tokens?.idToken?.toString();

    const res = await fetch("https://synthera-django-777268942678.asia-south1.run.app/api/chat-history", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const json = await res.json();
    setHistory(json);
    setHistoryOpen(true);
  };

  const runAgent = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setResult(null);
    setEmailSent(false);

    const session = await fetchAuthSession();
    const token = session.tokens?.idToken?.toString();

    const res = await fetch(
      "http://3.111.30.223:8080/agent-run",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ user_input: query }),
      }
    );

    const json = await res.json();

    if (json.status === "success") {
      setResult(json.data);
      setEmailSent(true);
    }

    setLoading(false);
  };

  return (
    <div className={`min-h-screen ${darkMode ? "bg-black text-white" : "bg-white text-black"} flex`}>
      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 h-full z-40 transition-all duration-300 ${
          sidebarOpen ? "w-64" : "w-16"
        } ${darkMode ? "bg-gray-900" : "bg-gray-100"} border-r p-4`}
      >
        <div className="flex justify-between items-center mb-6">
          <h1 className="font-bold">{sidebarOpen ? "Synthera" : "🧪"}</h1>
          <button onClick={toggleSidebar}>
            {sidebarOpen ? <FiX /> : <FiMenu />}
          </button>
        </div>

        <div className="space-y-4 text-sm">
          <div className="flex gap-2 items-center">
            <FiPlus /> {sidebarOpen && "New Query"}
          </div>
          <div
            className="flex gap-2 items-center cursor-pointer hover:opacity-80"
            onClick={fetchHistory}
          >
            <FiBook /> {sidebarOpen && "History"}
          </div>
        </div>
      </aside>

      {/* Main */}
      <main className={`flex-1 px-6 py-8 ${sidebarOpen ? "ml-64" : "ml-16"}`}>
        {/* Top bar */}
        <div className="flex justify-end gap-4 mb-6">
          <FiBell />
          <button onClick={toggleTheme}>
            {darkMode ? <FiSun /> : <FiMoon />}
          </button>
          <button
            onClick={handleLogout}
            className="text-xs bg-purple-600 px-3 py-1 rounded"
          >
            Sign out
          </button>
        </div>

        {/* Input */}
        <div className="max-w-3xl mx-auto mb-6">
          <div className={`flex items-center rounded-full px-4 py-3 ${darkMode ? "bg-gray-800" : "bg-gray-200"}`}>
            <input
              className="flex-1 bg-transparent outline-none"
              placeholder="Ask a medical / market intelligence question"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={loading}
            />
            <button onClick={runAgent} disabled={loading}>
              <FiArrowRight className={loading ? "animate-spin" : ""} />
            </button>
          </div>
        </div>

        {emailSent && (
          <div className="max-w-3xl mx-auto mb-4 bg-green-600/20 border border-green-500 p-3 rounded text-sm">
            📧 Report link sent to your email
          </div>
        )}

        {result && (
          <div className="max-w-4xl mx-auto space-y-8">
            {result.web && (
              <section>
                <h2 className="text-xl font-semibold mb-2">🌐 Web Intelligence</h2>
                <div className="prose prose-invert max-w-none">
                  <ReactMarkdown>{result.web}</ReactMarkdown>
                </div>
              </section>
            )}

            {result.clinical?.active_trials && (
              <section>
                <h2 className="text-xl font-semibold mb-2">🧪 Clinical Trials</h2>
                <table className="w-full text-sm border border-gray-700">
                  <thead>
                    <tr className="bg-gray-800">
                      <th className="p-2">Title</th>
                      <th>Phase</th>
                      <th>Sponsor</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.clinical.active_trials.map((t: any) => (
                      <tr key={t.nct_id} className="border-t border-gray-700">
                        <td className="p-2">{t.title}</td>
                        <td>{t.phase}</td>
                        <td>{t.sponsor}</td>
                        <td>{t.status}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </section>
            )}

            {result.pdf_url && (
              <a
                href={result.pdf_url}
                target="_blank"
                className="inline-block bg-purple-600 px-4 py-2 rounded"
              >
                📄 Download PDF
              </a>
            )}
          </div>
        )}
      </main>

      {/* History Drawer */}
      {historyOpen && (
        <div className="fixed top-0 right-0 h-full w-96 bg-gray-900 border-l p-4 z-50 overflow-y-auto">
          <div className="flex justify-between mb-4">
            <h2 className="font-semibold">🕒 Chat History</h2>
            <button onClick={() => setHistoryOpen(false)}>
              <FiX />
            </button>
          </div>

          <div className="space-y-3">
            {history.map((h) => (
              <div
                key={h.id}
                className="p-3 bg-gray-800 rounded cursor-pointer hover:bg-gray-700"
                onClick={() => {
                  setResult(h.data);
                  setHistoryOpen(false);
                }}
              >
                <div className="text-xs opacity-60">
                  {new Date(h.timestamp).toLocaleString()}
                </div>
                <div className="text-sm font-medium truncate">
                  {h.data.user_input}
                </div>
                <a
                  href={h.file_url}
                  target="_blank"
                  className="text-xs text-purple-400"
                  onClick={(e) => e.stopPropagation()}
                >
                  📄 PDF
                </a>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
