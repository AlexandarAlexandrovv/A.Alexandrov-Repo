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
        return f"URL: {self.url}\nText: {self.text}\nContent: {self.content}\n"

class WebCrawler:
    def __init__(self, base_url, urls, tag, attributes):
        self.base_url = base_url
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
                        # Convert relative URL to absolute URL
                        full_url = urljoin(self.base_url, href)
                        # Extract content from the linked URL
                        content = self.extract_content(full_url)
                        extracted_data.append((full_url, text, content))

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

            # Remove the <div class="article_related article_related_right"> tag if it exists
            related_div = soup.find('div', {'class': 'article_related article_related_right'})
            if related_div:
                related_div.decompose()

            # Extract the text within the <div id="art_start"> tag
            art_start_div = soup.find('div', {'id': 'art_start'})
            if art_start_div:
                paragraphs = art_start_div.find_all('p')
                if paragraphs:
                    # Exclude the last paragraph
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
    # Base URL to use for converting relative URLs to absolute
    base_url = 'https://www.dnes.bg/'

    # List of URLs to crawl
    urls = [
        'https://www.dnes.bg/?cat=1'
        # Add more URLs as needed
    ]

    # HTML tag and attributes to extract text from
    tag = 'div'
    attributes = {'class': ['aside-tabs', 'active']}

    crawler = WebCrawler(base_url, urls, tag, attributes)
    crawler.crawl()
    crawler.display_results()

if __name__ == "__main__":
    main()
