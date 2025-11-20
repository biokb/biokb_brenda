# BRENDA Data Import Models

This package provides SQLAlchemy models and import functionality for BRENDA enzyme data in JSON format.

## Overview

The BRENDA (BRaunschweig ENzyme DAtabase) importer allows you to:
- Import enzyme data from JSON files into a relational database
- Query enzyme information using SQLAlchemy ORM
- Access comprehensive enzyme properties including kinetics, stability, inhibitors, etc.

## Files

- `brenda_models.py` - SQLAlchemy model definitions for all BRENDA data types
- `brenda_importer.py` - Import functionality to load JSON data into database
- `brenda_example.py` - Example usage scripts
- `brenda_import_example.ipynb` - Interactive Jupyter notebook examples

## Database Schema

### Core Tables

**EnzymeClass** - Main enzyme entry identified by EC number
- `ec_number` (primary key)
- `recommended_name`
- `systematic_name`

**Protein** - Protein variants from specific organisms
- `id` (composite: ec_number#protein_number)
- `protein_number`
- `organism`
- `comment`

**Reference** - Literature references
- `id` (composite: ec_number#reference_number)
- `title`, `authors`, `journal`, `year`, `pages`, `volume`, `pmid`

### Property Tables

Each enzyme can have multiple entries for:
- `Synonym` - Alternative names
- `Reaction` - Catalyzed reactions
- `ReactionType` - Types of reactions
- `SourceTissue` - Tissue sources
- `Localization` - Cellular localization
- `NaturalSubstrateProduct` - Natural substrates/products
- `SubstrateProduct` - Substrates/products
- `TurnoverNumber` - kcat values
- `KmValue` - Km values
- `KiValue` - Ki values
- `KcatKmValue` - kcat/Km values
- `PhOptimum` - Optimal pH
- `PhRange` - pH activity range
- `PhStability` - pH stability
- `TemperatureOptimum` - Optimal temperature
- `TemperatureRange` - Temperature activity range
- `TemperatureStability` - Temperature stability
- `SpecificActivity` - Specific activity values
- `ActivatingCompound` - Activators
- `Inhibitor` - Inhibitors
- `MetalIon` - Metal ion requirements
- `MolecularWeight` - Molecular weights
- `PosttranslationalModification` - PTMs
- `Subunit` - Subunit structure
- `PiValue` - Isoelectric points
- `Application` - Applications
- `ProteinVariant` - Mutations/variants
- `ClonedInfo` - Cloning information
- `Purification` - Purification protocols
- `GeneralStability` - General stability info
- `OrganicSolventStability` - Organic solvent stability
- `StorageStability` - Storage conditions
- `Expression` - Expression patterns
- `GeneralInformation` - Other information

## Installation

Ensure you have the required dependencies:

```bash
pip install sqlalchemy
```

## Quick Start

### 1. Import from JSON file

```python
from plant_drug.db.brenda_importer import import_brenda_json

# Simple import
enzyme = import_brenda_json('brenda.json', 'sqlite:///brenda.db')
print(f"{enzyme.ec_number}: {enzyme.recommended_name}")
```

### 2. Using the BrendaImporter class

```python
from plant_drug.db.brenda_importer import BrendaImporter

# Create importer
importer = BrendaImporter("sqlite:///brenda.db")

# Create tables
importer.create_tables()

# Import data
enzyme = importer.import_from_file('brenda.json')

# Access data
print(f"EC Number: {enzyme.ec_number}")
print(f"Name: {enzyme.recommended_name}")
print(f"Proteins: {len(enzyme.proteins)}")
print(f"References: {len(enzyme.references)}")
```

### 3. Query the database

```python
from plant_drug.db.brenda_models import EnzymeClass, Protein, Inhibitor

# Get a session
session = importer.query_session()

# Query enzyme by EC number
enzyme = session.query(EnzymeClass).filter_by(ec_number="2.4.1.5").first()

# Find proteins from specific organism
e_coli = session.query(Protein).filter(
    Protein.organism.like('%Escherichia coli%')
).all()

# Find inhibitors containing copper
cu_inhibitors = session.query(Inhibitor).filter(
    Inhibitor.value.like('%Cu%')
).all()

session.close()
```

## Data Structure

The JSON format follows BRENDA's structure:

```json
{
  "id": "2.4.1.5",
  "recommended_name": "dextransucrase",
  "systematic_name": "sucrose:(1->6)-alpha-D-glucan 6-alpha-D-glucosyltransferase",
  "protein": {
    "1": {
      "id": "1",
      "organism": "Escherichia coli",
      "references": ["92"],
      "comment": ""
    }
  },
  "reference": {
    "1": {
      "id": "1",
      "title": "...",
      "authors": ["Author1", "Author2"],
      "journal": "...",
      "year": 2003,
      "pmid": 12681910
    }
  },
  "km_value": [
    {
      "value": "1.4 {sucrose}",
      "proteins": ["10"],
      "references": ["60"],
      "comment": "pH 7.0, 30°C, mutant R624G"
    }
  ]
}
```

## Examples

### Access Kinetic Parameters

```python
# Get Km values
for km in enzyme.km_values:
    print(f"Km: {km.value}")
    print(f"  Conditions: {km.comment}")
    print(f"  Proteins: {km.proteins}")

# Get turnover numbers
for kcat in enzyme.turnover_numbers:
    print(f"kcat: {kcat.value}")
```

### Access Optimal Conditions

```python
# pH optima
for ph in enzyme.ph_optima:
    print(f"pH optimum: {ph.value} - {ph.comment}")

# Temperature optima
for temp in enzyme.temperature_optima:
    print(f"Temperature optimum: {temp.value}°C - {temp.comment}")
```

### Access Inhibitors

```python
for inhibitor in enzyme.inhibitors:
    print(f"Inhibitor: {inhibitor.value}")
    if inhibitor.comment:
        print(f"  Effect: {inhibitor.comment}")
```

### Access References

```python
import json

for ref in enzyme.references:
    print(f"\n{ref.title}")
    if ref.authors:
        authors = json.loads(ref.authors)
        print(f"Authors: {', '.join(authors)}")
    print(f"Journal: {ref.journal} ({ref.year})")
    if ref.pmid:
        print(f"PMID: {ref.pmid}")
```

## Advanced Usage

### Custom Queries

```python
from sqlalchemy import func

session = importer.query_session()

# Count enzymes by reaction type
from plant_drug.db.brenda_models import ReactionType

reaction_counts = session.query(
    ReactionType.value, 
    func.count(ReactionType.id)
).group_by(ReactionType.value).all()

for reaction_type, count in reaction_counts:
    print(f"{reaction_type}: {count}")
```

### Export to DataFrame

```python
import pandas as pd

# Export Km values to DataFrame
km_data = []
for km in enzyme.km_values:
    km_data.append({
        'Value': km.value,
        'Proteins': km.proteins,
        'References': km.references,
        'Comment': km.comment
    })

df = pd.DataFrame(km_data)
print(df)
```

### Batch Import

```python
import glob

importer = BrendaImporter("sqlite:///brenda_all.db")
importer.create_tables()

# Import all JSON files
for json_file in glob.glob("data/*.json"):
    try:
        enzyme = importer.import_from_file(json_file)
        print(f"Imported: {enzyme.ec_number}")
    except Exception as e:
        print(f"Error importing {json_file}: {e}")
```

## Database Backends

The importer works with any SQLAlchemy-supported database:

```python
# SQLite (file-based)
importer = BrendaImporter("sqlite:///brenda.db")

# PostgreSQL
importer = BrendaImporter("postgresql://user:pass@localhost/brenda")

# MySQL
importer = BrendaImporter("mysql://user:pass@localhost/brenda")

# In-memory SQLite (testing)
importer = BrendaImporter("sqlite:///:memory:")
```

## Notes

- Protein and reference IDs are composite keys combining EC number and original ID
- List fields (proteins, references) are stored as comma-separated strings
- Author lists in references are stored as JSON strings
- All text fields support Unicode
- The importer handles updates - re-importing will update existing entries

## See Also

- [BRENDA Database](https://www.brenda-enzymes.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
