import type { Message, PaperItem } from "@/lib/types";

const PAPERS_KEY = "ars_papers";
const MESSAGES_KEY = "ars_messages";

// ---- Papers ----

export function loadPapersFromStorage(): PaperItem[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(PAPERS_KEY);
    return raw ? (JSON.parse(raw) as PaperItem[]) : [];
  } catch {
    return [];
  }
}

export function savePapersToStorage(papers: PaperItem[]): void {
  if (typeof window === "undefined") return;
  try {
    // Strip transient fields before persisting
    const cleaned = papers.map(({ id, name, uploadedAt, summary }) => ({
      id,
      name,
      uploadedAt,
      summary,
    }));
    window.localStorage.setItem(PAPERS_KEY, JSON.stringify(cleaned));
  } catch {
    // Storage full or unavailable — silently ignore
  }
}

// ---- Messages ----

export function loadMessagesFromStorage(): Record<string, Message[]> {
  if (typeof window === "undefined") return {};
  try {
    const raw = window.localStorage.getItem(MESSAGES_KEY);
    return raw ? (JSON.parse(raw) as Record<string, Message[]>) : {};
  } catch {
    return {};
  }
}

export function saveMessagesToStorage(messages: Record<string, Message[]>): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(MESSAGES_KEY, JSON.stringify(messages));
  } catch {
    // Storage full or unavailable — silently ignore
  }
}
