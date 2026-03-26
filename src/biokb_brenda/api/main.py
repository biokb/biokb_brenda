import logging
import os
import re
import secrets
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Generator, Sequence, Tuple

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import Engine, create_engine, select
from sqlalchemy.engine.row import Row
from sqlalchemy.orm import Session

from biokb_brenda.api import schemas
from biokb_brenda.api.query_tools import SASearchResults, build_dynamic_query
from biokb_brenda.api.tags import Tag
from biokb_brenda.constants import (
    DB_DEFAULT_CONNECTION_STR,
    NEO4J_PASSWORD,
    NEO4J_URI,
    NEO4J_USER,
    ZIPPED_TTLS_PATH,
)
from biokb_brenda.db import manager, models
from biokb_brenda.rdf.neo4j_importer import Neo4jImporter
from biokb_brenda.rdf.turtle import TurtleCreator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

USERNAME = os.environ.get("BRENDA_API_USERNAME", "admin")
PASSWORD = os.environ.get("BRENDA_API_PASSWORD", "admin")


def get_engine() -> Engine:
    conn_url = os.environ.get("CONNECTION_STR", DB_DEFAULT_CONNECTION_STR)
    engine: Engine = create_engine(conn_url)
    return engine


def get_session() -> Generator[Session, None, None]:
    engine: Engine = get_engine()
    session = Session(bind=engine)
    try:
        yield session
    finally:
        session.close()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize app resources on startup and cleanup on shutdown."""
    engine = get_engine()
    manager.DbManager(engine)
    yield
    # Clean up resources if needed
    pass


description = """A RESTful API for BRENDA. Reference: https://www.brenda-enzymes.org/"""

app = FastAPI(
    title="RESTful API for BRENDA",
    description=description,
    version="0.1.0",
    lifespan=lifespan,
    root_path=os.environ.get("API_BRENDA_ROOT_PATH", ""),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


def run_api(host: str = "0.0.0.0", port: int = 8000) -> None:
    uvicorn.run(
        app="biokb_brenda.api.main:app",
        host=host,
        port=port,
        log_level="warning",
    )


def verify_credentials(
    credentials: HTTPBasicCredentials = Depends(HTTPBasic()),
) -> None:
    is_correct_username = secrets.compare_digest(credentials.username, USERNAME)
    is_correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )


###############################################################################
# Database Management
###############################################################################


@app.post(
    path="/import_data/",
    response_model=dict[str, int],
    tags=[Tag.DBMANAGE],
)
def import_data(
    credentials: HTTPBasicCredentials = Depends(verify_credentials),
    force_download: bool = Query(
        False,
        description=(
            "Whether to re-download data files even if they already exist,"
            " ensuring the newest version."
        ),
    ),
    delete_files: bool = Query(
        False,
        description=(
            "Whether to delete the downloaded files"
            " after importing them into the database."
        ),
    ),
) -> dict[str, int]:
    """Download data (if not exists) and load in database.

    Can take up to 15 minutes to complete.
    """
    try:
        dbm = manager.DbManager()
        result = dbm.import_data(
            force_download=force_download, delete_files=delete_files
        )
    except Exception as e:
        logger.error(f"Error importing data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing data. {e}",
        ) from e
    return result


@app.get("/export_ttls/", tags=[Tag.DBMANAGE])
async def create_ttls(
    credentials: HTTPBasicCredentials = Depends(verify_credentials),
    force_create: bool = Query(
        False,
        description="Whether to re-generate the TTL files even if they already exist.",
    ),
) -> FileResponse:

    file_path = ZIPPED_TTLS_PATH
    if not os.path.exists(file_path) or force_create:
        try:
            TurtleCreator().create_ttls()
        except Exception as e:
            logger.error(f"Error generating TTL files: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error generating TTL files. Data already imported?",
            ) from e
    return FileResponse(
        path=file_path, filename="brenda_ttls.zip", media_type="application/zip"
    )


