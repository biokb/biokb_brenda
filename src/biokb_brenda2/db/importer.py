"""Importer for BRENDA enzyme data from JSON format."""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from tqdm import tqdm

from biokb_brenda2.db.models import (
    ActivatingCompound,
    Application,
    Author,
    Base,
    ClonedInfo,
    Compound,
    EnzymeClass,
    Expression,
    GeneralInformation,
    GeneralStability,
    Inhibitor,
    KcatKmValue,
    KiValue,
    KmValue,
    Localization,
    MetalIon,
    MolecularWeight,
    NaturalSubstrateProduct,
    OrganicSolventStability,
    Organism,
    PhOptimum,
    PhRange,
    PhStability,
    PiValue,
    PosttranslationalModification,
    Protein,
    ProteinVariant,
    Purification,
    Reaction,
    ReactionType,
    Reference,
    SourceTissue,
    SpecificActivity,
    StorageStability,
    SubstrateProduct,
    Subunit,
    Synonym,
    TemperatureOptimum,
    TemperatureRange,
    TemperatureStability,
    TurnoverNumber,
)


class BrendaImporter:
    """Import BRENDA enzyme data from JSON files into database."""

    def __init__(self, engine: Engine):
        """Initialize importer with database URL.

        Args:
            db_url: SQLAlchemy database URL
        """
        self.engine = engine
        self.Session = sessionmaker(bind=self.engine)
        self.org_cache: Dict[int, Organism] = (
            {}
        )  # Cache for organisms by their original ID
        self.ref_cache: Dict[int, Reference] = (
            {}
        )  # Cache for references by their original ID

    def clear_caches(self):
        """Clear the internal caches."""
        self.org_cache.clear()
        self.ref_cache.clear()

    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(self.engine)

    def drop_tables(self):
        """Drop all database tables."""
        Base.metadata.drop_all(self.engine)

    def recreate_tables(self):
        """Drop and recreate all database tables."""
        self.drop_tables()
        self.create_tables()

    def import_from_file(self, file_path: str | Path) -> int:
        """Import enzyme data from a JSON file.

        Args:
            file_path: Path to JSON file containing BRENDA data

        Returns:
            EnzymeClass object created from the data
        """
        with open(file_path, "r", encoding="utf-8") as f:
            enzyme_classes = json.load(f)["data"]
        for enzyme_class in tqdm(enzyme_classes.values()):
            self.clear_caches()
            with self.Session.begin() as session:
                self.import_from_dict(session, enzyme_class)
        return len(enzyme_classes.values())

    def import_from_dict(self, session: Session, enzyme_class: Dict[str, Any]):
        """Import enzyme data from a dictionary.

        Args:
            data: Dictionary containing BRENDA enzyme data

        Returns:
            EnzymeClass object created from the data
        """

        self._import_enzyme_class(session, enzyme_class)

    def _import_enzyme_class(
        self, session: Session, data: Dict[str, Any]
    ) -> EnzymeClass:
        """Import main enzyme class and all related data.

        Args:
            session: SQLAlchemy session
            data: Dictionary containing enzyme data

        Returns:
            EnzymeClass object
        """
        ec_number = data["id"]

        enzyme_class = EnzymeClass(
            ec_number=ec_number,
            recommended_name=data.get("recommended_name"),
            systematic_name=data.get("systematic_name"),
        )
        session.add(enzyme_class)
        session.flush()

        # Import references
        if "reference" in data:
            self._import_references(session, data["reference"])

        # Import proteins
        if "protein" in data:
            self._import_proteins(session, enzyme_class, data["protein"])

        # Import simple list fields
        if "synonyms" in data:
            self._import_list_items(session, ec_number, data["synonyms"], Synonym)

        only_value_fields = {
            "reaction_type": ReactionType,
        }

        for field_name, model_class in only_value_fields.items():
            if field_name in data:
                for entry in data[field_name]:
                    model_instance = model_class(
                        value=entry.get("value", None), ec_number=ec_number
                    )
                    session.add(model_instance)
                    session.flush()

        # Import complex fields with proteins/references/comments
        field_mapping = {
            "reaction": Reaction,
            "source_tissue": SourceTissue,
            "localization": Localization,
            "natural_substrates_products": NaturalSubstrateProduct,
            "substrates_products": SubstrateProduct,
            "ph_optimum": PhOptimum,
            "ph_range": PhRange,
            "specific_activity": SpecificActivity,
            "temperature_optimum": TemperatureOptimum,
            "temperature_range": TemperatureRange,
            "activating_compound": ActivatingCompound,
            "inhibitor": Inhibitor,
            "metals_ions": MetalIon,
            "molecular_weight": MolecularWeight,
            "posttranslational_modification": PosttranslationalModification,
            "subunits": Subunit,
            "pi_value": PiValue,
            "application": Application,
            "protein_variants": ProteinVariant,
            "expression": Expression,
            "general_information": GeneralInformation,
            "organic_solvent_stability": OrganicSolventStability,
            "ph_stability": PhStability,
            "temperature_stability": TemperatureStability,
        }

        for field_name, model_class in field_mapping.items():
            if field_name in data:
                self._import_complex_items(
                    session, ec_number, data[field_name], model_class
                )

        field_with_compounds = {
            "ki_value": KiValue,
            "km_value": KmValue,
            "kcat_km_value": KcatKmValue,
            "turnover_number": TurnoverNumber,
        }

        for field_name, model_class in field_with_compounds.items():
            if field_name in data:
                self._import_items_with_compounds(
                    session, ec_number, data[field_name], model_class
                )

        # # Import fields without 'value' attribute (only comments)
        # no_value_mapping = {
        #     "cloned": ClonedInfo,
        #     "purification": Purification,
        #     "general_stability": GeneralStability,
        #     "storage_stability": StorageStability,
        # }

        # for field_name, model_class in no_value_mapping.items():
        #     if field_name in data:
        #         self._import_no_value_items(
        #             session, ec_number, data[field_name], model_class
        # )

        return enzyme_class

    def _import_proteins(
        self,
        session: Session,
        enzyme_class: EnzymeClass,
        proteins_data: Dict[str, Dict],
    ):
        """Import protein entries.

        Args:
            session: SQLAlchemy session
            ec_number: EC number of the enzyme
            proteins_data: Dictionary of protein data
        """
        for org_id, protein_info in proteins_data.items():
            # check database for organism
            organism = (
                session.query(Organism)
                .filter_by(name=protein_info.get("organism"))
                .first()
            )
            # create organism if not in database
            if organism is None:
                organism = Organism(name=protein_info.get("organism", ""))
                session.add(organism)
                session.flush()  # Ensure organism.id is populated
            self.org_cache[int(org_id)] = organism

            protein = Protein(
                ec_number=enzyme_class.ec_number,
                organism_id=organism.id,
                comment=protein_info.get("comment") or None,
                references=self.get_references(protein_info),
            )
            session.add(protein)
            session.flush()  # Ensure protein.id is populated
            enzyme_class.proteins.append(protein)

    def get_references(self, info: dict) -> List[Reference]:
        reference_num_list = info.get("references", [])
        # Deduplicate reference IDs to prevent unique constraint violations
        unique_ids = list(dict.fromkeys([int(x) for x in reference_num_list]))
        references: List[Reference] = [
            self.ref_cache[ref_id] for ref_id in unique_ids if ref_id in self.ref_cache
        ]

        # Deduplicate by reference.id since multiple reference IDs can map to same reference
        seen = set()
        deduped = []
        for r in references:
            if r.id not in seen:
                seen.add(r.id)
                deduped.append(r)

        return deduped

    def get_organisms(self, info: dict) -> List[Organism]:
        organism_num_list = info.get("proteins", [])
        # Deduplicate organism IDs to prevent unique constraint violations
        unique_ids = list(dict.fromkeys([int(x) for x in organism_num_list]))

        organisms: List[Organism] = [
            self.org_cache[org_id] for org_id in unique_ids if org_id in self.org_cache
        ]

        # Deduplicate by organism.id since multiple protein IDs can map to same organism
        seen = set()
        deduped = []
        for o in organisms:
            if o.id not in seen:
                seen.add(o.id)
                deduped.append(o)

        return deduped

    def _import_references(
        self,
        session: Session,
        references_data: Dict[str, Dict],
    ):
        """Import reference entries.

        Args:
            session: SQLAlchemy session
            ec_number: EC number of the enzyme
            references_data: Dictionary of reference data
        """
        for ref_id, ref_info in references_data.items():
            pmid = ref_info.get("pmid")
            if pmid:
                reference = session.query(Reference).filter_by(pmid=pmid).first()
                if reference:
                    self.ref_cache[int(ref_id)] = reference
                    continue
            else:
                # if pmid is None, query for fields other than pmid
                reference = (
                    session.query(Reference)
                    .filter_by(
                        title=ref_info.get("title"),
                        journal=ref_info.get("journal"),
                        year=ref_info.get("year"),
                        pages=ref_info.get("pages"),
                        volume=ref_info.get("vol"),
                    )
                    .first()
                )
                if reference:
                    self.ref_cache[int(ref_id)] = reference
                    continue

            authors_list = []
            for author_name in ref_info.get("authors", []):
                author = session.query(Author).filter_by(name=author_name).first()
                if not author:
                    author = Author(name=author_name)
                    session.add(author)
                    session.flush()  # Ensure author.id is populated
                authors_list.append(author)

            new_reference = Reference(
                title=ref_info.get("title"),
                journal=ref_info.get("journal"),
                year=ref_info.get("year"),
                pages=ref_info.get("pages"),
                volume=ref_info.get("vol"),
                pmid=ref_info.get("pmid"),
                authors=authors_list,
            )
            session.add(new_reference)
            session.flush()
            self.ref_cache[int(ref_id)] = new_reference

    def _import_list_items(
        self, session: Session, ec_number: str, items: List[Dict], model_class
    ):
        """Import simple list items (e.g., synonyms, reaction_type).

        Args:
            session: SQLAlchemy session
            ec_number: EC number of the enzyme
            items: List of items to import
            model_class: SQLAlchemy model class
        """
        for item in items:
            obj = model_class(ec_number=ec_number, value=item.get("value", ""))
            session.add(obj)
            session.flush()

    def _import_items_with_compounds(
        self, session: Session, ec_number: str, items: List[Dict], model_class
    ):
        for item in items:
            # Get deduplicated organisms and references
            organisms = self.get_organisms(item)
            references = self.get_references(item)

            value_comp = re.search(
                r"^(?P<value>-?\d+(\.\d+)?)(\s*-\s*(?P<value_max>-?\d+(\.\d+)?))?\s+\{(?P<compound>.*)\}$",
                item.get("value", ""),
            )
            if value_comp:
                value = value_comp.group("value")
                value_max = value_comp.group("value_max")
                comp = value_comp.group("compound")

                # check if compound already exists
                compound = session.query(Compound).filter_by(name=comp).first()
                if compound is None:
                    compound = Compound(name=comp)
                    session.add(compound)
                    session.flush()

                obj = model_class(
                    ec_number=ec_number,
                    value=value,
                    value_max=value_max,
                    compound=compound,
                    organisms=organisms,
                    references=references,
                    comment=item.get("comment") or None,
                )
                session.add(obj)
                session.flush()
            else:
                raise ValueError(
                    f"Invalid format for item value with compound: {item.get('value', '')}"
                )

    def _import_complex_items(
        self, session: Session, ec_number: str, items: List[Dict], model_class
    ):
        """Import complex items with value, proteins, references, and comments.

        Args:
            session: SQLAlchemy session
            ec_number: EC number of the enzyme
            items: List of items to import
            model_class: SQLAlchemy model class
        """
        for item in items:
            # Get deduplicated organisms and references
            organisms = self.get_organisms(item)
            references = self.get_references(item)

            obj = model_class(
                ec_number=ec_number,
                value=item.get("value", ""),
                organisms=organisms,
                references=references,
                comment=item.get("comment") or None,
            )
            session.add(obj)
            session.flush()


