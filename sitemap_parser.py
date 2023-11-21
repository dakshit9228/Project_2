import requests
import pandas as pd
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse


class SitemapParser:
    """
    A parser for sitemaps, capable of fetching and parsing sitemap URLs
    and extracting URLs contained within them.

    Attributes:
        domain (str): The base domain for which the sitemap is to be parsed.
        sitemap_dataframes (dict): A dictionary to store parsed data as pandas DataFrames.
    """

    def __init__(self, domain):
        """
        Initializes the SitemapParser with a specified domain.

        Args:
            domain (str): The domain for which the sitemaps are to be parsed.
        """
        self.domain = domain
        self.base_url = f"https://{domain}"
        self.sitemap_dataframes = {}
        self.get_all_sitemaps()

    def fetch_content(self, url):
        """
        Fetches content from a given URL.

        Args:
            url (str): URL from which to fetch content.

        Returns:
            str: The content fetched from the URL.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching content from {url}: {e}")
            return ""

    def parse_sitemap(self, sitemap_url):
        """
        Parses a sitemap from a given URL.

        Args:
            sitemap_url (str): URL of the sitemap to be parsed.
        """
        xml_content = self.fetch_content(sitemap_url)
        if not xml_content:
            return
        soup = BeautifulSoup(xml_content, "xml")
        urls = []

        for loc in soup.find_all("loc"):
            url = loc.text
            urls.append(url)
            if url.endswith(".xml"):
                self.parse_sitemap(url)

        key = urlparse(sitemap_url).path.split("/")[-1]
        df = pd.DataFrame(urls, columns=["URLs"])
        self.sitemap_dataframes[key] = df

    def get_all_sitemaps(self):
        """
        Retrieves and parses all sitemaps listed in the robots.txt file of the domain.
        """
        robots_txt_url = f"{self.base_url}/robots.txt"
        robots_txt = self.fetch_content(robots_txt_url)
        if not robots_txt:
            return

        for line in robots_txt.split("\n"):
            if line.startswith("Sitemap:"):
                sitemap_url = line.split(": ")[1].strip()
                self.parse_sitemap(sitemap_url)

    def save_as_csv(self, filename="combined_sitemap.csv"):
        """
        Saves the combined DataFrames as a single CSV file.

        Args:
            filename (str, optional): The filename for the CSV file. Defaults to "combined_sitemap.csv".
        """
        combined_df = pd.concat(self.sitemap_dataframes.values(), ignore_index=True)
        combined_df.to_csv(filename, index=False)

    def get_combined_dataframe(self):
        """
        Returns the combined DataFrame containing all parsed sitemap data.

        Returns:
            pandas.DataFrame: The combined DataFrame from all parsed sitemaps.
        """
        return pd.concat(self.sitemap_dataframes.values(), ignore_index=True)