@app.get("/import_neo4j/", tags=[Tag.DBMANAGE])
async def import_neo4j(
    credentials: HTTPBasicCredentials = Depends(verify_credentials),
    uri: str | None = Query(
        default=os.environ.get("NEO4J_URI", NEO4J_URI),
        description="The Neo4j URI. If not provided, "
        "the default from environment variable is used.",
    ),
    user: str | None = Query(
        default=os.environ.get("NEO4J_USER", NEO4J_USER),
        description="The Neo4j user. If not provided,"
        " the default from environment variable is used.",
    ),
    password: str | None = Query(
        NEO4J_PASSWORD,
        description="The Neo4j password. If not provided,"
        " the default from environment variable is used.",
    ),
) -> dict[str, str]:
    """Import RDF turtle files in Neo4j."""
    try:
        if not os.path.exists(ZIPPED_TTLS_PATH):
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail=(
                    "Zipped TTL files not found. Please "
                    "generate them first using /export_ttls/ endpoint."
                ),
            )
        importer = Neo4jImporter(neo4j_uri=uri, neo4j_user=user, neo4j_pwd=password)
        importer.import_ttls()
    except Exception as e:
        logger.error(f"Error importing data into Neo4j: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing data into Neo4j: {e}",
        ) from e
    return {"status": "Neo4j import completed successfully."}


###############################################################################
# Enzyme Classes
###############################################################################


@app.get(
    "/enzyme_classes/",
    response_model=schemas.EnzymeClassSearchResult,
    tags=[Tag.ENZYME],
)
async def search_enzyme_classes(
    search: schemas.EnzymeClassSearch = Depends(),
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search enzyme classes by EC number, recommended name, or systematic name.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.EnzymeClass,
        db=session,
    )


@app.get(
    "/enzymes/by_organism/",
    response_model=list[schemas.OrganismEnzymeSearchResult],
    tags=[Tag.ENZYME],
)
async def search_enzymes_by_organism(
    organism: str = Query(..., description="Organism"),
    limit: int | None = Query(
        description="Maximum number of results to return", default=None
    ),
    session: Session = Depends(get_session),
):
    """
    Search enzyme classes by EC number, recommended name, or systematic name.
    """
    organism = re.sub(r"\s{2,}", " ", organism.strip())
    stmt = (
        select(
            models.Organism.name.label("organism_name"),
            models.EnzymeClass.ec_number,
            models.EnzymeClass.recommended_name,
            models.EnzymeClass.systematic_name,
        )
        .join(models.Protein, models.Protein.organism_id == models.Organism.id)
        .join(
            models.EnzymeClass, models.Protein.ec_number == models.EnzymeClass.ec_number
        )
        .where(models.Organism.name.like(f"{organism}%"))
    )
    if limit is not None:
        stmt = stmt.limit(limit)
    results = session.execute(stmt).mappings().all()
    return results


@app.get(
    "/enzyme_classes/{ec_number}",
    response_model=schemas.EnzymeClassBase,
    tags=[Tag.ENZYME],
)
async def get_enzyme_class(
    ec_number: str,
    session: Session = Depends(get_session),
) -> models.EnzymeClass:
    """
    Get a specific enzyme class by EC number.
    """
    enzyme = session.get(models.EnzymeClass, ec_number)
    if not enzyme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enzyme class with EC number {ec_number} not found",
        )
    return enzyme


###############################################################################
# Organisms
###############################################################################


@app.get(
    "/organisms/",
    response_model=schemas.OrganismSearchResult,
    tags=[Tag.ORGANISM],
)
async def search_organisms(
    search: schemas.OrganismSearch = Depends(),
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search organisms by name or taxonomy ID.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Organism,
        db=session,
    )


@app.get(
    "/organisms/{organism_id}",
    response_model=schemas.OrganismBase,
    tags=[Tag.ORGANISM],
)
async def get_organism(
    organism_id: int,
    session: Session = Depends(get_session),
) -> models.Organism:
    """
    Get a specific organism by ID.
    """
    organism = session.get(models.Organism, organism_id)
    if not organism:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organism with ID {organism_id} not found",
        )
    return organism


###############################################################################
# Compounds
###############################################################################


@app.get(
    "/compounds/",
    response_model=schemas.CompoundSearchResult,
    tags=[Tag.COMPOUND],
)
async def search_compounds(
    search: schemas.CompoundSearch = Depends(),
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search compounds by name, InChI key, or ChEBI ID.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Compound,
        db=session,
    )


@app.get(
    "/compounds/{compound_id}",
    response_model=schemas.CompoundBase,
    tags=[Tag.COMPOUND],
)
async def get_compound(
    compound_id: int,
    session: Session = Depends(get_session),
) -> models.Compound:
    """
    Get a specific compound by ID.
    """
    compound = session.get(models.Compound, compound_id)
    if not compound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compound with ID {compound_id} not found",
        )
    return compound


###############################################################################
# References
###############################################################################


