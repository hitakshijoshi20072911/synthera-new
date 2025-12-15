// "use client";

// import { useState } from "react";
// import { useRouter } from "next/navigation";
// import { fetchAuthSession, signOut } from "aws-amplify/auth";
// import ReactMarkdown from "react-markdown";
// import {
//   FiPlus,
//   FiBook,
//   FiArrowRight,
//   FiBell,
//   FiSun,
//   FiMoon,
//   FiMenu,
//   FiX,
// } from "react-icons/fi";

// export default function ChatPage() {
//   const router = useRouter();

//   const [query, setQuery] = useState("");
//   const [darkMode, setDarkMode] = useState(true);
//   const [sidebarOpen, setSidebarOpen] = useState(true);
//   const [loading, setLoading] = useState(false);
//   const [result, setResult] = useState<any>(null);
//   const [emailSent, setEmailSent] = useState(false);

//   const [historyOpen, setHistoryOpen] = useState(false);
//   const [history, setHistory] = useState<any[]>([]);

//   const toggleTheme = () => setDarkMode(!darkMode);
//   const toggleSidebar = () => setSidebarOpen(!sidebarOpen);

//   const handleLogout = async () => {
//     await signOut();
//     router.push("/");
//   };

//   const fetchHistory = async () => {
//     const session = await fetchAuthSession();
//     const token = session.tokens?.idToken?.toString();

//     const res = await fetch(
//       "https://synthera-django-777268942678.asia-south1.run.app/api/chat-history",
//       {
//         headers: {
//           Authorization: `Bearer ${token}`,
//         },
//       }
//     );

//     const json = await res.json();
//     setHistory(json);
//     setHistoryOpen(true);
//   };

//   const runAgent = async () => {
//     if (!query.trim()) return;

//     setLoading(true);
//     setResult(null);
//     setEmailSent(false);

//     const session = await fetchAuthSession();
//     const token = session.tokens?.idToken?.toString();

//     const res = await fetch("/api/proxy/agent-run", {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json",
//         Authorization: `Bearer ${token}`,
//       },
//       body: JSON.stringify({ user_input: query }),
//     });

//     const json = await res.json();

//     if (json.status === "success") {
//       setResult(json.data);
//       setEmailSent(true);
//     }

//     setLoading(false);
//   };

//   return (
//     <div
//       className={`min-h-screen ${
//         darkMode ? "bg-black text-white" : "bg-white text-black"
//       } flex`}
//     >
//       {/* Sidebar */}
//       <aside
//         className={`fixed top-0 left-0 h-full z-40 transition-all duration-300 ${
//           sidebarOpen ? "w-64" : "w-16"
//         } ${
//           darkMode ? "bg-gray-900" : "bg-gray-100"
//         } border-r p-4`}
//       >
//         <div className="flex justify-between items-center mb-6">
//           <h1 className="font-bold">{sidebarOpen ? "Synthera" : "🧪"}</h1>
//           <button onClick={toggleSidebar}>
//             {sidebarOpen ? <FiX /> : <FiMenu />}
//           </button>
//         </div>

//         <div className="space-y-4 text-sm">
//           <div className="flex gap-2 items-center">
//             <FiPlus /> {sidebarOpen && "New Query"}
//           </div>
//           <div
//             className="flex gap-2 items-center cursor-pointer hover:opacity-80"
//             onClick={fetchHistory}
//           >
//             <FiBook /> {sidebarOpen && "History"}
//           </div>
//         </div>
//       </aside>

//       {/* Main */}
//       <main
//         className={`flex-1 px-6 py-8 ${
//           sidebarOpen ? "ml-64" : "ml-16"
//         }`}
//       >
//         {/* Top bar */}
//         <div className="flex justify-end gap-4 mb-6">
//           <FiBell />
//           <button onClick={toggleTheme}>
//             {darkMode ? <FiSun /> : <FiMoon />}
//           </button>
//           <button
//             onClick={handleLogout}
//             className="text-xs bg-purple-600 px-3 py-1 rounded"
//           >
//             Sign out
//           </button>
//         </div>

