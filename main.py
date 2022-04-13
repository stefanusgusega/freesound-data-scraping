"""
The main program
"""

from src.downloader import Downloader

downloader_instance = Downloader()
downloader_instance.download(to_search="sneeze")

while len(downloader_instance.all_error_instances) != 0:
    downloader_instance.redownload()
