import os.path
import re
import sqlite3
from logging import getLogger
from typing import Optional

import requests
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import sessionmaker

from biokb_brenda.constants import DATA_FOLDER, DB_DEFAULT_CONNECTION_STR, DOWNLOAD_URL
from biokb_brenda.db.importer import DbImporter

logger = getLogger(__name__)


class DbManager:

    def __init__(
        self,
        engine: Optional[Engine] = None,
    ):
        """Initialize the database manager.

        Configures the SQLAlchemy engine and session factory used by the
        importer. If no engine is provided, one is created from the
        ``CONNECTION_STR`` environment variable or the default
        ``DB_DEFAULT_CONNECTION_STR`` constant.

        Args:
            engine: Optional pre-configured SQLAlchemy ``Engine``. If ``None``,
                a new engine is created from configuration.
        """
        self.data_file_path: str
        connection_str = os.getenv("CONNECTION_STR", DB_DEFAULT_CONNECTION_STR)
        self.__engine: Engine = engine if engine else create_engine(connection_str)
        if self.__engine.dialect.name == "sqlite":
            with self.__engine.connect() as connection:
                connection.execute(text("pragma foreign_keys=ON"))
        logger.info("Engine: %s", self.__engine)
        self.Session = sessionmaker(bind=self.__engine)

    def __download_data_file(self, force: bool = False) -> str:
        """Download the current BRENDA data archive.

        Downloads the latest JSON archive advertised on the BRENDA download
        page into ``DATA_FOLDER``. If the file already exists and ``force`` is
        ``False``, the existing file is reused.

        Args:
            force: If ``True``, download even if the file already exists.

        Returns:
            str: Absolute path to the downloaded (or existing) archive file.

        Notes:
            Network errors during download are logged and the function returns
            the intended file path regardless. Callers should verify file
            existence/contents if strict guarantees are required.
        """

        download_file_name = self.__get_current_filename()
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

    def __get_current_filename(self):
        """Retrieve the current BRENDA JSON archive filename from the site.

        Parses the BRENDA download page and extracts the filename advertised
        for the JSON archive (e.g., ``brenda_2025_1.json.tar.gz``).

        Returns:
            str: The filename of the current JSON archive.

        Raises:
            requests.exceptions.RequestException: If the HTTP request fails or
                returns a non-2xx status.
            ValueError: If the expected filename pattern is not found.
        """
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
        keep_files: bool = True,
    ):
        """Import BRENDA data into the database.

        Ensures a data archive is available (downloading if needed), then
        delegates import to ``DbImporter``. Optionally removes the archive
        after import.

        Args:
            data_file_path: Path to a BRENDA JSON archive. If ``None``, the
                latest archive is fetched from the download page.
            force_download: When ``True`` and ``data_file_path`` is ``None``,
                forces re-downloading the current archive even if present.
            keep_files: If ``True``, leaves the archive on disk after import.

        Returns:
            None
        """
        if data_file_path is None:
            data_file_path = self.__download_data_file(force=force_download)
        importer = DbImporter(self.__engine)
        importer.import_from_file(data_file_path)
        if not keep_files:
            os.remove(data_file_path)
