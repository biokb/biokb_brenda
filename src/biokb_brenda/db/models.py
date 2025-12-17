"""SQLAlchemy models for BRENDA enzyme data."""

import enum
from typing import Optional

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from biokb_brenda2.constants import PROJECT_NAME

table_prefix = PROJECT_NAME + "_"


class Base(DeclarativeBase):
    pass


class EnzymeClass(Base):
    """Main enzyme class identified by EC number."""

    __tablename__ = table_prefix + "enzyme_class"

    ec_number: Mapped[str] = mapped_column(String(30), primary_key=True)
    recommended_name: Mapped[Optional[str]] = mapped_column(String(500))
    systematic_name: Mapped[Optional[str]] = mapped_column(String(500))

    # relationships

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
    nsp_reactions: Mapped[list["NSPReaction"]] = relationship(
        back_populates="enzyme_class"
    )
    sp_reactions: Mapped[list["SPReaction"]] = relationship(
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
    metal_ions: Mapped[list["MetalIon"]] = relationship(back_populates="enzyme_class")
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
    ic50_values: Mapped[list["IC50Value"]] = relationship(back_populates="enzyme_class")
    cofactors: Mapped[list["Cofactor"]] = relationship(back_populates="enzyme_class")

    def __repr__(self) -> str:
        return f"<EnzymeClass(ec_number='{self.ec_number}', recommended_name='{self.recommended_name}')>"


class Organism(Base):
    """Organism information."""

    __tablename__ = table_prefix + "organism"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    tax_id: Mapped[Optional[int]] = mapped_column(default=None)

    proteins: Mapped[list["Protein"]] = relationship(back_populates="organism")
    reactions: Mapped[list["Reaction"]] = relationship(
        secondary=table_prefix + "reaction__organism", back_populates="organisms"
    )
    source_tissues: Mapped[list["SourceTissue"]] = relationship(
        secondary=table_prefix + "source_tissue__organism", back_populates="organisms"
    )
    localizations: Mapped[list["Localization"]] = relationship(
        secondary=table_prefix + "localization__organism", back_populates="organisms"
    )
    nsp_reactions: Mapped[list["NSPReaction"]] = relationship(
        secondary=table_prefix + "nsp_reaction__organism", back_populates="organisms"
    )
    sp_reactions: Mapped[list["SPReaction"]] = relationship(
        secondary=table_prefix + "sp_reaction__organism", back_populates="organisms"
    )
    turnover_numbers: Mapped[list["TurnoverNumber"]] = relationship(
        secondary=table_prefix + "turnover_number__organism", back_populates="organisms"
    )
    km_values: Mapped[list["KmValue"]] = relationship(
        secondary=table_prefix + "km_value__organism", back_populates="organisms"
    )
    ph_optimums: Mapped[list["PhOptimum"]] = relationship(
        secondary=table_prefix + "ph_optimum__organism", back_populates="organisms"
    )
    ph_ranges: Mapped[list["PhRange"]] = relationship(
        secondary=table_prefix + "ph_range__organism", back_populates="organisms"
    )
    specific_activities: Mapped[list["SpecificActivity"]] = relationship(
        secondary=table_prefix + "specific_activity__organism",
        back_populates="organisms",
    )
    temperature_optimums: Mapped[list["TemperatureOptimum"]] = relationship(
        secondary=table_prefix + "temperature_optimum__organism",
        back_populates="organisms",
    )
    temperature_ranges: Mapped[list["TemperatureRange"]] = relationship(
        secondary=table_prefix + "temperature_range__organism",
        back_populates="organisms",
    )
    activating_compounds: Mapped[list["ActivatingCompound"]] = relationship(
        secondary=table_prefix + "activating_compound__organism",
        back_populates="organisms",
    )
    inhibitors: Mapped[list["Inhibitor"]] = relationship(
        secondary=table_prefix + "inhibitor__organism", back_populates="organisms"
    )
    metal_ions: Mapped[list["MetalIon"]] = relationship(
        secondary=table_prefix + "metal_ion__organism", back_populates="organisms"
    )
    molecular_weights: Mapped[list["MolecularWeight"]] = relationship(
        secondary=table_prefix + "molecular_weight__organism",
        back_populates="organisms",
    )
    posttranslational_modifications: Mapped[list["PosttranslationalModification"]] = (
        relationship(
            secondary=table_prefix + "posttranslational_modification__organism",
            back_populates="organisms",
        )
    )
    subunits: Mapped[list["Subunit"]] = relationship(
        secondary=table_prefix + "subunit__organism", back_populates="organisms"
    )
    pi_values: Mapped[list["PiValue"]] = relationship(
        secondary=table_prefix + "pi_value__organism", back_populates="organisms"
    )
    applications: Mapped[list["Application"]] = relationship(
        secondary=table_prefix + "application__organism", back_populates="organisms"
    )
    protein_variants: Mapped[list["ProteinVariant"]] = relationship(
        secondary=table_prefix + "protein_variant__organism", back_populates="organisms"
    )
    ki_values: Mapped[list["KiValue"]] = relationship(
        secondary=table_prefix + "ki_value__organism", back_populates="organisms"
    )
    kcat_km_values: Mapped[list["KcatKmValue"]] = relationship(
        secondary=table_prefix + "kcat_km_value__organism", back_populates="organisms"
    )
    expressions: Mapped[list["Expression"]] = relationship(
        secondary=table_prefix + "expression__organism", back_populates="organisms"
    )
    general_information: Mapped[list["GeneralInformation"]] = relationship(
        secondary=table_prefix + "general_information__organism",
        back_populates="organisms",
    )
    organic_solvent_stabilities: Mapped[list["OrganicSolventStability"]] = relationship(
        secondary=table_prefix + "organic_solvent_stability__organism",
        back_populates="organisms",
    )
    ph_stabilities: Mapped[list["PhStability"]] = relationship(
        secondary=table_prefix + "ph_stability__organism", back_populates="organisms"
    )
    temperature_stabilities: Mapped[list["TemperatureStability"]] = relationship(
        secondary=table_prefix + "temperature_stability__organism",
        back_populates="organisms",
    )
    cloned_infos: Mapped[list["ClonedInfo"]] = relationship(
        secondary=table_prefix + "cloned_info__organism", back_populates="organisms"
    )
    purifications: Mapped[list["Purification"]] = relationship(
        secondary=table_prefix + "purification__organism", back_populates="organisms"
    )
    general_stabilities: Mapped[list["GeneralStability"]] = relationship(
        secondary=table_prefix + "general_stability__organism",
        back_populates="organisms",
    )
    storage_stabilities: Mapped[list["StorageStability"]] = relationship(
        secondary=table_prefix + "storage_stability__organism",
        back_populates="organisms",
    )
    ic50_values: Mapped[list["IC50Value"]] = relationship(
        secondary=table_prefix + "ic50_value__organism", back_populates="organisms"
    )
    cofactors: Mapped[list["Cofactor"]] = relationship(
        secondary=table_prefix + "cofactor__organism", back_populates="organisms"
    )

    def __repr__(self) -> str:
        return f"<Organism(tax_id='{self.tax_id}', name='{self.name}')>"


class Protein(Base):
    """Protein variant from specific organism."""

    __tablename__ = table_prefix + "protein"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )
    organism_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(table_prefix + "organism.id")
    )

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="proteins")
    organism: Mapped[Optional["Organism"]] = relationship(back_populates="proteins")
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "protein__reference",  # back_populates="proteins"
    )

    def __repr__(self) -> str:
        return f"<Protein(id='{self.id}', organism='{self.organism}')>"