//         {/* Input */}
//         <div className="max-w-3xl mx-auto mb-6">
//           <div
//             className={`flex items-center rounded-full px-4 py-3 ${
//               darkMode ? "bg-gray-800" : "bg-gray-200"
//             }`}
//           >
//             <input
//               className="flex-1 bg-transparent outline-none"
//               placeholder="Ask a medical / market intelligence question"
//               value={query}
//               onChange={(e) => setQuery(e.target.value)}
//               disabled={loading}
//             />
//             <button onClick={runAgent} disabled={loading}>
//               {loading ? (
//                 <div className="w-5 h-5 border-2 border-purple-400 border-t-transparent rounded-full animate-spin" />
//               ) : (
//                 <FiArrowRight />
//               )}
//             </button>
//           </div>
//         </div>

//         {/* Skeleton Loader */}
//         {loading && !result && (
//           <div className="max-w-4xl mx-auto space-y-4 animate-pulse">
//             <div className="h-6 bg-gray-700 rounded w-1/3" />
//             <div className="h-4 bg-gray-700 rounded w-full" />
//             <div className="h-4 bg-gray-700 rounded w-5/6" />
//             <div className="h-4 bg-gray-700 rounded w-2/3" />
//           </div>
//         )}

//         {emailSent && (
//           <div className="max-w-3xl mx-auto mb-4 bg-green-600/20 border border-green-500 p-3 rounded text-sm">
//             📧 Report link sent to your email
//           </div>
//         )}

//         {result && (
//           <div className="max-w-4xl mx-auto space-y-8 animate-fadeIn">
//             {result.web && (
//               <section>
//                 <h2 className="text-xl font-semibold mb-2">
//                   🌐 Web Intelligence
//                 </h2>
//                 <div className="prose prose-invert max-w-none">
//                   <ReactMarkdown>{result.web}</ReactMarkdown>
//                 </div>
//               </section>
//             )}

//             {result.clinical?.active_trials && (
//               <section>
//                 <h2 className="text-xl font-semibold mb-2">
//                   🧪 Clinical Trials
//                 </h2>
//                 <table className="w-full text-sm border border-gray-700">
//                   <thead>
//                     <tr className="bg-gray-800">
//                       <th className="p-2">Title</th>
//                       <th>Phase</th>
//                       <th>Sponsor</th>
//                       <th>Status</th>
//                     </tr>
//                   </thead>
//                   <tbody>
//                     {result.clinical.active_trials.map((t: any) => (
//                       <tr
//                         key={t.nct_id}
//                         className="border-t border-gray-700"
//                       >
//                         <td className="p-2">{t.title}</td>
//                         <td>{t.phase}</td>
//                         <td>{t.sponsor}</td>
//                         <td>{t.status}</td>
//                       </tr>
//                     ))}
//                   </tbody>
//                 </table>
//               </section>
//             )}

//             {result.pdf_url && (
//               <a
//                 href={result.pdf_url}
//                 target="_blank"
//                 className="inline-block bg-purple-600 px-4 py-2 rounded"
//               >
//                 📄 Download PDF
//               </a>
//             )}
//           </div>
//         )}
//       </main>

//       {/* History Drawer */}
//       {historyOpen && (
//         <div className="fixed top-0 right-0 h-full w-96 bg-gray-900 border-l p-4 z-50 overflow-y-auto animate-slideIn">
//           <div className="flex justify-between mb-4">
//             <h2 className="font-semibold">🕒 Chat History</h2>
//             <button onClick={() => setHistoryOpen(false)}>
//               <FiX />
//             </button>
//           </div>

