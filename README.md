# DeepEval Metrics Implementation with RAG

This repository demonstrates a Retrieval-Augmented Generation (RAG) workflow enhanced with DeepEval-based evaluation metrics. It combines a React-based front end, a Node.js/Express backend, and a Python FastAPI service to evaluate generated answers against retrieved context.

The project is designed to showcase how to:

- build and query a RAG system over structured project data
- index and retrieve documents using hybrid search approaches
- generate embeddings for search and retrieval
- evaluate answer quality using DeepEval metrics such as faithfulness, answer relevancy, contextual precision, and contextual recall

---

## Project Overview

This repo contains two main components:

1. DeepEval Evaluation Service
   - A Python FastAPI service that exposes evaluation endpoints
   - Uses DeepEval and LLM-based scoring for RAG evaluation

2. RAG Implementation
   - A Node.js server for document ingestion, search, and retrieval
   - A React client to interact with the search and evaluation flow

---

## Features

- Hybrid retrieval workflow using BM25 and vector-based search
- Embedding generation and storage support for project data
- Search over Jira stories, test cases, and related content
- React-based UI for querying and exploring results
- DeepEval-powered evaluation for:
  - faithfulness
  - answer relevancy
  - contextual precision
  - contextual recall
  - conversation completeness
  - hallucination, bias, and toxicity checks

---

## Repository Structure

```text
deepeval-implementation/
  deepeval_server.py
  requirements.txt
  src/
  test_metrics_diagnostic.py

rag-implementation/
  client/
  server/
  src/
  scripts/
```

---

## Prerequisites

Before running the project, make sure you have:

- Node.js and npm
- Python 3.9+
- Access to required LLM/API providers such as OpenAI or Groq
- MongoDB Atlas or a compatible MongoDB environment if you are using the vector search flow

---

## Environment Variables

Configure the required service credentials and connection settings securely in your environment before running the application. The exact variables depend on your local setup and the model providers you choose to use.

If you are using the provided services, make sure to set the required environment variables in your shell or deployment platform without including secrets in the repository.

---

## Installation

### 1) Install Python dependencies

```bash
cd deepeval-implementation
pip install -r requirements.txt
```

### 2) Install Node.js dependencies

```bash
cd rag-implementation
npm install
```

The project also installs the React client dependencies automatically through the root package setup.

---

## Running the Application

### Start the DeepEval service

```bash
cd deepeval-implementation
python deepeval_server.py
```

This starts the FastAPI server on port 8000 by default.

### Start the RAG application

In a separate terminal:

```bash
cd rag-implementation
npm run dev
```

This will start the backend and client app for the RAG workflow.

---

## Usage

1. Open the React client in your browser.
2. Upload or load the relevant data sources.
3. Run searches or queries through the interface.
4. Use the evaluation service to score the generated outputs using DeepEval metrics.

---

## Notes

- Some parts of the project depend on external API keys and cloud services.
- The evaluation pipeline is intended for experimentation and demonstration purposes.
- For production use, consider adding authentication, secure secret management, logging, and more robust deployment configuration.

---

## License

This project is intended for educational and demonstration purposes. Please check the repository owner’s licensing terms before reuse or redistribution.

---

## Acknowledgements

This project uses:
- DeepEval
- FastAPI
- Express
- React
- MongoDB
- OpenAI / Groq / Mistral APIs
