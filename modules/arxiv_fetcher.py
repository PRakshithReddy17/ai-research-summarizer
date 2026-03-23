import arxiv
import requests
import os
import re
from typing import List, Dict, Optional


def fetch_papers(query: str, max_results: int = 5) -> List[Dict]:
    """
    Fetch research papers from arXiv.

    Args:
        query (str): Topic to search.
        max_results (int): Number of papers to retrieve.

    Returns:
        List[Dict]: List containing metadata of papers.
    """

    papers = []

    try:
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        for result in search.results():

            paper = {
                "title": result.title.strip(),
                "authors": [author.name for author in result.authors],
                "summary": result.summary.strip()[:1200],  # limit summary length
                "pdf_url": result.pdf_url,
                "published": result.published.strftime("%Y-%m-%d"),
            }

            papers.append(paper)

    except Exception as e:
        print(f"[ERROR] Failed to fetch papers: {e}")

    return papers


def clean_filename(text: str) -> str:
    """
    Convert a paper title into a safe filename.
    """

    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "_", text)

    return text[:80]


def download_pdf(pdf_url: str, title: str, save_dir: str = "data") -> Optional[str]:
    """
    Download a PDF from arXiv and save locally.

    Args:
        pdf_url (str): URL of the paper PDF
        title (str): Paper title
        save_dir (str): Folder to store PDFs

    Returns:
        str | None: Path to downloaded file
    """

    os.makedirs(save_dir, exist_ok=True)

    filename = clean_filename(title) + ".pdf"
    filepath = os.path.join(save_dir, filename)

    try:
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()

        with open(filepath, "wb") as f:
            f.write(response.content)

        return filepath

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to download PDF: {e}")
        return None


def print_paper_info(paper: Dict, index: int):
    """
    Pretty print paper details.
    """

    print(f"\nPaper {index}")
    print("-" * 50)
    print("Title:", paper["title"])
    print("Authors:", ", ".join(paper["authors"]))
    print("Published:", paper["published"])
    print("PDF:", paper["pdf_url"])


# Run test when file executed directly
if __name__ == "__main__":

    QUERY = "large language models"

    print(f"\nSearching arXiv for: {QUERY}\n")

    papers = fetch_papers(QUERY, max_results=3)

    if not papers:
        print("No papers found.")
        exit()

    for i, paper in enumerate(papers, start=1):

        print_paper_info(paper, i)

        path = download_pdf(paper["pdf_url"], paper["title"])

        if path:
            print("Saved to:", path)
        else:
            print("Download failed.")