class ProteinReference(Base):
    """Association table for Protein and Reference."""

    __tablename__ = table_prefix + "protein__reference"
    # primary keys
    protein_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "protein.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class Reference(Base):
    """Literature reference."""

    __tablename__ = table_prefix + "reference"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[Optional[str]] = mapped_column(Text)
    journal: Mapped[Optional[str]] = mapped_column(String(255))
    year: Mapped[Optional[int]]
    pages: Mapped[Optional[str]] = mapped_column(String(50))
    volume: Mapped[Optional[str]] = mapped_column(String(50))
    pmid: Mapped[Optional[int]] = mapped_column(index=True)

    # relationships
    proteins: Mapped[list["Protein"]] = relationship(
        secondary=table_prefix + "protein__reference", back_populates="references"
    )
    authors: Mapped[list["Author"]] = relationship(
        secondary=table_prefix + "reference__author", back_populates="references"
    )
    reactions: Mapped[list["Reaction"]] = relationship(
        secondary=table_prefix + "reaction__reference", back_populates="references"
    )
    source_tissues: Mapped[list["SourceTissue"]] = relationship(
        secondary=table_prefix + "source_tissue__reference", back_populates="references"
    )
    localizations: Mapped[list["Localization"]] = relationship(
        secondary=table_prefix + "localization__reference", back_populates="references"
    )
    nsp_reactions: Mapped[list["NSPReaction"]] = relationship(
        secondary=table_prefix + "nsp_reaction__reference",
        back_populates="references",
    )
    sp_reactions: Mapped[list["SPReaction"]] = relationship(
        secondary=table_prefix + "sp_reaction__reference", back_populates="references"
    )
    turnover_numbers: Mapped[list["TurnoverNumber"]] = relationship(
        secondary=table_prefix + "turnover_number__reference",
        back_populates="references",
    )
    km_values: Mapped[list["KmValue"]] = relationship(
        secondary=table_prefix + "km_value__reference", back_populates="references"
    )
    ph_optimums: Mapped[list["PhOptimum"]] = relationship(
        secondary=table_prefix + "ph_optimum__reference", back_populates="references"
    )
    ph_ranges: Mapped[list["PhRange"]] = relationship(
        secondary=table_prefix + "ph_range__reference", back_populates="references"
    )
    specific_activities: Mapped[list["SpecificActivity"]] = relationship(
        secondary=table_prefix + "specific_activity__reference",
        back_populates="references",
    )
    temperature_optimums: Mapped[list["TemperatureOptimum"]] = relationship(
        secondary=table_prefix + "temperature_optimum__reference",
        back_populates="references",
    )
    temperature_ranges: Mapped[list["TemperatureRange"]] = relationship(
        secondary=table_prefix + "temperature_range__reference",
        back_populates="references",
    )
    activating_compounds: Mapped[list["ActivatingCompound"]] = relationship(
        secondary=table_prefix + "activating_compound__reference",
        back_populates="references",
    )
    inhibitors: Mapped[list["Inhibitor"]] = relationship(
        secondary=table_prefix + "inhibitor__reference", back_populates="references"
    )
    metal_ions: Mapped[list["MetalIon"]] = relationship(
        secondary=table_prefix + "metal_ion__reference", back_populates="references"
    )
    molecular_weights: Mapped[list["MolecularWeight"]] = relationship(
        secondary=table_prefix + "molecular_weight__reference",
        back_populates="references",
    )
    posttranslational_modifications: Mapped[list["PosttranslationalModification"]] = (
        relationship(
            secondary=table_prefix + "posttranslational_modification__reference",
            back_populates="references",
        )
    )
    subunits: Mapped[list["Subunit"]] = relationship(
        secondary=table_prefix + "subunit__reference", back_populates="references"
    )
    pi_values: Mapped[list["PiValue"]] = relationship(
        secondary=table_prefix + "pi_value__reference", back_populates="references"
    )
    applications: Mapped[list["Application"]] = relationship(
        secondary=table_prefix + "application__reference", back_populates="references"
    )
    protein_variants: Mapped[list["ProteinVariant"]] = relationship(
        secondary=table_prefix + "protein_variant__reference",
        back_populates="references",
    )
    ki_values: Mapped[list["KiValue"]] = relationship(
        secondary=table_prefix + "ki_value__reference", back_populates="references"
    )
    kcat_km_values: Mapped[list["KcatKmValue"]] = relationship(
        secondary=table_prefix + "kcat_km_value__reference", back_populates="references"
    )
    expressions: Mapped[list["Expression"]] = relationship(
        secondary=table_prefix + "expression__reference", back_populates="references"
    )
    general_information: Mapped[list["GeneralInformation"]] = relationship(
        secondary=table_prefix + "general_information__reference",
        back_populates="references",
    )
    organic_solvent_stabilities: Mapped[list["OrganicSolventStability"]] = relationship(
        secondary=table_prefix + "organic_solvent_stability__reference",
        back_populates="references",
    )
    ph_stabilities: Mapped[list["PhStability"]] = relationship(
        secondary=table_prefix + "ph_stability__reference", back_populates="references"
    )
    temperature_stabilities: Mapped[list["TemperatureStability"]] = relationship(
        secondary=table_prefix + "temperature_stability__reference",
        back_populates="references",
    )
    cloned_infos: Mapped[list["ClonedInfo"]] = relationship(
        secondary=table_prefix + "cloned_info__reference", back_populates="references"
    )
    purifications: Mapped[list["Purification"]] = relationship(
        secondary=table_prefix + "purification__reference", back_populates="references"
    )
    general_stabilities: Mapped[list["GeneralStability"]] = relationship(
        secondary=table_prefix + "general_stability__reference",
        back_populates="references",
    )
    storage_stabilities: Mapped[list["StorageStability"]] = relationship(
        secondary=table_prefix + "storage_stability__reference",
        back_populates="references",
    )
    ic50_values: Mapped[list["IC50Value"]] = relationship(
        secondary=table_prefix + "ic50_value__reference", back_populates="references"
    )
    cofactors: Mapped[list["Cofactor"]] = relationship(
        secondary=table_prefix + "cofactor__reference", back_populates="references"
    )

    # create index on title, journal,year,pages,volume
    __table_args__ = (
        Index(
            "ix_reference_multi",  # Name des Index
            "title",
            "journal",
            "year",
            "pages",
            "volume",
            mysql_length={
                "title": 255,
            },
        ),
    )

    def __repr__(self) -> str:
        return f"<Reference(id='{self.id}', title='{self.title}')>"


