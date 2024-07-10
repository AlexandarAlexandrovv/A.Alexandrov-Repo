import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class ImotBGScraper:
    def __init__(self, base_url, word_search_api_url, model):
        self.base_url = base_url
        self.word_search_api_url = word_search_api_url
        self.model = model

    def extract_info(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.select('a.photoLink[href]')

            for link in links:
                href = link['href']
                full_url = urljoin(self.base_url, href)
                if self.check_for_keyword(full_url):
                    print(f"The keyword was found in URL: {full_url}")
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")

    def check_for_keyword(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            description_div = soup.find('div', id='description_div')
            if description_div:
                content = description_div.get_text(separator=' ', strip=True)
                return self.check_with_ai(content)
            else:
                print(f"Content not found for URL: {url}")
                return False
        except requests.RequestException as e:
            print(f"Error fetching content from {url}: {e}")
            return False
        except Exception as e:
            print(f"Other error: {e}")
            return False

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

def main():
    base_url = 'https://www.imot.bg'
    word_search_api_url = 'http://localhost:8888/v1/chat/completions'  # Replace with your word search API endpoint
    model = 'meta-llama/Meta-Llama-3-8B-Instruct'  # Replace with your specific AI model

    search_url = 'https://www.imot.bg/pcgi/imot.cgi?act=3&slink=aumdiw&f1=1'  # URL for Blagoevgrad - Bansko

    scraper = ImotBGScraper(base_url, word_search_api_url, model)
    scraper.crawl(search_url)

if __name__ == "__main__":
    main()
