"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface SearchResult {
  title: string;
  url: string;
  snippet: string;
  company?: string;
}

interface EnrichResponse {
  email: string;
  email_confidence: "found" | "inferred" | "none";
  cold_email_draft: string;
}

interface DetailPanelProps {
  result: SearchResult | null;
  onClose: () => void;
}

function parseName(title: string): { name: string; role: string } {
  // LinkedIn titles are usually "Name - Role at Company | LinkedIn" or "Name | Title"
  const cleaned = title.replace(/\s*[\|·]\s*LinkedIn\s*$/i, "").trim();
  const dashIdx = cleaned.indexOf(" - ");
  if (dashIdx !== -1) {
    return { name: cleaned.slice(0, dashIdx).trim(), role: cleaned.slice(dashIdx + 3).trim() };
  }
  const pipeIdx = cleaned.indexOf(" | ");
  if (pipeIdx !== -1) {
    return { name: cleaned.slice(0, pipeIdx).trim(), role: cleaned.slice(pipeIdx + 3).trim() };
  }
  return { name: cleaned, role: "" };
}

export function DetailPanel({ result, onClose }: DetailPanelProps) {
  const [enrichData, setEnrichData] = useState<EnrichResponse | null>(null);
  const [enrichLoading, setEnrichLoading] = useState(false);
  const [draftOpen, setDraftOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const [prevUrl, setPrevUrl] = useState<string | null>(null);

  // Reset state when a new result is selected
  if (result && result.url !== prevUrl) {
    setPrevUrl(result.url);
    setEnrichData(null);
    setEnrichLoading(false);
    setDraftOpen(false);
    setCopied(false);
  }

  const findEmail = async () => {
    if (!result) return;
    setEnrichLoading(true);
    const { name } = parseName(result.title);
    try {
      const res = await fetch("https://crm123-mggu.onrender.com/api/enrich", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          company: result.company || "",
          linkedin_url: result.url,
          snippet: result.snippet,
          title: result.title,
        }),
      });
      const data: EnrichResponse = await res.json();
      setEnrichData(data);
    } catch {
      setEnrichData({ email: "", email_confidence: "none", cold_email_draft: "" });
    } finally {
      setEnrichLoading(false);
    }
  };

  const copyDraft = () => {
    if (enrichData?.cold_email_draft) {
      navigator.clipboard.writeText(enrichData.cold_email_draft);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const { name, role } = result ? parseName(result.title) : { name: "", role: "" };

  const confidenceBadge = (c: string) => {
    if (c === "found") return <span className="ml-2 text-xs px-1.5 py-0.5 rounded bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300">✓ Found</span>;
    if (c === "inferred") return <span className="ml-2 text-xs px-1.5 py-0.5 rounded bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300">~ Inferred</span>;
    return <span className="ml-2 text-xs px-1.5 py-0.5 rounded bg-neutral-100 text-neutral-500">Not found</span>;
  };

  return (
    <AnimatePresence>
      {result && (
        <>
          {/* Backdrop */}
          <motion.div
            key="backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/30 z-40"
          />

          {/* Panel */}
          <motion.div
            key="panel"
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className="fixed top-0 right-0 h-full w-full max-w-md bg-white dark:bg-neutral-900 shadow-2xl z-50 flex flex-col overflow-y-auto"
          >
            {/* Header */}
            <div className="flex items-start justify-between p-6 border-b border-neutral-200 dark:border-neutral-800">
              <div className="flex-1 pr-4">
                <h2 className="text-xl font-bold text-neutral-900 dark:text-white leading-tight">{name || result.title}</h2>
                {role && <p className="text-sm text-neutral-500 dark:text-neutral-400 mt-1">{role}</p>}
                {result.company && (
                  <span className="inline-block mt-2 px-2 py-0.5 rounded text-xs bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400">
                    {result.company}
                  </span>
                )}
              </div>
              <button
                onClick={onClose}
                className="text-neutral-400 hover:text-neutral-700 dark:hover:text-white text-2xl leading-none mt-0.5 flex-shrink-0"
              >
                ×
              </button>
            </div>

            {/* Body */}
            <div className="flex flex-col gap-6 p-6 flex-1">
              {/* LinkedIn */}
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-neutral-400 mb-2">LinkedIn</p>
                <a
                  href={result.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 text-sm text-blue-600 dark:text-blue-400 hover:underline break-all"
                >
                  <svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                  </svg>
                  {result.url.replace("https://", "")}
                </a>
              </div>

              {/* About */}
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-neutral-400 mb-2">About</p>
                <p className="text-sm text-neutral-700 dark:text-neutral-300 leading-relaxed">{result.snippet || "No description available."}</p>
              </div>

              {/* Email */}
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-neutral-400 mb-2">Email</p>
                {!enrichData && !enrichLoading && (
                  <button
                    onClick={findEmail}
                    className="text-sm px-3 py-1.5 rounded-lg bg-neutral-900 text-white dark:bg-white dark:text-neutral-900 hover:opacity-80 transition-opacity"
                  >
                    Find Email
                  </button>
                )}
                {enrichLoading && (
                  <p className="text-sm text-neutral-400 animate-pulse">Searching...</p>
                )}
                {enrichData && !enrichLoading && (
                  <div className="flex items-center flex-wrap gap-1">
                    <span className="text-sm font-mono text-neutral-800 dark:text-neutral-200">
                      {enrichData.email || "—"}
                    </span>
                    {confidenceBadge(enrichData.email_confidence)}
                  </div>
                )}
              </div>

              {/* Cold Email Draft */}
              {enrichData && enrichData.cold_email_draft && (
                <div>
                  <button
                    onClick={() => setDraftOpen(!draftOpen)}
                    className="text-xs font-semibold uppercase tracking-wide text-neutral-400 mb-2 flex items-center gap-1 hover:text-neutral-700 dark:hover:text-neutral-200 transition-colors"
                  >
                    Cold Email Draft
                    <span className="text-base leading-none">{draftOpen ? "▾" : "▸"}</span>
                  </button>
                  <AnimatePresence>
                    {draftOpen && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        transition={{ duration: 0.2 }}
                        className="overflow-hidden"
                      >
                        <div className="relative rounded-lg bg-neutral-50 dark:bg-neutral-800 p-4 text-sm text-neutral-700 dark:text-neutral-300 leading-relaxed whitespace-pre-wrap">
                          {enrichData.cold_email_draft}
                          <button
                            onClick={copyDraft}
                            className="absolute top-2 right-2 text-xs px-2 py-1 rounded bg-neutral-200 dark:bg-neutral-700 text-neutral-600 dark:text-neutral-300 hover:opacity-80 transition-opacity"
                          >
                            {copied ? "Copied!" : "Copy"}
                          </button>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
