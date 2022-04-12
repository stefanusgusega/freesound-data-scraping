"""
Main program
"""
import os
import pickle as pkl
import sys
from urllib.error import ContentTooShortError, URLError
import freesound
import pandas as pd
from dotenv import load_dotenv
from icecream import ic
from tqdm import tqdm

PER_PAGE_COUNT = 15
DUMP_PATH = "dump"

# Load the environment variables on .env
load_dotenv()

api_key = os.getenv("API_KEY")
auth_token = os.getenv("AUTH_TOKEN")
ic(auth_token)
if api_key is None:
    print(
        "You need to set your API key as an environment variable",
    )
    print("named FREESOUND_API_KEY")
    sys.exit(-1)

client = freesound.FreesoundClient()
client.set_token(api_key, "token")
client.set_token(auth_token, "oauth")
# ic(client.header)

sneeze_results = client.text_search(
    query="sneeze",
    filter="original_filename:sneeze",
    fields="id,name,tags,username,license,previews,type",
)
ic(sneeze_results.count)

page_count = sneeze_results.count // PER_PAGE_COUNT
# This array used to save readable error data --> CSV
errors = []
# This array used to save the sound instances that is occuring error --> pickle
error_sound_instances = []

for i in range(page_count):
    print(f"Downloading from page {i+1}/{page_count}")
    for sound in tqdm(sneeze_results, total=len(sneeze_results.results)):
        # for sound in sneeze_results:
        try:
            # ic(sound.name)
            # ic(sound.type)
            # ic(sound)
            sound.retrieve("data/sneeze", name=f"{sound.name}.{sound.type}")
        except (ContentTooShortError, URLError) as e:
            error = dict(id=sound.id, name=sound.name, type=sound.type, error=str(e))
            errors.append(error)
            error_sound_instances.append(sound)
            print(f"Error on #{sound.id} - {sound.name} : {str(e)}")

    # Go to next page of the pagination
    sneeze_results = sneeze_results.next_page()

# Save errors to CSV
error_df = pd.DataFrame(data=errors)
error_df.to_csv(os.path.join(DUMP_PATH, "errors.csv"), index=False)

# Save errors to pickle file
with open(os.path.join(DUMP_PATH, "errors.pkl"), "wb") as f:
    pkl.dump(f)
