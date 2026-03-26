"""Pydantic schemas for BRENDA enzyme database API."""

from typing import Annotated, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class OffsetLimit(BaseModel):
    """Base schema for pagination."""

    limit: Annotated[int, Field(le=100)] = 10
    offset: int = 0


# ============================================================================
# Enzyme Class Schemas
# ============================================================================


class OrganismEnzymeSearchResult(BaseModel):
    organism_name: str
    ec_number: str
    recommended_name: str
    systematic_name: str


class EnzymeClassBase(BaseModel):
    """Base schema for enzyme class."""

    ec_number: str = Field(..., description="EC number identifier")
    recommended_name: Optional[str] = Field(None, description="Recommended enzyme name")
    systematic_name: Optional[str] = Field(None, description="Systematic enzyme name")

    model_config = ConfigDict(from_attributes=True)


class EnzymeClassDetail(EnzymeClassBase):
    """Detailed enzyme class with related data."""

    pass


class EnzymeClassSearch(OffsetLimit):
    """Search parameters for enzyme classes."""

    ec_number: Optional[str] = Field(None, description="EC number to search")
    recommended_name: Optional[str] = Field(
        None, description="Recommended name to search"
    )
    systematic_name: Optional[str] = Field(
        None, description="Systematic name to search"
    )


class EnzymeClassSearchResult(BaseModel):
    """Search results for enzyme classes."""

    count: int
    offset: int
    limit: int
    results: List[EnzymeClassBase]


# ============================================================================
# Organism Schemas
# ============================================================================


class OrganismBase(BaseModel):
    """Base schema for organism."""

    id: int = Field(..., description="Unique identifier")
    name: str = Field(..., description="Organism name")
    tax_id: Optional[int] = Field(None, description="NCBI Taxonomy ID")

    model_config = ConfigDict(from_attributes=True)


class OrganismSearch(OffsetLimit):
    """Search parameters for organisms."""

    name: Optional[str] = Field(None, description="Organism name to search")
    tax_id: Optional[int] = Field(None, description="NCBI Taxonomy ID to search")


class OrganismSearchResult(BaseModel):
    """Search results for organisms."""

    count: int
    offset: int
    limit: int
    results: List[OrganismBase]


# ============================================================================
# Compound Schemas
# ============================================================================


class CompoundBase(BaseModel):
    """Base schema for compound."""

    id: int = Field(..., description="Unique identifier")
    name: str = Field(..., description="Compound name")
    inchi: Optional[str] = Field(None, description="InChI string")
    inchi_key: Optional[str] = Field(None, description="InChI key")
    chebi_id: Optional[int] = Field(None, description="ChEBI identifier")
    brenda_ligand_id: Optional[int] = Field(
        None, description="BRENDA ligand identifier"
    )

    model_config = ConfigDict(from_attributes=True)


class CompoundSearch(OffsetLimit):
    """Search parameters for compounds."""

    name: Optional[str] = Field(None, description="Compound name to search")
    inchi_key: Optional[str] = Field(None, description="InChI key to search")
    chebi_id: Optional[int] = Field(None, description="ChEBI identifier to search")


class CompoundSearchResult(BaseModel):
    """Search results for compounds."""

    count: int
    offset: int
    limit: int
    results: List[CompoundBase]


# ============================================================================
# Reference Schemas
# ============================================================================


class AuthorBase(BaseModel):
    """Base schema for author."""

    id: int = Field(..., description="Unique identifier")
    name: str = Field(..., description="Author name")

    model_config = ConfigDict(from_attributes=True)


class ReferenceBase(BaseModel):
    """Base schema for reference."""

    id: int = Field(..., description="Unique identifier")
    title: Optional[str] = Field(None, description="Publication title")
    journal: Optional[str] = Field(None, description="Journal name")
    year: Optional[int] = Field(None, description="Publication year")
    pages: Optional[str] = Field(None, description="Page numbers")
    volume: Optional[str] = Field(None, description="Volume number")
    pmid: Optional[int] = Field(None, description="PubMed ID")

    model_config = ConfigDict(from_attributes=True)


