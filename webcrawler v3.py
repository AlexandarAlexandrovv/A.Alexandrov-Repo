import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import json
import time

class EstateInfo:
    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return f"URL: {self.url}"

class ImotBGScraper:
    def __init__(self, base_url, word_search_api_url, model):
        self.base_url = base_url
        self.word_search_api_url = word_search_api_url
        self.model = model
        self.results = []

    def extract_info(self, search_url, limit=10):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()
            content = response.content.decode('windows-1251')
            
            pattern = r'<a[^>]*\s+href=["\']([^"\']+)["\']*\s+class=["\'][^"\']*lnk1[^"\']*["\'][^>]*>.*?</a>'
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)[:limit]
            
            for href in matches:
                full_url = urljoin(self.base_url, href)
                content = self.extract_content(full_url)
                
                if content:
                    if self.check_with_ai(content):
                        print(f"Keyword found in URL: {full_url}")
                        self.results.append(EstateInfo(full_url))
                    else:
                        print(f"Keyword not found in URL: {full_url}")
                else:
                    print(f"Content not found for URL: {full_url}")
        
        except requests.RequestException as e:
            print(f"Error fetching {search_url}: {e}")
        except Exception as e:
            print(f"Other error: {e}")

    def extract_content(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            description_div = soup.find('div', id='description_div')
            if description_div:
                main_content = description_div.get_text(separator=' ', strip=True)
            else:
                main_content = None
            return main_content
        except requests.RequestException as e:
            print(f"Error fetching content from {url}: {e}")
            return None
        except Exception as e:
            print(f"Other error: {e}")
            return None

    def check_with_ai(self, text):
        retries = 3
        timeout = 120  # Increase timeout to 2 minutes
        for attempt in range(retries):
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
                response = requests.post(self.word_search_api_url, headers=headers, json=payload, timeout=timeout)
                response.raise_for_status()
                
                result_json = response.json()
                result_text = result_json.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if not result_text:
                    print(f"Empty response from AI service on attempt {attempt + 1}")
                    continue

                # Check for variations of the word "Комплекс"
                if 'комплекс' in result_text.lower() or 'комплексът' in result_text.lower() or 'Комплекс' in result_text:
                    return True
                return False
            except requests.RequestException as e:
                print(f"Error checking text with AI (attempt {attempt + 1} of {retries}): {e}")
                time.sleep(5)  # Wait before retrying
            except Exception as e:
                print(f"Other error: {e}")
                return False
        return False

    def crawl(self, search_url, limit=10):
        self.extract_info(search_url, limit=limit)
        return self.results

def main():
    base_url = 'https://www.imot.bg'
    word_search_api_url = 'http://localhost:8888/v1/chat/completions'  # Replace with your word search API endpoint
    model = 'lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf'  # Replace with your specific AI model

    search_url = 'https://www.imot.bg/pcgi/imot.cgi?act=3&slink=aum7dh&f1=1'  # URL for Blagoevgrad - Bansko

    scraper = ImotBGScraper(base_url, word_search_api_url, model)
    results = scraper.crawl(search_url, limit=10)  # Limiting to process only 10 URLs temporarily
    
    if results:
        print("Keyword was found in the following URLs:")
        for result in results:
            print(result.url)
    else:
        print("No URLs contained the keyword.")

if __name__ == "__main__":
    main()