@app.get(
    "/references/",
    response_model=schemas.ReferenceSearchResult,
    tags=[Tag.REFERENCE],
)
async def search_references(
    search: schemas.ReferenceSearch = Depends(),
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search references by title, journal, year, or PubMed ID.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Reference,
        db=session,
    )


@app.get(
    "/references/{reference_id}",
    response_model=schemas.ReferenceDetail,
    tags=[Tag.REFERENCE],
)
async def get_reference(
    reference_id: int,
    session: Session = Depends(get_session),
) -> models.Reference:
    """
    Get a specific reference by ID, including authors.
    """
    reference = session.get(models.Reference, reference_id)
    if not reference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reference with ID {reference_id} not found",
        )
    return reference


###############################################################################
# Reactions
###############################################################################


@app.get(
    "/reactions/",
    response_model=schemas.ReactionSearchResult,
    tags=[Tag.REACTION],
)
async def search_reactions(
    search: schemas.ReactionSearch = Depends(),
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search reactions by EC number or reaction string.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Reaction,
        db=session,
    )


@app.get(
    "/reactions/{reaction_id}",
    response_model=schemas.ReactionBase,
    tags=[Tag.REACTION],
)
async def get_reaction(
    reaction_id: int,
    session: Session = Depends(get_session),
) -> models.Reaction:
    """
    Get a specific reaction by ID.
    """
    reaction = session.get(models.Reaction, reaction_id)
    if not reaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reaction with ID {reaction_id} not found",
        )
    return reaction


@app.get(
    "/reactions/enzyme/{ec_number}",
    response_model=list[schemas.ReactionBase],
    tags=[Tag.REACTION],
)
async def get_reactions_by_enzyme(
    ec_number: str,
    session: Session = Depends(get_session),
    limit: int = Query(100, le=1000),
) -> Sequence[models.Reaction]:
    """
    Get all reactions for a specific enzyme class.
    """
    stmt = (
        select(models.Reaction)
        .where(models.Reaction.ec_number == ec_number)
        .limit(limit)
    )
    result = session.execute(stmt)
    return result.scalars().all()


###############################################################################
# Kinetic Parameters
###############################################################################


@app.get(
    "/km_values/enzyme/{ec_number}",
    response_model=list[schemas.KmValueBase],
    tags=[Tag.KINETICS],
)
async def get_km_values_by_enzyme(
    ec_number: str,
    session: Session = Depends(get_session),
    limit: int = Query(100, le=1000),
) -> Sequence[models.KmValue]:
    """
    Get all Km values for a specific enzyme class.
    """
    stmt = (
        select(models.KmValue).where(models.KmValue.ec_number == ec_number).limit(limit)
    )
    result = session.execute(stmt)
    return result.scalars().all()


@app.get(
    "/km_values/{km_id}",
    response_model=schemas.KmValueBase,
    tags=[Tag.KINETICS],
)
async def get_km_value(
    km_id: int,
    session: Session = Depends(get_session),
) -> models.KmValue:
    """
    Get a specific Km value by ID.
    """
    km_value = session.get(models.KmValue, km_id)
    if not km_value:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Km value with ID {km_id} not found",
        )
    return km_value


@app.get(
    "/turnover_numbers/enzyme/{ec_number}",
    response_model=list[schemas.TurnoverNumberBase],
    tags=[Tag.KINETICS],
)
async def get_turnover_numbers_by_enzyme(
    ec_number: str,
    session: Session = Depends(get_session),
    limit: int = Query(100, le=1000),
) -> Sequence[models.TurnoverNumber]:
    """
    Get all turnover numbers (kcat) for a specific enzyme class.
    """
    stmt = (
        select(models.TurnoverNumber)
        .where(models.TurnoverNumber.ec_number == ec_number)
        .limit(limit)
    )
    result = session.execute(stmt)
    return result.scalars().all()


@app.get(
    "/ki_values/enzyme/{ec_number}",
    response_model=list[schemas.KiValueBase],
    tags=[Tag.KINETICS],
)
async def get_ki_values_by_enzyme(
    ec_number: str,
    session: Session = Depends(get_session),
    limit: int = Query(100, le=1000),
) -> Sequence[models.KiValue]:
    """
    Get all Ki values for a specific enzyme class.
    """
    stmt = (
        select(models.KiValue).where(models.KiValue.ec_number == ec_number).limit(limit)
    )
    result = session.execute(stmt)
    return result.scalars().all()


