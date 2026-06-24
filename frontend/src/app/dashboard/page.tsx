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
}

export default function Dashboard() {
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  // Default to localhost if env var is missing during dev
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [analysesRes, statsRes] = await Promise.all([
          fetch(`${apiUrl}/api/analyses`),
          fetch(`${apiUrl}/api/analyses/stats`),
        ]);
        
        if (analysesRes.ok) {
          setAnalyses(await analysesRes.json());
        }
        if (statsRes.ok) {
          setStats(await statsRes.json());
        }
      } catch (error) {
        console.error("Failed to fetch dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    // Refresh every 10 seconds
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, [apiUrl]);

  // Helper to get relative time
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
    if (score < 30) return "bg-[#6c757d] border-[#5a6268]"; // Grey (safe but some minor risks)
    if (score < 50) return "bg-[#ff9800] border-[#f57c00]"; // Orange
    return "bg-[#e53935] border-[#c62828]"; // Red
  };

  return (
    <div className="min-h-screen bg-[#1e1e1e] text-white p-6 font-mono selection:bg-gray-700">
      <div className="flex justify-between items-center mb-8 border-b border-gray-700 pb-4">
        <div>
          <h1 className="text-4xl font-bold tracking-tight" style={{ fontFamily: 'cursive, sans-serif' }}>PRISM Board <span className="text-sm text-gray-400 font-sans tracking-normal ml-2">(v2.0)</span></h1>
        </div>
        
        {stats && (
          <div className="flex gap-6 text-sm">
            <div className="flex flex-col items-end">
              <span className="text-gray-400 uppercase text-xs">Total Analyzed</span>
              <span className="text-xl font-bold text-blue-400">{stats.total_analyzed}</span>
            </div>
            <div className="flex flex-col items-end">
              <span className="text-gray-400 uppercase text-xs">Avg Score</span>
              <span className="text-xl font-bold text-yellow-400">{stats.avg_score}</span>
            </div>
            <div className="flex flex-col items-end">
              <span className="text-gray-400 uppercase text-xs">High Risk</span>
              <span className="text-xl font-bold text-red-500">{stats.high_risk_count}</span>
            </div>
          </div>
        )}
      </div>

      {loading && analyses.length === 0 ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-white"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
          {analyses.length === 0 ? (
            <div className="col-span-full text-center text-gray-500 py-12">
              No pull requests analyzed yet.
            </div>
          ) : (
            analyses.map((analysis) => {
              const bgClass = getCardColor(analysis.score);
              return (
                <div 
                  key={`${analysis.repo}-${analysis.pr_number}`} 
                  className={`${bgClass} rounded-sm border shadow-lg flex flex-col h-32 hover:brightness-110 transition-all cursor-default overflow-hidden relative group`}
                >
                  {/* Diagonal stripes overlay for effect on hover */}
                  <div className="absolute inset-0 opacity-0 group-hover:opacity-10 pointer-events-none" style={{ backgroundImage: 'repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(255,255,255,0.5) 10px, rgba(255,255,255,0.5) 20px)' }}></div>
                  
                  <div className="p-3 flex-grow break-words text-sm font-semibold leading-tight text-white drop-shadow-md">
                    {analysis.repo.split('/').pop()} :: PR #{analysis.pr_number} :: {analysis.pr_title}
                  </div>
                  
                  <div className="px-3 py-1.5 bg-black/20 text-xs flex justify-between items-center text-gray-100 font-medium">
                    <div className="flex items-center gap-1">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {timeAgo(analysis.timestamp)}
                    </div>
                    <div>
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
  );
}
