import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class ExtractedText:
    def __init__(self, url, text, content):
        self.url = url
        self.text = text
        self.content = content

    def __repr__(self):
        return f"URL: {self.url}\nText: {self.text}\nContent: {self.content[:200]}...\n"

class WebCrawler:
    def __init__(self, base_url, summary_api_url, model):
        self.base_url = base_url
        self.summary_api_url = summary_api_url
        self.model = model
        self.results = []

    def extract_content(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            content_div = soup.find('div', class_='description')
            if content_div:
                main_content = content_div.get_text(separator=' ', strip=True)
            else:
                main_content = 'Content not found'
            return main_content
        except requests.RequestException as e:
            print(f"Error fetching content from {url}: {e}")
            return "Content could not be fetched."

    def summarize_and_check(self, text):
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
            return 'комплекс' in summary.lower()
        except requests.RequestException as e:
            print(f"Error summarizing text: {e}")
            return False

    def crawl(self, search_url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            listings = soup.find_all('div', class_='result-row')

            for listing in listings:
                link = listing.find('a', href=True)
                if link:
                    href = link['href']
                    full_url = urljoin(self.base_url, href)
                    text = link.get_text(strip=True)
                    content = self.extract_content(full_url)
                    if self.summarize_and_check(content):
                        self.results.append(ExtractedText(full_url, text, content))
        except requests.RequestException as e:
            print(f"Error fetching {search_url}: {e}")

    def display_results(self):
        for result in self.results:
            print(result)

def main():
    base_url = 'https://www.imot.bg'
    search_url = 'https://www.imot.bg/pcgi/imot.cgi?act=3&slink=7np27o&f1=1&f2=6&f3=2,3'  # Example search results URL
    summary_api_url = 'http://192.168.255.17/v1/chat/completions'  # Replace with your summarization API endpoint
    model = 'meta-llama/Meta-Llama-3-8B-Instruct'  # Replace with your specific AI model

    crawler = WebCrawler(base_url, summary_api_url, model)
    crawler.crawl(search_url)
    crawler.display_results()

if __name__ == "__main__":
    main()
