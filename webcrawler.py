import requests
from bs4 import BeautifulSoup

# URL to crawl
url = 'https://www.dnes.bg/?cat=1'

while True:
    # Send a GET request to the URL
    response = requests.get(url)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all div elements with class "aside-tabs active"
    matches = soup.find_all('div', {'class': ['aside-tabs', 'active']})

    for match in matches:
        print(match.get_text().strip())

    # Follow links to next page (if available)
    next_url = soup.find('a', {'class': 'next-page'})
    if next_url:
        url = next_url['href']
    else:
        break