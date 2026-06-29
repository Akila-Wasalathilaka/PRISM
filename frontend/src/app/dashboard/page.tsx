"use client";

import { useEffect, useState } from "react";

interface Analysis {
  repo: string;
  pr_number: number;
  pr_title: string;
  author: string;
  score: number;
  risk_count: number;
  merged: boolean;
  timestamp: string;
}

interface Stats {
  total_analyzed: number;
  avg_score: number;
  high_risk_count: number;
  critical_risk_count: number;
  recent_repos: string[];
  total_files_analyzed: number;
  total_lines_added: number;
  total_lines_deleted: number;
  auto_merged_count: number;
  safe_pr_percentage: number;
  top_categories: { name: string; count: number }[];
  top_authors: { name: string; count: number }[];
  risk_trend: { day: string; date: string; avg_score: number; count: number }[];
  llm_provider: string;
  project_stats: {
    repo: string;
    pr_count: number;
    avg_score: number;
    safe_prs: number;
    auto_merged: number;
    critical_risks: number;
  }[];
}

export default function Dashboard() {
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedRepo, setSelectedRepo] = useState<string | null>(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

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
    const seconds = Math.floor(
      (new Date().getTime() - new Date(dateStr).getTime()) / 1000,
    );
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  };

  const getCardColor = (score: number) => {
    if (score === 0) return "bg-[#33a047] border-[#228033]";
    if (score < 30) return "bg-[#6c757d] border-[#5a6268]";
    if (score < 50) return "bg-[#ff9800] border-[#f57c00]";
    return "bg-[#e53935] border-[#c62828]";
  };

  const providerBadge = (provider: string) => {
    const badges: Record<
      string,
      { icon: string; label: string; color: string }
    > = {
      openai: { icon: "🟢", label: "OpenAI", color: "text-green-400" },
      anthropic: { icon: "🟠", label: "Anthropic", color: "text-orange-400" },
      gemini: { icon: "🔵", label: "Gemini", color: "text-blue-400" },
      mistral: { icon: "🟣", label: "Mistral", color: "text-purple-400" },
      ollama: { icon: "🦙", label: "Ollama", color: "text-yellow-400" },
      custom: { icon: "⚙️", label: "Custom", color: "text-gray-400" },
      none: { icon: "🔧", label: "Deterministic", color: "text-gray-500" },
    };
    return badges[provider] || badges.none;
  };

  const filteredAnalyses = selectedRepo
    ? analyses.filter((a) => a.repo === selectedRepo)
    : analyses;

  const issues = filteredAnalyses.filter((a) => a.score > 0);
  const maxTrend = stats?.risk_trend
    ? Math.max(...stats.risk_trend.map((t) => t.avg_score), 1)
    : 1;

  return (
    <div className="flex flex-col md:flex-row min-h-screen bg-[#1e1e1e] text-white font-mono selection:bg-gray-700">
      {/* MOBILE HEADER */}
      <div className="md:hidden flex items-center justify-between p-4 bg-[#161616] border-b border-gray-800 sticky top-0 z-20">
        <h2
          className="text-2xl font-bold tracking-tight"
          style={{ fontFamily: "cursive, sans-serif" }}
        >
          PRISM
        </h2>
        <button
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          className="p-2 text-gray-400 hover:text-white focus:outline-none"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            {isMobileMenuOpen ? (
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            ) : (
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16"
              />
            )}
          </svg>
        </button>
      </div>

      {/* LEFT SIDEBAR */}
      <div
        className={`w-full md:w-80 border-r border-gray-800 bg-[#161616] p-6 flex-col overflow-y-auto ${isMobileMenuOpen ? "fixed inset-0 top-[73px] z-10 flex" : "hidden md:flex md:static"}`}
      >
        <h2
          className="text-3xl font-bold tracking-tight mb-8"
          style={{ fontFamily: "cursive, sans-serif" }}
        >
          PRISM{" "}
          <span className="text-sm text-gray-500 font-sans tracking-normal ml-1">
            v2.1
          </span>
        </h2>

        {/* LLM Provider Badge */}
        {stats && (
          <div className="mb-6 p-3 bg-[#1e1e1e] rounded-lg border border-gray-800">
            <div className="text-xs text-gray-500 uppercase tracking-widest mb-1">
              AI Engine
            </div>
            <div
              className={`text-sm font-bold ${providerBadge(stats.llm_provider).color}`}
            >
              {providerBadge(stats.llm_provider).icon}{" "}
              {providerBadge(stats.llm_provider).label}
            </div>
          </div>
        )}

        {/* Repositories */}
        <div className="mb-10">
          <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4 flex items-center gap-2">
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"
              />
            </svg>
            Active Repos
          </h3>
          {stats?.recent_repos && stats.recent_repos.length > 0 ? (
            <ul className="space-y-3 text-sm text-gray-300">
              <li
                onClick={() => { setSelectedRepo(null); setIsMobileMenuOpen(false); }}
                className={`flex items-center gap-3 p-2 rounded-md border cursor-pointer transition-colors ${selectedRepo === null ? "bg-[#2a2a2a] border-gray-600 font-bold" : "bg-[#1e1e1e] border-gray-800 hover:border-gray-600"}`}
              >
                <div className="w-2 h-2 rounded-full bg-white shadow-[0_0_8px_rgba(255,255,255,0.8)]"></div>
                <span className="truncate">All Projects</span>
              </li>
              {stats.recent_repos.map((r) => (
                <li
                  key={r}
                  onClick={() => { setSelectedRepo(r); setIsMobileMenuOpen(false); }}
                  className={`flex items-center gap-3 p-2 rounded-md border cursor-pointer transition-colors ${selectedRepo === r ? "bg-[#2a2a2a] border-gray-600 font-bold" : "bg-[#1e1e1e] border-gray-800 hover:border-gray-600"}`}
                >
                  <div className="w-2 h-2 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.8)]"></div>
                  <span className="truncate">{r.split("/").pop()}</span>
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-sm text-gray-600 italic">
              No repos detected
            </div>
          )}
        </div>

        {/* Pending Issues */}
        <div className="mb-10 flex-grow">
          <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4 flex items-center gap-2">
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            Pending Issues
          </h3>
          {issues.length > 0 ? (
            <div className="space-y-3">
              {issues.slice(0, 5).map((issue) => (
                <div
                  key={`${issue.repo}-${issue.pr_number}`}
                  className="p-3 bg-[#2a1a1a] border border-red-900/50 rounded-md shadow-sm hover:border-red-700 transition-colors"
                >
                  <div className="flex justify-between items-start mb-1">
                    <div className="text-xs text-red-400 font-bold">
                      Score: {issue.score}/100
                    </div>
                    <div className="text-xs text-gray-500">
                      {timeAgo(issue.timestamp)}
                    </div>
                  </div>
                  <div className="text-sm text-gray-200 leading-tight">
                    <span className="text-gray-400">
                      {issue.repo.split("/").pop()}
                    </span>{" "}
                    #{issue.pr_number}
                  </div>
                  <div className="text-xs text-gray-400 mt-1 truncate">
                    {issue.pr_title}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sm text-green-500/70 p-3 bg-green-900/10 border border-green-900/30 rounded-md">
              All clear! No pending risks. 🚀
            </div>
          )}
        </div>

        {/* Recent Activity */}
        <div>
          <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4 flex items-center gap-2">
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            Recent Activity
          </h3>
          <div className="space-y-5 relative before:absolute before:inset-0 before:ml-1 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-gray-800 before:to-transparent pl-4">
            {analyses.slice(0, 4).map((a, i) => (
              <div key={i} className="relative flex items-start gap-4">
                <div
                  className={`absolute -left-[21px] mt-1.5 w-2.5 h-2.5 rounded-full border-2 border-[#161616] ${a.score === 0 ? "bg-green-500" : "bg-orange-500"}`}
                ></div>
                <div>
                  <div className="text-xs text-gray-500 mb-0.5">
                    {timeAgo(a.timestamp)}
                  </div>
                  <div className="text-sm text-gray-300 leading-tight">
                    Analyzed{" "}
                    <span className="text-blue-400">#{a.pr_number}</span>
                    <span className="text-gray-500 ml-1">
                      ({a.score === 0 ? "Merged" : "Review"})
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* MAIN CONTENT */}
      <div className="flex-1 p-6 lg:p-10 flex flex-col overflow-y-auto h-screen bg-[#1e1e1e]">
        {/* Header */}
        <div className="flex justify-between items-end mb-8 pb-4 border-b border-gray-800">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-gray-100">
              Gitaction Board
            </h1>
          </div>

          {stats && (
            <div className="flex gap-8 text-sm">
              <div className="flex flex-col items-end">
                <span className="text-gray-500 uppercase text-xs font-bold tracking-wider">
                  Total PRs
                </span>
                <span className="text-3xl font-bold text-blue-400 drop-shadow-sm">
                  {stats.total_analyzed}
                </span>
              </div>
              <div className="flex flex-col items-end">
                <span className="text-gray-500 uppercase text-xs font-bold tracking-wider">
                  Avg Score
                </span>
                <span className="text-3xl font-bold text-yellow-500 drop-shadow-sm">
                  {stats.avg_score}
                </span>
              </div>
              <div className="flex flex-col items-end">
                <span className="text-gray-500 uppercase text-xs font-bold tracking-wider">
                  High Risk
                </span>
                <span className="text-3xl font-bold text-red-500 drop-shadow-sm">
                  {stats.high_risk_count}
                </span>
              </div>
              <div className="flex flex-col items-end">
                <span className="text-gray-500 uppercase text-xs font-bold tracking-wider">
                  Critical
                </span>
                <span className="text-3xl font-bold text-orange-500 drop-shadow-sm">
                  {stats.critical_risk_count}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Analytics Widgets */}
        {stats && !loading && analyses.length > 0 && !selectedRepo && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            {/* Risk Trend Chart */}
            <div className="bg-[#161616] border border-gray-800 rounded-xl p-5 shadow-sm">
              <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                <svg
                  className="w-4 h-4 text-cyan-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
                7-Day Risk Trend
              </h3>
              <div className="flex items-end gap-1 h-24">
                {stats.risk_trend.map((t) => {
                  const height =
                    maxTrend > 0 ? (t.avg_score / maxTrend) * 100 : 0;
                  const barColor =
                    t.avg_score === 0
                      ? "bg-green-600"
                      : t.avg_score < 30
                        ? "bg-gray-500"
                        : t.avg_score < 50
                          ? "bg-yellow-500"
                          : t.avg_score < 70
                            ? "bg-orange-500"
                            : "bg-red-500";
                  return (
                    <div
                      key={t.date}
                      className="flex-1 flex flex-col items-center gap-1"
                    >
                      <div className="text-[10px] text-gray-500">
                        {t.count > 0 ? t.avg_score : ""}
                      </div>
                      <div
                        className={`w-full rounded-t ${barColor} transition-all duration-500 min-h-[2px]`}
                        style={{ height: `${Math.max(height, 2)}%` }}
                        title={`${t.day}: ${t.avg_score} avg (${t.count} PRs)`}
                      ></div>
                      <div className="text-[10px] text-gray-600">{t.day}</div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Project Progress */}
            <div className="bg-[#161616] border border-gray-800 rounded-xl p-5 shadow-sm">
              <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                <svg
                  className="w-4 h-4 text-blue-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                  />
                </svg>
                Project Progress
              </h3>
              <div className="grid grid-cols-3 gap-3 mb-4">
                <div className="bg-[#1e1e1e] rounded-lg p-2.5 border border-gray-800/50">
                  <div className="text-[10px] text-gray-500 mb-0.5">Files</div>
                  <div className="text-lg font-bold text-gray-200">
                    {stats.total_files_analyzed}
                  </div>
                </div>
                <div className="bg-[#1e1e1e] rounded-lg p-2.5 border border-green-900/30">
                  <div className="text-[10px] text-green-600 mb-0.5">Added</div>
                  <div className="text-lg font-bold text-green-500">
                    +{stats.total_lines_added}
                  </div>
                </div>
                <div className="bg-[#1e1e1e] rounded-lg p-2.5 border border-red-900/30">
                  <div className="text-[10px] text-red-600 mb-0.5">Deleted</div>
                  <div className="text-lg font-bold text-red-500">
                    -{stats.total_lines_deleted}
                  </div>
                </div>
              </div>
              {/* Safe PR Rate */}
              <div className="mt-2">
                <div className="flex justify-between text-xs mb-1.5">
                  <span className="text-gray-500">Safe PR Rate</span>
                  <span className="text-green-400 font-bold">
                    {stats.safe_pr_percentage}%
                  </span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-green-600 to-green-400 h-2 rounded-full transition-all duration-700"
                    style={{ width: `${stats.safe_pr_percentage}%` }}
                  ></div>
                </div>
              </div>
            </div>

            {/* Bot Analytics */}
            <div className="bg-[#161616] border border-gray-800 rounded-xl p-5 shadow-sm">
              <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                <svg
                  className="w-4 h-4 text-purple-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                  />
                </svg>
                Bot Analytics
              </h3>
              <div className="flex gap-4 mb-3">
                <div className="bg-[#1e1e1e] rounded-lg p-2.5 border border-gray-800/50 flex-1">
                  <div className="text-[10px] text-gray-500 mb-0.5">
                    Auto-Merged
                  </div>
                  <div className="flex items-end gap-1.5">
                    <span className="text-xl font-bold text-purple-400">
                      {stats.auto_merged_count}
                    </span>
                    <span className="text-xs text-gray-500 mb-0.5">
                      / {stats.total_analyzed}
                    </span>
                  </div>
                </div>
                <div className="flex-1">
                  <div className="text-[10px] text-gray-500 mb-1.5">
                    Top Contributors
                  </div>
                  {stats.top_authors && stats.top_authors.length > 0 ? (
                    <div className="space-y-1">
                      {stats.top_authors.map((a) => (
                        <div
                          key={a.name}
                          className="flex justify-between items-center text-xs bg-[#1e1e1e] px-2 py-0.5 rounded border border-gray-800/50"
                        >
                          <span className="text-gray-300 truncate mr-2">
                            {a.name}
                          </span>
                          <span className="text-blue-400 font-bold">
                            {a.count}
                          </span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-xs text-gray-600 italic">
                      No data yet
                    </div>
                  )}
                </div>
              </div>
              {/* Risk Categories */}
              {stats.top_categories && stats.top_categories.length > 0 && (
                <div>
                  <div className="text-[10px] text-gray-500 mb-1.5">
                    Top Risk Categories
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {stats.top_categories.map((cat) => (
                      <span
                        key={cat.name}
                        className="text-[10px] bg-orange-900/30 text-orange-400 px-2 py-0.5 rounded-full border border-orange-800/30"
                      >
                        {cat.name} ({cat.count})
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Project Performance Section */}
        {!loading &&
          stats &&
          stats.project_stats &&
          stats.project_stats.length > 0 &&
          !selectedRepo && (
            <div className="mb-8">
              <h3 className="text-xl font-bold tracking-tight mb-4 flex items-center gap-2">
                <svg
                  className="w-5 h-5 text-gray-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                  />
                </svg>
                Project Performance
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                {stats.project_stats.map((proj) => (
                  <div
                    key={proj.repo}
                    className="bg-[#161616] border border-gray-800 rounded-xl p-4 shadow-sm flex flex-col hover:border-gray-700 transition-colors"
                  >
                    <div
                      className="text-sm font-bold text-gray-300 truncate mb-3"
                      title={proj.repo}
                    >
                      {proj.repo.split("/").pop()}
                    </div>
                    <div className="grid grid-cols-2 gap-3 mb-3">
                      <div className="bg-[#1e1e1e] rounded-lg p-2 border border-gray-800/50 flex flex-col justify-center items-center">
                        <div className="text-[10px] text-gray-500">PRs</div>
                        <div className="text-sm font-bold text-gray-200">
                          {proj.pr_count}
                        </div>
                      </div>
                      <div className="bg-[#1e1e1e] rounded-lg p-2 border border-gray-800/50 flex flex-col justify-center items-center">
                        <div className="text-[10px] text-gray-500">
                          Avg Score
                        </div>
                        <div
                          className={`text-sm font-bold ${proj.avg_score === 0 ? "text-green-500" : proj.avg_score < 30 ? "text-gray-300" : proj.avg_score < 50 ? "text-orange-400" : "text-red-500"}`}
                        >
                          {proj.avg_score}
                        </div>
                      </div>
                    </div>
                    <div className="flex justify-between items-center text-xs px-1">
                      <div className="flex gap-1.5 items-center">
                        <span className="w-2 h-2 rounded-full bg-green-500 inline-block"></span>
                        <span className="text-gray-400">
                          Safe: {proj.safe_prs}
                        </span>
                      </div>
                      {proj.critical_risks > 0 && (
                        <div className="flex gap-1.5 items-center">
                          <span className="w-2 h-2 rounded-full bg-red-500 inline-block"></span>
                          <span className="text-red-400 font-medium">
                            Critical: {proj.critical_risks}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

        {/* PR Cards Grid */}
        {loading && analyses.length === 0 ? (
          <div className="flex flex-1 justify-center items-center">
            <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredAnalyses.length === 0 ? (
              <div className="col-span-full flex flex-col items-center justify-center text-gray-500 py-32 border-2 border-dashed border-gray-800 rounded-xl">
                <svg
                  className="w-16 h-16 text-gray-700 mb-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1}
                    d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"
                  />
                </svg>
                <div className="text-xl">No pull requests analyzed yet</div>
                <p className="text-sm mt-2">
                  Open a Pull Request on GitHub to see live data here.
                </p>
              </div>
            ) : (
              filteredAnalyses.map((analysis) => {
                const bgClass = getCardColor(analysis.score);
                return (
                  <a
                    key={`${analysis.repo}-${analysis.pr_number}-${analysis.timestamp}`}
                    href={`https://github.com/${analysis.repo}/pull/${analysis.pr_number}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`${bgClass} rounded-[3px] border shadow-2xl flex flex-col h-36 hover:brightness-110 hover:scale-[1.02] transition-all cursor-pointer overflow-hidden relative group`}
                  >
                    <div
                      className="absolute inset-0 opacity-0 group-hover:opacity-10 pointer-events-none transition-opacity"
                      style={{
                        backgroundImage:
                          "repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(255,255,255,0.5) 10px, rgba(255,255,255,0.5) 20px)",
                      }}
                    ></div>

                    <div className="p-3 flex-grow break-words text-[13px] font-semibold leading-snug text-white drop-shadow-md">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-white/80 text-[11px]">
                          @{analysis.author}
                        </span>
                        {analysis.risk_count > 0 && (
                          <span className="text-[10px] bg-black/30 px-1.5 py-0.5 rounded-full">
                            {analysis.risk_count} issues
                          </span>
                        )}
                      </div>
                      {analysis.repo.split("/").pop()} :: PR #
                      {analysis.pr_number} :: {analysis.pr_title}
                    </div>

                    <div className="px-3 py-1.5 bg-black/20 text-[11px] flex justify-between items-center text-gray-100 font-medium border-t border-black/10">
                      <div className="flex items-center gap-1.5 opacity-90">
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          className="h-3.5 w-3.5"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                          />
                        </svg>
                        {timeAgo(analysis.timestamp)}
                      </div>
                      <div className="font-bold tracking-wide">
                        Score: {analysis.score}
                      </div>
                    </div>
                  </a>
                );
              })
            )}
          </div>
        )}
      </div>
    </div>
  );
}
