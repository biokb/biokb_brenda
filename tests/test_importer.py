import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from biokb_brenda.db.importer import DbImporter

"""Tests for BRENDA database importer."""


from biokb_brenda.db.models import (
    Author,
    Base,
    Compound,
    EnzymeClass,
    Organism,
    Protein,
    Reference,
    Synonym,
)


@pytest.fixture
def engine():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def importer(engine):
    """Create a DbImporter instance for testing."""
    return DbImporter(engine)


@pytest.fixture
def sample_enzyme_data():
    """Sample enzyme class data for testing."""
    return {
        "id": "1.1.1.1",
        "recommended_name": "Alcohol dehydrogenase",
        "systematic_name": "Alcohol:NAD+ oxidoreductase",
        "synonyms": [{"value": "ADH"}, {"value": "Aldehyde reductase"}],
        "protein": {
            "1": {
                "organism": "Homo sapiens",
                "comment": "Test protein",
                "references": ["1"],
            }
        },
        "reference": {
            "1": {
                "title": "Test Article",
                "journal": "Test Journal",
                "year": 2020,
                "pages": "1-10",
                "vol": "1",
                "pmid": "12345678",
                "authors": ["Smith J", "Doe J"],
            }
        },
    }


class TestDbImporter:
    """Test cases for DbImporter class."""

    def test_init(self, engine):
        """Test DbImporter initialization."""
        importer = DbImporter(engine)
        assert importer.engine == engine
        assert importer.Session is not None
        assert importer.org_cache == {}
        assert importer.ref_cache == {}

    def test_create_tables(self, importer, engine):
        """Test table creation."""
        importer.drop_tables()
        importer.create_tables()

        # Verify tables exist by checking metadata
        assert len(Base.metadata.tables) > 0

    def test_drop_tables(self, importer, engine):
        """Test table dropping."""
        importer.create_tables()
        importer.drop_tables()

        # Try to create tables again - should work if drop was successful
        importer.create_tables()

    def test_recreate_tables(self, importer):
        """Test table recreation."""
        importer.recreate_tables()

        # Verify tables exist
        assert len(Base.metadata.tables) > 0

    def test_clear_enzyme_class_caches(self, importer):
        """Test cache clearing."""
        importer.org_cache = {1: Mock()}
        importer.ref_cache = {1: Mock()}

        importer.clear_enzyme_class_caches()

        assert len(importer.org_cache) == 0
        assert len(importer.ref_cache) == 0

    def test_load_json_from_file_json(self, tmp_path):
        """Test loading JSON from .json file."""
        test_data = {"data": {"1.1.1.1": {"id": "1.1.1.1"}}}
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(test_data))

        engine = create_engine("sqlite:///:memory:")
        importer = DbImporter(engine)
        result = importer.load_json_from_file(str(json_file))

        assert result == test_data["data"]

    def test_get_or_create_compound_new(self, importer):
        """Test creating a new compound."""
        with importer.Session.begin() as session:
            compound = importer._get_or_create_compound(session, "ATP")
            session.flush()

            assert compound.name == "ATP"
            assert compound.id is not None

    def test_get_or_create_compound_existing(self, importer):
        """Test getting an existing compound."""
        with importer.Session.begin() as session:
            # Create first compound
            compound1 = importer._get_or_create_compound(session, "ATP")
            session.flush()
            first_id = compound1.id

            # Get same compound
            compound2 = importer._get_or_create_compound(session, "ATP")

            assert compound2.id == first_id
            assert compound1 == compound2

    def test_get_or_create_compound_empty_name(self, importer):
        """Test that empty compound name raises error."""
        with importer.Session.begin() as session:
            with pytest.raises(ValueError, match="Compound name could not be empty"):
                importer._get_or_create_compound(session, None)

    def test_delete_stoichiometry(self, importer):
        """Test stoichiometry removal from reaction parts."""
        assert importer._DbImporter__delete_stoichiometry("2 ATP") == "ATP"
        assert importer._DbImporter__delete_stoichiometry("n NADH") == "NADH"
        assert importer._DbImporter__delete_stoichiometry("glucose") == "glucose"
        assert importer._DbImporter__delete_stoichiometry("  3 H2O  ") == "H2O"

    def test_import_list_items(self, importer, sample_enzyme_data):
        """Test importing simple list items like synonyms."""
        with importer.Session.begin() as session:
            ec_number = "1.1.1.1"
            synonyms = sample_enzyme_data["synonyms"]

            importer._import_list_items(session, ec_number, synonyms, Synonym)
            session.flush()

            results = session.query(Synonym).filter_by(ec_number=ec_number).all()
            assert len(results) == 2
            assert {r.value for r in results} == {"ADH", "Aldehyde reductase"}

    def test_get_references(self, importer):
        """Test getting references from cache."""
        # Setup mock references in cache
        ref1 = Mock(spec=Reference, id=1)
        ref2 = Mock(spec=Reference, id=2)
        importer.ref_cache = {1: ref1, 2: ref2}

        info = {"references": ["1", "2", "1"]}  # Include duplicate

        references = importer.get_references(info)

        assert len(references) == 2
        assert ref1 in references
        assert ref2 in references

    def test_get_organisms(self, importer):
        """Test getting organisms from cache."""
        # Setup mock organisms in cache
        org1 = Mock(spec=Organism, id=1)
        org2 = Mock(spec=Organism, id=2)
        importer.org_cache = {1: org1, 2: org2}

        info = {"proteins": ["1", "2", "1"]}  # Include duplicate

        organisms = importer.get_organisms(info)

        assert len(organisms) == 2
        assert org1 in organisms
        assert org2 in organisms

    def test_get_references_empty(self, importer):
        """Test getting references with empty list."""
        info = {"references": []}
        references = importer.get_references(info)
        assert references == []

    def test_get_organisms_missing_from_cache(self, importer):
        """Test getting organisms when some are missing from cache."""
        org1 = Mock(spec=Organism, id=1)
        importer.org_cache = {1: org1}

        info = {"proteins": ["1", "2", "3"]}

        organisms = importer.get_organisms(info)

        # Should only return the one in cache
        assert len(organisms) == 1
        assert org1 in organisms
