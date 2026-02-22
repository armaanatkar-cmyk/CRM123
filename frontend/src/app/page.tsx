"use client";

import { PlaceholdersAndVanishInput } from "@/components/ui/placeholders-and-vanish-input";
import { BackgroundPaths } from "@/components/ui/background-paths";
import { useState } from "react";
import { motion } from "framer-motion";

interface SearchResult {
  title: string;
  url: string;
  snippet: string;
  company?: string;
}

interface SearchResponse {
  agencies: SearchResult[];
  people: SearchResult[];
  company_people: SearchResult[];
  parsed_intent: {
    icp: string;
    industry: string;
    region: string;
    search_type: string;
  };
}

export default function PlaceholdersAndVanishInputDemo() {
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [currentQuery, setCurrentQuery] = useState("");

  const placeholders = [
    "VP Marketing for healthcare agencies in California",
    "Growth Leads at fintech startups in New York",
    "Sales Directors for SaaS companies in Texas",
    "Founders of AI startups in Europe",
    "Head of HR at logistics firms in Canada",
  ];

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCurrentQuery(e.target.value);
  };

  const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!currentQuery.trim()) return;

    setLoading(true);
    setError("");
    setResults(null);

    try {
      const res = await fetch("https://crm123-mggu.onrender.com/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: currentQuery }),
      });

      if (!res.ok) {
        throw new Error("Failed to fetch results");
      }

      const data: SearchResponse = await res.json();
      setResults(data);
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const ResultCard = ({ result }: { result: SearchResult }) => (
    <a
      href={result.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block p-4 rounded-lg border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors"
    >
      <h3 className="font-semibold text-blue-600 dark:text-blue-400 mb-1 line-clamp-1">
        {result.title}
      </h3>
      {result.company && (
        <span className="inline-block px-2 py-0.5 rounded text-xs bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400 mb-2">
          {result.company}
        </span>
      )}
      <p className="text-sm text-neutral-600 dark:text-neutral-400 line-clamp-2">
        {result.snippet}
      </p>
    </a>
  );

  return (
    <div className="min-h-screen flex flex-col items-center">
      <BackgroundPaths title="ICP Finder AI" />

      <div className="w-full max-w-7xl px-4 flex flex-col items-center -mt-10 pb-20">
      <div className="w-full max-w-xl mb-12">
        <PlaceholdersAndVanishInput
          placeholders={placeholders}
          onChange={handleChange}
          onSubmit={onSubmit}
        />
      </div>

      <div className="w-full max-w-5xl space-y-8">
        {loading && (
          <div className="text-center text-neutral-500 animate-pulse">
            Searching specifically for your ICP...
          </div>
        )}

        {error && (
          <div className="text-center text-red-500 bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
            {error}
          </div>
        )}

        {results && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-12"
          >
             <div className="text-center text-neutral-500 mb-8">
              Found matches for <strong>{results.parsed_intent.icp}</strong> in{" "}
              <strong>{results.parsed_intent.industry}</strong> around{" "}
              <strong>{results.parsed_intent.region}</strong>
            </div>

            {results.agencies.length > 0 && (
              <section>
                <h3 className="text-2xl font-bold mb-4 dark:text-white">Agencies & Companies</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {results.agencies.map((r, i) => (
                    <ResultCard key={i} result={r} />
                  ))}
                </div>
              </section>
            )}
            
            {results.company_people.length > 0 && (
               <section>
                <h3 className="text-2xl font-bold mb-4 dark:text-white">People at Target Companies</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {results.company_people.map((r, i) => (
                    <ResultCard key={i} result={r} />
                  ))}
                </div>
              </section>
            )}


            {results.people.length > 0 && (
              <section>
                <h3 className="text-2xl font-bold mb-4 dark:text-white">Individual Profiles</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {results.people.map((r, i) => (
                    <ResultCard key={i} result={r} />
                  ))}
                </div>
              </section>
            )}

            {results.agencies.length === 0 && results.people.length === 0 && (
              <div className="text-center text-neutral-500">
                No results found. Try adjusting your query.
              </div>
            )}
          </motion.div>
        )}
      </div>
      </div>
    </div>
  );
}
