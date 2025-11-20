"""SQLAlchemy models for BRENDA enzyme data."""

from typing import Optional

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class EnzymeClass(Base):
    """Main enzyme class identified by EC number."""

    __tablename__ = "enzyme_class"

    ec_number: Mapped[str] = mapped_column(primary_key=True)
    recommended_name: Mapped[Optional[str]]
    systematic_name: Mapped[Optional[str]]

    # Relationships

    proteins: Mapped[list["Protein"]] = relationship(back_populates="enzyme_class")
    reactions: Mapped[list["Reaction"]] = relationship(back_populates="enzyme_class")
    synonyms: Mapped[list["Synonym"]] = relationship(back_populates="enzyme_class")
    reaction_types: Mapped[list["ReactionType"]] = relationship(
        back_populates="enzyme_class"
    )
    source_tissues: Mapped[list["SourceTissue"]] = relationship(
        back_populates="enzyme_class"
    )
    localizations: Mapped[list["Localization"]] = relationship(
        back_populates="enzyme_class"
    )
    natural_substrates_products: Mapped[list["NaturalSubstrateProduct"]] = relationship(
        back_populates="enzyme_class"
    )
    substrates_products: Mapped[list["SubstrateProduct"]] = relationship(
        back_populates="enzyme_class"
    )
    turnover_numbers: Mapped[list["TurnoverNumber"]] = relationship(
        back_populates="enzyme_class"
    )
    km_values: Mapped[list["KmValue"]] = relationship(back_populates="enzyme_class")
    ph_optima: Mapped[list["PhOptimum"]] = relationship(back_populates="enzyme_class")
    ph_ranges: Mapped[list["PhRange"]] = relationship(back_populates="enzyme_class")
    specific_activities: Mapped[list["SpecificActivity"]] = relationship(
        back_populates="enzyme_class"
    )
    temperature_optima: Mapped[list["TemperatureOptimum"]] = relationship(
        back_populates="enzyme_class"
    )
    temperature_ranges: Mapped[list["TemperatureRange"]] = relationship(
        back_populates="enzyme_class"
    )
    activating_compounds: Mapped[list["ActivatingCompound"]] = relationship(
        back_populates="enzyme_class"
    )
    inhibitors: Mapped[list["Inhibitor"]] = relationship(back_populates="enzyme_class")
    metals_ions: Mapped[list["MetalIon"]] = relationship(back_populates="enzyme_class")
    molecular_weights: Mapped[list["MolecularWeight"]] = relationship(
        back_populates="enzyme_class"
    )
    posttranslational_modifications: Mapped[list["PosttranslationalModification"]] = (
        relationship(back_populates="enzyme_class")
    )
    subunits: Mapped[list["Subunit"]] = relationship(back_populates="enzyme_class")
    pi_values: Mapped[list["PiValue"]] = relationship(back_populates="enzyme_class")
    applications: Mapped[list["Application"]] = relationship(
        back_populates="enzyme_class"
    )
    protein_variants: Mapped[list["ProteinVariant"]] = relationship(
        back_populates="enzyme_class"
    )
    cloned_info: Mapped[list["ClonedInfo"]] = relationship(
        back_populates="enzyme_class"
    )
    purifications: Mapped[list["Purification"]] = relationship(
        back_populates="enzyme_class"
    )
    general_stabilities: Mapped[list["GeneralStability"]] = relationship(
        back_populates="enzyme_class"
    )
    organic_solvent_stabilities: Mapped[list["OrganicSolventStability"]] = relationship(
        back_populates="enzyme_class"
    )
    ph_stabilities: Mapped[list["PhStability"]] = relationship(
        back_populates="enzyme_class"
    )
    storage_stabilities: Mapped[list["StorageStability"]] = relationship(
        back_populates="enzyme_class"
    )
    temperature_stabilities: Mapped[list["TemperatureStability"]] = relationship(
        back_populates="enzyme_class"
    )
    ki_values: Mapped[list["KiValue"]] = relationship(back_populates="enzyme_class")
    kcat_km_values: Mapped[list["KcatKmValue"]] = relationship(
        back_populates="enzyme_class"
    )
    expressions: Mapped[list["Expression"]] = relationship(
        back_populates="enzyme_class"
    )
    general_information: Mapped[list["GeneralInformation"]] = relationship(
        back_populates="enzyme_class"
    )

    def __repr__(self) -> str:
        return f"<EnzymeClass(ec_number='{self.ec_number}', recommended_name='{self.recommended_name}')>"


