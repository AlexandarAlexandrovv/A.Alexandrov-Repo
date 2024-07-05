import re
import requests
from bs4 import BeautifulSoup

class ExtractedText:
    def __init__(self, url, text, content):
        self.url = url
        self.text = text
        self.content = content

    def __repr__(self):
        return f"URL: {self.url}\nText: {self.text}\nContent: {self.content}\n"

class WebCrawler:
    def __init__(self, urls, tag, attributes):
        self.urls = urls
        self.tag = tag
        self.attributes = attributes
        self.results = []

    def extract_text_and_urls(self, url):
        try:
            # Send a GET request to the URL
            response = requests.get(url)
            response.raise_for_status()  # Check for request errors

            # Parse the HTML content of the page
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all specified tags with the given attributes
            tags = soup.find_all(self.tag, self.attributes)

            extracted_data = []
            for tag in tags:
                # Ensure no ancestor has the class 'stats'
                if tag.find_parent(class_='stats'):
                    continue

                # Find all links within the tag
                links = tag.find_all('a', href=True)
                for link in links:
                    # Ensure no ancestor has the class 'stats'
                    if link.find_parent(class_='stats'):
                        continue

                    text = link.get_text(strip=True)
                    href = link['href']
                    # Remove time indicators (like 12:03)
                    text = re.sub(r'\b\d{1,2}:\d{2}\b', '', text).strip()
                    if text:  # Only add non-empty text
                        # Extract content from the linked URL
                        content = self.extract_content(href)
                        extracted_data.append((href, text, content))

            return extracted_data
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return []

    def extract_content(self, url):
        try:
            # Send a GET request to the URL
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Check for request errors

            # Parse the HTML content of the page
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract main content (example: all text within <body> tag)
            main_content = soup.body.get_text(separator=' ', strip=True) if soup.body else 'Content not found'
            return main_content
        except requests.RequestException as e:
            print(f"Error fetching content from {url}: {e}")
            return "Content could not be fetched."

    def crawl(self):
        for url in self.urls:
            data = self.extract_text_and_urls(url)
            for href, text, content in data:
                self.results.append(ExtractedText(href, text, content))

    def display_results(self):
        for result in self.results:
            print(f"URL: {result.url}")
            print(f"  Text: {result.text}")
            print(f"  Content: {result.content}\n")

def main():
    # List of URLs to crawl
    urls = [
        'https://www.dnes.bg/?cat=1'
    ]

    # HTML tag and attributes to extract text from
    tag = 'div'
    attributes = {'class': ['aside-tabs', 'active']}

    crawler = WebCrawler(urls, tag, attributes)
    crawler.crawl()
    crawler.display_results()

if __name__ == "__main__":
    main()
