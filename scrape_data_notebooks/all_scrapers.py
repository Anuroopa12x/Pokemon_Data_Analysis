import pandas as pd 
import time 
import requests
from bs4 import BeautifulSoup

class SrapePokemonDetails():
	def __init__(self):
		self.session = requests.Session()
		self.session.headers.update({
			"User-Agent": "Mozilla/5.0 (compatible; MyFreelanceScraper/1.0; contact@client-email.com)"
			})
		self.result = []

	def fetch_data(self, url, max_retries=3, initial_delay=1):
		for attempt in range(max_retries):
			try:
				response = self.session.get(url, timeout=10)
				response.raise_for_status()
				return BeautifulSoup(response.text, "lxml")
			except requests.exceptions.RequestException as e:
				print(f"{e} for attempt({attempt+1})")
				if attempt < max_retries -1:
					delay = initial_delay*(2**attempt)
					print(f"Retrying in {delay} seconds")
					time.sleep(delay)
				else:
					print("All Retries Used up")
					raise
	def parse_data(self, soup):
		#overall data 
		data = soup.find_all("td", class_="roundy")
		if len(data) < 40:
			print("Don't have enough data")
			return None

		#name, number, 
