export interface Message {
  role: "user" | "assistant";
  content: string;
}

export interface PaperItem {
  id: string;
  name: string;
  uploadedAt: string;
  summary?: string;
  summaryLoading?: boolean;
}
