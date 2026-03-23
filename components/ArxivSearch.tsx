"use client";

import { useState } from "react";
import {
  Download,
  ExternalLink,
  Loader2,
  Search,
  Users,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  searchArxiv,
  importArxivPaper,
  type ArxivPaper,
} from "@/lib/api";

interface ArxivSearchProps {
  onImportSuccess: (payload: { paperId: string; fileName: string }) => void;
  onImportError: (message: string) => void;
}

export function ArxivSearch({ onImportSuccess, onImportError }: ArxivSearchProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<ArxivPaper[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [importingUrl, setImportingUrl] = useState<string | null>(null);

  const handleSearch = async () => {
    const trimmed = query.trim();
    if (!trimmed || isSearching) return;

    setIsSearching(true);
    setResults([]);

    try {
      const res = await searchArxiv(trimmed, 5);
      setResults(res.results);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Search failed.";
      onImportError(msg);
    } finally {
      setIsSearching(false);
    }
  };

  const handleImport = async (paper: ArxivPaper) => {
    if (importingUrl) return;

    setImportingUrl(paper.pdf_url);

    try {
      const res = await importArxivPaper(paper.pdf_url, paper.title);
      onImportSuccess({ paperId: res.paper_id, fileName: res.file_name });
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Import failed.";
      onImportError(msg);
    } finally {
      setImportingUrl(null);
    }
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <Search className="h-4 w-4 text-primary" />
          Search arXiv
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSearch();
          }}
          className="flex gap-2"
        >
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. large language models"
            disabled={isSearching}
          />
          <Button type="submit" size="sm" disabled={isSearching || !query.trim()}>
            {isSearching ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Search className="h-4 w-4" />
            )}
          </Button>
        </form>

        {results.length > 0 && (
          <div className="max-h-[340px] space-y-3 overflow-y-auto pr-1">
            {results.map((paper) => (
              <div
                key={paper.pdf_url}
                className="rounded-2xl border border-border/70 bg-background/70 p-3 space-y-2"
              >
                <p className="text-sm font-medium leading-5">{paper.title}</p>

                <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <Users className="h-3 w-3" />
                  <span className="truncate">
                    {paper.authors.slice(0, 3).join(", ")}
                    {paper.authors.length > 3 && " et al."}
                  </span>
                  <span className="ml-auto shrink-0">{paper.published}</span>
                </div>

                <p className="text-xs leading-5 text-muted-foreground line-clamp-3">
                  {paper.summary}
                </p>

                <div className="flex items-center gap-2 pt-1">
                  <Button
                    size="sm"
                    variant="outline"
                    className="h-7 text-xs"
                    onClick={() => handleImport(paper)}
                    disabled={importingUrl !== null}
                  >
                    {importingUrl === paper.pdf_url ? (
                      <>
                        <Loader2 className="mr-1.5 h-3 w-3 animate-spin" />
                        Importing...
                      </>
                    ) : (
                      <>
                        <Download className="mr-1.5 h-3 w-3" />
                        Import
                      </>
                    )}
                  </Button>
                  <a
                    href={paper.pdf_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition"
                  >
                    <ExternalLink className="h-3 w-3" />
                    PDF
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}

        {!isSearching && results.length === 0 && query.trim() === "" && (
          <div className="rounded-2xl border border-dashed border-border/80 bg-secondary/40 p-4 text-center">
            <p className="text-xs text-muted-foreground">
              Search for a topic to find and import papers from arXiv.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
