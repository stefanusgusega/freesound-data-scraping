"""
The main program
"""

from src.downloader import Downloader

API_KEY = str(input("Enter your API KEY: "))
AUTH_TOKEN = str(input("Enter your AUTH TOKEN: "))

downloader_instance = Downloader(api_key=API_KEY, auth_token=AUTH_TOKEN)
downloader_instance.download(to_search="sneeze")

while len(downloader_instance.all_error_instances) != 0:
    downloader_instance.redownload()
