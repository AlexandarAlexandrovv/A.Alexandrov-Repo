
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class EstateInfo:
    def __init__(self, url, content):
        self.url = url
        self.content = content

    def __repr__(self):
        return f"URL: {self.url}\nContent: {self.content[:200]}...\n"

class ImotBGScraper:
    def __init__(self, base_url, word_search_api_url, model):
        self.base_url = base_url
        self.word_search_api_url = word_search_api_url
        self.model = model
        self.results = []

    def extract_info(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.select('a.lnk1[href]')

            for link in links:
                href = link['href']
                full_url = urljoin(self.base_url, href)
                content = self.extract_content(full_url)
                if content:
                    if self.check_with_ai(content):
                        self.results.append(EstateInfo(full_url, content))
                    else:
                        print(f"Keyword not found in URL: {full_url}")
                else:
                    print(f"Content not found for URL: {full_url}")
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")

    def extract_content(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            description_div = soup.find('div', id='description_div')
            if description_div:
                main_content = description_div.get_text(separator=' ', strip=True)
            else:
                main_content = 'Content not found'
            return main_content
        except requests.RequestException as e:
            print(f"Error fetching content from {url}: {e}")
            return "Content could not be fetched."
        except Exception as e:
            print(f"Other error: {e}")
            return "Content could not be fetched."

    def check_with_ai(self, text):
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
            response = requests.post(self.word_search_api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result_text = response.json().get("choices", [{}])[0].get("message", {}).get("content", "Result not found")
            # Check for variations of the word "Комплекс"
            if 'комплекс' in result_text.lower() or 'комплексът' in result_text.lower() or 'Комплекс' in result_text:
                return True
            return False
        except requests.RequestException as e:
            print(f"Error checking text with AI: {e}")
            return False
        except Exception as e:
            print(f"Other error: {e}")
            return False

    def crawl(self, search_url):
        self.extract_info(search_url)
        return [result.url for result in self.results]

def main():
    base_url = 'https://www.imot.bg'
    word_search_api_url = 'http://localhost:8888/v1/chat/completions'  # Replace with your word search API endpoint
    model = 'meta-llama/BgGPT-7B-Instruct-v0.2.Q4_K_S.gguf'  # Replace with your specific AI model

    search_url = 'https://www.imot.bg/pcgi/imot.cgi?act=3&slink=aum7dh&f1=1'  # URL for Blagoevgrad - Bansko

    scraper = ImotBGScraper(base_url, word_search_api_url, model)
    results = scraper.crawl(search_url)
    if results:
        print("Keyword was found in the following URLs:")
        for url in results:
            print(url)
    else:
        print("No URLs contained the keyword.")

if __name__ == "__main__":
    main()