class Organism(Base):
    """Organism information."""

    __tablename__ = "organism"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    tax_id: Mapped[Optional[int]]

    proteins: Mapped[list["Protein"]] = relationship(back_populates="organism")
    reactions: Mapped[list["Reaction"]] = relationship(
        secondary="reaction__organism", back_populates="organisms"
    )
    source_tissues: Mapped[list["SourceTissue"]] = relationship(
        secondary="source_tissue__organism", back_populates="organisms"
    )
    localizations: Mapped[list["Localization"]] = relationship(
        secondary="localization__organism", back_populates="organisms"
    )
    natural_substrates_products: Mapped[list["NaturalSubstrateProduct"]] = relationship(
        secondary="natural_substrate_product__organism", back_populates="organisms"
    )
    substrates_products: Mapped[list["SubstrateProduct"]] = relationship(
        secondary="substrate_product__organism", back_populates="organisms"
    )
    turnover_numbers: Mapped[list["TurnoverNumber"]] = relationship(
        secondary="turnover_number__organism", back_populates="organisms"
    )
    km_values: Mapped[list["KmValue"]] = relationship(
        secondary="km_value__organism", back_populates="organisms"
    )
    ph_optimums: Mapped[list["PhOptimum"]] = relationship(
        secondary="ph_optimum__organism", back_populates="organisms"
    )
    ph_ranges: Mapped[list["PhRange"]] = relationship(
        secondary="ph_range__organism", back_populates="organisms"
    )
    specific_activities: Mapped[list["SpecificActivity"]] = relationship(
        secondary="specific_activity__organism", back_populates="organisms"
    )
    temperature_optimums: Mapped[list["TemperatureOptimum"]] = relationship(
        secondary="temperature_optimum__organism", back_populates="organisms"
    )
    temperature_ranges: Mapped[list["TemperatureRange"]] = relationship(
        secondary="temperature_range__organism", back_populates="organisms"
    )
    activating_compounds: Mapped[list["ActivatingCompound"]] = relationship(
        secondary="activating_compound__organism", back_populates="organisms"
    )
    inhibitors: Mapped[list["Inhibitor"]] = relationship(
        secondary="inhibitor__organism", back_populates="organisms"
    )
    metal_ions: Mapped[list["MetalIon"]] = relationship(
        secondary="metal_ion__organism", back_populates="organisms"
    )
    molecular_weights: Mapped[list["MolecularWeight"]] = relationship(
        secondary="molecular_weight__organism", back_populates="organisms"
    )
    posttranslational_modifications: Mapped[list["PosttranslationalModification"]] = (
        relationship(
            secondary="posttranslational_modification__organism",
            back_populates="organisms",
        )
    )
    subunits: Mapped[list["Subunit"]] = relationship(
        secondary="subunit__organism", back_populates="organisms"
    )
    pi_values: Mapped[list["PiValue"]] = relationship(
        secondary="pi_value__organism", back_populates="organisms"
    )
    applications: Mapped[list["Application"]] = relationship(
        secondary="application__organism", back_populates="organisms"
    )
    protein_variants: Mapped[list["ProteinVariant"]] = relationship(
        secondary="protein_variant__organism", back_populates="organisms"
    )
    ki_values: Mapped[list["KiValue"]] = relationship(
        secondary="ki_value__organism", back_populates="organisms"
    )
    kcat_km_values: Mapped[list["KcatKmValue"]] = relationship(
        secondary="kcat_km_value__organism", back_populates="organisms"
    )
    expressions: Mapped[list["Expression"]] = relationship(
        secondary="expression__organism", back_populates="organisms"
    )
    general_information: Mapped[list["GeneralInformation"]] = relationship(
        secondary="general_information__organism", back_populates="organisms"
    )
    organic_solvent_stabilities: Mapped[list["OrganicSolventStability"]] = relationship(
        secondary="organic_solvent_stability__organism", back_populates="organisms"
    )
    ph_stabilities: Mapped[list["PhStability"]] = relationship(
        secondary="ph_stability__organism", back_populates="organisms"
    )
    temperature_stabilities: Mapped[list["TemperatureStability"]] = relationship(
        secondary="temperature_stability__organism", back_populates="organisms"
    )

    def __repr__(self) -> str:
        return f"<Organism(tax_id='{self.tax_id}', name='{self.name}')>"


