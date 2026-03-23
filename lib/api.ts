const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

const API_KEY = process.env.NEXT_PUBLIC_API_KEY ?? "";

function authHeaders(): Record<string, string> {
  const headers: Record<string, string> = {};
  if (API_KEY) {
    headers["X-API-Key"] = API_KEY;
  }
  return headers;
}

export interface UploadResponse {
  paper_id: string;
  message: string;
}

export interface AskResponse {
  answer: string;
}

export interface SummaryResponse {
  paper_id: string;
  summary: string;
}

export interface PaperListItem {
  paper_id: string;
  file_name: string;
  has_summary: boolean;
}

export interface PapersListResponse {
  papers: PaperListItem[];
}

function parseErrorMessage(payload: unknown, fallback: string) {
  if (!payload || typeof payload !== "object") {
    return fallback;
  }

  if ("detail" in payload && typeof payload.detail === "string") {
    return payload.detail;
  }

  if ("message" in payload && typeof payload.message === "string") {
    return payload.message;
  }

  return fallback;
}

function parseResponseSafely(responseText: string) {
  try {
    return JSON.parse(responseText);
  } catch {
    return null;
  }
}

export function uploadPDF(
  file: File,
  onProgress?: (progress: number) => void
): Promise<UploadResponse> {
  return new Promise((resolve, reject) => {
    const formData = new FormData();
    formData.append("file", file);

    const request = new XMLHttpRequest();
    request.open("POST", `${API_URL}/upload`);
    request.responseType = "json";
    if (API_KEY) request.setRequestHeader("X-API-Key", API_KEY);

    request.upload.onprogress = (event) => {
      if (!event.lengthComputable) {
        return;
      }

      const progress = Math.round((event.loaded / event.total) * 100);
      onProgress?.(progress);
    };

    request.onload = () => {
      const payload =
        request.response ??
        (request.responseText ? parseResponseSafely(request.responseText) : null);

      if (request.status >= 200 && request.status < 300) {
        onProgress?.(100);
        resolve(payload as UploadResponse);
        return;
      }

      reject(
        new Error(parseErrorMessage(payload, "Unable to upload the PDF right now."))
      );
    };

    request.onerror = () => {
      reject(new Error("Network error while uploading the PDF."));
    };

    request.send(formData);
  });
}

export async function askQuestion(
  paper_id: string,
  question: string
): Promise<AskResponse> {
  const response = await fetch(`${API_URL}/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
    },
    body: JSON.stringify({ paper_id, question })
  });

  const payload = (await response.json()) as AskResponse | { detail?: string };

  if (!response.ok) {
    throw new Error(
      parseErrorMessage(payload, "Unable to get an answer from the assistant.")
    );
  }

  return payload as AskResponse;
}

export async function fetchSummary(
  paper_id: string
): Promise<SummaryResponse> {
  const response = await fetch(`${API_URL}/summarize/${paper_id}`, {
    headers: authHeaders(),
  });

  const payload = (await response.json()) as SummaryResponse | { detail?: string };

  if (!response.ok) {
    throw new Error(
      parseErrorMessage(payload, "Unable to generate the paper summary.")
    );
  }

  return payload as SummaryResponse;
}

// ---- cross-paper Q&A ----

export interface AskAllResponse {
  answer: string;
  sources: string[];
}

export async function askAllPapers(
  question: string
): Promise<AskAllResponse> {
  const response = await fetch(`${API_URL}/ask-all`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ question }),
  });

  const payload = (await response.json()) as AskAllResponse | { detail?: string };

  if (!response.ok) {
    throw new Error(
      parseErrorMessage(payload, "Unable to search across papers.")
    );
  }

  return payload as AskAllResponse;
}

// ---- arXiv types ----

export interface ArxivPaper {
  title: string;
  authors: string[];
  summary: string;
  pdf_url: string;
  published: string;
}

export interface ArxivSearchResponse {
  results: ArxivPaper[];
}

export interface ArxivImportResponse {
  paper_id: string;
  file_name: string;
  message: string;
}

// ---- arXiv API calls ----

export async function searchArxiv(
  query: string,
  maxResults: number = 5
): Promise<ArxivSearchResponse> {
  const response = await fetch(`${API_URL}/search-arxiv`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ query, max_results: maxResults }),
  });

  const payload = (await response.json()) as ArxivSearchResponse | { detail?: string };

  if (!response.ok) {
    throw new Error(
      parseErrorMessage(payload, "Unable to search arXiv.")
    );
  }

  return payload as ArxivSearchResponse;
}

export async function importArxivPaper(
  pdfUrl: string,
  title: string
): Promise<ArxivImportResponse> {
  const response = await fetch(`${API_URL}/import-arxiv`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ pdf_url: pdfUrl, title }),
  });

  const payload = (await response.json()) as ArxivImportResponse | { detail?: string };

  if (!response.ok) {
    throw new Error(
      parseErrorMessage(payload, "Unable to import the paper from arXiv.")
    );
  }

  return payload as ArxivImportResponse;
}

// ---- papers list ----

export async function listPapers(): Promise<PapersListResponse> {
  const response = await fetch(`${API_URL}/papers`, {
    headers: authHeaders(),
  });

  const payload = (await response.json()) as PapersListResponse | { detail?: string };

  if (!response.ok) {
    throw new Error(
      parseErrorMessage(payload, "Unable to fetch papers list.")
    );
  }

  return payload as PapersListResponse;
}
