import Link from "next/link";
import { ArrowRight, Database, FileSearch, MessageSquareText, Upload } from "lucide-react";

import { Navbar } from "@/components/Navbar";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

const features = [
  {
    title: "PDF Upload",
    description: "Send research papers to the FastAPI backend and index them for retrieval.",
    icon: Upload
  },
  {
    title: "Grounded Answers",
    description: "Ask paper-specific questions powered by embeddings, FAISS, and Ollama.",
    icon: MessageSquareText
  },
  {
    title: "RAG Pipeline",
    description: "Built to connect directly with your parser, chunker, vector store, and local LLM.",
    icon: Database
  }
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-grid-fade">
      <Navbar />

      <main className="mx-auto flex max-w-7xl flex-col gap-12 px-4 py-12 sm:px-6 lg:px-8">
        <section className="grid gap-8 lg:grid-cols-[1.15fr_0.85fr] lg:items-center">
          <div className="space-y-6">
            <div className="inline-flex items-center gap-2 rounded-full border border-border/70 bg-background/80 px-4 py-2 text-sm text-muted-foreground shadow-soft">
              <FileSearch className="h-4 w-4 text-primary" />
              Vercel-ready AI dashboard for research workflows
            </div>

            <div className="space-y-4">
              <h1 className="max-w-3xl text-4xl font-semibold tracking-tight sm:text-5xl">
                Chat with research papers using your Python RAG backend.
              </h1>
              <p className="max-w-2xl text-lg leading-8 text-muted-foreground">
                Upload PDFs, ask grounded questions, and explore papers through a
                modern interface inspired by ChatGPT, Notion, and Perplexity.
              </p>
            </div>

            <div className="flex flex-wrap gap-3">
              <Button asChild size="lg">
                <Link href="/dashboard">
                  Open Dashboard
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button asChild variant="outline" size="lg">
                <a href={process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"} target="_blank" rel="noreferrer">
                  View Backend API
                </a>
              </Button>
            </div>
          </div>

          <Card className="overflow-hidden border-primary/10 bg-gradient-to-br from-primary/10 via-background to-background">
            <CardContent className="space-y-6 p-6 sm:p-8">
              <div className="rounded-3xl border border-border/70 bg-background/80 p-5">
                <p className="text-sm font-medium text-muted-foreground">Example flow</p>
                <div className="mt-4 space-y-4">
                  <div className="rounded-2xl bg-secondary/70 p-4 text-sm">
                    Upload `paper.pdf`
                  </div>
                  <div className="rounded-2xl bg-primary p-4 text-sm text-primary-foreground">
                    What is the paper&apos;s main contribution?
                  </div>
                  <div className="rounded-2xl bg-secondary/70 p-4 text-sm leading-6">
                    The assistant retrieves relevant chunks from the vector store and
                    returns a grounded answer from the indexed paper.
                  </div>
                </div>
              </div>

              <div className="grid gap-4">
                {features.map((feature) => (
                  <div
                    key={feature.title}
                    className="flex items-start gap-4 rounded-3xl border border-border/70 bg-background/70 p-4"
                  >
                    <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-primary/10 text-primary">
                      <feature.icon className="h-5 w-5" />
                    </div>
                    <div>
                      <h2 className="font-medium">{feature.title}</h2>
                      <p className="mt-1 text-sm leading-6 text-muted-foreground">
                        {feature.description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </section>
      </main>
    </div>
  );
}