class ReferenceAuthor(Base):
    """Association table for Reference and Author."""

    __tablename__ = table_prefix + "reference__author"
    # primary keys
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "author.id"), primary_key=True
    )


class Author(Base):
    """Authors of a reference."""

    __tablename__ = table_prefix + "author"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))

    # relationships
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "reference__author", back_populates="authors"
    )


class Synonym(Base):
    """Enzyme synonym."""

    __tablename__ = table_prefix + "synonym"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str] = mapped_column(String(255))

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="synonyms")


class Reaction(Base):
    """Reaction catalyzed by enzyme."""

    __tablename__ = table_prefix + "reaction"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str] = mapped_column(Text)
    reversibility: Mapped[Optional[bool]]
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="reactions")
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "reaction__organism", back_populates="reactions"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "reaction__reference", back_populates="reactions"
    )
    substrates: Mapped[list["Compound"]] = relationship(
        secondary=table_prefix + "reaction_substrate",
        back_populates="reactions_as_substrate",
    )
    products: Mapped[list["Compound"]] = relationship(
        secondary=table_prefix + "reaction_product",
        back_populates="reactions_as_product",
    )


class ReactionSubstrate(Base):
    __tablename__ = table_prefix + "reaction_substrate"

    reaction_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reaction.id"), primary_key=True
    )
    compound_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "compound.id"), primary_key=True
    )


class ReactionProduct(Base):
    __tablename__ = table_prefix + "reaction_product"

    reaction_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reaction.id"), primary_key=True
    )
    compound_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "compound.id"), primary_key=True
    )


class ReactionOrganism(Base):
    """Organism associated with a reaction."""

    __tablename__ = table_prefix + "reaction__organism"
    # primary keys
    reaction_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reaction.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class ReactionReference(Base):
    """Reference associated with a reaction."""

    __tablename__ = table_prefix + "reaction__reference"
    # primary keys
    reaction_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reaction.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class ReactionType(Base):
    """Type of reaction."""

    __tablename__ = table_prefix + "reaction_type"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str] = mapped_column(String(255))

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="reaction_types")


class SourceTissue(Base):
    """Source tissue information."""

    __tablename__ = table_prefix + "source_tissue"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str] = mapped_column(String(255))
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="source_tissues")
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "source_tissue__organism",
        back_populates="source_tissues",
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "source_tissue__reference",
        back_populates="source_tissues",
    )


class SourceTissueOrganism(Base):
    """Organism associated with a source tissue."""

    __tablename__ = table_prefix + "source_tissue__organism"
    # primary keys
    source_tissue_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "source_tissue.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class SourceTissueReference(Base):
    """Reference associated with a source tissue."""

    __tablename__ = table_prefix + "source_tissue__reference"
    # primary keys
    source_tissue_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "source_tissue.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class Localization(Base):
    """Cellular localization."""

    __tablename__ = table_prefix + "localization"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str] = mapped_column(String(255))
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )

    # relationships
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "localization__organism",
        back_populates="localizations",
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "localization__reference",
        back_populates="localizations",
    )
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="localizations")


class LocalizationOrganism(Base):
    """Organism associated with a localization."""

    __tablename__ = table_prefix + "localization__organism"
    # primary keys
    localization_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "localization.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class LocalizationReference(Base):
    """Reference associated with a localization."""

    __tablename__ = table_prefix + "localization__reference"
    # primary keys
    localization_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "localization.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class NSPReaction(Base):
    """Natural substrate and product reaction."""

    __tablename__ = table_prefix + "nsp_reaction"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str] = mapped_column(Text)  # reaction string
    comment: Mapped[Optional[str]] = mapped_column(Text)
    reversibility: Mapped[Optional[bool]]

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="nsp_reactions")
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "nsp_reaction__organism",
        back_populates="nsp_reactions",
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "nsp_reaction__reference",
        back_populates="nsp_reactions",
    )
    substrates: Mapped[list["Compound"]] = relationship(
        secondary=table_prefix + "nsp_reaction_substrate",
        back_populates="nsp_reactions_as_substrate",
    )
    products: Mapped[list["Compound"]] = relationship(
        secondary=table_prefix + "nsp_reaction_product",
        back_populates="nsp_reactions_as_product",
    )


