import requests
from bs4 import BeautifulSoup
import csv
import argparse
import sys
import json
from urllib.parse import urljoin


def scrape_quotes(base_url, max_pages=1):
    '''
    Scrape quotes from quotes.toscrape.com with pagination support
    Returns a list of dictionaries containing quote data
    '''
    all_quotes = []
    current_url = base_url
    pages_scraped = 0
    
    while current_url and pages_scraped < max_pages:
        try:
            print(f"Scraping page {pages_scraped + 1}: {current_url}")
            response = requests.get(current_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract quotes from current page
            for quote_div in soup.find_all('div', class_='quote'):
                text = quote_div.find('span', class_='text').get_text()
                author = quote_div.find('small', class_='author').get_text()
                tags = [tag.get_text() for tag in quote_div.find_all('a', class_='tag')]
                
                all_quotes.append({
                    'text': text,
                    'author': author,
                    'tags': tags
                })
            
            # Find next page link
            next_link = soup.find('li', class_='next')
            if next_link:
                next_href = next_link.find('a')['href']
                current_url = urljoin(current_url, next_href)
            else:
                current_url = None  # No more pages
                
            pages_scraped += 1
            
        except Exception as e:
            print(f"Error scraping page {current_url}: {e}")
            break
    
    return all_quotes


def save_to_csv(quotes, filename='quotes.csv'):
    '''
    Save quotes data to CSV file
    '''
    if not quotes:
        print("No quotes to save")
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['text', 'author', 'tags']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for quote in quotes:
            # Convert tags list to string for CSV
            quote_copy = quote.copy()
            quote_copy['tags'] = ', '.join(quote_copy['tags'])
            writer.writerow(quote_copy)
    
    print(f"Saved {len(quotes)} quotes to {filename}")


def save_to_json(quotes, filename='quotes.json'):
    '''
    Save quotes data to JSON file
    '''
    if not quotes:
        print("No quotes to save")
        return
    
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(quotes, jsonfile, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(quotes)} quotes to {filename}")


def main():
    parser = argparse.ArgumentParser(description='Scrape quotes from a website')
    parser.add_argument('--url', default='http://quotes.toscrape.com',
                        help='URL to scrape quotes from (default: http://quotes.toscrape.com)')
    parser.add_argument('--output', '-o', default='quotes.csv',
                        help='Output file name (default: quotes.csv)')
    parser.add_argument('--format', '-f', choices=['csv', 'json'], default='csv',
                        help='Output format: csv or json (default: csv)')
    parser.add_argument('--max-pages', type=int, default=1,
                        help='Maximum number of pages to scrape (default: 1)')
    
    args = parser.parse_args()
    
    print(f"Starting web scraper for {args.url} (max {args.max_pages} pages)...")
    
    quotes = scrape_quotes(args.url, args.max_pages)
    
    if quotes:
        print(f"Scraped {len(quotes)} quotes")
        for i, quote in enumerate(quotes[:3], 1):  # Show first 3
            print(f"{i}. {quote['text']} - {quote['author']}")
        
        if args.format == 'csv':
            save_to_csv(quotes, args.output)
        else:
            save_to_json(quotes, args.output)
    else:
        print("No quotes scraped")


if __name__ == '__main__':
    main()