@app.get(
    "/ic50_values/enzyme/{ec_number}",
    response_model=list[schemas.IC50ValueBase],
    tags=[Tag.KINETICS],
)
async def get_ic50_values_by_enzyme(
    ec_number: str,
    session: Session = Depends(get_session),
    limit: int = Query(100, le=1000),
) -> Sequence[models.IC50Value]:
    """
    Get all IC50 values for a specific enzyme class.
    """
    stmt = (
        select(models.IC50Value)
        .where(models.IC50Value.ec_number == ec_number)
        .limit(limit)
    )
    result = session.execute(stmt)
    return result.scalars().all()


@app.get(
    "/kcat_km_values/enzyme/{ec_number}",
    response_model=list[schemas.KcatKmValueBase],
    tags=[Tag.KINETICS],
)
async def get_kcat_km_values_by_enzyme(
    ec_number: str,
    session: Session = Depends(get_session),
    limit: int = Query(100, le=1000),
) -> Sequence[models.KcatKmValue]:
    """
    Get all Kcat/Km values for a specific enzyme class.
    """
    stmt = (
        select(models.KcatKmValue)
        .where(models.KcatKmValue.ec_number == ec_number)
        .limit(limit)
    )
    result = session.execute(stmt)
    return result.scalars().all()


###############################################################################
# pH and Temperature Parameters
###############################################################################


@app.get(
    "/ph_optima/enzyme/{ec_number}",
    response_model=list[schemas.PhOptimumBase],
    tags=[Tag.PH_TEMP],
)
async def get_ph_optima_by_enzyme(
    ec_number: str,
    session: Session = Depends(get_session),
    limit: int = Query(100, le=1000),
) -> Sequence[models.PhOptimum]:
    """
    Get all pH optima for a specific enzyme class.
    """
    stmt = (
        select(models.PhOptimum)
        .where(models.PhOptimum.ec_number == ec_number)
        .limit(limit)
    )
    result = session.execute(stmt)
    return result.scalars().all()


@app.get(
    "/ph_ranges/enzyme/{ec_number}",
    response_model=list[schemas.PhRangeBase],
    tags=[Tag.PH_TEMP],
)
async def get_ph_ranges_by_enzyme(
    ec_number: str,
    session: Session = Depends(get_session),
    limit: int = Query(100, le=1000),
) -> Sequence[models.PhRange]:
    """
    Get all pH ranges for a specific enzyme class.
    """
    stmt = (
        select(models.PhRange).where(models.PhRange.ec_number == ec_number).limit(limit)
    )
    result = session.execute(stmt)
    return result.scalars().all()


@app.get(
    "/temperature_optima/enzyme/{ec_number}",
    response_model=list[schemas.TemperatureOptimumBase],
    tags=[Tag.PH_TEMP],
)
async def get_temperature_optima_by_enzyme(
    ec_number: str,
    session: Session = Depends(get_session),
    limit: int = Query(100, le=1000),
) -> Sequence[models.TemperatureOptimum]:
    """
    Get all temperature optima for a specific enzyme class.
    """
    stmt = (
        select(models.TemperatureOptimum)
        .where(models.TemperatureOptimum.ec_number == ec_number)
        .limit(limit)
    )
    result = session.execute(stmt)
    return result.scalars().all()


@app.get(
    "/temperature_ranges/enzyme/{ec_number}",
    response_model=list[schemas.TemperatureRangeBase],
    tags=[Tag.PH_TEMP],
)
async def get_temperature_ranges_by_enzyme(
    ec_number: str,
    session: Session = Depends(get_session),
    limit: int = Query(100, le=1000),
) -> Sequence[models.TemperatureRange]:
    """
    Get all temperature ranges for a specific enzyme class.
    """
    stmt = (
        select(models.TemperatureRange)
        .where(models.TemperatureRange.ec_number == ec_number)
        .limit(limit)
    )
    result = session.execute(stmt)
    return result.scalars().all()


###############################################################################
# Activity and Stability
###############################################################################


@app.get(
    "/specific_activities/enzyme/{ec_number}",
    response_model=list[schemas.SpecificActivityBase],
    tags=[Tag.STABILITY],
)
async def get_specific_activities_by_enzyme(
    ec_number: str,
    session: Session = Depends(get_session),
    limit: int = Query(100, le=1000),
) -> Sequence[models.SpecificActivity]:
    """
    Get all specific activities for a specific enzyme class.
    """
    stmt = (
        select(models.SpecificActivity)
        .where(models.SpecificActivity.ec_number == ec_number)
        .limit(limit)
    )
    result = session.execute(stmt)
    return result.scalars().all()