//           <div className="space-y-3">
//             {history.map((h) => (
//               <div
//                 key={h.id}
//                 className="p-3 bg-gray-800 rounded cursor-pointer hover:bg-gray-700"
//                 onClick={() => {
//                   setResult(h.data);
//                   setHistoryOpen(false);
//                 }}
//               >
//                 <div className="text-xs opacity-60">
//                   {new Date(h.timestamp).toLocaleString()}
//                 </div>
//                 <div className="text-sm font-medium truncate">
//                   {h.data.user_input}
//                 </div>
//                 <a
//                   href={h.file_url}
//                   target="_blank"
//                   className="text-xs text-purple-400"
//                   onClick={(e) => e.stopPropagation()}
//                 >
//                   📄 PDF
//                 </a>
//               </div>
//             ))}
//           </div>
//         </div>
//       )}

//       {/* Global Loader Overlay */}
//       {loading && (
//         <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center">
//           <div className="flex flex-col items-center gap-4">
//             <div className="w-10 h-10 border-4 border-purple-500 border-t-transparent rounded-full animate-spin" />
//             <p className="text-sm text-purple-200 animate-pulse">
//               Running agent, generating intelligence…
//             </p>
//           </div>
//         </div>
//       )}

//       {/* Animations */}
//       <style jsx global>{`
//         @keyframes fadeIn {
//           from {
//             opacity: 0;
//             transform: translateY(6px);
//           }
//           to {
//             opacity: 1;
//             transform: translateY(0);
//           }
//         }
//         .animate-fadeIn {
//           animation: fadeIn 0.4s ease-out;
//         }