class Protein(Base):
    """Protein variant from specific organism."""

    __tablename__ = "protein"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))
    organism_id: Mapped[Optional[int]] = mapped_column(ForeignKey("organism.id"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="proteins")
    organism: Mapped[Optional["Organism"]] = relationship(back_populates="proteins")
    references: Mapped[list["Reference"]] = relationship(
        secondary="protein__reference",  # back_populates="proteins"
    )

    def __repr__(self) -> str:
        return f"<Protein(id='{self.id}', organism='{self.organism}')>"


class ProteinReference(Base):
    """Association table for Protein and Reference."""

    __tablename__ = "protein__reference"
    # primary keys
    protein_id: Mapped[int] = mapped_column(ForeignKey("protein.id"), primary_key=True)
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class Reference(Base):
    """Literature reference."""

    __tablename__ = "reference"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[Optional[str]] = mapped_column(Text)
    journal: Mapped[Optional[str]]
    year: Mapped[Optional[int]]
    pages: Mapped[Optional[str]]
    volume: Mapped[Optional[str]]
    pmid: Mapped[Optional[int]] = mapped_column(index=True)

    # Relationships
    proteins: Mapped[list["Protein"]] = relationship(
        secondary="protein__reference", back_populates="references"
    )
    authors: Mapped[list["Author"]] = relationship(
        secondary="reference__author", back_populates="references"
    )
    reactions: Mapped[list["Reaction"]] = relationship(
        secondary="reaction__reference", back_populates="references"
    )
    source_tissues: Mapped[list["SourceTissue"]] = relationship(
        secondary="source_tissue__reference", back_populates="references"
    )
    localizations: Mapped[list["Localization"]] = relationship(
        secondary="localization__reference", back_populates="references"
    )
    natural_substrates_products: Mapped[list["NaturalSubstrateProduct"]] = relationship(
        secondary="natural_substrate_product__reference", back_populates="references"
    )
    substrates_products: Mapped[list["SubstrateProduct"]] = relationship(
        secondary="substrate_product__reference", back_populates="references"
    )
    turnover_numbers: Mapped[list["TurnoverNumber"]] = relationship(
        secondary="turnover_number__reference", back_populates="references"
    )
    km_values: Mapped[list["KmValue"]] = relationship(
        secondary="km_value__reference", back_populates="references"
    )
    ph_optimums: Mapped[list["PhOptimum"]] = relationship(
        secondary="ph_optimum__reference", back_populates="references"
    )
    ph_ranges: Mapped[list["PhRange"]] = relationship(
        secondary="ph_range__reference", back_populates="references"
    )
    specific_activities: Mapped[list["SpecificActivity"]] = relationship(
        secondary="specific_activity__reference", back_populates="references"
    )
    temperature_optimums: Mapped[list["TemperatureOptimum"]] = relationship(
        secondary="temperature_optimum__reference", back_populates="references"
    )
    temperature_ranges: Mapped[list["TemperatureRange"]] = relationship(
        secondary="temperature_range__reference", back_populates="references"
    )
    activating_compounds: Mapped[list["ActivatingCompound"]] = relationship(
        secondary="activating_compound__reference", back_populates="references"
    )
    inhibitors: Mapped[list["Inhibitor"]] = relationship(
        secondary="inhibitor__reference", back_populates="references"
    )
    metal_ions: Mapped[list["MetalIon"]] = relationship(
        secondary="metal_ion__reference", back_populates="references"
    )
    molecular_weights: Mapped[list["MolecularWeight"]] = relationship(
        secondary="molecular_weight__reference", back_populates="references"
    )
    posttranslational_modifications: Mapped[list["PosttranslationalModification"]] = (
        relationship(
            secondary="posttranslational_modification__reference",
            back_populates="references",
        )
    )
    subunits: Mapped[list["Subunit"]] = relationship(
        secondary="subunit__reference", back_populates="references"
    )
    pi_values: Mapped[list["PiValue"]] = relationship(
        secondary="pi_value__reference", back_populates="references"
    )
    applications: Mapped[list["Application"]] = relationship(
        secondary="application__reference", back_populates="references"
    )
    protein_variants: Mapped[list["ProteinVariant"]] = relationship(
        secondary="protein_variant__reference", back_populates="references"
    )
    ki_values: Mapped[list["KiValue"]] = relationship(
        secondary="ki_value__reference", back_populates="references"
    )
    kcat_km_values: Mapped[list["KcatKmValue"]] = relationship(
        secondary="kcat_km_value__reference", back_populates="references"
    )
    expressions: Mapped[list["Expression"]] = relationship(
        secondary="expression__reference", back_populates="references"
    )
    general_information: Mapped[list["GeneralInformation"]] = relationship(
        secondary="general_information__reference", back_populates="references"
    )
    organic_solvent_stabilities: Mapped[list["OrganicSolventStability"]] = relationship(
        secondary="organic_solvent_stability__reference", back_populates="references"
    )
    ph_stabilities: Mapped[list["PhStability"]] = relationship(
        secondary="ph_stability__reference", back_populates="references"
    )
    temperature_stabilities: Mapped[list["TemperatureStability"]] = relationship(
        secondary="temperature_stability__reference", back_populates="references"
    )

    def __repr__(self) -> str:
        return f"<Reference(id='{self.id}', title='{self.title}')>"


class ReferenceAuthor(Base):
    """Association table for Reference and Author."""

    __tablename__ = "reference__author"
    # primary keys
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"), primary_key=True)


class Author(Base):
    """Authors of a reference."""

    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]

    references: Mapped[list["Reference"]] = relationship(
        secondary="reference__author", back_populates="authors"
    )


class Synonym(Base):
    """Enzyme synonym."""

    __tablename__ = "synonym"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str]

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="synonyms")


class Reaction(Base):
    """Reaction catalyzed by enzyme."""

    __tablename__ = "reaction"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str] = mapped_column(Text)
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="reactions")
    organisms: Mapped[list["Organism"]] = relationship(
        secondary="reaction__organism", back_populates="reactions"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary="reaction__reference", back_populates="reactions"
    )


class ReactionOrganism(Base):
    """Organism associated with a reaction."""

    __tablename__ = "reaction__organism"
    # primary keys
    reaction_id: Mapped[int] = mapped_column(
        ForeignKey("reaction.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey("organism.id"), primary_key=True
    )


class ReactionReference(Base):
    """Reference associated with a reaction."""

    __tablename__ = "reaction__reference"
    # primary keys
    reaction_id: Mapped[int] = mapped_column(
        ForeignKey("reaction.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class ReactionType(Base):
    """Type of reaction."""

    __tablename__ = "reaction_type"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str]

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="reaction_types")


class SourceTissue(Base):
    """Source tissue information."""

    __tablename__ = "source_tissue"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str]
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="source_tissues")
    organisms: Mapped[list["Organism"]] = relationship(
        secondary="source_tissue__organism", back_populates="source_tissues"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary="source_tissue__reference", back_populates="source_tissues"
    )