class ReferenceDetail(ReferenceBase):
    """Detailed reference with authors."""

    authors: List[AuthorBase] = Field([], description="List of authors")


class ReferenceSearch(OffsetLimit):
    """Search parameters for references."""

    title: Optional[str] = Field(None, description="Title to search")
    journal: Optional[str] = Field(None, description="Journal to search")
    year: Optional[int] = Field(None, description="Publication year")
    pmid: Optional[int] = Field(None, description="PubMed ID")


class ReferenceSearchResult(BaseModel):
    """Search results for references."""

    count: int
    offset: int
    limit: int
    results: List[ReferenceBase]


# ============================================================================
# Reaction Schemas
# ============================================================================


class ReactionBase(BaseModel):
    """Base schema for reaction."""

    id: int = Field(..., description="Unique identifier")
    value: str = Field(..., description="Reaction string")
    reversibility: Optional[bool] = Field(
        None, description="Whether reaction is reversible"
    )
    comment: Optional[str] = Field(None, description="Additional comments")
    ec_number: str = Field(..., description="Associated EC number")

    model_config = ConfigDict(from_attributes=True)


class ReactionDetail(ReactionBase):
    """Detailed reaction with substrates and products."""

    substrates: List[CompoundBase] = Field([], description="Substrate compounds")
    products: List[CompoundBase] = Field([], description="Product compounds")
    organisms: List[OrganismBase] = Field([], description="Associated organisms")


class ReactionSearch(OffsetLimit):
    """Search parameters for reactions."""

    ec_number: Optional[str] = Field(None, description="EC number to search")
    value: Optional[str] = Field(None, description="Reaction string to search")


class ReactionSearchResult(BaseModel):
    """Search results for reactions."""

    count: int
    offset: int
    limit: int
    results: List[ReactionBase]


# ============================================================================
# Kinetic Parameter Schemas
# ============================================================================


class KmValueBase(BaseModel):
    """Base schema for Km value."""

    id: int = Field(..., description="Unique identifier")
    value: float = Field(..., description="Km value")
    value_max: Optional[float] = Field(None, description="Maximum Km value for range")
    comment: Optional[str] = Field(None, description="Additional comments")
    ec_number: str = Field(..., description="Associated EC number")
    compound_id: int = Field(..., description="Substrate compound ID")

    model_config = ConfigDict(from_attributes=True)


class KmValueDetail(KmValueBase):
    """Detailed Km value with compound and organisms."""

    compound: CompoundBase
    organisms: List[OrganismBase] = Field([], description="Associated organisms")


class TurnoverNumberBase(BaseModel):
    """Base schema for turnover number (kcat)."""

    id: int = Field(..., description="Unique identifier")
    value: float = Field(..., description="Kcat value")
    value_max: Optional[float] = Field(None, description="Maximum kcat value for range")
    comment: Optional[str] = Field(None, description="Additional comments")
    ec_number: str = Field(..., description="Associated EC number")
    compound_id: int = Field(..., description="Substrate compound ID")

    model_config = ConfigDict(from_attributes=True)


class KiValueBase(BaseModel):
    """Base schema for Ki value."""

    id: int = Field(..., description="Unique identifier")
    value: float = Field(..., description="Ki value")
    value_max: Optional[float] = Field(None, description="Maximum Ki value for range")
    comment: Optional[str] = Field(None, description="Additional comments")
    ec_number: str = Field(..., description="Associated EC number")
    compound_id: int = Field(..., description="Inhibitor compound ID")

    model_config = ConfigDict(from_attributes=True)


class IC50ValueBase(BaseModel):
    """Base schema for IC50 value."""

    id: int = Field(..., description="Unique identifier")
    value: float = Field(..., description="IC50 value")
    value_max: Optional[float] = Field(None, description="Maximum IC50 value for range")
    comment: Optional[str] = Field(None, description="Additional comments")
    ec_number: str = Field(..., description="Associated EC number")
    compound_id: int = Field(..., description="Inhibitor compound ID")

    model_config = ConfigDict(from_attributes=True)


