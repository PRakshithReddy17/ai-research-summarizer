"use client";

import { type ChangeEvent, useRef, useState } from "react";
import { Loader2, UploadCloud } from "lucide-react";

import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { uploadPDF } from "@/lib/api";

interface UploadPDFProps {
  onUploadSuccess: (payload: { paperId: string; fileName: string }) => void;
  onUploadError: (message: string) => void;
}

export function UploadPDF({
  onUploadSuccess,
  onUploadError
}: UploadPDFProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleFileSelection = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    if (file.type !== "application/pdf") {
      onUploadError("Please upload a valid PDF file.");
      event.target.value = "";
      return;
    }

    setIsUploading(true);
    setProgress(0);

    try {
      const response = await uploadPDF(file, setProgress);
      onUploadSuccess({ paperId: response.paper_id, fileName: file.name });
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Unable to upload this PDF.";
      onUploadError(message);
    } finally {
      setIsUploading(false);
      event.target.value = "";
      window.setTimeout(() => setProgress(0), 600);
    }
  };

  return (
    <Card className="border-primary/10 bg-gradient-to-br from-primary/5 to-background">
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Upload Research Paper</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          className="hidden"
          onChange={handleFileSelection}
        />

        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          disabled={isUploading}
          className="flex w-full flex-col items-center justify-center rounded-3xl border border-dashed border-border/80 bg-background/70 px-4 py-6 text-center transition hover:border-primary/40 hover:bg-background disabled:cursor-not-allowed disabled:opacity-70"
        >
          <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
            {isUploading ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <UploadCloud className="h-5 w-5" />
            )}
          </div>
          <p className="text-sm font-medium">
            {isUploading ? "Uploading PDF..." : "Choose a PDF to upload"}
          </p>
          <p className="mt-1 text-xs text-muted-foreground">
            Your document will be indexed for retrieval-augmented chat.
          </p>
        </button>

        {isUploading ? (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>Upload progress</span>
              <span>{progress}%</span>
            </div>
            <Progress value={progress} />
          </div>
        ) : null}

        <Button
          type="button"
          variant="outline"
          className="w-full"
          onClick={() => inputRef.current?.click()}
          disabled={isUploading}
        >
          {isUploading ? "Uploading..." : "Upload Paper"}
        </Button>
      </CardContent>
    </Card>
  );
}
