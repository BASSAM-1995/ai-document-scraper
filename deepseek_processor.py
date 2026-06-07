import json
import os
from groq import Groq  # تأكد من تثبيت المكتبة: pip install groq

class AIProcessor:
    def __init__(self, api_key=None):
        # 1. جلب المفتاح من متغير البيئة أو من الكود مباشرةً
        key = api_key or os.getenv("GROQ_API_KEY")
        if not key:
            raise ValueError("GROQ_API_KEY not found. Please set it as an environment variable.")

        # 2. تهيئة عميل Groq (Client)
        self.client = Groq(api_key=key)

    def _generate(self, prompt, text):
        """وظيفة داخلية مسؤولة عن إرسال الطلب إلى Groq واستلام الرد"""
        try:
            # استخدام نموذج Llama 4 Scout من Groq - سريع جدًا ومجاني
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": prompt,
                    },
                    {
                        "role": "user",
                        "content": text[:3000],  # نرسل أول 3000 حرف فقط
                    }
                ],
                model="llama-3.3-70b-versatile",  # النموذج الموصى به والأسرع [citation:9]
                temperature=0.3,  # تحكم في إبداع النموذج
                max_tokens=500,
            )
            # استخراج نص الرد من الكائن الذي أعاده Groq
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"An error occurred: {e}")
            return ""

    # بقية الدوال (classify_document, extract_entities, ...) لا تحتاج إلى تغيير
    # لأنها تعتمد على `self._generate` التي قمنا بتعديلها أعلاه.
    def classify_document(self, text):
        prompt = "Classify this text into ONE category: Job Posting, Product Listing, News Article, Blog Post, Technical Documentation, Other. Return only the category name."
        return self._generate(prompt, text)

    def extract_entities(self, text):
        prompt = """Extract entities as JSON only (no other text). Format:
{"names": [], "emails": [], "phone_numbers": [], "prices": [], "dates": [], "locations": [], "key_topics": []}"""
        result = self._generate(prompt, text)
        cleaned = result.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(cleaned)
        except:
            return {"names": [], "emails": [], "phone_numbers": [], "prices": [], "dates": [], "locations": [], "key_topics": []}

    def summarize_document(self, text, max_words=100):
        prompt = f"Summarize this in {max_words} words or less. Focus on key points."
        return self._generate(prompt, text)

    def enrich_document(self, doc):
        text = doc.get("text", "")
        if len(text) < 50:
            doc["category"] = "Too Short"
            doc["summary"] = ""
            doc["entities"] = {}
            return doc
        doc["category"] = self.classify_document(text)
        doc["summary"] = self.summarize_document(text)
        doc["entities"] = self.extract_entities(text)
        return doc

    def process_batch(self, documents, output_path="enriched_output.json"):
        results = []
        for i, doc in enumerate(documents):
            print(f"Processing {i+1}/{len(documents)}: {doc.get('url', 'unknown')[:60]}")
            enriched = self.enrich_document(doc)
            results.append(enriched)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(results)} enriched documents to {output_path}")
        return results