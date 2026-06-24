"use client";

import { useEffect, useState } from "react";

interface Analysis {
  repo: string;
  pr_number: number;
  pr_title: string;
  author: string;
  score: number;
  risk_count: number;
  timestamp: string;
}

interface Stats {
  total_analyzed: number;
  avg_score: number;
  high_risk_count: number;
  critical_risk_count: number;
  recent_repos: string[];
}

export default function Dashboard() {
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  // Cloudflare proxy uses relative URLs, local dev defaults to localhost if empty
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "";

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [analysesRes, statsRes] = await Promise.all([
          fetch(`${apiUrl}/api/analyses`),
          fetch(`${apiUrl}/api/analyses/stats`),
        ]);
        
        if (analysesRes.ok) setAnalyses(await analysesRes.json());
        if (statsRes.ok) setStats(await statsRes.json());
      } catch (error) {
        console.error("Failed to fetch dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, [apiUrl]);

  const timeAgo = (dateStr: string) => {
    const seconds = Math.floor((new Date().getTime() - new Date(dateStr).getTime()) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  };

  const getCardColor = (score: number) => {
    if (score === 0) return "bg-[#33a047] border-[#228033]"; // Green
    if (score < 30) return "bg-[#6c757d] border-[#5a6268]"; // Grey
    if (score < 50) return "bg-[#ff9800] border-[#f57c00]"; // Orange
    return "bg-[#e53935] border-[#c62828]"; // Red
  };

  const issues = analyses.filter(a => a.score > 0);

  return (
    <div className="flex min-h-screen bg-[#1e1e1e] text-white font-mono selection:bg-gray-700">
      
      {/* LEFT SIDEBAR */}
      <div className="w-80 border-r border-gray-800 bg-[#161616] p-6 flex flex-col hidden md:flex overflow-y-auto">
        <h2 className="text-3xl font-bold tracking-tight mb-8" style={{ fontFamily: 'cursive, sans-serif' }}>
          PRISM <span className="text-sm text-gray-500 font-sans tracking-normal ml-1">v2.0</span>
        </h2>

        {/* Repositories */}
        <div className="mb-10">
          <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4 flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" /></svg>
            Active Repos
          </h3>
          {stats?.recent_repos && stats.recent_repos.length > 0 ? (
            <ul className="space-y-3 text-sm text-gray-300">
              {stats.recent_repos.map(r => (
                <li key={r} className="flex items-center gap-3 p-2 bg-[#1e1e1e] rounded-md border border-gray-800">
                  <div className="w-2 h-2 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.8)]"></div>
                  <span className="truncate">{r.split('/').pop()}</span>
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-sm text-gray-600 italic">No repos detected</div>
          )}
        </div>

        {/* Issues List */}
        <div className="mb-10 flex-grow">
          <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4 flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
            Pending Issues
          </h3>
          {issues.length > 0 ? (
            <div className="space-y-3">
              {issues.slice(0, 5).map(issue => (
                <div key={issue.pr_number} className="p-3 bg-[#2a1a1a] border border-red-900/50 rounded-md shadow-sm hover:border-red-700 transition-colors">
                  <div className="flex justify-between items-start mb-1">
                    <div className="text-xs text-red-400 font-bold">Score: {issue.score}/100</div>
                    <div className="text-xs text-gray-500">{timeAgo(issue.timestamp)}</div>
                  </div>
                  <div className="text-sm text-gray-200 leading-tight">
                    <span className="text-gray-400">{issue.repo.split('/').pop()}</span> #{issue.pr_number}
                  </div>
                  <div className="text-xs text-gray-400 mt-1 truncate">{issue.pr_title}</div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sm text-green-500/70 p-3 bg-green-900/10 border border-green-900/30 rounded-md">
              All clear! No pending risks. 🚀
            </div>
          )}
        </div>

        {/* Activity Log */}
        <div>
          <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4 flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            Recent Activity
          </h3>
          <div className="space-y-5 relative before:absolute before:inset-0 before:ml-1 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-gray-800 before:to-transparent pl-4">
            {analyses.slice(0, 4).map((a, i) => (
              <div key={i} className="relative flex items-start gap-4">
                <div className={`absolute -left-[21px] mt-1.5 w-2.5 h-2.5 rounded-full border-2 border-[#161616] ${a.score === 0 ? 'bg-green-500' : 'bg-orange-500'}`}></div>
                <div>
                  <div className="text-xs text-gray-500 mb-0.5">{timeAgo(a.timestamp)}</div>
                  <div className="text-sm text-gray-300 leading-tight">
                    Analyzed <span className="text-blue-400">#{a.pr_number}</span>
                    <span className="text-gray-500 ml-1">({a.score === 0 ? 'Merged' : 'Review'})</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* MAIN CONTENT */}
      <div className="flex-1 p-6 lg:p-10 flex flex-col overflow-y-auto h-screen bg-[#1e1e1e]">
        <div className="flex justify-between items-end mb-8 pb-4 border-b border-gray-800">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-gray-100">Gitaction Board</h1>
          </div>
          
          {stats && (
            <div className="flex gap-8 text-sm">
              <div className="flex flex-col items-end">
                <span className="text-gray-500 uppercase text-xs font-bold tracking-wider">Total PRs</span>
                <span className="text-3xl font-bold text-blue-400 drop-shadow-sm">{stats.total_analyzed}</span>
              </div>
              <div className="flex flex-col items-end">
                <span className="text-gray-500 uppercase text-xs font-bold tracking-wider">Avg Score</span>
                <span className="text-3xl font-bold text-yellow-500 drop-shadow-sm">{stats.avg_score}</span>
              </div>
              <div className="flex flex-col items-end">
                <span className="text-gray-500 uppercase text-xs font-bold tracking-wider">High Risk</span>
                <span className="text-3xl font-bold text-red-500 drop-shadow-sm">{stats.high_risk_count}</span>
              </div>
            </div>
          )}
        </div>

        {loading && analyses.length === 0 ? (
          <div className="flex flex-1 justify-center items-center">
            <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {analyses.length === 0 ? (
              <div className="col-span-full flex flex-col items-center justify-center text-gray-500 py-32 border-2 border-dashed border-gray-800 rounded-xl">
                <svg className="w-16 h-16 text-gray-700 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                </svg>
                <div className="text-xl">No pull requests analyzed yet</div>
                <p className="text-sm mt-2">Open a Pull Request on GitHub to see live data here.</p>
              </div>
            ) : (
              analyses.map((analysis) => {
                const bgClass = getCardColor(analysis.score);
                return (
                  <div 
                    key={`${analysis.repo}-${analysis.pr_number}-${analysis.timestamp}`} 
                    className={`${bgClass} rounded-[3px] border shadow-2xl flex flex-col h-32 hover:brightness-110 transition-all cursor-default overflow-hidden relative group`}
                  >
                    <div className="absolute inset-0 opacity-0 group-hover:opacity-10 pointer-events-none transition-opacity" style={{ backgroundImage: 'repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(255,255,255,0.5) 10px, rgba(255,255,255,0.5) 20px)' }}></div>
                    
                    <div className="p-3 flex-grow break-words text-[13px] font-semibold leading-snug text-white drop-shadow-md">
                      {analysis.repo.split('/').pop()} :: PR #{analysis.pr_number} :: {analysis.pr_title}
                    </div>
                    
                    <div className="px-3 py-1.5 bg-black/20 text-[11px] flex justify-between items-center text-gray-100 font-medium border-t border-black/10">
                      <div className="flex items-center gap-1.5 opacity-90">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {timeAgo(analysis.timestamp)}
                      </div>
                      <div className="font-bold tracking-wide">
                        Score: {analysis.score}
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        )}
      </div>
    </div>
  );
}
