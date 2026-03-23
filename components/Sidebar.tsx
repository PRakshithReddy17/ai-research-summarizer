import { FileText, Sparkles } from "lucide-react";

import { ArxivSearch } from "@/components/ArxivSearch";
import { UploadPDF } from "@/components/UploadPDF";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { PaperItem } from "@/lib/types";

interface SidebarProps {
  papers: PaperItem[];
  currentPaperId: string | null;
  onSelectPaper: (paperId: string) => void;
  onUploadSuccess: (payload: { paperId: string; fileName: string }) => void;
  onUploadError: (message: string) => void;
}

export function Sidebar({
  papers,
  currentPaperId,
  onSelectPaper,
  onUploadSuccess,
  onUploadError
}: SidebarProps) {
  return (
    <aside className="flex w-full flex-col gap-4 lg:w-[340px]">
      <UploadPDF
        onUploadSuccess={onUploadSuccess}
        onUploadError={onUploadError}
      />

      <ArxivSearch
        onImportSuccess={onUploadSuccess}
        onImportError={onUploadError}
      />

      <Card className="flex-1">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <Sparkles className="h-4 w-4 text-primary" />
            Uploaded Papers
          </CardTitle>
        </CardHeader>

        <CardContent className="space-y-3">
          {papers.length === 0 ? (
            <div className="rounded-3xl border border-dashed border-border/80 bg-secondary/40 p-4 text-sm text-muted-foreground">
              Upload a paper to create your first RAG chat workspace.
            </div>
          ) : (
            papers.map((paper) => (
              <button
                key={paper.id}
                type="button"
                onClick={() => onSelectPaper(paper.id)}
                className={cn(
                  "w-full rounded-3xl border p-4 text-left transition",
                  currentPaperId === paper.id
                    ? "border-primary/30 bg-primary/5"
                    : "border-border/70 bg-background/60 hover:bg-accent"
                )}
              >
                <div className="flex items-start gap-3">
                  <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl bg-secondary text-secondary-foreground">
                    <FileText className="h-4 w-4" />
                  </div>
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium">{paper.name}</p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      Paper ID: {paper.id.slice(0, 8)}...
                    </p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      Uploaded {new Date(paper.uploadedAt).toLocaleString()}
                    </p>
                  </div>
                </div>
              </button>
            ))
          )}
        </CardContent>
      </Card>
    </aside>
  );
}