@app.get(
    "/ph_stabilities/enzyme/{ec_number}",
    response_model=list[schemas.PhStabilityBase],
    tags=[Tag.STABILITY],
)
async def get_ph_stabilities_by_enzyme(
    ec_number: str,
    session: Session = Depends(get_session),
    limit: int = Query(100, le=1000),
) -> Sequence[models.PhStability]:
    """
    Get all pH stabilities for a specific enzyme class.
    """
    stmt = (
        select(models.PhStability)
        .where(models.PhStability.ec_number == ec_number)
        .limit(limit)
    )
    result = session.execute(stmt)
    return result.scalars().all()


@app.get(
    "/temperature_stabilities/enzyme/{ec_number}",
    response_model=list[schemas.TemperatureStabilityBase],
    tags=[Tag.STABILITY],
)
async def get_temperature_stabilities_by_enzyme(
    ec_number: str,
    session: Session = Depends(get_session),
    limit: int = Query(100, le=1000),
) -> Sequence[models.TemperatureStability]:
    """
    Get all temperature stabilities for a specific enzyme class.
    """
    stmt = (
        select(models.TemperatureStability)
        .where(models.TemperatureStability.ec_number == ec_number)
        .limit(limit)
    )
    result = session.execute(stmt)
    return result.scalars().all()


###############################################################################
# Protein Properties
###############################################################################


@app.get(
    "/proteins/enzyme/{ec_number}",
    response_model=list[schemas.ProteinBase],
    tags=[Tag.PROTEIN],
)
async def get_proteins_by_enzyme(
    ec_number: str,
    session: Session = Depends(get_session),
    limit: int = Query(100, le=1000),
) -> Sequence[models.Protein]:
    """
    Get all proteins for a specific enzyme class.
    """
    stmt = (
        select(models.Protein).where(models.Protein.ec_number == ec_number).limit(limit)
    )
    result = session.execute(stmt)
    return result.scalars().all()


@app.get(
    "/molecular_weights/enzyme/{ec_number}",
    response_model=list[schemas.MolecularWeightBase],
    tags=[Tag.PROTEIN],
)
async def get_molecular_weights_by_enzyme(
    ec_number: str,
    session: Session = Depends(get_session),
    limit: int = Query(100, le=1000),
) -> Sequence[models.MolecularWeight]:
    """
    Get all molecular weights for a specific enzyme class.
    """
    stmt = (
        select(models.MolecularWeight)
        .where(models.MolecularWeight.ec_number == ec_number)
        .limit(limit)
    )
    result = session.execute(stmt)
    return result.scalars().all()


@app.get(
    "/subunits/enzyme/{ec_number}",
    response_model=list[schemas.SubunitBase],
    tags=[Tag.PROTEIN],
)
async def get_subunits_by_enzyme(
    ec_number: str,
    session: Session = Depends(get_session),
    limit: int = Query(100, le=1000),
) -> Sequence[models.Subunit]:
    """
    Get all subunit structures for a specific enzyme class.
    """
    stmt = (
        select(models.Subunit).where(models.Subunit.ec_number == ec_number).limit(limit)
    )
    result = session.execute(stmt)
    return result.scalars().all()


@app.get(
    "/pi_values/enzyme/{ec_number}",
    response_model=list[schemas.PiValueBase],
    tags=[Tag.PROTEIN],
)
async def get_pi_values_by_enzyme(
    ec_number: str,
    session: Session = Depends(get_session),
    limit: int = Query(100, le=1000),
) -> Sequence[models.PiValue]:
    """
    Get all isoelectric points for a specific enzyme class.
    """
    stmt = (
        select(models.PiValue).where(models.PiValue.ec_number == ec_number).limit(limit)
    )
    result = session.execute(stmt)
    return result.scalars().all()


###############################################################################
# Cofactors and Effectors
###############################################################################


@app.get(
    "/cofactors/enzyme/{ec_number}",
    response_model=list[schemas.CofactorBase],
    tags=[Tag.COFACTOR],
)
async def get_cofactors_by_enzyme(
    ec_number: str,
    session: Session = Depends(get_session),
    limit: int = Query(100, le=1000),
) -> Sequence[models.Cofactor]:
    """
    Get all cofactors for a specific enzyme class.
    """
    stmt = (
        select(models.Cofactor)
        .where(models.Cofactor.ec_number == ec_number)
        .limit(limit)
    )
    result = session.execute(stmt)
    return result.scalars().all()


