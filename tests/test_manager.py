import os
from unittest.mock import MagicMock, Mock, patch

import pytest
from sqlalchemy import create_engine

from biokb_brenda2.db.manager import DbManager


@pytest.fixture
def mock_engine():
    """Create a mock engine for testing."""
    engine = Mock()
    return engine


@pytest.fixture
def db_manager(mock_engine):
    """Create a DbManager instance with a mock engine."""
    return DbManager(engine=mock_engine)


@pytest.fixture
def test_data_path():
    """Return the path to the test data file."""
    current_dir = os.path.dirname(__file__)
    return os.path.join(current_dir, "data", "brenda_test.json")


class TestDbManagerImportData:
    """Tests for the import_data method."""

    def test_import_data_with_provided_path(self, db_manager, test_data_path):
        """Test import_data when data_file_path is provided."""
        with patch("biokb_brenda2.db.manager.DbImporter") as mock_importer_class:
            mock_importer = MagicMock()
            mock_importer_class.return_value = mock_importer

            db_manager.import_data(data_file_path=test_data_path)

            mock_importer_class.assert_called_once_with(db_manager.engine)
            mock_importer.import_from_file.assert_called_once_with(test_data_path)

    def test_import_data_without_path_downloads_file(self, db_manager):
        """Test import_data downloads file when no path is provided."""
        with (
            patch.object(db_manager, "download_data_file") as mock_download,
            patch("biokb_brenda2.db.manager.DbImporter") as mock_importer_class,
        ):

            mock_download.return_value = "/path/to/downloaded/file.json"
            mock_importer = MagicMock()
            mock_importer_class.return_value = mock_importer

            db_manager.import_data()

            mock_download.assert_called_once_with(force=False)
            mock_importer.import_from_file.assert_called_once_with(
                "/path/to/downloaded/file.json"
            )

    def test_import_data_with_force_download(self, db_manager):
        """Test import_data with force_download=True."""
        with (
            patch.object(db_manager, "download_data_file") as mock_download,
            patch("biokb_brenda2.db.manager.DbImporter") as mock_importer_class,
        ):

            mock_download.return_value = "/path/to/downloaded/file.json"
            mock_importer = MagicMock()
            mock_importer_class.return_value = mock_importer

            db_manager.import_data(force_download=True)

            mock_download.assert_called_once_with(force=True)
            mock_importer.import_from_file.assert_called_once_with(
                "/path/to/downloaded/file.json"
            )

    def test_import_data_creates_importer_with_engine(self, db_manager, test_data_path):
        """Test that import_data creates DbImporter with the correct engine."""
        with patch("biokb_brenda2.db.manager.DbImporter") as mock_importer_class:
            mock_importer = MagicMock()
            mock_importer_class.return_value = mock_importer

            db_manager.import_data(data_file_path=test_data_path)

            mock_importer_class.assert_called_once_with(db_manager.engine)