class NSPReactionSubstrate(Base):
    __tablename__ = table_prefix + "nsp_reaction_substrate"

    nsp_reaction_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "nsp_reaction.id"), primary_key=True
    )
    compound_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "compound.id"), primary_key=True
    )


class NSPReactionProduct(Base):
    __tablename__ = table_prefix + "nsp_reaction_product"

    nsp_reaction_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "nsp_reaction.id"), primary_key=True
    )
    compound_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "compound.id"), primary_key=True
    )


class NSPReactionOrganism(Base):
    """Organism associated with a natural substrate/product."""

    __tablename__ = table_prefix + "nsp_reaction__organism"
    # primary keys
    nsp_reaction_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "nsp_reaction.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class NSPReactionReference(Base):
    """Reference associated with a natural substrate/product."""

    __tablename__ = table_prefix + "nsp_reaction__reference"
    # primary keys
    nsp_reaction_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "nsp_reaction.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class SPReaction(Base):
    """Substrate and product reaction."""

    __tablename__ = table_prefix + "sp_reaction"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str] = mapped_column(Text)
    reversibility: Mapped[Optional[bool]]
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="sp_reactions")
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "sp_reaction__organism", back_populates="sp_reactions"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "sp_reaction__reference", back_populates="sp_reactions"
    )
    substrates: Mapped[list["Compound"]] = relationship(
        secondary=table_prefix + "sp_reaction_substrate",
        back_populates="sp_reactions_as_substrate",
    )
    products: Mapped[list["Compound"]] = relationship(
        secondary=table_prefix + "sp_reaction_product",
        back_populates="sp_reactions_as_product",
    )


class SPReactionSubstrate(Base):
    __tablename__ = table_prefix + "sp_reaction_substrate"

    nsp_reaction_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "sp_reaction.id"), primary_key=True
    )
    compound_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "compound.id"), primary_key=True
    )


class SPReactionProduct(Base):
    __tablename__ = table_prefix + "sp_reaction_product"

    nsp_reaction_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "sp_reaction.id"), primary_key=True
    )
    compound_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "compound.id"), primary_key=True
    )


class SPReactionOrganism(Base):
    """Organism associated with a substrate/product."""

    __tablename__ = table_prefix + "sp_reaction__organism"
    # primary keys
    sp_reaction_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "sp_reaction.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class SPReactionReference(Base):
    """Reference associated with a substrate/product."""

    __tablename__ = table_prefix + "sp_reaction__reference"
    # primary keys
    sp_reaction_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "sp_reaction.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class TurnoverNumber(Base):
    """Turnover number (kcat)."""

    __tablename__ = table_prefix + "turnover_number"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[float]
    value_max: Mapped[Optional[float]]
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )
    compound_id: Mapped[int] = mapped_column(ForeignKey(table_prefix + "compound.id"))

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(
        back_populates="turnover_numbers"
    )
    compound: Mapped["Compound"] = relationship()
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "turnover_number__organism",
        back_populates="turnover_numbers",
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "turnover_number__reference",
        back_populates="turnover_numbers",
    )


