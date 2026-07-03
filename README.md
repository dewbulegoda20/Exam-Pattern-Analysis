# AI-Powered Exam Pattern Analysis and Question Prediction System

<<<<<<< Updated upstream
Analyze **your own** past examination papers using NLP and OpenAI to discover question patterns, identify important topics, and generate probable future exam questions.
=======
An end-to-end system that analyzes a user's own past examination papers to discover recurring question patterns, identify important topics, and generate probable future exam questions — powered by Mistral OCR, Pinecone vector retrieval, cross-encoder reranking, and a multi-agent orchestration layer.
>>>>>>> Stashed changes

The system uses **no sample or fixture data**. Every result is derived from PDFs the user uploads, and subjects are entirely user-defined (e.g. Physics, Law, Nursing, Finance) rather than drawn from a fixed list.

---

<<<<<<< Updated upstream
- **Past Exam Paper Upload** — Extract questions from PDF exam papers (any subject)
- **Subject PDF Upload** — Add syllabus, notes, or textbook PDFs as OpenAI context
- **Dynamic Topic Discovery** — KMeans clustering on your exam content (no predefined topics)
- **OpenAI Question Generation** — GPT-4o generates new questions from your patterns
- **Multi-Subject Support** — Upload papers for multiple subjects and filter analysis
- **Interactive Dashboard** — Topic charts, similarity search, analytics, CSV/PDF export

## Tech Stack

- Python 3.12+, Streamlit, OpenAI API
- Sentence Transformers, Scikit-learn, NLTK
- pdfplumber, Plotly, Pandas
=======
## Table of Contents

