import os
import requests
import pandas as pd
import time
import random
from dotenv import load_dotenv
from typing import Dict, List, Optional, Callable
from db.db_ingestion import ingest_data  # Updated import

def load_config(url_key: str, suffix_key: str) -> Dict[str, str]:
    load_dotenv()
    return {
        'base_url': os.getenv(url_key),
        'pagination_suffix': os.getenv(suffix_key)
    }

def create_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en,en-US;q=0.9,de-DE;q=0.8,de;q=0.7,fr-FR;q=0.6,fr;q=0.5,es-ES;q=0.4,es;q=0.3',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        'Sec-Ch-Ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"macOS"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
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
    max_pages: int = 4
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

def main(scraper_module, url_key: str, suffix_key: str, marketplace_name: str):
    config = load_config(url_key, suffix_key)
    session = create_session()
    products = scrape_all_pages(session, config, scraper_module.scrape_page)
    save_to_csv(products, f"{scraper_module.__name__.split('_')[0]}_products.csv")
    
    # Ingest data into the database
    ingest_data(products, marketplace_name)

if __name__ == "__main__":
    # Import the specific scraper modules here
    import urltwo_scraper
    import urlthree_scraper

    # Run both scrapers
    main(urltwo_scraper, 'urltwo', 'urltwo_pagination_suffix', 'URLTwo')
    main(urlthree_scraper, 'urlthree', 'urlthree_pagination_suffix', 'URLThree')