#     def _import_no_value_items(
#         self, session: Session, ec_number: str, items: List[Dict], model_class
#     ):
#         """Import items without value field (only proteins, references, comments).

#         Args:
#             session: SQLAlchemy session
#             ec_number: EC number of the enzyme
#             items: List of items to import
#             model_class: SQLAlchemy model class
#         """
#         for item in items:
#             # Convert protein and reference lists to comma-separated strings
#             proteins_str = None
#             if "proteins" in item and item["proteins"]:
#                 proteins_str = ",".join(item["proteins"])

#             references_str = None
#             if "references" in item and item["references"]:
#                 references_str = ",".join(item["references"])

#             obj = model_class(
#                 ec_number=ec_number,
#                 proteins=proteins_str,
#                 references=references_str,
#                 comment=item.get("comment"),
#             )
#             session.add(obj)

#     def get_enzyme(self, ec_number: str) -> Optional[EnzymeClass]:
#         """Retrieve an enzyme class by EC number.

#         Args:
#             ec_number: EC number of the enzyme

#         Returns:
#             EnzymeClass object or None if not found
#         """
#         with self.Session() as session:
#             return session.query(EnzymeClass).filter_by(ec_number=ec_number).first()

#     def query_session(self) -> Session:
#         """Get a new database session for custom queries.

#         Returns:
#             SQLAlchemy Session object
#         """
#         return self.Session()


# def import_brenda_json(
#     json_file: str | Path, db_url: str = "sqlite:///brenda.db"
# ) -> EnzymeClass:
#     """Convenience function to import a BRENDA JSON file.

#     Args:
#         json_file: Path to JSON file
#         db_url: Database URL (default: SQLite file)

#     Returns:
#         EnzymeClass object created from the data

#     Example:
#         >>> enzyme = import_brenda_json('brenda.json')
#         >>> print(enzyme.ec_number, enzyme.recommended_name)
#     """
#     importer = BrendaImporter(db_url)
#     importer.create_tables()
#     return importer.import_from_file(json_file)
