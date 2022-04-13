"""
Main program
"""
import os
from urllib.error import ContentTooShortError, URLError
import json
import freesound
from dotenv import load_dotenv
from icecream import ic
from tqdm import tqdm

PER_PAGE_COUNT = 15
DUMP_PATH = "dump"


class Downloader:
    """
    This is for downloading the data and provide redownload too
    """

    def __init__(
        self,
        api_key: str = None,
        auth_token: str = None,
        errors_json_path: str = None,
        destination_path: str = None,
    ) -> None:
        # Load the environment variables on .env
        load_dotenv()

        if api_key is None:
            api_key = os.getenv("API_KEY")
        if auth_token is None:
            auth_token = os.getenv("AUTH_TOKEN")

        self.api_key = api_key
        self.auth_token = auth_token
        ic(self.auth_token)

        self.client = freesound.FreesoundClient()
        self.client.set_token(self.api_key, "token")
        self.client.set_token(self.auth_token, "oauth")

        # Init the error instances array
        self.all_error_instances = []

        # Load the errors specified on JSON file
        if errors_json_path is not None:
            with open(errors_json_path, "r", encoding="utf-8") as f:
                self.all_error_instances = json.load(f)

        self.destination_path = destination_path

    def download(self, to_search: str = "sneeze"):
        folder_path = f"{self.destination_path}/{to_search}"

        # If the folder to store hasn't created yet, then create it
        if to_search not in os.listdir(self.destination_path):
            os.mkdir(folder_path)

        results = self.client.text_search(
            query=to_search,
            filter=f"original_filename:{to_search}",
            fields="id,name,tags,username,license,previews,type",
        )

        page_count = results.count // PER_PAGE_COUNT

        error_sound_instances = []
        errors = []

        for i in range(page_count):
            print(f"Downloading from page {i+1}/{page_count}")
            for sound in tqdm(results, total=len(results.results)):
                try:
                    sound.retrieve(
                        folder_path,
                        name=f"{sound.id}_{sound.name}.{sound.type}",
                    )
                except (ContentTooShortError, URLError, OSError) as e:
                    error = dict(
                        id=sound.id, name=sound.name, type=sound.type, error=str(e)
                    )
                    errors.append(error)
                    error_sound_instances.append(sound)
                    print(f"Error on #{sound.id} - {sound.name} : {str(e)}")

            # Go to next page of the pagination
            results = results.next_page()

        # Store all error sound instances and the error description itself to the attribute
        self.all_error_instances = [
            dict(to_search=to_search, instances=error_sound_instances, errors=errors)
        ]
        ic(self.all_error_instances)

        # Save all error instances and the error itself to json file if there are
        if len(self.all_error_instances) != 0:
            with open(
                os.path.join(DUMP_PATH, "errors.json"), "w", encoding="utf-8"
            ) as f:
                json.dump(self.all_error_instances, f)

        else:
            print("No errors. Ignoring write to json file.")

    def redownload(self):
        errors = []
        error_sound_instances = []
        for sound_kind in self.all_error_instances:
            to_search = sound_kind["to_search"]
            for sound_instance in sound_kind["instances"]:
                try:
                    sound_instance.retrieve(
                        f"{self.destination_path}/{to_search}",
                        name=f"{sound_instance.name}.{sound_instance.type}",
                    )
                except (ContentTooShortError, URLError, OSError) as e:
                    error = dict(
                        id=sound_instance.id,
                        name=sound_instance.name,
                        type=sound_instance.type,
                        error=str(e),
                    )
                    errors.append(error)
                    error_sound_instances.append(sound_instance)
                    print(
                        f"Error on #{sound_instance.id} - {sound_instance.name} : {str(e)}"
                    )

        # Store all error sound instances and the error description itself to the attribute
        self.all_error_instances = [
            dict(to_search=to_search, instances=error_sound_instances, errors=errors)
        ]

        # Save all error instances and the error itself to json file if there are
        if len(self.all_error_instances) != 0:
            with open(
                os.path.join(DUMP_PATH, "errors.json"), "w", encoding="utf-8"
            ) as f:
                json.dump(self.all_error_instances, f)

        else:
            print("No errors. Ignoring write to json file.")
