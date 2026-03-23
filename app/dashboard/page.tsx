"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { AlertCircle, CheckCircle2 } from "lucide-react";

import { ChatWindow } from "@/components/ChatWindow";
import { Navbar } from "@/components/Navbar";
import { PaperSummaryCard } from "@/components/PaperSummaryCard";
import { QuestionInput } from "@/components/QuestionInput";
import { Sidebar } from "@/components/Sidebar";
import { Card } from "@/components/ui/card";
import { askQuestion, askAllPapers, fetchSummary, listPapers } from "@/lib/api";
import {
  loadPapersFromStorage,
  savePapersToStorage,
  loadMessagesFromStorage,
  saveMessagesToStorage,
} from "@/lib/local-storage";
import type { Message, PaperItem } from "@/lib/types";

type StatusState =
  | { type: "success"; text: string }
  | { type: "error"; text: string }
  | null;

export default function DashboardPage() {
  const [papers, setPapers] = useState<PaperItem[]>(() => loadPapersFromStorage());
  const [currentPaperId, setCurrentPaperId] = useState<string | null>(null);
  const [messagesByPaper, setMessagesByPaper] = useState<Record<string, Message[]>>(
    () => loadMessagesFromStorage()
  );
  const [loadingPaperId, setLoadingPaperId] = useState<string | null>(null);
  const [status, setStatus] = useState<StatusState>(null);
  const hasFetchedPapers = useRef(false);

  const currentPaper = useMemo(
    () => papers.find((paper) => paper.id === currentPaperId) ?? null,
    [papers, currentPaperId]
  );

  const activeChatId = currentPaperId ?? "__all__";
  const currentMessages = messagesByPaper[activeChatId] ?? [];

  // Persist papers & messages to localStorage whenever they change
  useEffect(() => { savePapersToStorage(papers); }, [papers]);
  useEffect(() => { saveMessagesToStorage(messagesByPaper); }, [messagesByPaper]);

  // Load previously uploaded papers from the backend on mount
  useEffect(() => {
    if (hasFetchedPapers.current) return;
    hasFetchedPapers.current = true;

    listPapers()
      .then((res) => {
        if (res.papers.length === 0) return;
        setPapers((prev) => {
          const existingIds = new Set(prev.map((p) => p.id));
          const restored = res.papers
            .filter((p) => !existingIds.has(p.paper_id))
            .map((p) => ({
              id: p.paper_id,
              name: p.file_name,
              uploadedAt: new Date().toISOString(),
            }));
          return [...prev, ...restored];
        });
      })
      .catch(() => {
        // Backend may not be running yet — silently ignore
      });
  }, []);

  useEffect(() => {
    if (!status) {
      return;
    }

    const timeout = window.setTimeout(() => setStatus(null), 4000);
    return () => window.clearTimeout(timeout);
  }, [status]);

  // Auto-fetch summary when a paper is selected and doesn't have one yet
  useEffect(() => {
    if (!currentPaperId) {
      return;
    }

    const paper = papers.find((p) => p.id === currentPaperId);
    if (!paper || paper.summary || paper.summaryLoading) {
      return;
    }

    // Mark as loading
    setPapers((prev) =>
      prev.map((p) =>
        p.id === currentPaperId ? { ...p, summaryLoading: true } : p
      )
    );

    fetchSummary(currentPaperId)
      .then((res) => {
        setPapers((prev) =>
          prev.map((p) =>
            p.id === currentPaperId
              ? { ...p, summary: res.summary, summaryLoading: false }
              : p
          )
        );
      })
      .catch(() => {
        setPapers((prev) =>
          prev.map((p) =>
            p.id === currentPaperId
              ? { ...p, summary: "Unable to generate summary.", summaryLoading: false }
              : p
          )
        );
      });
  }, [currentPaperId, papers]);

  const appendMessage = (paperId: string, message: Message) => {
    setMessagesByPaper((previous) => ({
      ...previous,
      [paperId]: [...(previous[paperId] ?? []), message]
    }));
  };

  const handleUploadSuccess = ({
    paperId,
    fileName
  }: {
    paperId: string;
    fileName: string;
  }) => {
    const nextPaper: PaperItem = {
      id: paperId,
      name: fileName,
      uploadedAt: new Date().toISOString()
    };

    setPapers((previous) => [nextPaper, ...previous.filter((paper) => paper.id !== paperId)]);
    setCurrentPaperId(paperId);
    setMessagesByPaper((previous) => ({
      ...previous,
      [paperId]:
        previous[paperId] ?? [
          {
            role: "assistant",
            content: `${fileName} is ready. Ask me about its contribution, methods, results, or limitations.`
          }
        ]
    }));
    setStatus({ type: "success", text: `${fileName} uploaded successfully.` });
  };

  const handleUploadError = (message: string) => {
    setStatus({ type: "error", text: message });
  };

  const handleQuestionSubmit = async (question: string) => {
    // If a paper is selected → ask that paper. Otherwise → ask across all papers.
    const paperId = currentPaperId ?? "__all__";

    appendMessage(paperId, { role: "user", content: question });
    setLoadingPaperId(paperId);

    try {
      if (currentPaperId) {
        const response = await askQuestion(currentPaperId, question);
        appendMessage(paperId, { role: "assistant", content: response.answer });
      } else {
        const response = await askAllPapers(question);
        const sourceLine = response.sources.length
          ? `\n\n**Sources:** ${response.sources.join(", ")}`
          : "";
        appendMessage(paperId, {
          role: "assistant",
          content: response.answer + sourceLine,
        });
      }
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Something went wrong while generating the answer.";

      appendMessage(paperId, {
        role: "assistant",
        content: `I couldn't complete that request. ${message}`
      });
      setStatus({ type: "error", text: message });
    } finally {
      setLoadingPaperId((previous) => (previous === paperId ? null : previous));
    }
  };

  return (
    <div className="min-h-screen bg-grid-fade">
      <Navbar />

      <main className="mx-auto flex max-w-7xl flex-col gap-6 px-4 py-6 sm:px-6 lg:px-8">
        {status ? (
          <Card
            className={`border px-4 py-3 ${
              status.type === "success"
                ? "border-emerald-500/20 bg-emerald-500/10"
                : "border-red-500/20 bg-red-500/10"
            }`}
          >
            <div className="flex items-center gap-3 text-sm">
              {status.type === "success" ? (
                <CheckCircle2 className="h-4 w-4 text-emerald-600" />
              ) : (
                <AlertCircle className="h-4 w-4 text-red-600" />
              )}
              <span>{status.text}</span>
            </div>
          </Card>
        ) : null}

        <div className="flex flex-col gap-6 lg:flex-row">
          <Sidebar
            papers={papers}
            currentPaperId={currentPaperId}
            onSelectPaper={setCurrentPaperId}
            onUploadSuccess={handleUploadSuccess}
            onUploadError={handleUploadError}
          />

          <section className="flex min-h-[70vh] flex-1 flex-col gap-4">
            {currentPaper ? (
              <PaperSummaryCard
                paperName={currentPaper.name}
                summary={currentPaper.summary}
                isLoading={currentPaper.summaryLoading}
              />
            ) : null}
            <ChatWindow
              messages={currentMessages}
              isLoading={loadingPaperId === activeChatId}
              selectedPaperName={currentPaper?.name ?? (papers.length > 0 ? "All Papers" : undefined)}
            />
            <QuestionInput
              disabled={papers.length === 0 || loadingPaperId !== null}
              isLoading={loadingPaperId === activeChatId}
              onSubmit={handleQuestionSubmit}
              placeholder={
                currentPaperId
                  ? undefined
                  : papers.length > 0
                    ? "Ask across all uploaded papers..."
                    : undefined
              }
            />
          </section>
        </div>
      </main>
    </div>
  );
}
