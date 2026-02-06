"""API tags for BRENDA enzyme database endpoints."""

from enum import StrEnum


class Tag(StrEnum):
    """API endpoint tags for organizing documentation."""

    DBMANAGE = "Database Management"
    ENZYME = "Enzyme Classes"
    ORGANISM = "Organisms"
    COMPOUND = "Compounds"
    REFERENCE = "References"
    REACTION = "Reactions"
    KINETICS = "Kinetic Parameters"
    PH_TEMP = "pH and Temperature"
    STABILITY = "Stability"
    PROTEIN = "Protein Properties"
    COFACTOR = "Cofactors and Effectors"
    INFO = "General Information"
