"""Importer for BRENDA enzyme data from JSON format."""

import io
import json
import logging
import os.path
import re
import tarfile
import zipfile
from ast import mod
from collections import namedtuple
from os import name
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.request import urlretrieve

import numpy as np
import pandas as pd
import requests
from rdkit import Chem, RDLogger
from sqlalchemy import Engine, create_engine, func, select, update
from sqlalchemy.orm import Session, sessionmaker
from tqdm import tqdm

from biokb_brenda.constants import (
    CHEBI_INCHI_URL,
    CHEBI_NAMES_URL,
    DATA_FOLDER,
    LIGAND_CHEBI_MAPPING_FILE,
    LIGAND_CHEBI_MAPPING_URL,
    LIGAND_INCHI_CHEBI_FILE,
    LIGAND_INCHI_CHEBI_URL,
    TAXONOMY_DATA_FOLDER,
    TAXONOMY_URL,
)
from biokb_brenda.db import models
from biokb_brenda.db.models import (
    ActivatingCompound,
    Application,
    Author,
    Base,
    ClonedInfo,
    CompInchiChebi,
    CompLigChebi,
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
    NSPReaction,
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
    SPReaction,
    StorageStability,
    Subunit,
    Synonym,
    TaxonomyName,
    TemperatureOptimum,
    TemperatureRange,
    TemperatureStability,
    TurnoverNumber,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",
    datefmt="%y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
rdkit_logger = RDLogger.logger()
rdkit_logger.setLevel(RDLogger.CRITICAL)

Ref = namedtuple(
    "Ref",
    [
        "title",
        "journal",
        "year",
        "pages",
        "volume",
        "pmid",
        "author_ids",
    ],
)


class DbImporter:
    """Import BRENDA enzyme data from JSON files into database."""

    def __init__(self, engine: Engine):
        """Initialize importer with database URL.

        Args:
            db_url: SQLAlchemy database URL
        """
        self.engine = engine
        self.Session = sessionmaker(bind=self.engine)
        self.df_org_ec_name_id: pd.DataFrame  # columns: ec, name, id
        self.lower_org_name_db_ids: dict[str, Any] = {}
        self.org_cache: Dict[
            int, Organism
        ] = {}  # Cache for organisms by their original ID
        self.ref_cache: Dict[
            int, Reference
        ] = {}  # Cache for references by their original ID
        self.comp_cache: Dict[str, Compound] = {}  # Cache for compounds by name

    def __clear_enzyme_class_caches(self):
        """Clear the internal caches."""
        self.org_cache.clear()
        self.ref_cache.clear()
        # don't clear comp_cache here to retain compound cache across imports

    def __recreate_tables(self):
        """Drop and recreate all database tables."""
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

    def __load_json_from_file(self, file_path) -> dict:
        """
        Opens a .tar.gz file, extracts the first file (assumed to be a single JSON file),
        and loads its content into a Python dictionary.
        """
        if file_path.endswith(".tar.gz"):
            with tarfile.open(file_path, "r:gz") as tar:
                member = tar.getmembers()[0]
                f_bytes = tar.extractfile(member)
                if f_bytes is not None:
                    with io.TextIOWrapper(f_bytes, encoding="utf-8") as f:
                        # Load and return the specific 'data' field
                        enzyme_classes: dict = json.load(f)["data"]
                        logger.info("Loaded %d enzyme classes", len(enzyme_classes))
                        if not isinstance(enzyme_classes, dict):
                            raise ValueError(
                                "The 'data' field in the JSON file is not a dictionary."
                            )
                        return enzyme_classes
                else:
                    raise ValueError("The tar.gz file is empty or could not be read.")
        elif file_path.endswith(".json"):
            with open(file_path, "r", encoding="utf-8") as f:
                enzyme_classes: dict = json.load(f)["data"]
                logger.info("Loaded %d enzyme classes", len(enzyme_classes))
                if not isinstance(enzyme_classes, dict):
                    raise ValueError(
                        "The 'data' field in the JSON file is not a dictionary."
                    )
                return enzyme_classes
        else:
            return {}

    def import_from_file(self, file_path: str | Path) -> Dict[str, int]:
        """Import enzyme data from a JSON file.

        Args:
            file_path: Path to JSON file containing BRENDA data

        Returns:
            EnzymeClass object created from the data
        """
        self.__recreate_tables()
        enzyme_classes = self.__load_json_from_file(file_path)
        logger.info("Read enzyme classes")
        self.__import_and_collect_organisms(enzyme_classes)
        self.__import_and_collect_references(enzyme_classes)
        counter = 0
        with self.Session() as session:
            for enzyme_class in tqdm(
                enzyme_classes.values(), desc="Importing enzyme classes"
            ):
                counter += 1
                self.__clear_enzyme_class_caches()
                self.__import_enzyme_class(session, enzyme_class)
                if counter % 100 == 0:
                    session.commit()
            session.commit()
        self.__update_brenda_ligand_ids()
        self.__update_compound_inchi_chebi()
        self.__update_chebi_ids_with_chebi()
        self.__update_inchi_by_chebi_id()
        self.__update_inchi_keys()
        self.__update_organism_tax_ids()

        return {"enzyme_classes": len(enzyme_classes.values())}

    def __import_and_collect_organisms(self, enzyme_classes):
        Org = namedtuple("Org", ["ec", "name", "id"])
        organism_set: set[Org] = set()
        for enzyme_class in tqdm(enzyme_classes.values(), desc="Collecting organisms"):
            ec_number = enzyme_class["id"]
            if "protein" in enzyme_class:
                for org_id, protein_info in enzyme_class["protein"].items():
                    organism_name = protein_info.get("organism")
                    if organism_name:
                        organism_set.add(Org(ec_number, organism_name, int(org_id)))
        self.df_org_ec_name_id = pd.DataFrame(organism_set)
        df_name = self.df_org_ec_name_id.loc[:, ["name"]]
        df_name["name_lower"] = df_name["name"].str.lower()
        df_name = (
            df_name.drop_duplicates(subset=["name_lower"], keep="first")
            .sort_values(by="name")
            .reset_index(drop=True)
        )
        df_name["tax_id"] = None
        df_name.index += 1
        df_name.index.rename("id", inplace=True)
        df_name.drop(columns=["name_lower"]).to_sql(
            Organism.__tablename__, self.engine, if_exists="append"
        )
        self.lower_org_name_db_ids = {
            r["name_lower"]: id for id, r in df_name.iterrows()
        }

    def __import_and_collect_references(self, enzyme_classes):
        # first collecting all authors
        authors = set()
        for enzyme_class in tqdm(enzyme_classes.values(), desc="Collecting authors"):
            if "reference" in enzyme_class:
                for ref_id, ref_info in enzyme_class["reference"].items():
                    for author_name in ref_info.get("authors", []):
                        authors.add(author_name)
        df_authors = pd.DataFrame(sorted(authors), columns=["name"])
        df_authors.index += 1
        df_authors.index.rename("id", inplace=True)
        df_authors.to_sql(Author.__tablename__, self.engine, if_exists="append")
        df_authors_id = df_authors.reset_index().set_index("name")
        get_db_id_by_author_name = lambda author_name: int(
            df_authors_id.loc[author_name].id
        )
        # then collecting all references

        reference_set: set[Ref] = set()
        pmids = set()
        for enzyme_class in tqdm(enzyme_classes.values(), desc="Collecting references"):
            if "reference" in enzyme_class:
                for ref_id, ref_info in enzyme_class["reference"].items():
                    # avoid duplicate pmid entries
                    pmid = ref_info.get("pmid")
                    if pmid:
                        if pmid in pmids:
                            continue
                        pmids.add(pmid)
                    author_ids = [
                        get_db_id_by_author_name(author_name)
                        for author_name in ref_info.get("authors", [])
                    ]
                    reference_set.add(
                        Ref(
                            title=ref_info.get("title"),
                            journal=ref_info.get("journal"),
                            year=ref_info.get("year"),
                            pages=ref_info.get("pages"),
                            volume=ref_info.get("vol"),
                            pmid=pmid,
                            author_ids=tuple(sorted(author_ids)),
                        )
                    )
        self.__insert_references(reference_set)

    def __insert_references(self, reference_set: set[Ref]):
        with self.Session.begin() as session:
            for ref in tqdm(reference_set, desc="Inserting references into database"):
                authors: list[Author] = (
                    session.query(Author).where(Author.id.in_(ref.author_ids)).all()
                )
                reference = Reference(
                    title=ref.title,
                    journal=ref.journal,
                    year=ref.year,
                    pages=ref.pages,
                    volume=ref.volume,
                    pmid=ref.pmid,
                    authors=authors,
                )
                session.add(reference)

    def __import_enzyme_class(
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

        # Set references
        if "reference" in data:
            self.__set_ref_cache(session, data["reference"])

        # Import proteins
        if "protein" in data:
            self.__set_org_cache(session, data["protein"])
            self.__import_proteins(session, enzyme_class, data["protein"])

        # Import simple list fields
        if "synonyms" in data:
            self.__import_list_items(session, ec_number, data["synonyms"], Synonym)

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

        fields_with_reactions: dict[str, type[Base]] = {
            "substrates_products": SPReaction,
            "natural_substrates_products": NSPReaction,
            "reaction": Reaction,
        }
        for field_name, model_class in fields_with_reactions.items():
            self.__import_reaction_field(
                session, ec_number, data.get(field_name, []), model_class
            )

        # Import complex fields with proteins/references/comments
        field_mapping = {
            "source_tissue": SourceTissue,
            "localization": Localization,
            "posttranslational_modification": PosttranslationalModification,
            "subunits": Subunit,
            "application": Application,
            "protein_variants": ProteinVariant,
            "expression": Expression,
            "general_information": GeneralInformation,
        }

        for field_name, model_class in field_mapping.items():
            if field_name in data:
                self.__import_complex_items(
                    session, ec_number, data[field_name], model_class
                )

        field_with_with_float_value_and_compounds = {
            "ki_value": KiValue,
            "km_value": KmValue,
            "kcat_km_value": KcatKmValue,
            "turnover_number": TurnoverNumber,
            "ic50_value": models.IC50Value,
        }

        for (
            field_name,
            model_class,
        ) in field_with_with_float_value_and_compounds.items():
            if field_name in data:
                self.__import_items_with_float_value_and_compounds(
                    session, ec_number, data[field_name], model_class
                )

        field_with_compounds = {
            "inhibitor": Inhibitor,
            "metals_ions": MetalIon,
            "organic_solvent_stability": OrganicSolventStability,
            "cofactor": models.Cofactor,
            "activating_compound": ActivatingCompound,
        }

        for field_name, model_class in field_with_compounds.items():
            if field_name in data:
                self.__import_items_with_compound(
                    session, ec_number, data[field_name], model_class
                )

        field_with_with_float_values = {
            "molecular_weight": MolecularWeight,
            "ph_optimum": PhOptimum,
            "ph_range": PhRange,
            "ph_stability": PhStability,
            "pi_value": PiValue,
            "specific_activity": SpecificActivity,
            "temperature_optimum": TemperatureOptimum,
            "temperature_range": TemperatureRange,
            "temperature_stability": TemperatureStability,
        }

        for (
            field_name,
            model_class,
        ) in field_with_with_float_values.items():
            if field_name in data:
                self.__import_items_with_with_float_values(
                    session, ec_number, data[field_name], model_class
                )

        fields_only_comment = {
            "cloned": ClonedInfo,
            "purification": Purification,
            "general_stability": GeneralStability,
            "storage_stability": StorageStability,
        }

        for field_name, model_class in fields_only_comment.items():
            if field_name in data:
                self.__import_items_only_comment(
                    session, ec_number, data[field_name], model_class
                )

        return enzyme_class

    def __import_proteins(
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
            organism_name = protein_info.get("organism")
            if organism_name:
                organism_id = self.lower_org_name_db_ids.get(organism_name.lower())
                if organism_id:
                    self.org_cache[int(org_id)].id = organism_id
                    protein = Protein(
                        ec_number=enzyme_class.ec_number,
                        organism_id=organism_id,
                        comment=protein_info.get("comment") or None,
                        references=self.__get_references(protein_info),
                    )
                    session.add(protein)
                    enzyme_class.proteins.append(protein)
                else:
                    raise ValueError(
                        f"Organism '{organism_name}' not found in database for protein with org_id {org_id} in EC {enzyme_class.ec_number}"
                    )
            else:
                raise ValueError(
                    f"Organism name missing for protein with org_id {org_id} in EC {enzyme_class.ec_number}"
                )

    def __get_references(self, info: dict) -> list[Reference]:
        reference_num_list = info.get("references", [])
        # Deduplicate reference IDs to prevent unique constraint violations
        unique_ids: set[int] = {int(x) for x in reference_num_list if x.isdigit()}
        references: set[Reference] = {
            self.ref_cache[ref_id] for ref_id in unique_ids if ref_id in self.ref_cache
        }

        return list(references)

    def __get_organisms(self, info: dict) -> list[Organism]:
        organism_num_list = info.get("proteins", [])
        # Deduplicate organism IDs to prevent unique constraint violations
        unique_ids: set[int] = {int(x) for x in organism_num_list}

        organisms: set[Organism] = {
            self.org_cache[org_id] for org_id in unique_ids if org_id in self.org_cache
        }

        return list(organisms)

    def __set_org_cache(
        self,
        session: Session,
        proteins_data: Dict[str, Dict],
    ):
        """Import organism entries.

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
            self.org_cache[int(org_id)] = organism

    def __set_ref_cache(
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

    def __import_list_items(
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

    def __get_or_create_compound(
        self, session: Session, compound_name: str | None
    ) -> Compound:
        """Get or create a Compound by name.

        Args:
            session: SQLAlchemy session
            compound_name: Name of the compound
        """
        if not compound_name:
            raise ValueError("Compound name could not be empty.")

        compound: Compound | None = self.comp_cache.get(compound_name)
        if compound is None:
            compound = Compound(name=compound_name)
            session.add(compound)
            session.flush()
            self.comp_cache[compound_name] = compound
        return compound

    def __delete_stoichiometry(self, reaction_part: str) -> str:
        return re.search(r"^\s*((\d+|n) )?(.*)\s*$", reaction_part.strip()).group(3)  # type: ignore because of the regex match

    def __import_reaction_field(
        self, session: Session, ec_number: str, items: List[Dict], model_class
    ):
        ir_mapping = {"ir": False, "r": True}

        for item in items:
            # Get deduplicated organisms and references
            organisms: List[Organism] = self.__get_organisms(item)
            references: List[Reference] = self.__get_references(item)
            reaction = item.get("value", "")
            reversibility_found: re.Match[str] | None = re.search(
                r"^\s*(?P<reaction>.*?)\s*\{(?P<reversibility>i?r)\}\s*$", reaction
            )
            reversibility: bool | None = None
            if reversibility_found:
                reaction = reversibility_found.group("reaction")
                rev_str = reversibility_found.group("reversibility")
                reversibility = ir_mapping[rev_str]

            # because in some cases there is a trailing | followed by a comment
            reaction: str = reaction.split(" |")[0]

            # get substrate and products
            reaction_splitted = reaction.split(" = ")
            if len(reaction_splitted) == 2:
                substrates_str, products_str = reaction_splitted
                substrate_names = [
                    self.__delete_stoichiometry(s) for s in substrates_str.split(" + ")
                ]
                product_names = [
                    self.__delete_stoichiometry(p) for p in products_str.split(" + ")
                ]
            else:
                substrate_names = [
                    self.__delete_stoichiometry(s)
                    for s in reaction_splitted[0].split(" + ")
                ]
                product_names = []

            substrates: List[Compound] = [
                self.__get_or_create_compound(session, name)
                for name in substrate_names
                if name
            ]
            products: list[Compound] = [
                self.__get_or_create_compound(session, name)
                for name in product_names
                if name
            ]

            nsp_reaction = model_class(
                ec_number=ec_number,
                value=reaction,
                reversibility=reversibility,
                organisms=organisms,
                references=references,
                comment=item.get("comment") or None,
                substrates=substrates,
                products=products,
            )
            session.add(nsp_reaction)

    def __import_items_with_compound(
        self, session: Session, ec_number: str, items: List[Dict], model_class
    ):
        for item in items:
            # Get deduplicated organisms and references
            organisms = self.__get_organisms(item)
            references = self.__get_references(item)

            compound: Compound = self.__get_or_create_compound(
                session, item.get("value")
            )

            obj = model_class(
                ec_number=ec_number,
                compound_id=compound.id,
                organisms=organisms,
                references=references,
                comment=item.get("comment") or None,
            )
            session.add(obj)

    def __import_items_only_comment(
        self, session: Session, ec_number: str, items: List[Dict], model_class
    ):
        for item in items:
            organisms = self.__get_organisms(item)
            references = self.__get_references(item)
            obj = model_class(
                ec_number=ec_number,
                comment=item.get("comment") or None,
                organisms=organisms,
                references=references,
            )
            session.add(obj)

    def __import_items_with_float_value_and_compounds(
        self, session: Session, ec_number: str, items: List[Dict], model_class
    ):
        for item in items:
            # Get deduplicated organisms and references
            organisms = self.__get_organisms(item)
            references = self.__get_references(item)

            value_comp = re.search(
                r"^(?P<value>(-?\d+(\.\d+)?)|(\d+(\.\d+)?e-\d+))(\s*-\s*(?P<value_max>(-?\d+(\.\d+)?)|(\d+(\.\d+)?e-\d+)))?\s+\{(?P<compound_name>.*)\}$",
                item.get("value", ""),
            )
            if value_comp:
                value = value_comp.group("value")
                value = float(value) if value is not None else None
                value_max = value_comp.group("value_max")
                value_max = float(value_max) if value_max is not None else None
                compound_name = value_comp.group("compound_name")
                compound = self.__get_or_create_compound(session, compound_name)

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
            else:
                raise ValueError(
                    f"Invalid format for item value with compound: {item.get('value', '')}"
                )

    def __import_items_with_with_float_values(
        self, session: Session, ec_number: str, items: List[Dict], model_class
    ):
        for item in items:
            # Get deduplicated organisms and references
            organisms = self.__get_organisms(item)
            references = self.__get_references(item)

            value_comp = re.search(
                r"^(?P<value>(-?\d+(\.\d+)?)|(\d+(\.\d+)?e-\d+))(\s*-\s*(?P<value_max>(-?\d+(\.\d+)?)|(\d+(\.\d+)?e-\d+)))?$",
                item.get("value", ""),
            )
            if value_comp:
                value = value_comp.group("value")
                value = float(value) if value is not None else None
                value_max = value_comp.group("value_max")
                value_max = float(value_max) if value_max is not None else None

                obj = model_class(
                    ec_number=ec_number,
                    value=value,
                    value_max=value_max,
                    organisms=organisms,
                    references=references,
                    comment=item.get("comment") or None,
                )
                session.add(obj)
            else:
                raise ValueError(
                    f"Invalid format for item value with float values: {item.get('value', '')}"
                )

    def __import_complex_items(
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
            organisms = self.__get_organisms(item)
            references = self.__get_references(item)

            obj = model_class(
                ec_number=ec_number,
                value=item.get("value", ""),
                organisms=organisms,
                references=references,
                comment=item.get("comment") or None,
            )
            session.add(obj)

    def __update_compound_inchi_chebi(self) -> Dict[str, int]:
        """Download compound InChI and ChEBI IDs from BRENDA and updates the database."""
        logger.info(
            "Download compound InChI and ChEBI IDs from BRENDA and updates the database."
        )
        models.CompInchiChebi.__table__.drop(self.engine, checkfirst=True)  # type: ignore
        models.CompInchiChebi.__table__.create(self.engine, checkfirst=True)  # type: ignore
        path_to_mapping_file = os.path.join(DATA_FOLDER, LIGAND_INCHI_CHEBI_FILE)

        # download file if not exists
        if not os.path.exists(path_to_mapping_file):
            urlretrieve(LIGAND_INCHI_CHEBI_URL, path_to_mapping_file)

        # load BRENDA ligands
        df = pd.read_csv(
            path_to_mapping_file,
            sep="\t",
            header=None,
            usecols=[0, 2, 3],  # Select only relevant columns
            names=["compound_name", "inchi", "chebi_id"],
            encoding="latin-1",  # Use latin-1 encoding to handle special characters
            index_col=False,
        ).drop_duplicates()
        # filter the dataframe with inchi !='-' or chebi_id != '-'
        df = df[(df["inchi"] != "-") | (df["chebi_id"] != "-")]
        df.replace("-", pd.NA, inplace=True)
        df.chebi_id = df.chebi_id.str.lstrip("CHEBI:").astype("Int64", errors="ignore")
        df.index += 1
        df.index.rename("id", inplace=True)
        df.to_sql(models.CompInchiChebi.__tablename__, self.engine, if_exists="append")

        with self.Session.begin() as session:
            # update the inchikeys in the compound (Compound) table with inchikeys in comp_inchi_chebi table (CompInchiChebi)
            stmt = (
                update(Compound)
                .where(Compound.name == CompInchiChebi.compound_name)
                .values(inchi=CompInchiChebi.inchi, chebi_id=CompInchiChebi.chebi_id)
            )
            session.execute(stmt)
        return {"comp_inchi_chebi": df.shape[0]}

    def __update_brenda_ligand_ids(self) -> Dict[str, int]:
        """Download and import BRENDA ligands.

        BRENDA ligand = BRENDA compound to use the same terminology as ChEBI.
        """
        logger.info("Import BRENDA ligands")
        models.CompLigChebi.__table__.drop(self.engine, checkfirst=True)  # type: ignore
        models.CompLigChebi.__table__.create(self.engine, checkfirst=True)  # type: ignore
        path_to_mapping_file = os.path.join(DATA_FOLDER, LIGAND_CHEBI_MAPPING_FILE)

        # download file if not exists
        if not os.path.exists(path_to_mapping_file):
            urlretrieve(LIGAND_CHEBI_MAPPING_URL, path_to_mapping_file)
        columns = ["compound_name", "brenda_ligand_id", "chebi_id"]

        # load BRENDA ligands
        df = pd.read_csv(
            path_to_mapping_file,
            sep="\t",
            encoding="ISO-8859-1",
            usecols=[0, 1, 2],
            names=columns,
        ).drop_duplicates()

        df.replace("-", np.nan, inplace=True)
        df.chebi_id = df.chebi_id.str.lstrip("CHEBI:").astype("Int64", errors="ignore")

        df.index += 1
        df.index.rename("id", inplace=True)
        df.sort_index().to_sql(
            models.CompLigChebi.__tablename__, self.engine, if_exists="append"
        )

        with self.Session.begin() as session:
            # update brenda_ligand_id in the compound (Compound) table with brenda_ligand_id in comp_lig_chebi table (CompLigChebi)
            stmt = (
                update(Compound)
                .where(Compound.name == CompLigChebi.compound_name)
                .values(brenda_ligand_id=CompLigChebi.brenda_ligand_id)
            )
            session.execute(stmt)

        return {"comp_lig_chebi": df.shape[0]}

    def __download_taxdmp(self, path_to_file: str):
        """Download the NCBI taxdump file."""
        if not os.path.exists(path_to_file):
            logger.info("Download taxonomy data")
            r = requests.get(
                TAXONOMY_URL,
                allow_redirects=True,
            )
            open(path_to_file, "wb").write(r.content)

    def __import_tax_names(self):
        """Import the taxonomy names.

        Returns:
            Dict[str, int]: table name, number of entries
        """
        logger.info("import taxonomy names (up to 5min)")
        TaxonomyName.__table__.drop(self.engine, checkfirst=True)  # type: ignore
        TaxonomyName.__table__.create(self.engine, checkfirst=True)  # type: ignore
        os.makedirs(TAXONOMY_DATA_FOLDER, exist_ok=True)
        taxtree_path_to_file = os.path.join(TAXONOMY_DATA_FOLDER, "taxdmp.zip")
        self.__download_taxdmp(taxtree_path_to_file)
        archive = zipfile.ZipFile(taxtree_path_to_file, "r")
        names = archive.read("names.dmp")
        df = pd.read_csv(
            io.StringIO(names.decode("utf-8")),
            sep=r"\t\|\t",
            engine="python",
            usecols=[0, 1, 3],
            names=["tax_id", "name", "name_type"],
        )
        df.name_type = df.name_type.str[:-2]
        df.index += 1
        df.index.rename("id", inplace=True)
        df.to_sql(
            TaxonomyName.__tablename__, self.engine, if_exists="append", chunksize=10000
        )

    def __update_organism_tax_ids(self):
        """Update the tax_ids in the organism table.

        This method performs a multi-step process to assign taxonomy IDs to organisms:
        1. Imports taxonomy names if not already present
        2. Matches organisms to tax IDs via exact scientific name match
        3. Matches organisms to tax IDs via any name match
        4. For organisms ending with "sp.", matches to genus/family level
        5. For remaining organisms, splits binomial names and matches to genus level
        Note: This process can take up to 5 minutes to complete.

        """
        logger.info("Update tax_ids in organism table (up to 5min)")
        self.__import_tax_names()

        with self.Session() as session:
            stmt = (
                update(Organism)
                .where(
                    Organism.name == TaxonomyName.name,
                    TaxonomyName.name_type == "scientific name",
                    Organism.tax_id.is_(None),
                )
                .values(tax_id=TaxonomyName.tax_id)
            )
            session.execute(stmt)
            session.commit()
            stmt = (
                update(Organism)
                .where(
                    Organism.name == TaxonomyName.name,
                    Organism.tax_id.is_(None),
                )
                .values(tax_id=TaxonomyName.tax_id)
            )
            session.execute(stmt)
            session.commit()
            # search for all organisms without tax_id and sp. at the end of the name
            # sp. means species, so we can't assign a tax_id to the family/genus level
            species_names = (
                session.query(Organism.name)
                .filter(Organism.tax_id.is_(None), Organism.name.like("%% sp."))
                .all()
            )
            for (name,) in species_names:
                base_name = name[:-4]
                tax_id_sq = (
                    select(TaxonomyName.tax_id)
                    .where(
                        TaxonomyName.name == base_name,
                    )
                    .limit(1)
                    .scalar_subquery()
                )
                stmt = (
                    update(Organism)
                    .where(
                        Organism.name == name,
                        Organism.tax_id.is_(None),
                    )
                    .values(tax_id=tax_id_sq)
                )
                session.execute(stmt)
                session.commit()
            # finally, update any remaining organisms without tax_id, by splitting the name in family and species name
            for (name,) in (
                session.query(Organism.name).filter(Organism.tax_id.is_(None)).all()
            ):
                if " " in name:
                    base_name = name.split(" ")[0]
                    tax_id_sq = (
                        select(TaxonomyName.tax_id)
                        .where(
                            TaxonomyName.name == base_name,
                        )
                        .limit(1)
                        .scalar_subquery()
                    )
                    stmt = (
                        update(Organism)
                        .where(
                            Organism.name == name,
                            Organism.tax_id.is_(None),
                        )
                        .values(tax_id=tax_id_sq)
                    )
                    session.execute(stmt)
                    session.commit()

    def __update_chebi_ids_with_chebi(self):
        """Update chebi_ids in the compound table using ChEBI data."""
        logger.info("Update chebi_ids in the compound table using ChEBI data.")
        models.ChebiName.__table__.drop(self.engine, checkfirst=True)  # type: ignore
        models.ChebiName.__table__.create(self.engine, checkfirst=True)  # type: ignore
        pd.read_csv(
            CHEBI_NAMES_URL,
            sep="\t",
            compression="gzip",
            usecols=["id", "ascii_name"],
        ).rename(columns={"ascii_name": "name", "id": "chebi_id"}).to_sql(
            models.ChebiName.__tablename__, self.engine, if_exists="append", index=False
        )

        with self.Session.begin() as session:
            # update chebi_id in the compound (Compound) table
            # with chebi_id in chebi_name table (ChebiName)
            stmt = (
                update(Compound)
                .where(
                    Compound.name == models.ChebiName.name, Compound.chebi_id.is_(None)
                )
                .values(chebi_id=models.ChebiName.id)
            )
            session.execute(stmt)

    def __update_inchi_by_chebi_id(self):
        """Update inchis in the compound table using ChEBI data."""
        logger.info("Update inchis in the compound table using ChEBI data.")
        models.ChebiInchi.__table__.drop(self.engine, checkfirst=True)  # type: ignore
        models.ChebiInchi.__table__.create(self.engine, checkfirst=True)  # type: ignore
        df = pd.read_csv(
            CHEBI_INCHI_URL,
            sep="\t",
            compression="gzip",
            usecols=["standard_inchi", "id"],
        ).rename(columns={"standard_inchi": "inchi", "id": "chebi_id"})
        # delete all where inchi is null
        df[df["inchi"].notna()].to_sql(
            models.ChebiInchi.__tablename__,
            self.engine,
            if_exists="append",
            index=False,
        )
        with self.Session.begin() as session:
            # update chebi_id in the compound (Compound) table with chebi_id in chebi_name table (ChebiName)
            logger.info("Update inchis in compound table using ChEBI InChI data")
            stmt = (
                update(Compound)
                .where(
                    Compound.chebi_id == models.ChebiInchi.chebi_id,
                    Compound.inchi.is_(None),
                )
                .values(inchi=models.ChebiInchi.inchi)
            )
            session.execute(stmt)

            logger.info("Update chebi_ids in compound table using ChEBI InChI data")
            stmt = (
                update(Compound)
                .where(
                    Compound.inchi == models.ChebiInchi.inchi,
                    Compound.chebi_id.is_(None),
                )
                .values(chebi_id=models.ChebiInchi.chebi_id)
            )
            session.execute(stmt)

    def __update_inchi_keys(self):
        """Update inchikeys in the compound table using RDKit."""
        logger.info("Update inchikeys in compound table using RDKit")
        with self.Session.begin() as session:
            logger.info("Update inchikeys in compound table using RDKit")
            compounds = session.query(Compound).filter(Compound.inchi.isnot(None)).all()
            for compound in tqdm(compounds, desc="Updating InChIKeys"):
                try:
                    mol = Chem.MolFromInchi(compound.inchi)
                    if mol:
                        inchikey = Chem.MolToInchiKey(mol)
                        compound.inchi_key = inchikey
                except Exception as e:
                    logger.warning(
                        f"Failed to process InChI for compound {compound.name}: {e}"
                    )
