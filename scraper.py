"""
Webscraper to scrape updated list of all predicted possible solution words for Wordle
(third party source, may not be comprehensive)
"""

import requests
from bs4 import BeautifulSoup

url = "https://wordletools.azurewebsites.net/weightedbottles"
response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

tables = soup.find_all("table")
table = tables[2]

first_column_values = []

for row in table.find_all("tr")[1:]:  # skip header row
    cells = row.find_all("td")
    if cells:
        first_column_values.append(cells[0].get_text(strip=True))

with open("./data/solutions.txt", "w") as f:
    for value in first_column_values:
        f.write(value + "\n")
