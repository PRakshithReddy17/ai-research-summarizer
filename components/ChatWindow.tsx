"use client";

import { useEffect, useRef } from "react";
import { FileText } from "lucide-react";

import { MessageBubble } from "@/components/MessageBubble";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Message } from "@/lib/types";

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
  selectedPaperName?: string;
}

export function ChatWindow({
  messages,
  isLoading,
  selectedPaperName
}: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <Card className="flex min-h-[55vh] flex-1 flex-col overflow-hidden">
      <CardHeader className="border-b border-border/60">
        <CardTitle className="flex items-center gap-2 text-base">
          <FileText className="h-4 w-4 text-primary" />
          {selectedPaperName ? selectedPaperName : "Select a paper to start chatting"}
        </CardTitle>
      </CardHeader>

      <CardContent className="flex flex-1 flex-col gap-4 overflow-y-auto p-4 sm:p-6">
        {messages.length === 0 ? (
          <div className="flex flex-1 items-center justify-center">
            <div className="max-w-lg rounded-3xl border border-dashed border-border/80 bg-secondary/40 px-6 py-10 text-center">
              <p className="text-lg font-semibold">Ask your paper anything</p>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">
                Upload a research PDF, select it from the sidebar, and start asking
                about contributions, methods, datasets, or results.
              </p>
            </div>
          </div>
        ) : (
          messages.map((message, index) => (
            <MessageBubble
              key={`${message.role}-${index}-${message.content.slice(0, 24)}`}
              role={message.role}
              content={message.content}
            />
          ))
        )}

        {isLoading ? <MessageBubble role="assistant" content="" isTyping /> : null}
        <div ref={bottomRef} />
      </CardContent>
    </Card>
  );
}
