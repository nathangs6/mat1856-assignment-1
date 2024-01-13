import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def scrape_bond_data(urls):
    data = []

    for url in urls:
        print(f"Getting data for {url}")
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        bond_rows = soup.find("div", {"id": "bond-searchresults-container"}).find_all('tr', {'class': 'table__tr'})

        for row in bond_rows:
            try:
                cells = row.find_all('td')
                if cells == []:
                    continue
                issuer = cells[0].text.strip()
                currency = cells[1].text.strip()
                coupon = cells[2].text.strip()
                yield_data = cells[3].text.strip()
                moodys_rating = cells[4].text.strip()
                maturity_date = cells[5].text.strip()
                bid = cells[6].text.strip()
                ask = cells[7].text.strip()

                bond_link = row.find('a', href=True)['href']
                bond_specific_url = 'https://markets.businessinsider.com' + bond_link

                bond_response = requests.get(bond_specific_url)
                bond_soup = BeautifulSoup(bond_response.content, 'html.parser')
                bond_specific_tds = bond_soup.find_all("td", class_="table__td")
                isin, issue_price, issue_date = None, None, None
                for i, td in enumerate(bond_specific_tds):
                    if 'ISIN' in td.text.strip():
                        isin = bond_specific_tds[i + 1].text.strip()
                    elif 'Issue Price' in td.text.strip():
                        issue_price = bond_specific_tds[i + 1].text.strip()
                    elif 'Issue Date' in td.text.strip():
                        issue_date = bond_specific_tds[i + 1].text.strip()

                data.append({
                    'Issuer': issuer,
                    'Currency': currency,
                    'Coupon': coupon,
                    'Yield': yield_data,
                    'Moody\'s Rating': moodys_rating,
                    'Maturity Date': maturity_date,
                    'Bid': bid,
                    'Ask': ask,
                    'ISIN': isin,
                    'Issue Price': issue_price,
                    'Issue Date': issue_date
                })
                print(f"Finished getting data for bond {isin}")
            except Exception as e:
                print(f"Error while scraping data: {e}")

    return data

# URLs to scrape
urls = [
    "https://markets.businessinsider.com/bonds/finder?p=1&borrower=71&maturity=shortterm&yield=&bondtype=2%2c3%2c4%2c16&coupon=&currency=184&rating=&country=19",
    "https://markets.businessinsider.com/bonds/finder?p=2&borrower=71&maturity=shortterm&yield=&bondtype=2%2c3%2c4%2c16&coupon=&currency=184&rating=&country=19",
    "https://markets.businessinsider.com/bonds/finder?borrower=71&maturity=midterm&yield=&bondtype=2%2c3%2c4%2c16&coupon=&currency=184&rating=&country=19"
]

bond_data = scrape_bond_data(urls)
df = pd.DataFrame(bond_data)
today = datetime.now().strftime("%d_%m_%Y")
filename = f"bond_data/bond_data_{today}.csv"
df.to_csv(filename, index=False)
print(f"Data written to {filename}")
