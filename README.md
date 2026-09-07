# QA Agent

A Retrieval-Augmented Generation (RAG) platform for QA teams. QA Agent combines application knowledge, specialized QA capabilities, LLM reasoning, and validation checkpoints to produce review-ready test artifacts.

Created by Gopi Rajendran.

Repository: https://github.com/gopi-rajend/QA-Agent

## What It Does

QA Agent provides a portal for:

- Requirement analysis
- Test case generation
- Test data generation
- API and BDD mapping
- Defect analysis
- Test plan creation

The workflow is organized as:

```text
QA request
  -> Agent orchestrator
  -> RAG knowledge retrieval
  -> Specialized QA reasoning
  -> Validation and guardrails
  -> Structured QA output
```

## Architecture

### QA Agent portal

The React client lets a QA engineer select a capability, describe an objective, choose an application area, and review the generated result.

### Agent orchestrator

The Node.js/Express API receives the selected capability and request, creates an agent plan, identifies retrieval sources, applies validation checks, and returns a structured QA response.

The orchestration endpoint is:

```text
POST /api/qa/orchestrate
```

### RAG knowledge layer

The RAG implementation supports application-specific knowledge from:

- User stories
- Historical test cases
- API specifications
- Defect history
- QA standards and templates

MongoDB Atlas stores searchable documents and vector embeddings. Mistral generates embeddings, while Groq supports reranking and summarization.

## Project Structure

```text
QA-Agent/
  client/                  React QA Agent portal
  server/                  Express API and orchestration routes
  src/config/              Search index configuration
  src/data/                Local JSON data sources
  src/scripts/             Embeddings, search, preprocessing, and utilities
  .env.example             Environment variable template
```

## Requirements

- Node.js and npm
- MongoDB Atlas or a compatible MongoDB deployment for live RAG search
- Mistral API access for embeddings
- Groq API access for reranking and summarization

## Configuration

Copy the environment template:

```powershell
cd QA-Agent
Copy-Item .env.example .env
```

Update `QA-Agent/.env` with the credentials and MongoDB details for the person or team running the project:

```env
MONGODB_URI="mongodb+srv://<username>:<password>@<cluster>"
DB_NAME="db_stories_tests"
COLLECTION_NAME="test_cases"
VECTOR_INDEX_NAME="vector_index_test_cases"
BM25_INDEX_NAME="bm25_search"
USER_STORIES_COLLECTION_NAME="user_stories"
USER_STORIES_VECTOR_INDEX_NAME="vector_index_user_story"

MISTRAL_API_KEY="<their-mistral-api-key>"
MISTRAL_EMBEDDING_MODEL="mistral-embed"

GROQ_API_KEY="<their-groq-api-key>"
GROQ_RERANK_MODEL="openai/gpt-oss-120b"
GROQ_SUMMARIZATION_MODEL="openai/gpt-oss-120b"
```

Never commit `.env` files or share API keys in the repository. Each user should create and manage their own credentials.

### MongoDB requirements

The MongoDB account must have:

- Access to the configured database and collections
- Network access from the machine running the project
- The configured vector search index
- The configured BM25 search index
- Read/write permissions when creating embeddings

## Install

Install the Node.js application dependencies:

```powershell
cd QA-Agent
npm install
```

## Run the Application

### QA Agent portal and API

From `QA-Agent`:

```powershell
npm run dev
```

Default endpoints:

- React portal: http://localhost:3000
- Node.js API: http://localhost:3001
- API health check: http://localhost:3001/api/health

The dev command starts the React client and Express server together.

Ports can be changed if the defaults are already in use. Update any client or service URL configuration when using custom ports.

## Usage

1. Open http://localhost:3000.
2. Select a QA capability from the navigation.
3. Enter a QA objective and application area.
4. Select **Run QA workflow**.
5. Review the agent plan, retrieved context, validation checks, and generated output.
6. Export or adapt the output for the team QA repository or test management tool.

The portal includes a preview fallback when live API services are unavailable. Live retrieval and provider-backed processing require MongoDB and the appropriate API keys.

## Useful Commands

```powershell
# Start client and API
cd QA-Agent
npm run dev

# Build the React client
npm run build

# Check server syntax
node server/index.js

```

## Security and Handoff Notes

For another person to run the project, share the repository and the required configuration names, not your private credentials. They need their own MongoDB connection details and provider API keys for live usage. Preview-only portal usage does not require live MongoDB or LLM credentials.

For production use, add authentication, secret management, request logging, rate limiting, protected CORS settings, and persistent job storage before exposing the services publicly.

## License

This project is intended for educational and demonstration purposes. Confirm the applicable licensing terms before redistributing or using it commercially.
