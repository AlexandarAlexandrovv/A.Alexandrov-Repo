import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class ExtractedText:
    def __init__(self, url, text, content, summary):
        self.url = url
        self.text = text
        self.content = content
        self.summary = summary

    def __repr__(self):
        return f"URL: {self.url}\nText: {self.text}\nContent: {self.content}\nSummary: {self.summary}\n"

class WebCrawler:
    def __init__(self, base_url, urls, tag, attributes, summary_api_url, model):
        self.base_url = base_url
        self.urls = urls
        self.tag = tag
        self.attributes = attributes
        self.summary_api_url = summary_api_url
        self.model = model
        self.results = []

    def extract_text_and_urls(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            tags = soup.find_all(self.tag, self.attributes)

            extracted_data = []
            for tag in tags:
                if tag.find_parent(class_='stats'):
                    continue

                links = tag.find_all('a', href=True)
                for link in links:
                    if link.find_parent(class_='stats'):
                        continue

                    text = link.get_text(strip=True)
                    href = link['href']
                    text = re.sub(r'\b\d{1,2}:\d{2}\b', '', text).strip()
                    if text:
                        full_url = urljoin(self.base_url, href)
                        content = self.extract_content(full_url)
                        summary = self.summarize_text(content)
                        extracted_data.append((full_url, text, content, summary))

            return extracted_data
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return []

    def extract_content(self, url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            related_div = soup.find('div', {'class': 'article_related article_related_right'})
            if related_div:
                related_div.decompose()

            art_start_div = soup.find('div', {'id': 'art_start'})
            if art_start_div:
                paragraphs = art_start_div.find_all('p')
                if paragraphs:
                    paragraphs = paragraphs[:-1]
                    main_content = ' '.join([p.get_text(separator=' ', strip=True) for p in paragraphs])
                else:
                    main_content = art_start_div.get_text(separator=' ', strip=True)
            else:
                main_content = 'Content not found'

            return main_content
        except requests.RequestException as e:
            print(f"Error fetching content from {url}: {e}")
            return "Content could not be fetched."

    def summarize_text(self, text):
        try:
            headers = {
                'Content-Type': 'application/json',
            }
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                "temperature": 0.7
            }
            response = requests.post(self.summary_api_url, headers=headers, json=payload)
            response.raise_for_status()
            summary = response.json().get("choices", [{}])[0].get("message", {}).get("content", "Summary not found")
            return summary
        except requests.RequestException as e:
            print(f"Error summarizing text: {e}")
            return "Summary could not be fetched."

    def crawl(self):
        for url in self.urls:
            data = self.extract_text_and_urls(url)
            for href, text, content, summary in data:
                self.results.append(ExtractedText(href, text, content, summary))

    def display_results(self):
        for result in self.results:
            print(f"URL: {result.url}")
            print(f"  Text: {result.text}")
            print(f"  Content: {result.content}")
            print(f"  Summary: {result.summary}\n")

def main():
    base_url = 'https://www.dnes.bg/'
    urls = [
        'https://www.dnes.bg/?cat=1'
    ]
    tag = 'div'
    attributes = {'class': ['aside-tabs', 'active']}
    summary_api_url = 'http://192.168.255.17/v1/chat/completions'
    model = 'meta-llama/Meta-Llama-3-8B-Instruct'

    crawler = WebCrawler(base_url, urls, tag, attributes, summary_api_url, model)
    crawler.crawl()
    crawler.display_results()

if __name__ == "__main__":
    main()