class KcatKmValueBase(BaseModel):
    """Base schema for Kcat/Km value."""

    id: int = Field(..., description="Unique identifier")
    value: float = Field(..., description="Kcat/Km value")
    value_max: Optional[float] = Field(
        None, description="Maximum Kcat/Km value for range"
    )
    comment: Optional[str] = Field(None, description="Additional comments")
    ec_number: str = Field(..., description="Associated EC number")
    compound_id: int = Field(..., description="Substrate compound ID")

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# pH and Temperature Parameter Schemas
# ============================================================================


class PhOptimumBase(BaseModel):
    """Base schema for pH optimum."""

    id: int = Field(..., description="Unique identifier")
    value: float = Field(..., description="pH optimum value")
    value_max: Optional[float] = Field(None, description="Maximum pH for range")
    comment: Optional[str] = Field(None, description="Additional comments")
    ec_number: str = Field(..., description="Associated EC number")

    model_config = ConfigDict(from_attributes=True)


class PhRangeBase(BaseModel):
    """Base schema for pH range."""

    id: int = Field(..., description="Unique identifier")
    value: float = Field(..., description="pH range minimum")
    value_max: Optional[float] = Field(None, description="pH range maximum")
    comment: Optional[str] = Field(None, description="Additional comments")
    ec_number: str = Field(..., description="Associated EC number")

    model_config = ConfigDict(from_attributes=True)


class TemperatureOptimumBase(BaseModel):
    """Base schema for temperature optimum."""

    id: int = Field(..., description="Unique identifier")
    value: float = Field(..., description="Temperature optimum (°C)")
    value_max: Optional[float] = Field(
        None, description="Maximum temperature for range"
    )
    comment: Optional[str] = Field(None, description="Additional comments")
    ec_number: str = Field(..., description="Associated EC number")

    model_config = ConfigDict(from_attributes=True)


class TemperatureRangeBase(BaseModel):
    """Base schema for temperature range."""

    id: int = Field(..., description="Unique identifier")
    value: float = Field(..., description="Temperature range minimum (°C)")
    value_max: Optional[float] = Field(None, description="Temperature range maximum")
    comment: Optional[str] = Field(None, description="Additional comments")
    ec_number: str = Field(..., description="Associated EC number")

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Activity and Stability Schemas
# ============================================================================


class SpecificActivityBase(BaseModel):
    """Base schema for specific activity."""

    id: int = Field(..., description="Unique identifier")
    value: float = Field(..., description="Specific activity value")
    value_max: Optional[float] = Field(None, description="Maximum value for range")
    comment: Optional[str] = Field(None, description="Additional comments")
    ec_number: str = Field(..., description="Associated EC number")

    model_config = ConfigDict(from_attributes=True)


class PhStabilityBase(BaseModel):
    """Base schema for pH stability."""

    id: int = Field(..., description="Unique identifier")
    value: float = Field(..., description="pH stability minimum")
    value_max: Optional[float] = Field(None, description="pH stability maximum")
    comment: Optional[str] = Field(None, description="Additional comments")
    ec_number: str = Field(..., description="Associated EC number")

    model_config = ConfigDict(from_attributes=True)


class TemperatureStabilityBase(BaseModel):
    """Base schema for temperature stability."""

    id: int = Field(..., description="Unique identifier")
    value: float = Field(..., description="Temperature stability minimum (°C)")
    value_max: Optional[float] = Field(
        None, description="Temperature stability maximum"
    )
    comment: Optional[str] = Field(None, description="Additional comments")
    ec_number: str = Field(..., description="Associated EC number")

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Protein and Molecular Property Schemas
# ============================================================================


class ProteinBase(BaseModel):
    """Base schema for protein."""

    id: int = Field(..., description="Unique identifier")
    comment: Optional[str] = Field(None, description="Additional comments")
    ec_number: str = Field(..., description="Associated EC number")
    organism_id: Optional[int] = Field(None, description="Organism ID")

    model_config = ConfigDict(from_attributes=True)


