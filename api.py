from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from scrapy.crawler import CrawlerProcess
from simple_scraper import SimpleSpider
from deepseek_processor import AIProcessor  # أضفنا هذا للـ enrich

app = FastAPI(title="Simple Scraper API")

class ScrapeRequest(BaseModel):
    urls: List[str]
    max_pages: Optional[int] = 1

class ScrapeResponse(BaseModel):
    status: str
    documents_count: int
    documents: List[dict]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/scrape", response_model=ScrapeResponse)
def scrape_endpoint(req: ScrapeRequest):
    results = []
    
    class SavePipeline:
        def process_item(self, item, spider):
            results.append(dict(item))
            return item
    
    settings = {
        "LOG_ENABLED": False,
        "CLOSESPIDER_PAGECOUNT": req.max_pages,
        "ITEM_PIPELINES": {SavePipeline: 300},
        "DOWNLOAD_DELAY": 1,
    }
    
    process = CrawlerProcess(settings)
    process.crawl(SimpleSpider, urls=req.urls)
    process.start()
    
    return ScrapeResponse(
        status="success",
        documents_count=len(results),
        documents=results,
    )

# ========== Endpoint التحليل بالذكاء الاصطناعي ==========
@app.post("/scrape-and-enrich")
def scrape_and_enrich(req: ScrapeRequest):
    # 1. تشغيل الـ Scraper
    scrape_results = []
    
    class TempPipeline:
        def process_item(self, item, spider):
            scrape_results.append(dict(item))
            return item
    
    settings = {
        "LOG_ENABLED": False,
        "CLOSESPIDER_PAGECOUNT": req.max_pages,
        "ITEM_PIPELINES": {TempPipeline: 300},
        "DOWNLOAD_DELAY": 1,
    }
    
    process = CrawlerProcess(settings)
    process.crawl(SimpleSpider, urls=req.urls)
    process.start()
    
    if not scrape_results:
        return {"status": "error", "message": "No documents scraped"}
    
    # 2. تحويل نتائج الـ Scraper إلى الشكل الذي يتوقعه AIProcessor
    documents = []
    for item in scrape_results:
        text = " ".join(item.get("text", [])) if isinstance(item.get("text"), list) else item.get("text", "")
        documents.append({
            "url": item.get("url", ""),
            "text": text[:3000]  # تقطيع النص الطويل
        })
    
    # 3. تشغيل الـ AIProcessor
    processor = AIProcessor()
    enriched_results = processor.process_batch(documents, output_path="output/scraped_enriched.json")
    
    return {
        "status": "success",
        "documents_count": len(enriched_results),
        "documents": enriched_results,
    }
# ======================================================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)