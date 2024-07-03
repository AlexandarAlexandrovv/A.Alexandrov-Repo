import requests
from bs4 import BeautifulSoup
import re

def extract_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    text = ''
    for tag in ['p', 'div', 'span']:
        for paragraph in soup.find_all(tag):
            text += paragraph.get_text() + '\n'
    return text.strip()

def search_for_keyphrases(text, keyphrases):
    matches = {}
    for keyphrase in keyphrases:
        if re.search(keyphrase, text, re.IGNORECASE):
            print(f"Found keyphrase: {keyphrase}")
            related_text = ''
            for paragraph in text.split('\n'):
                if keyphrase.lower() in paragraph.lower():
                    related_text += paragraph + '\n'
            matches[keyphrase] = related_text.strip()
    return matches

url = 'http://www.pmgvt.org/'
text = extract_text(url)

keyphrases = ["Ротари клуб"]
matches = search_for_keyphrases(text, keyphrases)

for keyphrase, related_text in matches.items():
    print(f"Keyphrase: {keyphrase}")
    print(related_text)
    print()