1. [Overview](#overview)
2. [Key Features](#key-features)
3. [System Architecture](#system-architecture)
4. [Tech Stack](#tech-stack)
5. [Project Structure](#project-structure)
6. [Installation & Setup](#installation--setup)
7. [Running the Application](#running-the-application)
8. [User Guide](#user-guide)
9. [Retrieval Evaluation Metrics](#retrieval-evaluation-metrics)
10. [Known Limitations](#known-limitations)
11. [License](#license)

---

## Overview

Students and educators often want to know *what is likely to be asked next* based on how a subject has been examined historically. This project automates that analysis:

1. Past exam papers are OCR'd and segmented into individual questions.
2. Questions (and optional syllabus/lecture material) are embedded and indexed in a vector database.
3. Topics are discovered automatically via clustering — no topic list is hand-defined.
4. When a user asks for predictions on a topic, the system retrieves the most relevant historical evidence, reranks it for relevance, and prompts an LLM to generate new, plausible exam questions grounded in that evidence.
5. A dedicated evaluation module measures how good the retrieval step actually is, using standard information-retrieval metrics.

## Key Features

| Feature | Description |
|---|---|
| **Past Exam Paper Upload** | Extracts individual questions from PDF exam papers using Mistral OCR |
| **Subject PDF Upload** | Adds syllabus, notes, or textbook PDFs as retrieval context |
| **Dynamic Topic Discovery** | K-Means clustering over exam content — topics emerge from the data, not a predefined taxonomy |
| **Retrieval-Augmented Prediction** | Pinecone stores question/material embeddings; a cross-encoder reranks retrieved candidates before generation |
| **Multi-Agent Workflow** | Ingestion, retrieval, generation, and evaluation are separated into distinct agents coordinated by a central orchestrator |
| **Mistral Question Generation** | Mistral chat completions generate new questions grounded in retrieved patterns and subject material |
| **Multi-Subject Support** | Multiple subjects can be uploaded and analyzed independently, with sidebar filtering |
| **Interactive Dashboard** | Topic visualizations, similarity search, retrieval evaluation, analytics, and CSV/PDF export, built in Streamlit |

## System Architecture

### Data Flow

```
PDF upload (Streamlit)
        │
        ▼
Mistral OCR  →  page-level Markdown/text
        │
        ├── Past-paper PDFs  →  segmented question rows
        └── Lecture/syllabus PDFs → reference text chunks
        │
        ▼
Sentence-Transformer embeddings
        │
        ▼
Pinecone vector index (namespaces: "past-papers", "lecture-pdfs")
        │
        ▼
Top-K retrieval  →  cross-encoder reranking
        │
        ▼
Mistral chat completion  →  generated questions
        │
        ▼
Retrieval evaluation (Precision@k, Recall@k, MRR, nDCG@k)
```

### Agent Responsibilities

The codebase organizes this pipeline into cooperating agent classes (`src/agents/exam_agents.py`):

| Agent | Responsibility |
|---|---|
| `PastPaperAgent` | Ingests past exam PDFs and converts them into structured question rows |
| `LecturePdfAgent` | Ingests syllabus/notes PDFs and converts them into reference chunks |
| `ExamAgentSystem` | Owns the shared vector store, reranker, and generator; indexes both corpora into Pinecone |
| `PredictionAgent` | Retrieves relevant context, reranks it, and prepares generation input for Mistral |
| `EvaluationAgent` | Reuses the retrieval path to compute ranking-quality metrics |

> **Note on orchestration:** the workflow is structured as a graph of single-responsibility agents in the "LangGraph style," but the current implementation runs this control flow directly in Python — `langgraph` is not a runtime dependency in `requirements.txt`. If it were installed, the code includes a routing path that would delegate to it; without it, the app falls back to the equivalent direct function calls with identical results.

## Tech Stack

- **Language / Runtime:** Python 3.12+
- **Application layer:** Streamlit
- **OCR:** Mistral OCR API
- **Embeddings:** Sentence Transformers
- **Vector store:** Pinecone
- **Reranking:** Cross-encoder model
- **Generation:** Mistral chat completions
- **Clustering:** Scikit-learn (K-Means)
- **NLP preprocessing:** NLTK
- **Visualization:** Plotly
- **Data handling:** Pandas, NumPy
>>>>>>> Stashed changes

## Project Structure

```
exam-pattern-analysis/
├── app/
│   └── streamlit_app.py        # Main dashboard entry point
├── src/
│   ├── agents/                 # Multi-agent orchestration (exam_agents.py)
│   ├── preprocessing/          # PDF extraction and text cleaning
│   ├── ocr/                    # Mistral OCR wrapper
│   ├── embeddings/             # Sentence-embedding generation
│   ├── classification/         # Topic clustering / classification
│   ├── retrieval/               # Pinecone vector store + reranker
│   ├── evaluation/              # Retrieval metrics + evaluator
│   ├── generation/              # Mistral-based question generation
│   ├── pipeline.py              # Shared data loading / subject utilities
│   └── utils.py                 # Logging and path configuration
├── scripts/                    # Utility scripts (OCR smoke test, project validation, sample data)
├── data/
│   ├── raw/                    # User-uploaded source PDFs
│   └── processed/              # questions.csv, subject_materials.csv (generated, git-ignored)
├── reports/                    # Project report and generated summaries
├── requirements.txt
└── README.md
```

## Installation & Setup

**Prerequisites:** Python 3.12+, a Mistral API key, and a Pinecone API key/index.

```powershell
Set-Location C:\Users\User\exam-pattern-analysis
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4')"
```

<<<<<<< Updated upstream
Edit `.env` and set your API key:
=======
Create a `.env` file in the project root with the following variables:
>>>>>>> Stashed changes

```env
GEMINI_API_KEY=AQ.your-real-key-here
```

| Variable | Required | Purpose |
|---|---|---|
| `MISTRAL_API_KEY` | Yes | OCR and question generation |
| `PINECONE_API_KEY` | Yes | Vector storage and retrieval |
| `PINECONE_INDEX_NAME` | Yes | Target Pinecone index |
| `MISTRAL_CHAT_MODEL` | Optional | Overrides the default chat model |

## Running the Application

```powershell
streamlit run app\streamlit_app.py
```

<<<<<<< Updated upstream
## How to Use

### 1. Upload Past Exam Papers
- Go to **Upload & Process → Past Exam Papers**
- Enter any **subject name** (not limited to a fixed list)
- Set the **exam year**
- Upload one or more PDF exam papers
- Click **Process Exam Papers**

### 2. Upload Subject Reference PDFs (optional but recommended)
- Go to **Upload & Process → Subject PDFs**
- Enter the matching **subject name**
- Upload syllabus, notes, or textbook PDFs
- These are sent to OpenAI as context when generating questions

### 3. Analyze & Generate
- **Topic Analysis** — Discovered topics from your papers (filter by subject in sidebar)
- **Question Predictions** — Select subject + discovered topic → OpenAI generates new questions
- **Similarity Search** — Search your uploaded question bank
- **Analytics Dashboard** — Stats across all uploaded subjects

##  API Key

Required for **Question Predictions**. Provide via:
- `API_KEY` in `.env`

## PDF Tips

- Use **text-based PDFs** (not scanned images)
- Exam papers should have **numbered questions** (`1.`, `Q1.`, etc.)
- Image-based PDFs show a friendly error message

## Project Structure
=======
To sanity-check the environment before a full run:
>>>>>>> Stashed changes

```powershell
python scripts\validate_project.py
python scripts\check_mistral_key.py
```
<<<<<<< Updated upstream
exam-pattern-analysis/
├── data/raw/              # Uploaded PDFs saved here
├── data/processed/        # questions.csv, subject_materials.csv
├── app/streamlit_app.py   # Main dashboard
├── src/                   # NLP, clustering, OpenAI generation
└── scripts/               # Utility scripts
```

## Screenshots


## Team Members


## License

MIT License
=======

## User Guide

The dashboard is organized into six pages, navigable from the sidebar:

### 1. Upload & Process
- **Past Exam Papers** — enter a subject name and exam year, then upload one or more PDF exam papers for OCR and question extraction.
- **Subject PDFs** — enter a matching subject name and upload syllabus, notes, or textbook PDFs as retrieval context.
- **Uploaded Data** — review what has already been ingested.

### 2. Topic Analysis
Displays topics discovered by clustering across uploaded papers, filterable by subject.

### 3. Question Predictions
Select a subject and a discovered topic; the system retrieves and reranks relevant historical evidence, then asks Mistral to generate new candidate questions with a chosen difficulty and generation strategy.

### 4. Similarity Search
Pinecone-backed semantic search across the indexed question bank and lecture material, plus cross-paper similar-question lookup.

### 5. Retrieval Evaluation
Runs the evaluation suite (Precision@k, Recall@k, MRR, nDCG@k) against the currently indexed corpus and lets the user adjust `k`.

### 6. Analytics Dashboard
Aggregate statistics across all uploaded subjects.

The sidebar also provides **Refresh Analysis** (recompute topics/embeddings) and **Clear All Uploaded Data** (wipes both the Pinecone namespaces and the local processed CSVs).

## Retrieval Evaluation Metrics

The **Retrieval Evaluation** page measures the quality of the retrieval + reranking stage that feeds the question generator — i.e., how relevant and well-ordered the evidence given to Mistral actually is.

| Metric | Question it answers | Formula |
|---|---|---|
| **Precision@k** | Of the top-k results, how many are relevant? | relevant in top-k ÷ k |
| **Recall@k** | Of all relevant items, how many were found in the top-k? | relevant in top-k ÷ total relevant |
| **MRR** | At what rank does the first relevant result typically appear? | mean of 1 ÷ rank of first relevant hit |
| **nDCG@k** | Are the most relevant results ranked highest, not just present? | DCG@k ÷ Ideal DCG@k |

**Illustrative run (k = 5), evaluated on the project's own uploaded corpus:**

| Metric | Score | Interpretation |
|---|---|---|
| Precision@5 | 0.664 | ~3–4 of 5 retrieved chunks are on-topic |
| Recall@5 | 1.000 | All relevant items in the sampled evaluation window were retrieved |
| MRR | 0.513 | The first relevant result appears at roughly rank 2 on average |
| nDCG@5 | 0.731 | Relevant content is generally ranked near the top |

Exact scores will vary by corpus and are recomputed live from whatever data is currently indexed — the table above reflects one illustrative run, not a fixed benchmark.

## Known Limitations

- **OCR-dependent segmentation:** question extraction relies on numbered patterns (`1.`, `Q1.`, etc.). Exam papers that don't follow a numbered format may segment poorly, and the app surfaces the underlying error rather than a tailored message in that case.
- **No fixed subject taxonomy:** because subjects and topics are fully dynamic, result quality on a new subject depends entirely on how much material has been uploaded for it.
- **`langgraph` is not an enforced dependency:** see the architecture note above — the agent workflow currently executes as direct Python calls rather than through an actual LangGraph graph.
- **Recall@k on a self-contained corpus:** the evaluation harness treats the retrieved candidate pool as the reference set for "total relevant items," rather than an independently labeled ground truth. This is a reasonable proxy for monitoring relative retrieval quality over time, but the resulting Recall@k figures should be read as an internal consistency check rather than an external benchmark.

>>>>>>> Stashed changes
