"use client";

import { BookOpen, Loader2 } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface PaperSummaryCardProps {
  paperName: string;
  summary?: string;
  isLoading?: boolean;
}

export function PaperSummaryCard({
  paperName,
  summary,
  isLoading = false,
}: PaperSummaryCardProps) {
  return (
    <Card className="border-primary/10 bg-gradient-to-br from-primary/5 via-background to-background">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-base">
          <BookOpen className="h-4 w-4 text-primary" />
          Paper Summary
        </CardTitle>
        <p className="text-xs text-muted-foreground">{paperName}</p>
      </CardHeader>

      <CardContent>
        {isLoading ? (
          <div className="flex items-center gap-3 rounded-2xl border border-dashed border-border/80 bg-secondary/40 p-4">
            <Loader2 className="h-4 w-4 animate-spin text-primary" />
            <p className="text-sm text-muted-foreground">
              Generating summary...
            </p>
          </div>
        ) : summary ? (
          <div className="rounded-2xl border border-border/70 bg-background/70 p-4">
            <p className="whitespace-pre-wrap text-sm leading-7 text-foreground">
              {summary}
            </p>
          </div>
        ) : (
          <div className="rounded-2xl border border-dashed border-border/80 bg-secondary/40 p-4">
            <p className="text-sm text-muted-foreground">
              No summary available yet.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