class SourceTissueOrganism(Base):
    """Organism associated with a source tissue."""

    __tablename__ = "source_tissue__organism"
    # primary keys
    source_tissue_id: Mapped[int] = mapped_column(
        ForeignKey("source_tissue.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey("organism.id"), primary_key=True
    )


class SourceTissueReference(Base):
    """Reference associated with a source tissue."""

    __tablename__ = "source_tissue__reference"
    # primary keys
    source_tissue_id: Mapped[int] = mapped_column(
        ForeignKey("source_tissue.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class Localization(Base):
    """Cellular localization."""

    __tablename__ = "localization"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str]
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    organisms: Mapped[list["Organism"]] = relationship(
        secondary="localization__organism", back_populates="localizations"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary="localization__reference", back_populates="localizations"
    )
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="localizations")


class LocalizationOrganism(Base):
    """Organism associated with a localization."""

    __tablename__ = "localization__organism"
    # primary keys
    localization_id: Mapped[int] = mapped_column(
        ForeignKey("localization.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey("organism.id"), primary_key=True
    )


class LocalizationReference(Base):
    """Reference associated with a localization."""

    __tablename__ = "localization__reference"
    # primary keys
    localization_id: Mapped[int] = mapped_column(
        ForeignKey("localization.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class NaturalSubstrateProduct(Base):
    """Natural substrate and product."""

    __tablename__ = "natural_substrate_product"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str] = mapped_column(Text)
    organisms: Mapped[list["Organism"]] = relationship(
        secondary="natural_substrate_product__organism",
        back_populates="natural_substrates_products",
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary="natural_substrate_product__reference",
        back_populates="natural_substrates_products",
    )
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(
        back_populates="natural_substrates_products"
    )


class NaturalSubstrateProductOrganism(Base):
    """Organism associated with a natural substrate/product."""

    __tablename__ = "natural_substrate_product__organism"
    # primary keys
    natural_substrate_product_id: Mapped[int] = mapped_column(
        ForeignKey("natural_substrate_product.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey("organism.id"), primary_key=True
    )


class NaturalSubstrateProductReference(Base):
    """Reference associated with a natural substrate/product."""

    __tablename__ = "natural_substrate_product__reference"
    # primary keys
    natural_substrate_product_id: Mapped[int] = mapped_column(
        ForeignKey("natural_substrate_product.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class SubstrateProduct(Base):
    """Substrate and product."""

    __tablename__ = "substrate_product"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str] = mapped_column(Text)
    organisms: Mapped[list["Organism"]] = relationship(
        secondary="substrate_product__organism", back_populates="substrates_products"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary="substrate_product__reference", back_populates="substrates_products"
    )
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(
        back_populates="substrates_products"
    )


class SubstrateProductOrganism(Base):
    """Organism associated with a substrate/product."""

    __tablename__ = "substrate_product__organism"
    # primary keys
    substrate_product_id: Mapped[int] = mapped_column(
        ForeignKey("substrate_product.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey("organism.id"), primary_key=True
    )


class SubstrateProductReference(Base):
    """Reference associated with a substrate/product."""

    __tablename__ = "substrate_product__reference"
    # primary keys
    substrate_product_id: Mapped[int] = mapped_column(
        ForeignKey("substrate_product.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class TurnoverNumber(Base):
    """Turnover number (kcat)."""

    __tablename__ = "turnover_number"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[float]
    value_max: Mapped[Optional[float]]
    organisms: Mapped[list["Organism"]] = relationship(
        secondary="turnover_number__organism", back_populates="turnover_numbers"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary="turnover_number__reference", back_populates="turnover_numbers"
    )
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))
    compound_id: Mapped[int] = mapped_column(ForeignKey("compound.id"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(
        back_populates="turnover_numbers"
    )
    compound: Mapped["Compound"] = relationship()


class TurnoverNumberOrganism(Base):
    """Organism associated with a turnover number."""

    __tablename__ = "turnover_number__organism"
    # primary keys
    turnover_number_id: Mapped[int] = mapped_column(
        ForeignKey("turnover_number.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey("organism.id"), primary_key=True
    )


class TurnoverNumberReference(Base):
    """Reference associated with a turnover number."""

    __tablename__ = "turnover_number__reference"
    # primary keys
    turnover_number_id: Mapped[int] = mapped_column(
        ForeignKey("turnover_number.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class KmValueOrganism(Base):
    """Organism associated with a km value."""

    __tablename__ = "km_value__organism"
    # primary keys
    km_value_id: Mapped[int] = mapped_column(
        ForeignKey("km_value.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey("organism.id"), primary_key=True
    )


class KmValueReference(Base):
    """Reference associated with a km value."""

    __tablename__ = "km_value__reference"
    # primary keys
    km_value_id: Mapped[int] = mapped_column(
        ForeignKey("km_value.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class PhOptimumOrganism(Base):
    """Organism associated with a ph optimum."""

    __tablename__ = "ph_optimum__organism"
    # primary keys
    ph_optimum_id: Mapped[int] = mapped_column(
        ForeignKey("ph_optimum.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey("organism.id"), primary_key=True
    )


class PhOptimumReference(Base):
    """Reference associated with a ph optimum."""

    __tablename__ = "ph_optimum__reference"
    # primary keys
    ph_optimum_id: Mapped[int] = mapped_column(
        ForeignKey("ph_optimum.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class PhRangeOrganism(Base):
    """Organism associated with a ph range."""

    __tablename__ = "ph_range__organism"
    # primary keys
    ph_range_id: Mapped[int] = mapped_column(
        ForeignKey("ph_range.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey("organism.id"), primary_key=True
    )


class PhRangeReference(Base):
    """Reference associated with a ph range."""

    __tablename__ = "ph_range__reference"
    # primary keys
    ph_range_id: Mapped[int] = mapped_column(
        ForeignKey("ph_range.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class SpecificActivityOrganism(Base):
    """Organism associated with a specific activity."""

    __tablename__ = "specific_activity__organism"
    # primary keys
    specific_activity_id: Mapped[int] = mapped_column(
        ForeignKey("specific_activity.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey("organism.id"), primary_key=True
    )


class SpecificActivityReference(Base):
    """Reference associated with a specific activity."""

    __tablename__ = "specific_activity__reference"
    # primary keys
    specific_activity_id: Mapped[int] = mapped_column(
        ForeignKey("specific_activity.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class TemperatureOptimumOrganism(Base):
    """Organism associated with a temperature optimum."""

    __tablename__ = "temperature_optimum__organism"
    # primary keys
    temperature_optimum_id: Mapped[int] = mapped_column(
        ForeignKey("temperature_optimum.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey("organism.id"), primary_key=True
    )


class TemperatureOptimumReference(Base):
    """Reference associated with a temperature optimum."""

    __tablename__ = "temperature_optimum__reference"
    # primary keys
    temperature_optimum_id: Mapped[int] = mapped_column(
        ForeignKey("temperature_optimum.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class TemperatureRangeOrganism(Base):
    """Organism associated with a temperature range."""

    __tablename__ = "temperature_range__organism"
    # primary keys
    temperature_range_id: Mapped[int] = mapped_column(
        ForeignKey("temperature_range.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey("organism.id"), primary_key=True
    )


class TemperatureRangeReference(Base):
    """Reference associated with a temperature range."""

    __tablename__ = "temperature_range__reference"
    # primary keys
    temperature_range_id: Mapped[int] = mapped_column(
        ForeignKey("temperature_range.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class ActivatingCompoundOrganism(Base):
    """Organism associated with a activating compound."""

    __tablename__ = "activating_compound__organism"
    # primary keys
    activating_compound_id: Mapped[int] = mapped_column(
        ForeignKey("activating_compound.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey("organism.id"), primary_key=True
    )


class ActivatingCompoundReference(Base):
    """Reference associated with a activating compound."""

    __tablename__ = "activating_compound__reference"
    # primary keys
    activating_compound_id: Mapped[int] = mapped_column(
        ForeignKey("activating_compound.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class InhibitorOrganism(Base):
    """Organism associated with a inhibitor."""

    __tablename__ = "inhibitor__organism"
    # primary keys
    inhibitor_id: Mapped[int] = mapped_column(
        ForeignKey("inhibitor.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey("organism.id"), primary_key=True
    )


class InhibitorReference(Base):
    """Reference associated with a inhibitor."""

    __tablename__ = "inhibitor__reference"
    # primary keys
    inhibitor_id: Mapped[int] = mapped_column(
        ForeignKey("inhibitor.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class MetalIonOrganism(Base):
    """Organism associated with a metal ion."""

    __tablename__ = "metal_ion__organism"
    # primary keys
    metal_ion_id: Mapped[int] = mapped_column(
        ForeignKey("metal_ion.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey("organism.id"), primary_key=True
    )


class MetalIonReference(Base):
    """Reference associated with a metal ion."""

    __tablename__ = "metal_ion__reference"
    # primary keys
    metal_ion_id: Mapped[int] = mapped_column(
        ForeignKey("metal_ion.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class MolecularWeightOrganism(Base):
    """Organism associated with a molecular weight."""

    __tablename__ = "molecular_weight__organism"
    # primary keys
    molecular_weight_id: Mapped[int] = mapped_column(
        ForeignKey("molecular_weight.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey("organism.id"), primary_key=True
    )


class MolecularWeightReference(Base):
    """Reference associated with a molecular weight."""

    __tablename__ = "molecular_weight__reference"
    # primary keys
    molecular_weight_id: Mapped[int] = mapped_column(
        ForeignKey("molecular_weight.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class PosttranslationalModificationOrganism(Base):
    """Organism associated with a posttranslational modification."""

    __tablename__ = "posttranslational_modification__organism"
    # primary keys
    posttranslational_modification_id: Mapped[int] = mapped_column(
        ForeignKey("posttranslational_modification.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey("organism.id"), primary_key=True
    )


class PosttranslationalModificationReference(Base):
    """Reference associated with a posttranslational modification."""

    __tablename__ = "posttranslational_modification__reference"
    # primary keys
    posttranslational_modification_id: Mapped[int] = mapped_column(
        ForeignKey("posttranslational_modification.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class SubunitOrganism(Base):
    """Organism associated with a subunit."""

    __tablename__ = "subunit__organism"
    # primary keys
    subunit_id: Mapped[int] = mapped_column(ForeignKey("subunit.id"), primary_key=True)
    organism_id: Mapped[int] = mapped_column(
        ForeignKey("organism.id"), primary_key=True
    )


class SubunitReference(Base):
    """Reference associated with a subunit."""

    __tablename__ = "subunit__reference"
    # primary keys
    subunit_id: Mapped[int] = mapped_column(ForeignKey("subunit.id"), primary_key=True)
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class PiValueOrganism(Base):
    """Organism associated with a pi value."""

    __tablename__ = "pi_value__organism"
    # primary keys
    pi_value_id: Mapped[int] = mapped_column(
        ForeignKey("pi_value.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey("organism.id"), primary_key=True
    )


class PiValueReference(Base):
    """Reference associated with a pi value."""

    __tablename__ = "pi_value__reference"
    # primary keys
    pi_value_id: Mapped[int] = mapped_column(
        ForeignKey("pi_value.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class ApplicationOrganism(Base):
    """Organism associated with a application."""

    __tablename__ = "application__organism"
    # primary keys
    application_id: Mapped[int] = mapped_column(
        ForeignKey("application.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey("organism.id"), primary_key=True
    )


class ApplicationReference(Base):
    """Reference associated with a application."""

    __tablename__ = "application__reference"
    # primary keys
    application_id: Mapped[int] = mapped_column(
        ForeignKey("application.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class ProteinVariantOrganism(Base):
    """Organism associated with a protein variant."""

    __tablename__ = "protein_variant__organism"
    # primary keys
    protein_variant_id: Mapped[int] = mapped_column(
        ForeignKey("protein_variant.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey("organism.id"), primary_key=True
    )


class ProteinVariantReference(Base):
    """Reference associated with a protein variant."""

    __tablename__ = "protein_variant__reference"
    # primary keys
    protein_variant_id: Mapped[int] = mapped_column(
        ForeignKey("protein_variant.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class KiValueOrganism(Base):
    """Organism associated with a ki value."""

    __tablename__ = "ki_value__organism"
    # primary keys
    ki_value_id: Mapped[int] = mapped_column(
        ForeignKey("ki_value.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey("organism.id"), primary_key=True
    )


class KiValueReference(Base):
    """Reference associated with a ki value."""

    __tablename__ = "ki_value__reference"
    # primary keys
    ki_value_id: Mapped[int] = mapped_column(
        ForeignKey("ki_value.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class KcatKmValueOrganism(Base):
    """Organism associated with a kcat km value."""

    __tablename__ = "kcat_km_value__organism"
    # primary keys
    kcat_km_value_id: Mapped[int] = mapped_column(
        ForeignKey("kcat_km_value.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey("organism.id"), primary_key=True
    )


class KcatKmValueReference(Base):
    """Reference associated with a kcat km value."""

    __tablename__ = "kcat_km_value__reference"
    # primary keys
    kcat_km_value_id: Mapped[int] = mapped_column(
        ForeignKey("kcat_km_value.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class ExpressionOrganism(Base):
    """Organism associated with a expression."""

    __tablename__ = "expression__organism"
    # primary keys
    expression_id: Mapped[int] = mapped_column(
        ForeignKey("expression.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey("organism.id"), primary_key=True
    )


class ExpressionReference(Base):
    """Reference associated with a expression."""

    __tablename__ = "expression__reference"
    # primary keys
    expression_id: Mapped[int] = mapped_column(
        ForeignKey("expression.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class GeneralInformationOrganism(Base):
    """Organism associated with a general information."""

    __tablename__ = "general_information__organism"
    # primary keys
    general_information_id: Mapped[int] = mapped_column(
        ForeignKey("general_information.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey("organism.id"), primary_key=True
    )


class GeneralInformationReference(Base):
    """Reference associated with a general information."""

    __tablename__ = "general_information__reference"
    # primary keys
    general_information_id: Mapped[int] = mapped_column(
        ForeignKey("general_information.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class OrganicSolventStabilityOrganism(Base):
    """Organism associated with a organic solvent stability."""

    __tablename__ = "organic_solvent_stability__organism"
    # primary keys
    organic_solvent_stability_id: Mapped[int] = mapped_column(
        ForeignKey("organic_solvent_stability.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey("organism.id"), primary_key=True
    )


class OrganicSolventStabilityReference(Base):
    """Reference associated with a organic solvent stability."""

    __tablename__ = "organic_solvent_stability__reference"
    # primary keys
    organic_solvent_stability_id: Mapped[int] = mapped_column(
        ForeignKey("organic_solvent_stability.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class PhStabilityOrganism(Base):
    """Organism associated with a ph stability."""

    __tablename__ = "ph_stability__organism"
    # primary keys
    ph_stability_id: Mapped[int] = mapped_column(
        ForeignKey("ph_stability.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey("organism.id"), primary_key=True
    )


class PhStabilityReference(Base):
    """Reference associated with a ph stability."""

    __tablename__ = "ph_stability__reference"
    # primary keys
    ph_stability_id: Mapped[int] = mapped_column(
        ForeignKey("ph_stability.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class TemperatureStabilityOrganism(Base):
    """Organism associated with a temperature stability."""

    __tablename__ = "temperature_stability__organism"
    # primary keys
    temperature_stability_id: Mapped[int] = mapped_column(
        ForeignKey("temperature_stability.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey("organism.id"), primary_key=True
    )


class TemperatureStabilityReference(Base):
    """Reference associated with a temperature stability."""

    __tablename__ = "temperature_stability__reference"
    # primary keys
    temperature_stability_id: Mapped[int] = mapped_column(
        ForeignKey("temperature_stability.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey("reference.id"), primary_key=True
    )


class Compound(Base):
    """Compound used in Km, Ki, or Kcat/Km values."""

    __tablename__ = "compound"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, unique=True)
    inchikey: Mapped[Optional[str]]
    ki_values: Mapped[list["KiValue"]] = relationship(back_populates="compound")
    km_values: Mapped[list["KmValue"]] = relationship(back_populates="compound")
    kcat_km_values: Mapped[list["KcatKmValue"]] = relationship(
        back_populates="compound"
    )


class KmValue(Base):
    """Km value."""

    __tablename__ = "km_value"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[float]
    value_max: Mapped[Optional[float]]
    organisms: Mapped[list["Organism"]] = relationship(
        secondary="km_value__organism", back_populates="km_values"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary="km_value__reference", back_populates="km_values"
    )
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))
    compound_id: Mapped[int] = mapped_column(ForeignKey("compound.id"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="km_values")
    compound: Mapped[Compound] = relationship(back_populates="km_values")


class PhOptimum(Base):
    """pH optimum."""

    __tablename__ = "ph_optimum"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str]
    organisms: Mapped[list["Organism"]] = relationship(
        secondary="ph_optimum__organism", back_populates="ph_optimums"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary="ph_optimum__reference", back_populates="ph_optimums"
    )
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="ph_optima")


class PhRange(Base):
    """pH range."""

    __tablename__ = "ph_range"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str]
    organisms: Mapped[list["Organism"]] = relationship(
        secondary="ph_range__organism", back_populates="ph_ranges"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary="ph_range__reference", back_populates="ph_ranges"
    )
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="ph_ranges")


class SpecificActivity(Base):
    """Specific activity."""

    __tablename__ = "specific_activity"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str]
    organisms: Mapped[list["Organism"]] = relationship(
        secondary="specific_activity__organism", back_populates="specific_activities"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary="specific_activity__reference", back_populates="specific_activities"
    )
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(
        back_populates="specific_activities"
    )


class TemperatureOptimum(Base):
    """Temperature optimum."""

    __tablename__ = "temperature_optimum"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str]
    organisms: Mapped[list["Organism"]] = relationship(
        secondary="temperature_optimum__organism", back_populates="temperature_optimums"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary="temperature_optimum__reference",
        back_populates="temperature_optimums",
    )
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(
        back_populates="temperature_optima"
    )


class TemperatureRange(Base):
    """Temperature range."""

    __tablename__ = "temperature_range"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str]
    organisms: Mapped[list["Organism"]] = relationship(
        secondary="temperature_range__organism", back_populates="temperature_ranges"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary="temperature_range__reference", back_populates="temperature_ranges"
    )
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(
        back_populates="temperature_ranges"
    )


class ActivatingCompound(Base):
    """Activating compound."""

    __tablename__ = "activating_compound"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str]
    organisms: Mapped[list["Organism"]] = relationship(
        secondary="activating_compound__organism", back_populates="activating_compounds"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary="activating_compound__reference",
        back_populates="activating_compounds",
    )
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(
        back_populates="activating_compounds"
    )


class Inhibitor(Base):
    """Inhibitor."""

    __tablename__ = "inhibitor"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str]
    organisms: Mapped[list["Organism"]] = relationship(
        secondary="inhibitor__organism", back_populates="inhibitors"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary="inhibitor__reference", back_populates="inhibitors"
    )
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="inhibitors")


class MetalIon(Base):
    """Metal ion requirement."""

    __tablename__ = "metal_ion"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str]
    organisms: Mapped[list["Organism"]] = relationship(
        secondary="metal_ion__organism", back_populates="metal_ions"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary="metal_ion__reference", back_populates="metal_ions"
    )
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="metals_ions")


class MolecularWeight(Base):
    """Molecular weight."""

    __tablename__ = "molecular_weight"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str]
    organisms: Mapped[list["Organism"]] = relationship(
        secondary="molecular_weight__organism", back_populates="molecular_weights"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary="molecular_weight__reference", back_populates="molecular_weights"
    )
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(
        back_populates="molecular_weights"
    )


class PosttranslationalModification(Base):
    """Posttranslational modification."""

    __tablename__ = "posttranslational_modification"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str]
    organisms: Mapped[list["Organism"]] = relationship(
        secondary="posttranslational_modification__organism",
        back_populates="posttranslational_modifications",
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary="posttranslational_modification__reference",
        back_populates="posttranslational_modifications",
    )
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(
        back_populates="posttranslational_modifications"
    )


class Subunit(Base):
    """Subunit structure."""

    __tablename__ = "subunit"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str]
    organisms: Mapped[list["Organism"]] = relationship(
        secondary="subunit__organism", back_populates="subunits"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary="subunit__reference", back_populates="subunits"
    )
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="subunits")


class PiValue(Base):
    """Isoelectric point."""

    __tablename__ = "pi_value"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str]
    organisms: Mapped[list["Organism"]] = relationship(
        secondary="pi_value__organism", back_populates="pi_values"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary="pi_value__reference", back_populates="pi_values"
    )
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="pi_values")


class Application(Base):
    """Application information."""

    __tablename__ = "application"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str] = mapped_column(Text)
    organisms: Mapped[list["Organism"]] = relationship(
        secondary="application__organism", back_populates="applications"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary="application__reference", back_populates="applications"
    )
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="applications")


class ProteinVariant(Base):
    """Protein variant/mutation."""

    __tablename__ = "protein_variant"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str]
    organisms: Mapped[list["Organism"]] = relationship(
        secondary="protein_variant__organism", back_populates="protein_variants"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary="protein_variant__reference", back_populates="protein_variants"
    )
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(
        back_populates="protein_variants"
    )


class ClonedInfo(Base):
    """Cloning information."""

    __tablename__ = "cloned_info"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    proteins: Mapped[Optional[str]]  # Stored as comma-separated
    references: Mapped[Optional[str]]  # Stored as comma-separated
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="cloned_info")


class Purification(Base):
    """Purification information."""

    __tablename__ = "purification"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    proteins: Mapped[Optional[str]]  # Stored as comma-separated
    references: Mapped[Optional[str]]  # Stored as comma-separated
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="purifications")


class GeneralStability(Base):
    """General stability information."""

    __tablename__ = "general_stability"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    proteins: Mapped[Optional[str]]  # Stored as comma-separated
    references: Mapped[Optional[str]]  # Stored as comma-separated
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(
        back_populates="general_stabilities"
    )


class OrganicSolventStability(Base):
    """Organic solvent stability."""

    __tablename__ = "organic_solvent_stability"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str]
    organisms: Mapped[list["Organism"]] = relationship(
        secondary="organic_solvent_stability__organism",
        back_populates="organic_solvent_stabilities",
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary="organic_solvent_stability__reference",
        back_populates="organic_solvent_stabilities",
    )
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(
        back_populates="organic_solvent_stabilities"
    )


class PhStability(Base):
    """pH stability."""

    __tablename__ = "ph_stability"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str]
    organisms: Mapped[list["Organism"]] = relationship(
        secondary="ph_stability__organism", back_populates="ph_stabilities"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary="ph_stability__reference", back_populates="ph_stabilities"
    )
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="ph_stabilities")


class StorageStability(Base):
    """Storage stability."""

    __tablename__ = "storage_stability"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    proteins: Mapped[Optional[str]]  # Stored as comma-separated
    references: Mapped[Optional[str]]  # Stored as comma-separated
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(
        back_populates="storage_stabilities"
    )


class TemperatureStability(Base):
    """Temperature stability."""

    __tablename__ = "temperature_stability"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str]
    organisms: Mapped[list["Organism"]] = relationship(
        secondary="temperature_stability__organism",
        back_populates="temperature_stabilities",
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary="temperature_stability__reference",
        back_populates="temperature_stabilities",
    )
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(
        back_populates="temperature_stabilities"
    )


class KiValue(Base):
    """Ki value."""

    __tablename__ = "ki_value"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[float]
    value_max: Mapped[Optional[float]]

    organisms: Mapped[list["Organism"]] = relationship(
        secondary="ki_value__organism", back_populates="ki_values"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary="ki_value__reference", back_populates="ki_values"
    )
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))
    compound_id: Mapped[int] = mapped_column(ForeignKey("compound.id"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="ki_values")
    compound: Mapped[Compound] = relationship(back_populates="ki_values")


class KcatKmValue(Base):
    """kcat/Km value."""

    __tablename__ = "kcat_km_value"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[float]
    value_max: Mapped[Optional[float]]
    organisms: Mapped[list["Organism"]] = relationship(
        secondary="kcat_km_value__organism", back_populates="kcat_km_values"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary="kcat_km_value__reference", back_populates="kcat_km_values"
    )
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))
    compound_id: Mapped[int] = mapped_column(ForeignKey("compound.id"))
    compound: Mapped[Compound] = relationship(back_populates="kcat_km_values")

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="kcat_km_values")


class Expression(Base):
    """Expression information."""

    __tablename__ = "expression"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str]
    organisms: Mapped[list["Organism"]] = relationship(
        secondary="expression__organism", back_populates="expressions"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary="expression__reference", back_populates="expressions"
    )
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="expressions")


class GeneralInformation(Base):
    """General information."""

    __tablename__ = "general_information"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str] = mapped_column(Text)
    organisms: Mapped[list["Organism"]] = relationship(
        secondary="general_information__organism", back_populates="general_information"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary="general_information__reference", back_populates="general_information"
    )
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    ec_number: Mapped[str] = mapped_column(ForeignKey("enzyme_class.ec_number"))

    # Relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(
        back_populates="general_information"
    )
