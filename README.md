# ReqLens RAG

ReqLens RAG is a Retrieval-Augmented Generation system that analyzes messy software requirements, client notes, and real GitHub issues, then converts them into developer-ready requirement cards.

The goal of this project is to help software teams turn unclear feature requests into structured planning outputs such as user stories, acceptance criteria, database entities, API endpoints, risks, missing questions, and implementation readiness.

---

## Problem

Software teams often receive requirements from different sources such as client messages, meeting notes, business rules, change requests, GitHub issues, feature requests, and product discussions.

These requirements are often messy, incomplete, unclear, or not ready for developers to implement directly.

ReqLens RAG solves this by retrieving the most relevant requirement context and using Gemini to generate structured software requirement analysis.

---
## What This Project Does

ReqLens RAG helps analyze unclear software requirements from client notes and GitHub issues.

It retrieves the most relevant context and uses Gemini to generate structured outputs such as user stories, acceptance criteria, technical impact, risks, and missing questions.

---

## APIs Used

### Google Gemini API

Gemini is used for:

* Creating embeddings for requirement documents and GitHub issues
* Creating embeddings for user questions
* Generating the final structured requirement analysis

### GitHub Issues API

The GitHub Issues API is used to fetch real public GitHub issues from selected repositories.

Fetched GitHub issues are saved as text files inside:

```text
data/github_issues/
```

These issues are then used as real-world software requirement data for the RAG system.

---

## Features

* Analyze messy software requirements
* Analyze real GitHub issues as requirement sources
* Convert GitHub issues into developer-ready requirement cards
* Generate user stories and acceptance criteria
* Suggest database entities and API endpoints
* Identify risks and ambiguities
* Generate missing questions
* Show best source match percentage
* Show retrieval confidence
* Use Gemini embeddings for semantic retrieval
* Use Gemini Flash for final requirement analysis
* Fetch GitHub issues using GitHub Issues API
* Store embeddings locally in a JSON vector store

---

## Tech Stack

* Python
* Google Gemini API
* Gemini Embeddings
* GitHub Issues API
* NumPy
* python-dotenv
* requests
* Local JSON vector store

---

## Data Sources

ReqLens RAG currently supports two types of data.

### 1. Sample Requirement Documents

Example:

```text
data/clinic_system/
├── client_message.txt
├── meeting_notes.txt
├── business_rules.txt
└── change_requests.txt
```

These files simulate real client requirement documents.

### 2. Real GitHub Issues

ReqLens RAG can fetch public GitHub issues using the GitHub Issues API and save them as text files inside:

```text
data/github_issues/
```

These GitHub issues are used as real-world requirement data.

---

## Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/samakhraim/ReqLens-RAG.git
cd ReqLens-RAG
```

### 2. Create a Virtual Environment

```bash
py -3.12 -m venv venv
```

### 3. Activate the Virtual Environment

Windows PowerShell:

```bash
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Create `.env`

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

`GITHUB_TOKEN` is optional, but recommended for higher GitHub API rate limits.

---

## Usage

### 1. Fetch Real GitHub Issues

```bash
python -m app.fetch_github_issues
```

This command uses the GitHub Issues API and saves fetched issues into:

```text
data/github_issues/
```

### 2. Build the Vector Store

```bash
python -m app.ingest
```

This command reads files from `data/`, splits them into chunks, creates Gemini embeddings, and saves chunks and embeddings into:

```text
vector_store/store.json
```

### 3. Ask ReqLens AI

```bash
python -m app.ask
```

Example questions:

```text
Convert the best retrieved GitHub issue into a developer-ready requirement card.
```

```text
Analyze the retrieved GitHub issue and give me the problem statement, user story, acceptance criteria, database impact, API impact, risks, and missing questions.
```

```text
Based on the GitHub issue, is this requirement ready for implementation?
```

```text
Analyze the clinic appointment system and give me the MVP scope, database entities, API endpoints, risks, and missing questions.
```

---

## Full Local Testing Flow

After cloning the project and setting up `.env`, run:

```bash
pip install -r requirements.txt
python -m app.fetch_github_issues
python -m app.ingest
python -m app.ask
```

Then ask:

```text
Convert the best retrieved GitHub issue into a developer-ready requirement card.
```

---

## Retrieval Match Percentage

ReqLens RAG shows a match percentage for retrieved chunks.

This percentage means how similar the retrieved source chunk is to the user question.

It does not mean final answer accuracy.

Example:

```text
Best Source Match: 74.99%
Retrieval Confidence: Medium
```

The final answer quality depends on:

* The quality of the retrieved source
* The clarity of the user question
* The quality of the prompt
* The completeness of the source documents

---

## Author

Built by Sama Khraim as a portfolio project focused on RAG, LLMs, software requirements analysis, and real-world software engineering workflows.
