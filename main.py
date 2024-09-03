import os
import requests
import pandas as pd
import time
import random
from dotenv import load_dotenv
from typing import Dict, List, Optional, Callable

def load_config() -> Dict[str, str]:
    load_dotenv()
    return {
        'base_url': os.getenv('urltwo'),
        'pagination_suffix': os.getenv('urltwo_pagination_suffix')
    }

def create_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    return session

def fetch_page(session: requests.Session, url: str) -> Optional[str]:
    try:
        response = session.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def scrape_all_pages(
    session: requests.Session, 
    config: Dict[str, str], 
    scrape_page_func: Callable[[str], List[Dict[str, str]]], 
    max_pages: int = 18
) -> List[Dict[str, str]]:
    all_products = []
    for page in range(1, max_pages + 1):
        url = config['base_url'] if page == 1 else f"{config['base_url']}{config['pagination_suffix']}{page}"
        print(f"Scraping page {page}: {url}")

        html = fetch_page(session, url)
        if not html:
            break

        products = scrape_page_func(html)
        all_products.extend(products)

        if not products:
            break

        time.sleep(random.uniform(1, 3))  # Random delay between requests

    return all_products

def save_to_csv(data: List[Dict[str, str]], filename: str) -> None:
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

def main(scraper_module):
    config = load_config()
    session = create_session()
    products = scrape_all_pages(session, config, scraper_module.scrape_page)
    save_to_csv(products, f"{scraper_module.__name__.split('_')[0]}_products.csv")

if __name__ == "__main__":
    # Import the specific scraper module here
    import urltwo_scraper
    main(urltwo_scraper)