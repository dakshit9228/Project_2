import requests
import pandas as pd
import logging
import os


class CollegeFootballDataAPI:
    """
    A Python class to interact with the College Football Data API. It fetches data about college football games.

    Attributes:
        token (str): API token for authenticating requests to the College Football Data API.
    """

    def __init__(self, token=None):
        """
        Initializes the CollegeFootballDataAPI with an API token.

        Args:
            token (str, optional): API token for the College Football Data API. Defaults to None.
        """
        self.base_url = "https://api.collegefootballdata.com/games"
        self.token = token or os.getenv("COLLEGE_FOOTBALL_DATA_API_TOKEN")
        self.headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

    def get_games_for_year_range(self, start_year, end_year, season_type):
        """
        Retrieves games data for a specified range of years and season type.

        Args:
            start_year (int): The starting year of the range.
            end_year (int): The ending year of the range.
            season_type (str): The type of the season (e.g., 'regular', 'postseason').

        Returns:
            pandas.DataFrame: A DataFrame containing the retrieved games data.
        """
        all_games = []
        for year in range(start_year, end_year + 1):
            try:
                params = {"year": str(year), "seasonType": season_type}
                response = requests.get(
                    self.base_url, params=params, headers=self.headers
                )
                response.raise_for_status()
                all_games.extend(response.json())
            except requests.exceptions.HTTPError as e:
                logging.error(f"HTTPError for year {year}: {e}")
            except requests.exceptions.RequestException as e:
                logging.error(f"RequestException for year {year}: {e}")

        return pd.DataFrame(all_games)
