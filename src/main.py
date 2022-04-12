"""
Main program
"""
import os
import sys
import freesound
from dotenv import load_dotenv
from icecream import ic
from tqdm import tqdm

PER_PAGE_COUNT = 15

# Load the environment variables on .env
load_dotenv()

api_key = os.getenv("API_KEY")
if api_key is None:
    print(
        "You need to set your API key as an evironment variable",
    )
    print("named FREESOUND_API_KEY")
    sys.exit(-1)

client = freesound.FreesoundClient()
client.set_token(api_key, "token")

sneeze_results = client.text_search(query="sneeze", filter="tag:sneeze")
ic(sneeze_results.count)

page_count = sneeze_results.count // PER_PAGE_COUNT

for i in range(page_count):
    print(f"Downloading from page {i+1}/{page_count}")
    # TODO: Should implement the OAuth2. See https://gist.github.com/ffont/3607ba4af9814f3877cd42894a564222
    for sound in tqdm(sneeze_results):
        sound.retrieve("data/sneeze")

# for sound in results:
#     ic(sound)

# for sound in results:
#     sound.retrieve_preview(".", sound.name + ".mp3")
#     print(sound.name)
