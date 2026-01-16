"""Module to create RDF turtle files from the BRENDA imported data."""

import io
import logging
import os.path
import re
import shutil
import sqlite3
import zipfile
from typing import List, Type, TypeVar, Union
from urllib.parse import urlparse
from urllib.request import urlretrieve

import numpy as np
import pandas as pd
from pandas import DataFrame
from rdflib import RDF, XSD, Graph, Literal, Namespace, URIRef
from sqlalchemy import Engine, create_engine, event, inspect
from sqlalchemy.orm import Session, sessionmaker
from tqdm import tqdm

logger = logging.getLogger(__name__)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(
    dbapi_connection: sqlite3.Connection, _connection_record: object
) -> None:
    """Enable foreign key constraint for SQLite."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


from biokb_brenda import constants
from biokb_brenda.constants import (
    BASIC_NODE_LABEL,
    DATA_FOLDER,
    EXPORT_FOLDER,
    TAXONOMY_URL,
)
from biokb_brenda.db import models
from biokb_brenda.rdf import namespaces

BaseModels = TypeVar("BaseModels", bound=models.Base)


def get_namespace(model: Type[models.Base]) -> Namespace:
    """Return the RDF namespace for a given SQLAlchemy model.

    Args:
        model: A SQLAlchemy declarative model class.

    Returns:
        Namespace: An `rdflib` Namespace rooted at
        `"{namespaces.BASE_URI}/{ModelName}#"`.
    """
    return Namespace(f"{namespaces.BASE_URI}/{model.__name__}#")


def get_empty_graph():
    """Create a pre-configured empty RDF graph.

    Returns:
        Graph: An `rdflib.Graph` instance with all required namespaces bound.
    """
    graph = Graph()
    graph.bind(prefix="chebi", namespace=namespaces.CHEBI_NS)
    graph.bind(prefix="node", namespace=namespaces.NODE_NS)
    graph.bind(prefix="rel", namespace=namespaces.RELATION_NS)
    graph.bind(prefix="xs", namespace=XSD)
    graph.bind(prefix="ec", namespace=namespaces.EC_NS)
    graph.bind(prefix="reac", namespace=get_namespace(models.Reaction))
    graph.bind(prefix="tax", namespace=namespaces.NCBI_TAXON_NS)
    graph.bind(prefix="ac", namespace=get_namespace(models.ActivatingCompound))
    graph.bind(prefix="cf", namespace=get_namespace(models.Cofactor))
    graph.bind(prefix="ic", namespace=get_namespace(models.IC50Value))
    graph.bind(prefix="kt", namespace=get_namespace(models.KcatKmValue))
    graph.bind(prefix="ki", namespace=get_namespace(models.KiValue))
    graph.bind(prefix="km", namespace=get_namespace(models.KmValue))
    graph.bind(prefix="cm", namespace=namespaces.COMPOUND_NS)
    graph.bind(prefix="lc", namespace=get_namespace(models.Localization))
    graph.bind(prefix="mi", namespace=get_namespace(models.MetalIon))
    graph.bind(prefix="ns", namespace=get_namespace(models.NSPReaction))
    graph.bind(prefix="sp", namespace=get_namespace(models.SPReaction))
    graph.bind(prefix="ik", namespace=namespaces.INCHI_NS)
    graph.bind(prefix="gi", namespace=get_namespace(models.GeneralInformation))
    graph.bind(prefix="ih", namespace=get_namespace(models.Inhibitor))
    graph.bind(prefix="pr", namespace=get_namespace(models.Protein))

    return graph


def get_rel_name(model: Type[models.Base]) -> str:
    """Convert a model class name to a relationship name.

    The format is uppercase snake case prefixed with ``HAS_``.

    Args:
        model: A SQLAlchemy model class.

    Returns:
        str: Relationship name in the form ``HAS_<UPPERCASE_WITH_UNDERSCORES>``.

    Examples:
        >>> get_rel_name(UserProfile)
        'HAS_USER_PROFILE'
    """

    name = model.__name__
    for match in re.findall(r"([A-Z]{2}[a-z])", name):
        name = f"{match[0]}_{match[1:]}".join(name.split(match))
    for match in re.findall(r"([a-z][A-Z])", name):
        name = f"{match[0]}_{match[1]}".join(name.split(match))
    return "HAS_" + name.upper()


def recursive_get_parents(
    df_tree: DataFrame, parent_id: int, tax_ids: set[int] = set()
) -> set[int]:
    """Collect all parent taxonomy IDs up to the root.

    Note: ``tax_ids`` is used as an accumulator.

    Args:
        df_tree: DataFrame mapping ``tax_id`` to ``parent_tax_id`` (indexed by ``tax_id``).
        parent_id: Starting taxonomy ID.
        tax_ids: Mutable accumulator set of collected taxonomy IDs.

    Returns:
        set[int]: The full lineage (including the starting ``parent_id``).
    """
    tax_ids.add(parent_id)
    current_id = df_tree.loc[parent_id, "parent_tax_id"]
    if parent_id != current_id and isinstance(current_id, np.integer):
        recursive_get_parents(
            df_tree=df_tree,
            parent_id=int(current_id),
            tax_ids=tax_ids,
        )
    return tax_ids


class TurtleCreator:
    def __init__(
        self,
        engine: Engine | None = None,
        export_to_folder: str | None = None,
        data_folder: str | None = None,
    ):
        """Initialize the creator used to generate RDF Turtle files.

        Args:
            engine: Optional SQLAlchemy ``Engine``. If ``None``, a new engine
                is created from ``DATABASE_URL`` or the default in constants.
            export_to_folder: Optional base folder to write output; a ``ttls``
                subfolder will be created inside it. Defaults to ``EXPORT_FOLDER``.
            data_folder: Optional folder containing required external data (e.g.,
                NCBI taxonomy archive). Defaults to ``DATA_FOLDER``.

        Raises:
            FileExistsError: If ``data_folder`` is provided but does not exist.
            Exception: If ``data_folder`` exists but is missing the required
                taxonomy archive file.
        """
        if export_to_folder:
            ttls_folder = os.path.join(export_to_folder, "ttls")
            self.__ttls_folder = ttls_folder
        else:
            self.__ttls_folder = EXPORT_FOLDER
        if not os.path.exists(self.__ttls_folder):
            os.makedirs(self.__ttls_folder)

        if data_folder:
            if os.path.exists(data_folder):
                taxonomy_file_name = os.path.basename(urlparse(TAXONOMY_URL).path)
                if taxonomy_file_name not in os.listdir(data_folder):
                    raise Exception(
                        f"Make sure {taxonomy_file_name} is in {data_folder}"
                    )
                self.__data_folder = data_folder
            else:
                raise FileExistsError(f"Data folder {data_folder} not exists")
        else:
            self.__data_folder = DATA_FOLDER

        connection_str = os.getenv("DATABASE_URL", constants.DB_DEFAULT_CONNECTION_STR)
        self.__engine = engine if engine else create_engine(str(connection_str))
        self.Session: sessionmaker[Session] = sessionmaker(bind=self.__engine)

    def create_ttls(self) -> str:
        """Generate all RDF Turtle files and return the ZIP path.

        This orchestrates generation for enzymes, proteins, compounds, reactions,
        cross-references, and standard tables, then zips the resulting Turtle
        files and removes the temporary folder.

        Returns:
            str: Absolute path to the generated ZIP archive containing all TTLs.
        """
        logging.info("Start creating turtle files.")
        self.__create_enzyme_nodes()
        self.__create_proteins()
        self.__create_compound()
        self.__create_compound_same_as_chebi()
        self.__create_compound_same_as_inchi()
        self.__create_reactions()
        self.__create_sp_reaction()
        self.__create_nsp_reaction()
        self.__create_compound_reaction_links()
        # self.create_taxonomy() # Not needed as we use biokb_taxtree
        self.__create_standard_ttls()
        path_to_zip_file: str = self.__create_zip_from_all_ttls()
        logging.info(f"Turtle files zipped in {path_to_zip_file} .")
        return path_to_zip_file

    def link_organisms(self, graph, model_instance, node):
        """Link a node to organism taxonomy entries when available.

        Args:
            graph: The RDF graph to add triples to.
            model_instance: An instance that exposes an ``organisms`` relationship.
            node: The subject node (URIRef) to link from.
        """
        organism: models.Organism
        for organism in model_instance.organisms:
            if organism.tax_id:
                graph.add(
                    triple=(
                        node,
                        namespaces.RELATION_NS[get_rel_name(models.Organism)],
                        namespaces.NCBI_TAXON_NS[str(int(organism.tax_id))],
                    )
                )

    def __create_standard_ttl(
        self,
        model: Union[
            models.IC50Value,
            models.KcatKmValue,
            models.KiValue,
            models.KmValue,
            models.Localization,
            models.GeneralInformation,
            models.ActivatingCompound,
            models.MetalIon,
            models.Inhibitor,
        ],
    ):
        """Create an RDF Turtle file for a standard table model.

        This converts all rows of the given model to RDF triples, linking to
        EC numbers and optional organisms/compounds, then serializes to a TTL
        file named ``{model.__tablename__}.ttl`` under the output folder.

        Args:
            model: One of the supported standard models (e.g., ``IC50Value``,
                ``KcatKmValue``, ``KiValue``, ``KmValue``, ``Localization``,
                ``GeneralInformation``, ``ActivatingCompound``, ``MetalIon``,
                ``Inhibitor``).

        Raises:
            Exception: Propagated from database access or file serialization
                if issues occur.
        """
        logging.info(f"Create RDF turtle file for {model.__tablename__}.")
        graph: Graph = get_empty_graph()

        with self.Session() as session:
            records = session.query(model).all()  # type: ignore

            for row in tqdm(records, desc=f"Creating {model.__tablename__} entries"):
                ec_node: URIRef = namespaces.EC_NS[str(row.ec_number)]
                namespace: Namespace = get_namespace(model)  # type: ignore
                n: URIRef = namespace[str(row.id)]
                graph.add(triple=(n, RDF.type, namespaces.NODE_NS[model.__name__]))
                graph.add(triple=(n, RDF.type, namespaces.NODE_NS[BASIC_NODE_LABEL]))
                graph.add((ec_node, namespaces.RELATION_NS[get_rel_name(model)], n))  # type: ignore

                attrs = inspect(model).attrs.keys()

                if "comment" in attrs:
                    graph.add(
                        triple=(
                            n,
                            namespaces.RELATION_NS["comment"],
                            Literal(row.comment, datatype=XSD.string),
                        )
                    )

                if "organisms" in attrs:
                    for organism in row.organisms:
                        if organism.tax_id:
                            graph.add(
                                triple=(
                                    n,
                                    namespaces.RELATION_NS[
                                        get_rel_name(models.Organism)
                                    ],
                                    namespaces.NCBI_TAXON_NS[str(int(organism.tax_id))],
                                )
                            )

                if "value" in attrs:
                    datatype = XSD.string
                    if isinstance(row.value, float):
                        datatype = XSD.float
                    graph.add(
                        triple=(
                            n,
                            namespaces.RELATION_NS["value"],
                            Literal(row.value, datatype=datatype),
                        )
                    )

                if "value_max" in attrs and row.value_max is not None:
                    graph.add(
                        triple=(
                            n,
                            namespaces.RELATION_NS["value_max"],
                            Literal(row.value_max, datatype=XSD.float),
                        )
                    )

                if (
                    "compound" in attrs
                    and row.compound
                    and row.compound.brenda_ligand_id
                ):
                    graph.add(
                        triple=(
                            n,
                            namespaces.RELATION_NS[get_rel_name(models.Compound)],
                            namespaces.COMPOUND_NS[
                                str(int(row.compound.brenda_ligand_id))
                            ],
                        )
                    )

        ttl_path = os.path.join(self.__ttls_folder, f"{model.__tablename__}.ttl")
        graph.commit()
        graph.serialize(ttl_path, format="turtle")
        del graph

    def __create_enzyme_nodes(self):
        """Create RDF nodes for all enzyme classes in the database.

        Writes ``brenda_enzyme_class.ttl`` with EC nodes and labels.
        """
        logging.info("Create RDF enzyme turtle file.")
        graph = get_empty_graph()

        with self.Session() as session:
            enzymes = session.query(
                models.EnzymeClass.ec_number,
                models.EnzymeClass.systematic_name,
                models.EnzymeClass.recommended_name,
            ).all()

            for enzyme in tqdm(enzymes, desc="Creating enzyme nodes"):
                subject: URIRef = namespaces.EC_NS[str(enzyme.ec_number)]
                graph.add(
                    triple=(
                        subject,
                        RDF.type,
                        namespaces.NODE_NS[models.EnzymeClass.__name__],
                    )
                )
                graph.add(
                    triple=(subject, RDF.type, namespaces.NODE_NS[BASIC_NODE_LABEL])
                )

                for column in ["systematic_name", "recommended_name", "ec_number"]:
                    graph.add(
                        triple=(
                            subject,
                            namespaces.RELATION_NS[column],
                            Literal(
                                lexical_or_value=getattr(enzyme, column),
                                datatype=XSD.string,
                            ),
                        )
                    )

        ttl_path = os.path.join(self.__ttls_folder, "brenda_enzyme_class.ttl")
        graph.serialize(ttl_path, format="turtle")
        del graph

    def __create_proteins(self):
        """Create RDF turtle file for proteins.

        Produces ``brenda_protein.ttl`` linking proteins to EC and organisms.
        """

        logging.info("Create RDF protein turtle file.")

        graph = get_empty_graph()
        with self.Session() as session:
            proteins: List[models.Protein] = session.query(models.Protein).all()

            for p in tqdm(tqdm(proteins), desc="Creating proteins"):
                namespace: Namespace = get_namespace(models.Protein)
                protein: URIRef = namespace[str(p.id)]
                graph.add(
                    triple=(
                        protein,
                        RDF.type,
                        namespaces.NODE_NS[models.Protein.__name__],
                    )
                )
                graph.add(
                    triple=(protein, RDF.type, namespaces.NODE_NS[BASIC_NODE_LABEL])
                )
                enzyme_class: URIRef = namespaces.EC_NS[str(p.ec_number)]
                graph.add(
                    (
                        enzyme_class,
                        namespaces.RELATION_NS[get_rel_name(models.Protein)],
                        protein,
                    )
                )
                organism = session.get(models.Organism, p.organism_id)
                if organism and organism.tax_id:
                    graph.add(
                        (
                            protein,
                            namespaces.RELATION_NS[get_rel_name(models.Organism)],
                            namespaces.NCBI_TAXON_NS[str(organism.tax_id)],
                        )
                    )
        ttl_path = os.path.join(self.__ttls_folder, "brenda_protein.ttl")
        graph.serialize(ttl_path, format="turtle")
        del graph

    def __create_reactions(self):
        """Create RDF turtle file for EC reactions.

        Produces ``brenda_reaction_ec.ttl`` with reaction nodes and labels.
        """
        logging.info("Create RDF reaction turtle file.")

        graph = get_empty_graph()
        with self.Session() as session:
            reactions: List[models.Reaction] = session.query(models.Reaction).all()

            for reaction in tqdm(reactions, desc="Creating reactions"):
                namespace = get_namespace(models.Reaction)
                subject: URIRef = namespace[str(reaction.id)]
                graph.add(
                    triple=(
                        subject,
                        RDF.type,
                        namespaces.NODE_NS[models.Reaction.__name__],
                    )
                )
                graph.add(
                    triple=(subject, RDF.type, namespaces.NODE_NS[BASIC_NODE_LABEL])
                )
                enzyme_class: URIRef = namespaces.EC_NS[str(reaction.ec_number)]
                graph.add(
                    (
                        enzyme_class,
                        namespaces.RELATION_NS[get_rel_name(models.Reaction)],
                        subject,
                    )
                )
                graph.add(
                    triple=(
                        subject,
                        namespaces.RELATION_NS["reaction"],
                        Literal(lexical_or_value=reaction.value, datatype=XSD.string),
                    )
                )
        ttl_path = os.path.join(self.__ttls_folder, "brenda_reaction_ec.ttl")
        graph.serialize(ttl_path, format="turtle")
        del graph

    def __create_substrate_product_nodes(
        self,
        reaction: models.Reaction | models.SPReaction | models.NSPReaction,
        reac_node: URIRef,
        graph: Graph,
    ):
        """Add substrate and product edges for a reaction node.

        Args:
            reaction: Reaction instance (EC, SP, or NSP).
            reac_node: Subject node representing the reaction.
            graph: RDF graph where triples are added.
        """
        for substrate in reaction.substrates:
            if substrate.brenda_ligand_id:
                graph.add(
                    triple=(
                        reac_node,
                        namespaces.RELATION_NS["HAS_SUBSTRATE"],
                        namespaces.COMPOUND_NS[str(int(substrate.brenda_ligand_id))],
                    )
                )
        for product in reaction.products:
            if product.brenda_ligand_id:
                graph.add(
                    triple=(
                        reac_node,
                        namespaces.RELATION_NS["HAS_PRODUCT"],
                        namespaces.COMPOUND_NS[str(int(product.brenda_ligand_id))],
                    )
                )

    def __create_sp_reaction(self):
        """Create RDF turtle file for substrate/product reactions.

        Produces ``brenda_reaction_sp.ttl`` with SP reaction nodes, their
        properties, substrates, products, organisms, and EC links.
        """
        logging.info("Create RDF substrate and reaction turtle file.")
        graph = get_empty_graph()

        with self.Session() as session:
            sp_reactions = session.query(models.SPReaction).all()

            for reaction in tqdm(sp_reactions, desc="Creating sp reactions"):
                namespace = get_namespace(models.SPReaction)
                sp_reac_node: URIRef = namespace[str(reaction.id)]
                graph.add(
                    triple=(
                        sp_reac_node,
                        RDF.type,
                        namespaces.NODE_NS[models.SPReaction.__name__],
                    )
                )
                graph.add(
                    triple=(
                        sp_reac_node,
                        RDF.type,
                        namespaces.NODE_NS[BASIC_NODE_LABEL],
                    )
                )
                enzyme_class: URIRef = namespaces.EC_NS[str(reaction.ec_number)]
                graph.add(
                    (
                        enzyme_class,
                        namespaces.RELATION_NS[get_rel_name(models.SPReaction)],
                        sp_reac_node,
                    )
                )
                for col in ["comment", "reversibility", "value"]:
                    if not pd.isna(getattr(reaction, col)):
                        graph.add(
                            triple=(
                                sp_reac_node,
                                namespaces.RELATION_NS[col],
                                Literal(getattr(reaction, col), datatype=XSD.string),
                            )
                        )

                self.__create_substrate_product_nodes(reaction, sp_reac_node, graph)

                self.link_organisms(graph, reaction, sp_reac_node)

        ttl_path = os.path.join(self.__ttls_folder, "brenda_reaction_sp.ttl")
        graph.serialize(ttl_path, format="turtle")
        del graph

    def __create_nsp_reaction(self):
        """Create RDF turtle file for natural substrate/product reactions.

        Produces ``nsp_reaction.ttl`` with NSP reaction nodes, their
        properties, organisms, and EC links.
        """
        logging.info("Create RDF Natural substrate and product reaction turtle file.")
        graph = get_empty_graph()
        with self.Session() as session:
            nsp_reactions = session.query(models.NSPReaction).all()

            for nsp_reaction in tqdm(nsp_reactions, desc="Creating nsp reactions"):
                namespace = get_namespace(models.NSPReaction)
                nsp_reac_node: URIRef = namespace[str(nsp_reaction.id)]
                graph.add(
                    triple=(
                        nsp_reac_node,
                        RDF.type,
                        namespaces.NODE_NS[models.NSPReaction.__name__],
                    )
                )
                graph.add(
                    triple=(
                        nsp_reac_node,
                        RDF.type,
                        namespaces.NODE_NS[BASIC_NODE_LABEL],
                    )
                )
                enzyme_class: URIRef = namespaces.EC_NS[str(nsp_reaction.ec_number)]
                graph.add(
                    (
                        enzyme_class,
                        namespaces.RELATION_NS[get_rel_name(models.NSPReaction)],
                        nsp_reac_node,
                    )
                )
                for col in ["comment", "reversibility", "value"]:
                    if not pd.isna(getattr(nsp_reaction, col)):
                        graph.add(
                            triple=(
                                nsp_reac_node,
                                namespaces.RELATION_NS[col],
                                Literal(
                                    getattr(nsp_reaction, col), datatype=XSD.string
                                ),
                            )
                        )

                self.link_organisms(graph, nsp_reaction, nsp_reac_node)
        ttl_path = os.path.join(
            self.__ttls_folder, f"{models.NSPReaction.__tablename__}.ttl"
        )
        graph.serialize(ttl_path, format="turtle")
        del graph

    def __create_compound(self):
        """Create RDF turtle file for compounds.

        Produces ``compound.ttl`` with BRENDA ligand compounds and names.
        """
        logging.info("Create RDF compound turtle file.")
        graph: Graph = get_empty_graph()
        with self.Session() as session:
            compounds = (
                session.query(models.Compound.brenda_ligand_id, models.Compound.name)
                .where(models.Compound.brenda_ligand_id.isnot(None))
                .group_by(models.Compound.brenda_ligand_id)
                .all()
            )

            for comp in tqdm(compounds, desc="Creating compounds"):
                if comp.brenda_ligand_id:

                    compound: URIRef = namespaces.COMPOUND_NS[
                        str(int(comp.brenda_ligand_id))
                    ]
                    graph.add(
                        (
                            compound,
                            RDF.type,
                            namespaces.NODE_NS[models.Compound.__name__],
                        )
                    )
                    graph.add(
                        (compound, RDF.type, namespaces.NODE_NS[BASIC_NODE_LABEL])
                    )
                    graph.add(
                        triple=(
                            compound,
                            namespaces.RELATION_NS["name"],
                            Literal(comp.name, datatype=XSD.string),
                        )
                    )

        ttl_path = os.path.join(
            self.__ttls_folder, f"{models.Compound.__tablename__}.ttl"
        )
        graph.serialize(ttl_path, format="turtle")
        del graph

    def __create_compound_same_as_chebi(self):
        """Create RDF links mapping compounds to ChEBI identifiers.

        Produces ``brenda_compound_same_as_chebi.ttl`` with ``SAME_AS`` edges
        from BRENDA compounds to matching ChEBI entries.
        """
        logging.info("Read compound same as chebi links")
        graph: Graph = get_empty_graph()
        with self.Session() as session:
            compounds = (
                session.query(
                    models.Compound.brenda_ligand_id, models.Compound.chebi_id
                )
                .where(
                    models.Compound.brenda_ligand_id.isnot(None),
                    models.Compound.chebi_id.isnot(None),
                )
                .group_by(models.Compound.brenda_ligand_id, models.Compound.chebi_id)
                .all()
            )

            for comp in tqdm(compounds, desc="Creating compound same as chebi links"):
                if comp.brenda_ligand_id:
                    compound: URIRef = namespaces.COMPOUND_NS[
                        str(int(comp.brenda_ligand_id))
                    ]
                    graph.add(
                        triple=(
                            compound,
                            namespaces.RELATION_NS["SAME_AS"],
                            namespaces.CHEBI_NS[str(int(comp.chebi_id))],
                        )
                    )

        ttl_path = os.path.join(self.__ttls_folder, "brenda_compound_same_as_chebi.ttl")
        graph.serialize(ttl_path, format="turtle")
        del graph

    def __create_compound_same_as_inchi(self):
        """Create RDF links mapping compounds to InChIKey identifiers.

        Produces ``brenda_compound_same_as_inchi.ttl`` with ``SAME_AS`` edges
        from BRENDA compounds to InChIKey URIs.
        """
        logging.info("Read compound same as inchi links")
        graph: Graph = get_empty_graph()
        with self.Session() as session:
            compounds = (
                session.query(
                    models.Compound.brenda_ligand_id, models.Compound.inchi_key
                )
                .where(
                    models.Compound.brenda_ligand_id.isnot(None),
                    models.Compound.inchi_key.isnot(None),
                )
                .group_by(models.Compound.brenda_ligand_id, models.Compound.inchi_key)
                .all()
            )

            for comp in tqdm(compounds, desc="Creating compound same as inchi links"):
                if comp.brenda_ligand_id:
                    compound: URIRef = namespaces.COMPOUND_NS[
                        str(int(comp.brenda_ligand_id))
                    ]
                    graph.add(
                        triple=(
                            compound,
                            namespaces.RELATION_NS["SAME_AS"],
                            namespaces.INCHI_NS[comp.inchi_key],
                        )
                    )

        ttl_path = os.path.join(self.__ttls_folder, "brenda_compound_same_as_inchi.ttl")
        graph.serialize(ttl_path, format="turtle")
        del graph

    def __create_compound_reaction_links(self):
        """Create RDF Turtle files linking compounds to reactions.

        For each reaction model (EC, SP, NSP), writes a TTL file with edges
        from reactions to their substrates and products.
        """
        logging.info("Create RDF compound-reaction link turtle files.")
        reaction_models = [models.Reaction, models.SPReaction, models.NSPReaction]
        for reaction_model in reaction_models:
            graph: Graph = get_empty_graph()
            logging.info(
                f"Create RDF substrate and product {reaction_model.__name__} nt file."
            )
            graph = get_empty_graph()
            with self.Session() as session:
                reactions = session.query(reaction_model).all()

                for reaction in tqdm(
                    reactions, desc=f"Creating {reaction_model.__name__.lower()}s"
                ):
                    namespace = get_namespace(reaction_model)
                    reac_node: URIRef = namespace[str(reaction.id)]
                    self.__create_substrate_product_nodes(reaction, reac_node, graph)

            ttl_path = os.path.join(
                self.__ttls_folder, f"{reaction_model.__tablename__}_compound_link.ttl"
            )
            graph.serialize(ttl_path, format="ttl", encoding="utf-8")
            del graph

    # TODO: Is this needed?
    def __create_taxonomy(self):
        """Create RDF taxonomy turtle file.

        Downloads and parses the NCBI taxonomy (if needed), builds the subset
        of nodes required by the BRENDA organisms present in the database, and
        serializes them to ``brenda_organism.ttl``.
        """
        logging.info("Create RDF taxonomy turtle file.")

        # download NCBI taxonomy if needed
        file_name = os.path.basename(urlparse(TAXONOMY_URL).path)
        taxdmp_path = os.path.join(self.__data_folder, file_name)

        if not os.path.exists(taxdmp_path):
            urlretrieve(TAXONOMY_URL, taxdmp_path)

        archive = zipfile.ZipFile(taxdmp_path, "r")

        # load nodes in Dataframe
        nodes = archive.read("nodes.dmp")
        df_tree = pd.read_csv(
            io.StringIO(nodes.decode("utf-8")),
            usecols=[0, 1],
            sep=r"\t\|\t",
            engine="python",
            names=["tax_id", "parent_tax_id"],
            index_col="tax_id",
        )

        # load names in Dataframe
        names_column_names = ["tax_id", "name_txt", "unique_name", "name_class"]
        names = archive.read("names.dmp")
        df_tax_names: DataFrame = pd.read_csv(
            io.StringIO(names.decode("utf-8")),
            sep=r"\t\|\t",
            engine="python",
            names=names_column_names,
            index_col="tax_id",
        )
        df_tax_names.name_class = df_tax_names.name_class.str.replace("\t|", "")
        df_names: DataFrame = df_tax_names[
            df_tax_names.name_class == "scientific name"
        ][["name_txt"]]

        with self.Session() as session:
            brenda_taxids = (
                session.query(models.Organism.tax_id)
                .where(models.Organism.tax_id.isnot(None))
                .distinct()
                .all()
            )
            brenda_taxids = [int(taxid[0]) for taxid in brenda_taxids]

        # get all needed tax ids (with parents), go up to the root
        needed_taxids: set[int] = set()
        for brenda_taxid in brenda_taxids:
            needed_taxids.update(
                recursive_get_parents(df_tree=df_tree, parent_id=brenda_taxid)
            )

        graph: Graph = get_empty_graph()
        for tax_id in needed_taxids:
            taxonomy_node: URIRef = namespaces.NCBI_TAXON_NS[str(tax_id)]
            graph.add(
                triple=(
                    taxonomy_node,
                    RDF.type,
                    namespaces.NODE_NS[models.Organism.__name__],
                )
            )
            graph.add(
                triple=(taxonomy_node, RDF.type, namespaces.NODE_NS["_NCBI_Taxonomy"])
            )
            name = df_names.loc[tax_id, "name_txt"]
            graph.add(
                triple=(
                    taxonomy_node,
                    namespaces.RELATION_NS["name"],
                    Literal(name, datatype=XSD.string),
                )
            )
            graph.add(
                triple=(
                    taxonomy_node,
                    namespaces.RELATION_NS["taxid"],
                    Literal(tax_id, datatype=XSD.integer),
                )
            )
            parent_tax_id = df_tree.loc[tax_id, "parent_tax_id"]
            if tax_id != parent_tax_id:
                parent_taxonomy_node: URIRef = namespaces.NCBI_TAXON_NS[
                    str(parent_tax_id)
                ]
                graph.add(
                    triple=(
                        taxonomy_node,
                        namespaces.RELATION_NS["HAS_PARENT"],
                        parent_taxonomy_node,
                    )
                )

        ttl_path: str = os.path.join(self.__ttls_folder, "brenda_organism.ttl")
        graph.serialize(destination=ttl_path, format="turtle")
        del graph

    def __create_standard_ttls(self):
        """Create RDF Turtle files for all supported standard models."""

        _models = [
            models.IC50Value,
            models.KcatKmValue,
            models.KiValue,
            models.KmValue,
            models.Localization,
            models.GeneralInformation,
            models.ActivatingCompound,
            models.MetalIon,
            models.Inhibitor,
            models.Cofactor,
        ]
        for _model in _models:
            logging.info(f"Creating turtle for { _model.__name__ }")
            self.__create_standard_ttl(_model)

        # self.create_standard_ttl(
        #     table="cofactor",
        #     node_label="CofactorInteraction",
        #     rel_name_1="has_cofactor_interaction",
        #     rel_name_2="has_cofactor",
        #     file_name_suffix="cofactor",
        #     namespace=namespaces.cofactor_ns,
        # )

    def __create_zip_from_all_ttls(self) -> str:
        """Zip all generated Turtle files and return the archive path.

        Returns:
            str: Absolute path to the created ZIP archive.
        """
        logger.info("Creating zip file from all turtle files.")
        path_to_zip_file = shutil.make_archive(
            base_name=self.__ttls_folder, format="zip", root_dir=self.__ttls_folder
        )
        shutil.rmtree(self.__ttls_folder)
        return path_to_zip_file