class TurnoverNumberOrganism(Base):
    """Organism associated with a turnover number."""

    __tablename__ = table_prefix + "turnover_number__organism"
    # primary keys
    turnover_number_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "turnover_number.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class TurnoverNumberReference(Base):
    """Reference associated with a turnover number."""

    __tablename__ = table_prefix + "turnover_number__reference"
    # primary keys
    turnover_number_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "turnover_number.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class KmValueOrganism(Base):
    """Organism associated with a km value."""

    __tablename__ = table_prefix + "km_value__organism"
    # primary keys
    km_value_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "km_value.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class KmValueReference(Base):
    """Reference associated with a km value."""

    __tablename__ = table_prefix + "km_value__reference"
    # primary keys
    km_value_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "km_value.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class PhOptimumOrganism(Base):
    """Organism associated with a ph optimum."""

    __tablename__ = table_prefix + "ph_optimum__organism"
    # primary keys
    ph_optimum_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "ph_optimum.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class PhOptimumReference(Base):
    """Reference associated with a ph optimum."""

    __tablename__ = table_prefix + "ph_optimum__reference"
    # primary keys
    ph_optimum_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "ph_optimum.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class PhRangeOrganism(Base):
    """Organism associated with a ph range."""

    __tablename__ = table_prefix + "ph_range__organism"
    # primary keys
    ph_range_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "ph_range.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class PhRangeReference(Base):
    """Reference associated with a ph range."""

    __tablename__ = table_prefix + "ph_range__reference"
    # primary keys
    ph_range_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "ph_range.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class SpecificActivityOrganism(Base):
    """Organism associated with a specific activity."""

    __tablename__ = table_prefix + "specific_activity__organism"
    # primary keys
    specific_activity_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "specific_activity.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class SpecificActivityReference(Base):
    """Reference associated with a specific activity."""

    __tablename__ = table_prefix + "specific_activity__reference"
    # primary keys
    specific_activity_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "specific_activity.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class TemperatureOptimumOrganism(Base):
    """Organism associated with a temperature optimum."""

    __tablename__ = table_prefix + "temperature_optimum__organism"
    # primary keys
    temperature_optimum_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "temperature_optimum.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class TemperatureOptimumReference(Base):
    """Reference associated with a temperature optimum."""

    __tablename__ = table_prefix + "temperature_optimum__reference"
    # primary keys
    temperature_optimum_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "temperature_optimum.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class TemperatureRangeOrganism(Base):
    """Organism associated with a temperature range."""

    __tablename__ = table_prefix + "temperature_range__organism"
    # primary keys
    temperature_range_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "temperature_range.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class TemperatureRangeReference(Base):
    """Reference associated with a temperature range."""

    __tablename__ = table_prefix + "temperature_range__reference"
    # primary keys
    temperature_range_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "temperature_range.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class ActivatingCompoundOrganism(Base):
    """Organism associated with a activating compound."""

    __tablename__ = table_prefix + "activating_compound__organism"
    # primary keys
    activating_compound_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "activating_compound.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class ActivatingCompoundReference(Base):
    """Reference associated with a activating compound."""

    __tablename__ = table_prefix + "activating_compound__reference"
    # primary keys
    activating_compound_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "activating_compound.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class InhibitorOrganism(Base):
    """Organism associated with a inhibitor."""

    __tablename__ = table_prefix + "inhibitor__organism"
    # primary keys
    inhibitor_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "inhibitor.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class InhibitorReference(Base):
    """Reference associated with a inhibitor."""

    __tablename__ = table_prefix + "inhibitor__reference"
    # primary keys
    inhibitor_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "inhibitor.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class MetalIonOrganism(Base):
    """Organism associated with a metal ion."""

    __tablename__ = table_prefix + "metal_ion__organism"
    # primary keys
    metal_ion_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "metal_ion.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class MetalIonReference(Base):
    """Reference associated with a metal ion."""

    __tablename__ = table_prefix + "metal_ion__reference"
    # primary keys
    metal_ion_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "metal_ion.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class MolecularWeightOrganism(Base):
    """Organism associated with a molecular weight."""

    __tablename__ = table_prefix + "molecular_weight__organism"
    # primary keys
    molecular_weight_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "molecular_weight.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class MolecularWeightReference(Base):
    """Reference associated with a molecular weight."""

    __tablename__ = table_prefix + "molecular_weight__reference"
    # primary keys
    molecular_weight_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "molecular_weight.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class PosttranslationalModificationOrganism(Base):
    """Organism associated with a posttranslational modification."""

    __tablename__ = table_prefix + "posttranslational_modification__organism"
    # primary keys
    posttranslational_modification_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "posttranslational_modification.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class PosttranslationalModificationReference(Base):
    """Reference associated with a posttranslational modification."""

    __tablename__ = table_prefix + "posttranslational_modification__reference"
    # primary keys
    posttranslational_modification_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "posttranslational_modification.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class SubunitOrganism(Base):
    """Organism associated with a subunit."""

    __tablename__ = table_prefix + "subunit__organism"
    # primary keys
    subunit_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "subunit.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class SubunitReference(Base):
    """Reference associated with a subunit."""

    __tablename__ = table_prefix + "subunit__reference"
    # primary keys
    subunit_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "subunit.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class PiValueOrganism(Base):
    """Organism associated with a pi value."""

    __tablename__ = table_prefix + "pi_value__organism"
    # primary keys
    pi_value_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "pi_value.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class PiValueReference(Base):
    """Reference associated with a pi value."""

    __tablename__ = table_prefix + "pi_value__reference"
    # primary keys
    pi_value_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "pi_value.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class ApplicationOrganism(Base):
    """Organism associated with a application."""

    __tablename__ = table_prefix + "application__organism"
    # primary keys
    application_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "application.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class ApplicationReference(Base):
    """Reference associated with a application."""

    __tablename__ = table_prefix + "application__reference"
    # primary keys
    application_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "application.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class ProteinVariantOrganism(Base):
    """Organism associated with a protein variant."""

    __tablename__ = table_prefix + "protein_variant__organism"
    # primary keys
    protein_variant_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "protein_variant.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class ProteinVariantReference(Base):
    """Reference associated with a protein variant."""

    __tablename__ = table_prefix + "protein_variant__reference"
    # primary keys
    protein_variant_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "protein_variant.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class KiValueOrganism(Base):
    """Organism associated with a ki value."""

    __tablename__ = table_prefix + "ki_value__organism"
    # primary keys
    ki_value_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "ki_value.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class KiValueReference(Base):
    """Reference associated with a ki value."""

    __tablename__ = table_prefix + "ki_value__reference"
    # primary keys
    ki_value_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "ki_value.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class KcatKmValueOrganism(Base):
    """Organism associated with a kcat km value."""

    __tablename__ = table_prefix + "kcat_km_value__organism"
    # primary keys
    kcat_km_value_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "kcat_km_value.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class KcatKmValueReference(Base):
    """Reference associated with a kcat km value."""

    __tablename__ = table_prefix + "kcat_km_value__reference"
    # primary keys
    kcat_km_value_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "kcat_km_value.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class ExpressionOrganism(Base):
    """Organism associated with a expression."""

    __tablename__ = table_prefix + "expression__organism"
    # primary keys
    expression_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "expression.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class ExpressionReference(Base):
    """Reference associated with a expression."""

    __tablename__ = table_prefix + "expression__reference"
    # primary keys
    expression_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "expression.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class GeneralInformationOrganism(Base):
    """Organism associated with a general information."""

    __tablename__ = table_prefix + "general_information__organism"
    # primary keys
    general_information_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "general_information.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class GeneralInformationReference(Base):
    """Reference associated with a general information."""

    __tablename__ = table_prefix + "general_information__reference"
    # primary keys
    general_information_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "general_information.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class OrganicSolventStabilityOrganism(Base):
    """Organism associated with a organic solvent stability."""

    __tablename__ = table_prefix + "organic_solvent_stability__organism"
    # primary keys
    organic_solvent_stability_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organic_solvent_stability.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class OrganicSolventStabilityReference(Base):
    """Reference associated with a organic solvent stability."""

    __tablename__ = table_prefix + "organic_solvent_stability__reference"
    # primary keys
    organic_solvent_stability_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organic_solvent_stability.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class PhStabilityOrganism(Base):
    """Organism associated with a ph stability."""

    __tablename__ = table_prefix + "ph_stability__organism"
    # primary keys
    ph_stability_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "ph_stability.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class PhStabilityReference(Base):
    """Reference associated with a ph stability."""

    __tablename__ = table_prefix + "ph_stability__reference"
    # primary keys
    ph_stability_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "ph_stability.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class TemperatureStabilityOrganism(Base):
    """Organism associated with a temperature stability."""

    __tablename__ = table_prefix + "temperature_stability__organism"
    # primary keys
    temperature_stability_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "temperature_stability.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class TemperatureStabilityReference(Base):
    """Reference associated with a temperature stability."""

    __tablename__ = table_prefix + "temperature_stability__reference"
    # primary keys
    temperature_stability_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "temperature_stability.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class Compound(Base):
    """Compound used in Km, Ki, or Kcat/Km values."""

    __tablename__ = table_prefix + "compound"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text)
    inchi: Mapped[Optional[str]] = mapped_column(Text)
    inchi_key: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    chebi_id: Mapped[Optional[int]] = mapped_column(index=True)
    brenda_ligand_id: Mapped[Optional[int]]

    # relationships
    ki_values: Mapped[list["KiValue"]] = relationship(back_populates="compound")
    ic50_values: Mapped[list["IC50Value"]] = relationship(back_populates="compound")
    km_values: Mapped[list["KmValue"]] = relationship(back_populates="compound")
    kcat_km_values: Mapped[list["KcatKmValue"]] = relationship(
        back_populates="compound"
    )
    inhibitors: Mapped[list["Inhibitor"]] = relationship(back_populates="compound")
    metal_ions: Mapped[list["MetalIon"]] = relationship(back_populates="compound")
    organic_solvent_stabilities: Mapped[list["OrganicSolventStability"]] = relationship(
        back_populates="compound"
    )
    nsp_reactions_as_substrate: Mapped[list["NSPReaction"]] = relationship(
        secondary=table_prefix + "nsp_reaction_substrate", back_populates="substrates"
    )
    nsp_reactions_as_product: Mapped[list["NSPReaction"]] = relationship(
        secondary=table_prefix + "nsp_reaction_product", back_populates="products"
    )
    sp_reactions_as_substrate: Mapped[list["SPReaction"]] = relationship(
        secondary=table_prefix + "sp_reaction_substrate", back_populates="substrates"
    )
    sp_reactions_as_product: Mapped[list["SPReaction"]] = relationship(
        secondary=table_prefix + "sp_reaction_product", back_populates="products"
    )
    reactions_as_substrate: Mapped[list["Reaction"]] = relationship(
        secondary=table_prefix + "reaction_substrate", back_populates="substrates"
    )
    reactions_as_product: Mapped[list["Reaction"]] = relationship(
        secondary=table_prefix + "reaction_product", back_populates="products"
    )
    cofactors: Mapped[list["Cofactor"]] = relationship(back_populates="compound")
    activating_compounds: Mapped[list["ActivatingCompound"]] = relationship(
        back_populates="compound"
    )

    __table_args__ = (
        Index(
            "ix_compound__name",
            name,
            mysql_length=255,
        ),
        Index(
            "ix_compound__inchi",
            inchi,
            mysql_length=255,
        ),
    )