@app.get(
    "/activating_compounds/enzyme/{ec_number}",
    response_model=list[schemas.ActivatingCompoundBase],
    tags=[Tag.COFACTOR],
)
async def get_activating_compounds_by_enzyme(
    ec_number: str,
    session: Session = Depends(get_session),
    limit: int = Query(100, le=1000),
) -> Sequence[models.ActivatingCompound]:
    """
    Get all activating compounds for a specific enzyme class.
    """
    stmt = (
        select(models.ActivatingCompound)
        .where(models.ActivatingCompound.ec_number == ec_number)
        .limit(limit)
    )
    result = session.execute(stmt)
    return result.scalars().all()


@app.get(
    "/inhibitors/enzyme/{ec_number}",
    response_model=list[schemas.InhibitorBase],
    tags=[Tag.COFACTOR],
)
async def get_inhibitors_by_enzyme(
    ec_number: str,
    session: Session = Depends(get_session),
    limit: int = Query(100, le=1000),
) -> Sequence[models.Inhibitor]:
    """
    Get all inhibitors for a specific enzyme class.
    """
    stmt = (
        select(models.Inhibitor)
        .where(models.Inhibitor.ec_number == ec_number)
        .limit(limit)
    )
    result = session.execute(stmt)
    return result.scalars().all()


@app.get(
    "/metal_ions/enzyme/{ec_number}",
    response_model=list[schemas.MetalIonBase],
    tags=[Tag.COFACTOR],
)
async def get_metal_ions_by_enzyme(
    ec_number: str,
    session: Session = Depends(get_session),
    limit: int = Query(100, le=1000),
) -> Sequence[models.MetalIon]:
    """
    Get all metal ion requirements for a specific enzyme class.
    """
    stmt = (
        select(models.MetalIon)
        .where(models.MetalIon.ec_number == ec_number)
        .limit(limit)
    )
    result = session.execute(stmt)
    return result.scalars().all()


###############################################################################
# General Information
###############################################################################


@app.get(
    "/synonyms/enzyme/{ec_number}",
    response_model=list[schemas.SynonymBase],
    tags=[Tag.INFO],
)
async def get_synonyms_by_enzyme(
    ec_number: str,
    session: Session = Depends(get_session),
    limit: int = Query(100, le=1000),
) -> Sequence[models.Synonym]:
    """
    Get all synonyms for a specific enzyme class.
    """
    stmt = (
        select(models.Synonym).where(models.Synonym.ec_number == ec_number).limit(limit)
    )
    result = session.execute(stmt)
    return result.scalars().all()


@app.get(
    "/localizations/enzyme/{ec_number}",
    response_model=list[schemas.LocalizationBase],
    tags=[Tag.INFO],
)
async def get_localizations_by_enzyme(
    ec_number: str,
    session: Session = Depends(get_session),
    limit: int = Query(100, le=1000),
) -> Sequence[models.Localization]:
    """
    Get all cellular localizations for a specific enzyme class.
    """
    stmt = (
        select(models.Localization)
        .where(models.Localization.ec_number == ec_number)
        .limit(limit)
    )
    result = session.execute(stmt)
    return result.scalars().all()


@app.get(
    "/source_tissues/enzyme/{ec_number}",
    response_model=list[schemas.SourceTissueBase],
    tags=[Tag.INFO],
)
async def get_source_tissues_by_enzyme(
    ec_number: str,
    session: Session = Depends(get_session),
    limit: int = Query(100, le=1000),
) -> Sequence[models.SourceTissue]:
    """
    Get all source tissues for a specific enzyme class.
    """
    stmt = (
        select(models.SourceTissue)
        .where(models.SourceTissue.ec_number == ec_number)
        .limit(limit)
    )
    result = session.execute(stmt)
    return result.scalars().all()


@app.get(
    "/applications/enzyme/{ec_number}",
    response_model=list[schemas.ApplicationBase],
    tags=[Tag.INFO],
)
async def get_applications_by_enzyme(
    ec_number: str,
    session: Session = Depends(get_session),
    limit: int = Query(100, le=1000),
) -> Sequence[models.Application]:
    """
    Get all applications for a specific enzyme class.
    """
    stmt = (
        select(models.Application)
        .where(models.Application.ec_number == ec_number)
        .limit(limit)
    )
    result = session.execute(stmt)
    return result.scalars().all()
