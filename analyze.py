import requests

from bs4 import BeautifulSoup

import re




# Example URL (replace with your target URL)

url = 'https://www.imot.bg/pcgi/imot.cgi?act=3&slink=aumdiw&f1=1'




# Send a GET request to the URL

response = requests.get(url)




# Parse the HTML content with Beautiful Soup

soup = BeautifulSoup(response.content, 'html.parser')




# Find all <a> elements

content = response.content.decode('windows-1251')




pattern = r'<a[^>]*\s+href=["\']([^"\']+)["\']*\s+class=["\'][^"\']*lnk1[^"\']*["\'][^>]*>.*?</a>'




# Find all matches in the HTML content

matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)




# Print the number of filtered elements found and their contents

print(f"Number of properties found: {len(matches)}")

for elem in matches:

    print(elem)