class KmValue(Base):
    """Km value."""

    __tablename__ = table_prefix + "km_value"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[float]
    value_max: Mapped[Optional[float]]

    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )
    compound_id: Mapped[int] = mapped_column(ForeignKey(table_prefix + "compound.id"))

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="km_values")
    compound: Mapped[Compound] = relationship(back_populates="km_values")
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "km_value__organism", back_populates="km_values"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "km_value__reference", back_populates="km_values"
    )


class Cofactor(Base):
    """Cofactor required for enzyme activity."""

    __tablename__ = table_prefix + "cofactor"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )
    compound_id: Mapped[int] = mapped_column(ForeignKey(table_prefix + "compound.id"))

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="cofactors")
    compound: Mapped[Compound] = relationship(back_populates="cofactors")
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "cofactor__organism", back_populates="cofactors"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "cofactor__reference", back_populates="cofactors"
    )


class CofactorOrganism(Base):
    """Organism associated with a cofactor."""

    __tablename__ = table_prefix + "cofactor__organism"
    # primary keys
    cofactor_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "cofactor.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class CofactorReference(Base):
    """Reference associated with a cofactor."""

    __tablename__ = table_prefix + "cofactor__reference"
    # primary keys
    cofactor_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "cofactor.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class IC50Value(Base):
    """IC50 value."""

    __tablename__ = table_prefix + "ic50_value"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[float]
    value_max: Mapped[Optional[float]]

    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )
    compound_id: Mapped[int] = mapped_column(ForeignKey(table_prefix + "compound.id"))

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="ic50_values")
    compound: Mapped[Compound] = relationship(back_populates="ic50_values")
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "ic50_value__organism", back_populates="ic50_values"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "ic50_value__reference", back_populates="ic50_values"
    )


class IC50ValueOrganism(Base):
    """Organism associated with a ic50 value."""

    __tablename__ = table_prefix + "ic50_value__organism"
    # primary keys
    ic50_value_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "ic50_value.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class IC50ValueReference(Base):
    """Reference associated with a ic50 value."""

    __tablename__ = table_prefix + "ic50_value__reference"
    # primary keys
    ic50_value_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "ic50_value.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class PhOptimum(Base):
    """pH optimum."""

    __tablename__ = table_prefix + "ph_optimum"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[float]
    value_max: Mapped[Optional[float]]
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="ph_optima")
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "ph_optimum__organism", back_populates="ph_optimums"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "ph_optimum__reference", back_populates="ph_optimums"
    )


class PhRange(Base):
    """pH range."""

    __tablename__ = table_prefix + "ph_range"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[float]
    value_max: Mapped[Optional[float]]
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="ph_ranges")
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "ph_range__organism", back_populates="ph_ranges"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "ph_range__reference", back_populates="ph_ranges"
    )


class SpecificActivity(Base):
    """Specific activity."""

    __tablename__ = table_prefix + "specific_activity"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[float]
    value_max: Mapped[Optional[float]]
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(
        back_populates="specific_activities"
    )
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "specific_activity__organism",
        back_populates="specific_activities",
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "specific_activity__reference",
        back_populates="specific_activities",
    )


class TemperatureOptimum(Base):
    """Temperature optimum."""

    __tablename__ = table_prefix + "temperature_optimum"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[float]
    value_max: Mapped[Optional[float]]
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(
        back_populates="temperature_optima"
    )
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "temperature_optimum__organism",
        back_populates="temperature_optimums",
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "temperature_optimum__reference",
        back_populates="temperature_optimums",
    )


class TemperatureRange(Base):
    """Temperature range."""

    __tablename__ = table_prefix + "temperature_range"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[float]
    value_max: Mapped[Optional[float]]
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(
        back_populates="temperature_ranges"
    )
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "temperature_range__organism",
        back_populates="temperature_ranges",
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "temperature_range__reference",
        back_populates="temperature_ranges",
    )


