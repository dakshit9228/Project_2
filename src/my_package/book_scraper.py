import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import logging


class BookScraper:
    """
    A class to scrape book data from the 'Books to Scrape' website.
    """

    def __init__(self, base_url):
        """
        Initializes the BookScraper with a specified base URL.
        Args:
            base_url (str): The base URL for the 'Books to Scrape' website.
        """
        self.base_url = base_url

    def generate_urls(self, start_page, end_page):
        """
        Generate URLs for a range of catalogue pages.
        Args:
            start_page (int): The starting page number.
            end_page (int): The ending page number.
        Returns:
            list: A list of URLs.
        """
        return [
            f"{self.base_url}page-{i}.html" for i in range(start_page, end_page + 1)
        ]

    def scrape_main_page(self, url):
        """
        Scrape the main page to get product links.
        Args:
            url (str): The URL of the main page to scrape.
        Returns:
            list: A list of product page URLs.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            return [
                urljoin(self.base_url, a["href"])
                for a in soup.select("article.product_pod h3 a")
            ]
        except requests.RequestException as e:
            logging.error(f"Failed to retrieve {url}: {e}")
            return []

    def scrape_product_page(self, url):
        """
        Scrape the product page and get product details.
        Args:
            url (str): The URL of the product page to scrape.
        Returns:
            dict: A dictionary containing product details.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            # Extract product data
            title = soup.find("h1").get_text().strip()
            image_url = urljoin(self.base_url, soup.find("img")["src"])
            price = soup.find("p", class_="price_color").get_text().strip()
            rating_tag = soup.find("p", class_="star-rating")
            rating = (
                " ".join(rating_tag["class"]).replace("star-rating", "").strip()
                if rating_tag
                else "No Rating"
            )
            description_tag = soup.find("div", id="product_description")
            description = (
                description_tag.find_next_sibling("p").get_text().strip()
                if description_tag
                else "No Description"
            )

            # Extract additional product information
            product_info = {}
            info_table = soup.find("table", class_="table table-striped")
            if info_table:
                for row in info_table.find_all("tr"):
                    key = row.find("th").get_text().strip()
                    value = row.find("td").get_text().strip()
                    product_info[key] = value

            return {
                "title": title,
                "image_url": image_url,
                "price": price,
                "rating": rating,
                "description": description,
                **product_info,
            }
        except requests.RequestException as e:
            logging.error(f"Failed to retrieve product page {url}: {e}")
            return {}

    def save_to_csv(self, data, filename):
        """
        Save scraped data to a CSV file.
        Args:
            data (list): List of dictionaries containing scraped data.
            filename (str): Filename to save the data.
        """
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        logging.info(f"Data saved to {filename}")


# Example usage
# scraper = BookScraper("https://books.toscrape.com/catalogue/")
# main_pages = scraper.generate_urls(1, 50)
# product_links = [link for page in main_pages for link in scraper.scrape_main_page(page)]
# all_product_data = [scraper.scrape_product_page(link) for link in product_links]
# scraper.save_to_csv(all_product_data, 'books_data.csv')
