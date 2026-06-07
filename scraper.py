import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import json
import re
from datetime import datetime


class DocumentSpider(scrapy.Spider):
    name = "document_scraper"

    def __init__(self, urls=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.urls = urls or []
        self.documents = []

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        doc = {
            "url": response.url,
            "title": response.css("title::text").get("").strip(),
            "text": self._clean_text(response.text),
            "html_length": len(response.text),
            "text_length": 0,
            "extracted_at": datetime.now().isoformat(),
            "links": [response.urljoin(l) for l in response.css("a::attr(href)").getall()[:50]],
            "emails": self._extract_emails(response.text),
        }
        doc["text_length"] = len(doc["text"])
        self.documents.append(doc)
        yield doc

    def _clean_text(self, html):
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text)
        return text.strip()[:10000]

    def _extract_emails(self, text):
        pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        return list(set(re.findall(pattern, text)))
