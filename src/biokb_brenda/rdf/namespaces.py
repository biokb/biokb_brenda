"""RDF namespace URIs."""

from rdflib import Namespace

from biokb_brenda2.constants import BASE_URI

CHEBI_NS = Namespace("http://purl.obolibrary.org/obo/CHEBI_")
NCBI_TAXON_NS = Namespace("http://purl.obolibrary.org/obo/NCBITaxon_")
INCHI_NS = Namespace("http://rdf.ncbi.nlm.nih.gov/pubchem/inchikey/")

# BRENDA URIs to Fraunhofer
NODE_NS = Namespace(f"{BASE_URI}/node#")
ACTIVATION_NS = Namespace(f"{BASE_URI}/activation#")
INHIBITION_NS = Namespace(f"{BASE_URI}/inhibition#")
COFACTOR_NS = Namespace(f"{BASE_URI}/cofactor_interaction#")
IC50_NS = Namespace(f"{BASE_URI}/ic50_value#")
KCAT_KM_NS = Namespace(f"{BASE_URI}/kcat_km#")
KI_NS = Namespace(f"{BASE_URI}/ki#")
KM_NS = Namespace(f"{BASE_URI}/km#")
RELATION_NS = Namespace(f"{BASE_URI}/relation#")
LOCATION_NS = Namespace(f"{BASE_URI}/location#")
METAL_ION_NS = Namespace(f"{BASE_URI}/metal_ion#")
NSP_REACTION_NS = Namespace(f"{BASE_URI}/nsp_reaction#")
SP_REACTION_NS = Namespace(f"{BASE_URI}/sp_reaction#")
INFORMATION_NS = Namespace(f"{BASE_URI}/information#")
PROTEIN_NS = Namespace(f"{BASE_URI}/protein#")

# BRENDA URIs to BRENDA
EC_NS = Namespace("https://www.brenda-enzymes.org/enzyme.php?ecno=")
REACTION_NS = Namespace("https://www.brenda-enzymes.org/enzyme.php?reaction=")
COMPOUND_NS = Namespace("https://www.brenda-enzymes.org/ligand.php?brenda_ligand_id=")