class ActivatingCompound(Base):
    """Activating compound."""

    __tablename__ = table_prefix + "activating_compound"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    compound_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(table_prefix + "compound.id")
    )
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(
        back_populates="activating_compounds"
    )
    compound: Mapped[Optional["Compound"]] = relationship(
        back_populates="activating_compounds"
    )
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "activating_compound__organism",
        back_populates="activating_compounds",
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "activating_compound__reference",
        back_populates="activating_compounds",
    )


class Inhibitor(Base):
    """Inhibitor."""

    __tablename__ = table_prefix + "inhibitor"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    compound_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(table_prefix + "compound.id")
    )
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="inhibitors")
    compound: Mapped[Optional["Compound"]] = relationship(back_populates="inhibitors")
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "inhibitor__organism", back_populates="inhibitors"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "inhibitor__reference", back_populates="inhibitors"
    )


class MetalIon(Base):
    """Metal ion requirement."""

    __tablename__ = table_prefix + "metal_ion"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )
    compound_id: Mapped[int] = mapped_column(ForeignKey(table_prefix + "compound.id"))

    # relationships
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "metal_ion__organism", back_populates="metal_ions"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "metal_ion__reference", back_populates="metal_ions"
    )
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="metal_ions")
    compound: Mapped["Compound"] = relationship(back_populates="metal_ions")


class MolecularWeight(Base):
    """Molecular weight."""

    __tablename__ = table_prefix + "molecular_weight"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[float]
    value_max: Mapped[Optional[float]]
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(
        back_populates="molecular_weights"
    )
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "molecular_weight__organism",
        back_populates="molecular_weights",
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "molecular_weight__reference",
        back_populates="molecular_weights",
    )


class PosttranslationalModification(Base):
    """Posttranslational modification."""

    __tablename__ = table_prefix + "posttranslational_modification"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str] = mapped_column(String(500))
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(
        back_populates="posttranslational_modifications"
    )
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "posttranslational_modification__organism",
        back_populates="posttranslational_modifications",
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "posttranslational_modification__reference",
        back_populates="posttranslational_modifications",
    )


class Subunit(Base):
    """Subunit structure."""

    __tablename__ = table_prefix + "subunit"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str] = mapped_column(String(500))
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="subunits")
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "subunit__organism", back_populates="subunits"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "subunit__reference", back_populates="subunits"
    )


class PiValue(Base):
    """Isoelectric point."""

    __tablename__ = table_prefix + "pi_value"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[float]
    value_max: Mapped[Optional[float]]
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="pi_values")
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "pi_value__organism", back_populates="pi_values"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "pi_value__reference", back_populates="pi_values"
    )


class Application(Base):
    """Application information."""

    __tablename__ = table_prefix + "application"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str] = mapped_column(Text)
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="applications")
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "application__organism", back_populates="applications"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "application__reference", back_populates="applications"
    )


class ProteinVariant(Base):
    """Protein variant/mutation."""

    __tablename__ = table_prefix + "protein_variant"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str] = mapped_column(String(500))
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(
        back_populates="protein_variants"
    )
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "protein_variant__organism",
        back_populates="protein_variants",
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "protein_variant__reference",
        back_populates="protein_variants",
    )


class ClonedInfo(Base):
    """Cloning information."""

    __tablename__ = table_prefix + "cloned_info"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="cloned_info")
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "cloned_info__organism", back_populates="cloned_infos"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "cloned_info__reference", back_populates="cloned_infos"
    )


class ClonedInfoOrganism(Base):
    """Organism associated with a cloned info."""

    __tablename__ = table_prefix + "cloned_info__organism"
    # primary keys
    cloned_info_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "cloned_info.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class ClonedInfoReference(Base):
    """Reference associated with a cloned info."""

    __tablename__ = table_prefix + "cloned_info__reference"
    # primary keys
    cloned_info_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "cloned_info.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class Purification(Base):
    """Purification information."""

    __tablename__ = table_prefix + "purification"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="purifications")
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "purification__organism",
        back_populates="purifications",
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "purification__reference",
        back_populates="purifications",
    )


class PurificationOrganism(Base):
    """Organism associated with a purification."""

    __tablename__ = table_prefix + "purification__organism"
    # primary keys
    purification_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "purification.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class PurificationReference(Base):
    """Reference associated with a purification."""

    __tablename__ = table_prefix + "purification__reference"
    # primary keys
    purification_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "purification.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class GeneralStability(Base):
    """General stability information."""

    __tablename__ = table_prefix + "general_stability"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(
        back_populates="general_stabilities"
    )
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "general_stability__organism",
        back_populates="general_stabilities",
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "general_stability__reference",
        back_populates="general_stabilities",
    )


class GeneralStabilityOrganism(Base):
    """Organism associated with a general stability."""

    __tablename__ = table_prefix + "general_stability__organism"
    # primary keys
    general_stability_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "general_stability.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class GeneralStabilityReference(Base):
    """Reference associated with a general stability."""

    __tablename__ = table_prefix + "general_stability__reference"
    # primary keys
    general_stability_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "general_stability.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class OrganicSolventStability(Base):
    """Organic solvent stability."""

    __tablename__ = table_prefix + "organic_solvent_stability"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )
    compound_id: Mapped[int] = mapped_column(ForeignKey(table_prefix + "compound.id"))

    # relationships
    compound: Mapped["Compound"] = relationship(
        back_populates="organic_solvent_stabilities"
    )
    enzyme_class: Mapped["EnzymeClass"] = relationship(
        back_populates="organic_solvent_stabilities"
    )
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "organic_solvent_stability__organism",
        back_populates="organic_solvent_stabilities",
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "organic_solvent_stability__reference",
        back_populates="organic_solvent_stabilities",
    )


class PhStability(Base):
    """pH stability."""

    __tablename__ = table_prefix + "ph_stability"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[float]
    value_max: Mapped[Optional[float]]
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="ph_stabilities")
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "ph_stability__organism",
        back_populates="ph_stabilities",
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "ph_stability__reference",
        back_populates="ph_stabilities",
    )


class StorageStability(Base):
    """Storage stability."""

    __tablename__ = table_prefix + "storage_stability"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(
        back_populates="storage_stabilities"
    )
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "storage_stability__organism",
        back_populates="storage_stabilities",
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "storage_stability__reference",
        back_populates="storage_stabilities",
    )


