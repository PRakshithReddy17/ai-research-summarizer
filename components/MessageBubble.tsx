"use client";

import { Bot, User2 } from "lucide-react";
import ReactMarkdown from "react-markdown";

import { cn } from "@/lib/utils";

interface MessageBubbleProps {
  role: "user" | "assistant";
  content: string;
  isTyping?: boolean;
}

export function MessageBubble({
  role,
  content,
  isTyping = false
}: MessageBubbleProps) {
  const isAssistant = role === "assistant";

  return (
    <div className={cn("flex w-full", isAssistant ? "justify-start" : "justify-end")}>
      <div
        className={cn(
          "flex max-w-[90%] gap-3 rounded-3xl border px-4 py-3 shadow-sm sm:max-w-[80%]",
          isAssistant
            ? "border-border bg-card text-card-foreground"
            : "border-primary/10 bg-primary text-primary-foreground"
        )}
      >
        <div
          className={cn(
            "mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
            isAssistant
              ? "bg-secondary text-secondary-foreground"
              : "bg-primary-foreground/15 text-primary-foreground"
          )}
        >
          {isAssistant ? <Bot className="h-4 w-4" /> : <User2 className="h-4 w-4" />}
        </div>

        <div className="space-y-1 min-w-0 flex-1">
          <p
            className={cn(
              "text-xs font-medium uppercase tracking-[0.2em]",
              isAssistant ? "text-muted-foreground" : "text-primary-foreground/70"
            )}
          >
            {isAssistant ? "Assistant" : "You"}
          </p>

          {isTyping ? (
            <div className="flex items-center gap-1.5 py-2">
              <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.3s]" />
              <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.15s]" />
              <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground" />
            </div>
          ) : isAssistant ? (
            <div className="prose prose-sm dark:prose-invert max-w-none leading-7 [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
              <ReactMarkdown>{content}</ReactMarkdown>
            </div>
          ) : (
            <p className="whitespace-pre-wrap text-sm leading-7">{content}</p>
          )}
        </div>
      </div>
    </div>
  );
}
