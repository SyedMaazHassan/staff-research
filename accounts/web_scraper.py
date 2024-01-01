import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re


class WebScraper:
    def __init__(self, link):
        self.link = link
        self.content = None
        self.title = None
        self.description = None

    def remove_extra_spaces(self):
        print(f"- Removing extra spaces from scrapped content")
        cleaned_text = re.sub(r'\s{2,}', '\n\n', self.content).strip()
        self.content = cleaned_text 

    def set_link_meta(self, soup):
        self.title = soup.title.string if soup.title else None
        description = soup.find('meta', attrs={'name': 'description'})
        self.description = description['content'] if description else None        

    def is_allowed_by_robots_txt(self):
        try:
            print("- Checking permissions to scrap web page")
            base_url = "{uri.scheme}://{uri.netloc}".format(uri=urlparse(self.link))
            robots_txt_url = urljoin(base_url, "/robots.txt")
            response = requests.get(robots_txt_url)

            if response.status_code == 200:
                parsed_link = urlparse(self.link)
                path = str(parsed_link.path).strip()

                disallowed_paths = self.get_disallowed_paths(response.text)
                return path not in disallowed_paths
            else:
                print(f"Warning: Unable to fetch robots.txt. Status Code: {response.status_code}")
                return True

        except Exception as e:
            print(f"Warning: Error checking robots.txt: {e}")
            return True

    def get_disallowed_paths(self, robots_txt_content):
        disallowed_paths = []
        lines = robots_txt_content.splitlines()

        for line in lines:
            if line.lower().startswith("disallow:"):
                path = line.split(":", 1)[1].strip()
                disallowed_paths.append(path)

        return disallowed_paths

    def scrape_html(self):
        try:
            if not self.is_allowed_by_robots_txt():
                error = "Warning: Scraping not allowed by robots.txt"
                print(error)
                raise Exception(error)
            print("- Permission allowed")

            print(f"- Starting to scrap {self.link}")
            response = requests.get(self.link)

            if response.status_code == 200:
                print(f"- Web page scrapped successfully")
                soup = BeautifulSoup(response.text, 'html.parser')
                self.content = soup.get_text()
                self.set_link_meta(soup)
                self.remove_extra_spaces()
            else:
                error = f"Error: Unable to fetch the page. Status Code: {response.status_code}"
                print(error)
                raise Exception(error)

        except Exception as e:
            print(e)
            raise 