class MolecularWeightBase(BaseModel):
    """Base schema for molecular weight."""

    id: int = Field(..., description="Unique identifier")
    value: float = Field(..., description="Molecular weight (kDa)")
    value_max: Optional[float] = Field(None, description="Maximum value for range")
    comment: Optional[str] = Field(None, description="Additional comments")
    ec_number: str = Field(..., description="Associated EC number")

    model_config = ConfigDict(from_attributes=True)


class SubunitBase(BaseModel):
    """Base schema for subunit structure."""

    id: int = Field(..., description="Unique identifier")
    value: str = Field(..., description="Subunit structure description")
    comment: Optional[str] = Field(None, description="Additional comments")
    ec_number: str = Field(..., description="Associated EC number")

    model_config = ConfigDict(from_attributes=True)


class PiValueBase(BaseModel):
    """Base schema for isoelectric point."""

    id: int = Field(..., description="Unique identifier")
    value: float = Field(..., description="Isoelectric point value")
    value_max: Optional[float] = Field(None, description="Maximum value for range")
    comment: Optional[str] = Field(None, description="Additional comments")
    ec_number: str = Field(..., description="Associated EC number")

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Cofactor and Effector Schemas
# ============================================================================


class CofactorBase(BaseModel):
    """Base schema for cofactor."""

    id: int = Field(..., description="Unique identifier")
    comment: Optional[str] = Field(None, description="Additional comments")
    ec_number: str = Field(..., description="Associated EC number")
    compound_id: int = Field(..., description="Cofactor compound ID")

    model_config = ConfigDict(from_attributes=True)


class ActivatingCompoundBase(BaseModel):
    """Base schema for activating compound."""

    id: int = Field(..., description="Unique identifier")
    comment: Optional[str] = Field(None, description="Additional comments")
    ec_number: str = Field(..., description="Associated EC number")
    compound_id: Optional[int] = Field(None, description="Activator compound ID")

    model_config = ConfigDict(from_attributes=True)


class InhibitorBase(BaseModel):
    """Base schema for inhibitor."""

    id: int = Field(..., description="Unique identifier")
    comment: Optional[str] = Field(None, description="Additional comments")
    ec_number: str = Field(..., description="Associated EC number")
    compound_id: Optional[int] = Field(None, description="Inhibitor compound ID")

    model_config = ConfigDict(from_attributes=True)


class MetalIonBase(BaseModel):
    """Base schema for metal ion."""

    id: int = Field(..., description="Unique identifier")
    comment: Optional[str] = Field(None, description="Additional comments")
    ec_number: str = Field(..., description="Associated EC number")
    compound_id: int = Field(..., description="Metal ion compound ID")

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Other Information Schemas
# ============================================================================


class SynonymBase(BaseModel):
    """Base schema for enzyme synonym."""

    id: int = Field(..., description="Unique identifier")
    value: str = Field(..., description="Synonym value")
    ec_number: str = Field(..., description="Associated EC number")

    model_config = ConfigDict(from_attributes=True)


class LocalizationBase(BaseModel):
    """Base schema for cellular localization."""

    id: int = Field(..., description="Unique identifier")
    value: str = Field(..., description="Localization description")
    comment: Optional[str] = Field(None, description="Additional comments")
    ec_number: str = Field(..., description="Associated EC number")

    model_config = ConfigDict(from_attributes=True)


class SourceTissueBase(BaseModel):
    """Base schema for source tissue."""

    id: int = Field(..., description="Unique identifier")
    value: str = Field(..., description="Source tissue description")
    comment: Optional[str] = Field(None, description="Additional comments")
    ec_number: str = Field(..., description="Associated EC number")

    model_config = ConfigDict(from_attributes=True)


class ApplicationBase(BaseModel):
    """Base schema for enzyme application."""

    id: int = Field(..., description="Unique identifier")
    value: str = Field(..., description="Application description")
    comment: Optional[str] = Field(None, description="Additional comments")
    ec_number: str = Field(..., description="Associated EC number")

    model_config = ConfigDict(from_attributes=True)
