# AI-Powered Document Scraper

End-to-end system that scrapes web documents, enriches them with AI (OpenAI GPT), and exposes everything via a REST API — all containerized with Docker.

## What This Project Shows Employers

| Skill | Proof |
|-------|-------|
| **Scrapy** | Production-grade spider with pipelines |
| **AI/LLM integration** | OpenAI API for classification, summarization, entity extraction |
| **REST API** | FastAPI endpoints for scraping and enrichment |
| **Docker** | Containerized with Dockerfile + docker-compose |
| **AWS-ready** | Designed to deploy on ECS/Fargate with S3, CloudWatch |
| **CI/CD ready** | Git-based with clear dependency management |

## Architecture

```
User → FastAPI → Scrapy Spider → Raw Documents
                         ↓
                    AIProcessor (OpenAI GPT-4o)
                         ↓
              Enriched Documents (classified, summarized, entities)
                         ↓
                    JSON Output / API Response
```

## Features

- **Web Scraping**: Scrapy-based spider with link extraction, email detection, text cleaning
- **AI Enrichment**: 
  - Document classification (job posting, product, article, etc.)
  - Entity extraction (names, emails, prices, dates, locations, topics)
  - Intelligent summarization
- **REST API**: FastAPI with `/scrape`, `/enrich`, `/scrape-and-enrich` endpoints
- **Containerized**: Docker + docker-compose for easy deployment
- **Extensible**: Add more spiders, AI models, or output formats

## Requirements

- Python 3.10+
- Docker (optional, for containerized deployment)
- Google Gemini API key - **free** from https://aistudio.google.com/apikey (set as `GEMINI_API_KEY`)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### 1. Set your OpenAI key

```bash
set OPENAI_API_KEY=sk-your-key-here
```

### 2. Run the API

```bash
python api.py
```

### 3. Call the API

```bash
# Scrape and enrich in one request
curl -X POST http://localhost:8000/scrape-and-enrich \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://example.com",
      "https://example.org"
    ],
    "max_pages": 5,
    "use_ai": true
  }'
```

### Or use Docker

```bash
docker-compose up --build
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/scrape` | Scrape URLs only |
| POST | `/enrich` | Enrich existing documents with AI |
| POST | `/scrape-and-enrich` | Scrape + enrich in one call |

## Project Structure

```
ai-document-scraper/
  scraper.py          # Scrapy spider (web scraping)
  processor.py        # AIProcessor (OpenAI enrichment)
  api.py              # FastAPI server
  Dockerfile          # Container build
  docker-compose.yml  # Orchestration
  requirements.txt    # Dependencies
  output/             # Scraped & enriched JSON results
```

## Deployment to AWS

1. Build Docker image:
   ```bash
   docker build -t ai-doc-scraper .
   ```

2. Push to ECR:
   ```bash
   aws ecr create-repository --repository-name ai-doc-scraper
   docker tag ai-doc-scraper:latest <account>.dkr.ecr.<region>.amazonaws.com/ai-doc-scraper:latest
   docker push <account>.dkr.ecr.<region>.amazonaws.com/ai-doc-scraper:latest
   ```

3. Deploy to ECS with Fargate (use `OPENAI_API_KEY` in Secrets Manager)