//         @keyframes slideIn {
//           from {
//             transform: translateX(100%);
//           }
//           to {
//             transform: translateX(0);
//           }
//         }
//         .animate-slideIn {
//           animation: slideIn 0.25s ease-out;
//         }
//       `}</style>
//     </div>
//   );
// }





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
  FiZap,
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
  const [loadingHistory, setLoadingHistory] = useState(false);

  const toggleTheme = () => setDarkMode(!darkMode);
  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);

  const handleLogout = async () => {
    await signOut();
    router.push("/");
  };

  const fetchHistory = async () => {
    setLoadingHistory(true);
    const session = await fetchAuthSession();
    const token = session.tokens?.idToken?.toString();

    const res = await fetch(
      "https://synthera-django-777268942678.asia-south1.run.app/api/chat-history",
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    const json = await res.json();
    setHistory(json);
    setHistoryOpen(true);
    setLoadingHistory(false);
  };

  const runAgent = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setResult(null);
    setEmailSent(false);

    const session = await fetchAuthSession();
    const token = session.tokens?.idToken?.toString();

    const res = await fetch("/api/proxy/agent-run", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ user_input: query }),
    });

    const json = await res.json();

    if (json.status === "success") {
      setResult(json.data);
      setEmailSent(true);
    }

    setLoading(false);
  };

  return (
    <div
      className={`min-h-screen ${
        darkMode ? "bg-gradient-to-br from-gray-900 via-black to-purple-900/20 text-white" : "bg-gradient-to-br from-gray-50 via-white to-purple-50 text-black"
      } flex relative overflow-hidden`}
    >
      {/* Animated background particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-20 w-72 h-72 bg-purple-500/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse delay-700" />
        <div className="absolute top-1/2 left-1/2 w-80 h-80 bg-pink-500/5 rounded-full blur-3xl animate-pulse delay-1000" />
      </div>

      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 h-full z-40 transition-all duration-300 ${
          sidebarOpen ? "w-64" : "w-16"
        } ${
          darkMode ? "bg-gray-900/80 backdrop-blur-xl border-gray-800" : "bg-white/80 backdrop-blur-xl border-gray-200"
        } border-r shadow-2xl`}
      >
        <div className="p-4">
          <div className="flex justify-between items-center mb-6">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <span className="text-lg">🧪</span>
              </div>
              {sidebarOpen && (
                <h1 className="font-bold text-lg bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                  Synthera
                </h1>
              )}
            </div>
            <button
              onClick={toggleSidebar}
              className={`p-2 rounded-lg transition-colors ${
                darkMode ? "hover:bg-gray-800" : "hover:bg-gray-100"
              }`}
            >
              {sidebarOpen ? <FiX /> : <FiMenu />}
            </button>
          </div>

          <div className="space-y-2 text-sm">
            <button
              className={`w-full flex gap-3 items-center p-3 rounded-lg transition-all ${
                darkMode ? "hover:bg-gray-800" : "hover:bg-gray-100"
              } group`}
            >
              <FiPlus className="group-hover:rotate-90 transition-transform" />
              {sidebarOpen && <span>New Query</span>}
            </button>
            <button
              onClick={fetchHistory}
              disabled={loadingHistory}
              className={`w-full flex gap-3 items-center p-3 rounded-lg transition-all ${
                darkMode ? "hover:bg-gray-800" : "hover:bg-gray-100"
              } group ${loadingHistory ? "opacity-50 cursor-not-allowed" : ""}`}
            >
              {loadingHistory ? (
                <div className="w-4 h-4 border-2 border-purple-400 border-t-transparent rounded-full animate-spin" />
              ) : (
                <FiBook className="group-hover:scale-110 transition-transform" />
              )}
              {sidebarOpen && <span>History</span>}
            </button>
          </div>
        </div>
      </aside>

      {/* Main */}
      <main
        className={`flex-1 px-6 py-8 ${
          sidebarOpen ? "ml-64" : "ml-16"
        } relative z-10`}
      >
        {/* Top bar */}
        <div className="flex justify-end gap-4 mb-6">
          <button
            className={`p-2 rounded-lg transition-all ${
              darkMode ? "hover:bg-gray-800" : "hover:bg-gray-100"
            }`}
          >
            <FiBell className="hover:animate-bounce" />
          </button>
          <button
            onClick={toggleTheme}
            className={`p-2 rounded-lg transition-all ${
              darkMode ? "hover:bg-gray-800" : "hover:bg-gray-100"
            }`}
          >
            {darkMode ? (
              <FiSun className="hover:rotate-180 transition-transform duration-500" />
            ) : (
              <FiMoon className="hover:-rotate-12 transition-transform" />
            )}
          </button>
          <button
            onClick={handleLogout}
            className="text-xs font-medium bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 px-4 py-2 rounded-lg transition-all shadow-lg hover:shadow-purple-500/50"
          >
            Sign out
          </button>
        </div>

        {/* Input */}
        <div className="max-w-3xl mx-auto mb-8">
          <div
            className={`flex items-center rounded-2xl px-6 py-4 transition-all ${
              darkMode
                ? "bg-gray-800/50 backdrop-blur-xl border border-gray-700 shadow-xl"
                : "bg-white/80 backdrop-blur-xl border border-gray-200 shadow-xl"
            } ${loading ? "ring-2 ring-purple-500 ring-opacity-50" : ""}`}
          >
            <input
              className="flex-1 bg-transparent outline-none placeholder-opacity-60"
              placeholder="Ask a medical / market intelligence question"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && runAgent()}
              disabled={loading}
            />
            <button
              onClick={runAgent}
              disabled={loading}
              className={`ml-4 p-3 rounded-xl transition-all ${
                loading
                  ? "bg-purple-500/20"
                  : "bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 shadow-lg hover:shadow-purple-500/50"
              }`}
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-purple-400 border-t-transparent rounded-full animate-spin" />
              ) : (
                <FiArrowRight className="hover:translate-x-1 transition-transform" />
              )}
            </button>
          </div>
        </div>

        {/* Enhanced Skeleton Loader */}
        {loading && !result && (
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="space-y-4 animate-pulse">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg animate-spin" />
                <div className="h-6 bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-lg w-1/3" />
              </div>
              <div className="space-y-3 pl-11">
                <div className="h-4 bg-gradient-to-r from-gray-700/50 to-gray-600/50 rounded-lg w-full shimmer" />
                <div className="h-4 bg-gradient-to-r from-gray-700/50 to-gray-600/50 rounded-lg w-5/6 shimmer delay-100" />
                <div className="h-4 bg-gradient-to-r from-gray-700/50 to-gray-600/50 rounded-lg w-4/6 shimmer delay-200" />
              </div>
            </div>
            <div className="space-y-4 animate-pulse delay-300">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg animate-pulse" />
                <div className="h-6 bg-gradient-to-r from-blue-500/20 to-cyan-500/20 rounded-lg w-1/4" />
              </div>
              <div className="grid grid-cols-4 gap-3 pl-11">
                {[...Array(8)].map((_, i) => (
                  <div
                    key={i}
                    className="h-16 bg-gradient-to-br from-gray-700/30 to-gray-600/30 rounded-lg shimmer"
                    style={{ animationDelay: `${i * 100}ms` }}
                  />
                ))}
              </div>
            </div>
          </div>
        )}

        {emailSent && (
          <div className="max-w-3xl mx-auto mb-6 bg-gradient-to-r from-green-600/20 to-emerald-600/20 border border-green-500/50 p-4 rounded-xl text-sm flex items-center gap-3 animate-slideDown backdrop-blur-sm">
            <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center animate-bounce">
              📧
            </div>
            <span className="font-medium">Report link sent to your email</span>
          </div>
        )}

        {result && (
          <div className="max-w-4xl mx-auto space-y-8 animate-fadeIn">
            {result.web && (
              <section
                className={`p-6 rounded-2xl ${
                  darkMode
                    ? "bg-gray-800/50 backdrop-blur-xl border border-gray-700"
                    : "bg-white/80 backdrop-blur-xl border border-gray-200"
                } shadow-xl`}
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center">
                    🌐
                  </div>
                  <h2 className="text-xl font-semibold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                    Web Intelligence
                  </h2>
                </div>
                <div className="prose prose-invert max-w-none">
                  <ReactMarkdown>{result.web}</ReactMarkdown>
                </div>
              </section>
            )}

            {result.clinical?.active_trials && (
              <section
                className={`p-6 rounded-2xl ${
                  darkMode
                    ? "bg-gray-800/50 backdrop-blur-xl border border-gray-700"
                    : "bg-white/80 backdrop-blur-xl border border-gray-200"
                } shadow-xl`}
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
                    🧪
                  </div>
                  <h2 className="text-xl font-semibold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                    Clinical Trials
                  </h2>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr
                        className={`${
                          darkMode ? "bg-gray-900/50" : "bg-gray-50"
                        }`}
                      >
                        <th className="p-3 text-left font-semibold">Title</th>
                        <th className="p-3 text-left font-semibold">Phase</th>
                        <th className="p-3 text-left font-semibold">Sponsor</th>
                        <th className="p-3 text-left font-semibold">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.clinical.active_trials.map((t: any, i: number) => (
                        <tr
                          key={t.nct_id}
                          className={`border-t ${
                            darkMode ? "border-gray-700" : "border-gray-200"
                          } hover:bg-purple-500/5 transition-colors`}
                          style={{ animationDelay: `${i * 50}ms` }}
                        >
                          <td className="p-3">{t.title}</td>
                          <td className="p-3">
                            <span className="px-2 py-1 bg-purple-500/20 rounded-lg text-xs">
                              {t.phase}
                            </span>
                          </td>
                          <td className="p-3">{t.sponsor}</td>
                          <td className="p-3">
                            <span className="px-2 py-1 bg-green-500/20 rounded-lg text-xs">
                              {t.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            )}

            {result.pdf_url && (
              <a
                href={result.pdf_url}
                target="_blank"
                className="inline-flex items-center gap-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 px-6 py-3 rounded-xl font-medium transition-all shadow-lg hover:shadow-purple-500/50 hover:scale-105"
              >
                📄 Download PDF
                <FiArrowRight />
              </a>
            )}
          </div>
        )}
      </main>

      {/* History Drawer */}
      {historyOpen && (
        <div
          className={`fixed top-0 right-0 h-full w-96 ${
            darkMode ? "bg-gray-900/95" : "bg-white/95"
          } backdrop-blur-xl border-l ${
            darkMode ? "border-gray-800" : "border-gray-200"
          } p-6 z-50 overflow-y-auto animate-slideIn shadow-2xl`}
        >
          <div className="flex justify-between items-center mb-6">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                🕒
              </div>
              <h2 className="font-semibold text-lg">Chat History</h2>
            </div>
            <button
              onClick={() => setHistoryOpen(false)}
              className={`p-2 rounded-lg transition-colors ${
                darkMode ? "hover:bg-gray-800" : "hover:bg-gray-100"
              }`}
            >
              <FiX />
            </button>
          </div>

          <div className="space-y-3">
            {history.map((h, i) => (
              <div
                key={h.id}
                className={`p-4 ${
                  darkMode ? "bg-gray-800/50" : "bg-gray-50"
                } rounded-xl cursor-pointer transition-all hover:scale-102 hover:shadow-lg border ${
                  darkMode ? "border-gray-700" : "border-gray-200"
                } animate-fadeIn`}
                style={{ animationDelay: `${i * 50}ms` }}
                onClick={() => {
                  setResult(h.data);
                  setHistoryOpen(false);
                }}
              >
                <div className="text-xs opacity-60 mb-2">
                  {new Date(h.timestamp).toLocaleString()}
                </div>
                <div className="text-sm font-medium mb-2 line-clamp-2">
                  {h.data.user_input}
                </div>
                <a
                  href={h.file_url}
                  target="_blank"
                  className="inline-flex items-center gap-1 text-xs text-purple-400 hover:text-purple-300 transition-colors"
                  onClick={(e) => e.stopPropagation()}
                >
                  📄 PDF
                  <FiArrowRight className="w-3 h-3" />
                </a>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Enhanced Global Loader Overlay */}
      {loading && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-md z-50 flex items-center justify-center">
          <div className="flex flex-col items-center gap-6">
            <div className="relative">
              <div className="w-20 h-20 border-4 border-purple-500/30 rounded-full" />
              <div className="w-20 h-20 border-4 border-purple-500 border-t-transparent rounded-full animate-spin absolute top-0" />
              <div className="w-16 h-16 border-4 border-pink-500/30 rounded-full absolute top-2 left-2" />
              <div className="w-16 h-16 border-4 border-pink-500 border-t-transparent rounded-full animate-spin absolute top-2 left-2" style={{ animationDirection: "reverse", animationDuration: "1s" }} />
              <FiZap className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-6 h-6 text-purple-400 animate-pulse" />
            </div>
            <div className="text-center">
              <p className="text-base font-medium text-white mb-2">
                Running agent...
              </p>
              <p className="text-sm text-purple-300 animate-pulse">
                Generating intelligence report
              </p>
            </div>
            <div className="flex gap-2">
              {[...Array(3)].map((_, i) => (
                <div
                  key={i}
                  className="w-2 h-2 bg-purple-500 rounded-full animate-bounce"
                  style={{ animationDelay: `${i * 150}ms` }}
                />
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Animations */}
      <style jsx global>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fadeIn {
          animation: fadeIn 0.5s ease-out;
        }

        @keyframes slideIn {
          from {
            transform: translateX(100%);
          }
          to {
            transform: translateX(0);
          }
        }
        .animate-slideIn {
          animation: slideIn 0.3s ease-out;
        }

        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-slideDown {
          animation: slideDown 0.4s ease-out;
        }

        @keyframes shimmer {
          0% {
            opacity: 0.5;
          }
          50% {
            opacity: 1;
          }
          100% {
            opacity: 0.5;
          }
        }
        .shimmer {
          animation: shimmer 1.5s ease-in-out infinite;
        }

        .delay-100 {
          animation-delay: 100ms;
        }
        .delay-200 {
          animation-delay: 200ms;
        }
        .delay-300 {
          animation-delay: 300ms;
        }
        .delay-700 {
          animation-delay: 700ms;
        }
        .delay-1000 {
          animation-delay: 1000ms;
        }

        .hover\:scale-102:hover {
          transform: scale(1.02);
        }

        .line-clamp-2 {
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
      `}</style>
    </div>
  );
}