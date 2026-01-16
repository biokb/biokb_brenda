"""Basic constants."""

import os.path
from os import makedirs
from pathlib import Path

# standard for all biokb projects, but individual set
PROJECT_NAME = "brenda"
BASIC_NODE_LABEL = "DbBRENDA"
# standard for all biokb projects
ORGANIZATION = "biokb"
LIBRARY_NAME = f"{ORGANIZATION}_{PROJECT_NAME}"
HOME = str(Path.home())
BIOKB_FOLDER = os.path.join(HOME, f".{ORGANIZATION}")
PROJECT_FOLDER = os.path.join(BIOKB_FOLDER, PROJECT_NAME)
DATA_FOLDER = os.path.join(PROJECT_FOLDER, "data")
EXPORT_FOLDER = os.path.join(DATA_FOLDER, "ttls")
ZIPPED_TTLS_PATH = os.path.join(DATA_FOLDER, "ttls.zip")
SQLITE_PATH = os.path.join(BIOKB_FOLDER, f"{ORGANIZATION}.db")
DB_DEFAULT_CONNECTION_STR = "sqlite:///" + SQLITE_PATH
NEO4J_PASSWORD = "neo4j_password"
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
LOGS_FOLDER = os.path.join(DATA_FOLDER, "logs")  # where to store log files
TABLE_PREFIX = PROJECT_NAME + "_"
os.makedirs(DATA_FOLDER, exist_ok=True)


# not standard for all biokb projects
DEFAULT_PATH_TO_DATA_FILE = os.path.join(DATA_FOLDER, "brenda.tar.gz")
DOWNLOAD_URL = "https://www.brenda-enzymes.org/download.php"


LIGAND_CHEBI_MAPPING_URL = "https://www.brenda-enzymes.org/result_download.php?a=13&RN=&RNV=1&os=1&pt=&FNV=1&tt=&SYN=&Textmining=&W[3]=%2A&T[3]=7&V[8]=1&nolimit=1"
LIGAND_CHEBI_MAPPING_FILE = "brenda_ligand_chebi_mapping.tsv"

LIGAND_INCHI_CHEBI_URL = "https://www.brenda-enzymes.org/result_download.php?a=13&RN=&RNV=&os=1&pt=&FNV=&tt=&SYN=1&Textmining=&W[1]=&T[1]=2&V[1]=1&W[2]=&T[2]=2&W[3]=%2A&T[3]=7&W[4]=&T[4]=2&W[6]=&T[6]=2&V[6]=1&W[8]=&T[8]=2&nolimit=1"
LIGAND_INCHI_CHEBI_FILE = "brenda_ligand_inchi.tsv"

TAXONOMY_URL = "https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdmp.zip"
TAXONOMY_DATA_FOLDER = os.path.join(BIOKB_FOLDER, "taxtree", "data")

BASE_URI = "https://biokb.scai.fraunhofer.de/brenda"
CHEBI_NAMES_URL = (
    "https://ftp.ebi.ac.uk/pub/databases/chebi/flat_files/compounds.tsv.gz"
)
CHEBI_INCHI_URL = (
    "https://ftp.ebi.ac.uk/pub/databases/chebi/flat_files/structures.tsv.gz"
)




