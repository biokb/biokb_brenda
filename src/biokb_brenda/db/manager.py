import os.path
import re
from logging import getLogger
from typing import Optional

import requests
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker

from biokb_brenda.constants import DATA_FOLDER, DB_DEFAULT_CONNECTION_STR, DOWNLOAD_URL
from biokb_brenda.db.importer import DbImporter

logger = getLogger(__name__)


class DbManager:

    def __init__(
        self,
        engine: Optional[Engine] = None,
    ):
        self.data_file_path: str
        connection_str = os.getenv("CONNECTION_STR", DB_DEFAULT_CONNECTION_STR)
        self.engine: Engine = engine if engine else create_engine(connection_str)
        logger.info(f"Using engine: {self.engine}")
        self.Session = sessionmaker(bind=self.engine)

    def download_data_file(self, force: bool = False) -> str:
        """Download the data file from BRENDA."""

        download_file_name = self.get_current_filename()
        os.makedirs(DATA_FOLDER, exist_ok=True)
        data_file_path = os.path.join(DATA_FOLDER, download_file_name)

        if os.path.exists(data_file_path) and not force:
            logger.info(f"File {data_file_path} already exists. Skipping download.")
            return data_file_path

        PAYLOAD = {
            # 1. License acceptance (from input name="accept-license" and value="1")
            "accept-license": "1",
            # 2. File selection (from input name="dlfile" which is set to button id="dl-json")
            "dlfile": "dl-json",
        }

        try:
            # Use POST request to submit the form data
            with requests.post(DOWNLOAD_URL, data=PAYLOAD, stream=True) as response:
                response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

                # Save the content to the file
                with open(data_file_path, "wb") as file:
                    logger.info(f"Download data")
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)

        except requests.exceptions.RequestException as e:
            logger.info(f"An error occurred during download: {e}")

        return data_file_path

    def get_current_filename(self):
        """Get the current filename from the download page."""
        pattern = r"data-filename=\"(brenda_\d{4}_\d+\.json\.tar\.gz)\""
        response = requests.get(DOWNLOAD_URL, timeout=10)
        response.raise_for_status()

        # Search for the pattern in the HTML content
        match = re.search(pattern, response.text)

        if match:
            current_filename = match.group(1)
            return current_filename
        else:
            raise ValueError("Filename pattern not found in the HTML content.")

    def import_data(
        self,
        data_file_path: Optional[str] = None,
        force_download: bool = False,
        keep_files: bool = False,
    ):
        """Import data into the database."""
        if data_file_path is None:
            data_file_path = self.download_data_file(force=force_download)
        importer = DbImporter(self.engine)
        importer.import_from_file(data_file_path)
        if not keep_files:
            os.remove(data_file_path)
