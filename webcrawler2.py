import requests
from bs4 import BeautifulSoup
import re

def extract_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return ""
    
    soup = BeautifulSoup(response.content, 'html.parser')
    text = ''
    
    # Extract text from specified tags and search within them directly
    for tag in ['p', 'div', 'span']:
        for element in soup.find_all(tag):
            paragraph_text = ' '.join(element.stripped_strings)
            text += paragraph_text + '\n'
    
    # Clean up text by removing extra spaces and newlines
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def search_for_keyphrases(text, keyphrases):
    matches = {}
    
    for keyphrase in keyphrases:
        regex = re.compile(r'\b{}\b'.format(re.escape(keyphrase)), re.IGNORECASE)
        found = False
        
        # Search within each paragraph directly
        for paragraph in text.split('\n'):
            if regex.search(paragraph):
                matches[keyphrase] = paragraph.strip()
                found = True
                break
        
        if found:
            print(f"Found keyphrase: {keyphrase}")
            print(matches[keyphrase])
            print()
    
    return matches

# Example usage
url = 'http://www.pmgvt.org/'
text = extract_text(url)

if text:
    keyphrases = ["Ротари клуб"]
    matches = search_for_keyphrases(text, keyphrases)