class StorageStabilityOrganism(Base):
    """Organism associated with a storage stability."""

    __tablename__ = table_prefix + "storage_stability__organism"
    # primary keys
    storage_stability_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "storage_stability.id"), primary_key=True
    )
    organism_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "organism.id"), primary_key=True
    )


class StorageStabilityReference(Base):
    """Reference associated with a storage stability."""

    __tablename__ = table_prefix + "storage_stability__reference"
    # primary keys
    storage_stability_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "storage_stability.id"), primary_key=True
    )
    reference_id: Mapped[int] = mapped_column(
        ForeignKey(table_prefix + "reference.id"), primary_key=True
    )


class TemperatureStability(Base):
    """Temperature stability."""

    __tablename__ = table_prefix + "temperature_stability"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[float]
    value_max: Mapped[Optional[float]]
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(
        back_populates="temperature_stabilities"
    )
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "temperature_stability__organism",
        back_populates="temperature_stabilities",
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "temperature_stability__reference",
        back_populates="temperature_stabilities",
    )


class KiValue(Base):
    """Ki value."""

    __tablename__ = table_prefix + "ki_value"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[float]
    value_max: Mapped[Optional[float]]
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )
    compound_id: Mapped[int] = mapped_column(ForeignKey(table_prefix + "compound.id"))

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="ki_values")
    compound: Mapped[Compound] = relationship(back_populates="ki_values")
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "ki_value__organism", back_populates="ki_values"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "ki_value__reference", back_populates="ki_values"
    )


class KcatKmValue(Base):
    """kcat/Km value."""

    __tablename__ = table_prefix + "kcat_km_value"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[float]
    value_max: Mapped[Optional[float]]
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )
    compound_id: Mapped[int] = mapped_column(ForeignKey(table_prefix + "compound.id"))

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="kcat_km_values")
    compound: Mapped[Compound] = relationship(back_populates="kcat_km_values")
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "kcat_km_value__organism",
        back_populates="kcat_km_values",
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "kcat_km_value__reference",
        back_populates="kcat_km_values",
    )


class Expression(Base):
    """Expression information."""

    __tablename__ = table_prefix + "expression"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str] = mapped_column(String(500))
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(back_populates="expressions")
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "expression__organism", back_populates="expressions"
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "expression__reference", back_populates="expressions"
    )


class GeneralInformation(Base):
    """General information."""

    __tablename__ = table_prefix + "general_information"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str] = mapped_column(Text)

    comment: Mapped[Optional[str]] = mapped_column(Text)

    # foreign keys
    ec_number: Mapped[str] = mapped_column(
        ForeignKey(table_prefix + "enzyme_class.ec_number")
    )

    # relationships
    enzyme_class: Mapped["EnzymeClass"] = relationship(
        back_populates="general_information"
    )
    organisms: Mapped[list["Organism"]] = relationship(
        secondary=table_prefix + "general_information__organism",
        back_populates="general_information",
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=table_prefix + "general_information__reference",
        back_populates="general_information",
    )


class CompInchiChebi(Base):
    """Ligand information."""

    __tablename__ = table_prefix + "comp_inchi_chebi"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    compound_name: Mapped[str] = mapped_column(Text)
    inchi: Mapped[Optional[str]] = mapped_column(Text)
    chebi_id: Mapped[Optional[str]] = mapped_column(String(20))

    __table_args__ = (
        Index(
            "ix_comp_inchi_chebi__compound_name",
            compound_name,
            mysql_length=255,
        ),
    )


class CompLigChebi(Base):
    """Ligand information with BRENDA ligand ID."""

    __tablename__ = table_prefix + "comp_lig_chebi"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    compound_name: Mapped[str] = mapped_column(Text)
    brenda_ligand_id: Mapped[Optional[int]]
    chebi_id: Mapped[Optional[str]] = mapped_column(String(20))

    __table_args__ = (
        Index(
            "ix_comp_lig_chebi__compound_name",
            compound_name,
            mysql_length=255,
        ),
    )


class TaxonomyNameTypes(enum.Enum):
    ACRONYM = "acronym"
    AUTHORITY = "authority"
    BLAST_NAME = "blast name"
    COMMON_NAME = "common name"
    EQUIVALENT_NAME = "equivalent name"
    GENBANK_ACRONYM = "genbank acronym"
    GENBANK_COMMON_NAME = "genbank common name"
    IN_PART = "in-part"
    INCLUDES = "includes"
    SCIENTIFIC_NAME = "scientific name"
    SYNONYM = "synonym"
    TYPE_MATERIAL = "type material"


class TaxonomyName(Base):
    """Class definition for table taxonomy_name. Name from
    NCBI taxonomy https://www.ncbi.nlm.nih.gov/taxonomys."""

    __tablename__ = table_prefix + "taxonomy_name"
    __table_args__ = {"comment": "Taxonomy names by NCBI"}
    id: Mapped[int] = mapped_column(primary_key=True)
    tax_id: Mapped[int] = mapped_column(index=True, comment="NCBI taxonomy Identifier")
    name: Mapped[str] = mapped_column(Text)
    name_type: Mapped[str] = mapped_column(
        SQLEnum(*[e.value for e in TaxonomyNameTypes]), index=True
    )

    __table_args__ = (
        Index(
            "ix_taxonomy_name__name",
            name,
            mysql_length=255,
        ),
    )


class ChebiName(Base):
    """ChEBI names."""

    __tablename__ = table_prefix + "chebi_name"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chebi_id: Mapped[int]
    name: Mapped[str] = mapped_column(Text)

    __table_args__ = (
        Index(
            "ix_chebi_name__name",
            name,
            mysql_length=255,
        ),
    )


class ChebiInchi(Base):
    """ChEBI InChI keys."""

    __tablename__ = table_prefix + "chebi_inchi"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chebi_id: Mapped[int] = mapped_column(index=True)
    inchi: Mapped[str] = mapped_column(Text)

    __table_args__ = (
        Index(
            "ix_chebi_inchi__inchi",
            inchi,
            mysql_length=255,
        ),
    )
