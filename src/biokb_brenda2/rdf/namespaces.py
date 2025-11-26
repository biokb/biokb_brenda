"""RDF namespace URIs."""

from rdflib import Namespace

from biokb_brenda2.constants import BASE_URI

chebi_ns = Namespace("http://purl.obolibrary.org/obo/CHEBI_")
tax_ns = Namespace("http://purl.obolibrary.org/obo/NCBITaxon_")
inchi_ns = Namespace("http://rdf.ncbi.nlm.nih.gov/pubchem/inchikey/")
# get with inchikey cid: https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/inchikey/[inchikey]/cids/JSON
# get props with cid: https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/[CID]/property/InChI,InChIKey,CanonicalSMILES,IUPACName/JSON

# BRENDA URIs to Fraunhofer
node = Namespace(f"{BASE_URI}/node#")
activation_ns = Namespace(f"{BASE_URI}/activation#")
inhibition_ns = Namespace(f"{BASE_URI}/inhibition#")
cofactor_ns = Namespace(f"{BASE_URI}/cofactor_interaction#")
ic50_ns = Namespace(f"{BASE_URI}/ic50_value#")
kcat_km_ns = Namespace(f"{BASE_URI}/kcat_km#")
ki_ns = Namespace(f"{BASE_URI}/ki#")
km_ns = Namespace(f"{BASE_URI}/km#")
relation = Namespace(f"{BASE_URI}/relation#")
location_ns = Namespace(f"{BASE_URI}/location#")
metal_ion_ns = Namespace(f"{BASE_URI}/metal_ion#")
nsp_reaction_ns = Namespace(f"{BASE_URI}/nsp_reaction#")
sp_reaction_ns = Namespace(f"{BASE_URI}/sp_reaction#")
information_ns = Namespace(f"{BASE_URI}/information#")
protein_ns = Namespace(f"{BASE_URI}/protein#")

# BRENDA URIs to BRENDA
ec_ns = Namespace("https://www.brenda-enzymes.org/enzyme.php?ecno=")
reaction_ns = Namespace("https://www.brenda-enzymes.org/enzyme.php?reaction=")
compound_ns = Namespace("https://www.brenda-enzymes.org/ligand.php?brenda_ligand_id=")
