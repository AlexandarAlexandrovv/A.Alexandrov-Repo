import requests
from bs4 import BeautifulSoup
import re
url = 'https://www.днес.bg/?cat=1'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

pattern = r'<div class="aside-tabs active">([.\n\r\s\S]*)</div>'
matches = soup.find_all(re.compile(pattern))

for match in matches:
    print(match.text.strip())