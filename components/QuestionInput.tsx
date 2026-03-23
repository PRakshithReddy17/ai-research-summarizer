"use client";

import { useState } from "react";
import { Loader2, SendHorizontal } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface QuestionInputProps {
  disabled?: boolean;
  isLoading?: boolean;
  placeholder?: string;
  onSubmit: (question: string) => Promise<void>;
}

export function QuestionInput({
  disabled = false,
  isLoading = false,
  placeholder,
  onSubmit
}: QuestionInputProps) {
  const [question, setQuestion] = useState("");

  const handleSubmit = async () => {
    const trimmedQuestion = question.trim();
    if (!trimmedQuestion || disabled || isLoading) {
      return;
    }

    await onSubmit(trimmedQuestion);
    setQuestion("");
  };

  return (
    <div className="rounded-[28px] border border-border/70 bg-card/90 p-3 shadow-soft backdrop-blur">
      <div className="flex flex-col gap-3">
        <Textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          disabled={disabled || isLoading}
          placeholder={
            disabled
              ? "Upload a paper to begin."
              : placeholder ?? "Ask about the paper's contribution, methodology, results, or limitations..."
          }
          className="min-h-[110px] resize-none border-0 bg-transparent p-2 shadow-none focus-visible:ring-0"
          onKeyDown={async (event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              await handleSubmit();
            }
          }}
        />

        <div className="flex items-center justify-between gap-3">
          <p className="text-xs text-muted-foreground">
            Press Enter to send, Shift + Enter for a new line.
          </p>

          <Button onClick={handleSubmit} disabled={disabled || isLoading || !question.trim()}>
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Thinking...
              </>
            ) : (
              <>
                <SendHorizontal className="mr-2 h-4 w-4" />
                Send
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
