"""
Template for generating mock data in Fabric notebooks.

This script can be adapted for any source by updating the template configuration.
For Alexis HR reference implementation, see the spec.
"""

# %% [markdown]
# # Mock Data Generation - Template
#
# **Purpose**: Generate synthetic data from metadata template for dev environment
# **Layer**: Utility (dev Bronze loading)
# **Source**: Metadata template
# **Target**: Dev Bronze tables
# **Schedule**: On-demand (one-time setup)

# %% Parameters
# Notebook parameters (can be overridden by pipeline)
source_name = "alexis"  # Name of the source system
template_path = ""  # Path to metadata template JSON
output_path = "Files/mock_data/"  # OneLake path for generated data
environment = "dev"  # Must be 'dev' - compliance check

# %% Imports
import json
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add utils to path if running in Fabric
try:
    from notebookutils import mssparkutils
    # In Fabric, we need to handle imports differently
    IN_FABRIC = True
except ImportError:
    IN_FABRIC = False

# For standalone execution
if not IN_FABRIC:
    import os
    sys.path.insert(0, str(Path(__file__).parent))

from faker import Faker
import uuid
from collections import defaultdict, deque

# %% Compliance Check
if environment != "dev":
    raise ValueError(
        f"Mock data generation is only allowed in 'dev' environment. "
        f"Current environment: {environment}"
    )

print(f"✓ Compliance check passed: Running in {environment} environment")

# %% Load Template
print(f"Loading metadata template from: {template_path}")

if IN_FABRIC:
    # Load from OneLake
    template_content = mssparkutils.fs.head(template_path)
    template = json.loads(template_content)
else:
    # Load from local filesystem
    with open(template_path, 'r') as f:
        template = json.load(f)

print(f"✓ Loaded template for source: {template['source']}")
print(f"  Entities: {len(template['entities'])}")
print(f"  Relationships: {len(template['relationships'])}")

# %% Data Generation Functions

class MockDataGenerator:
    """Generate synthetic data from metadata template."""

    def __init__(self, template: Dict[str, Any], seed: int = 42):
        self.template = template
        self.fake = Faker()
        Faker.seed(seed)
        self.generated_data = {}
        self.primary_keys = {}

    def generate_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate data for all entities in dependency order."""
        sorted_entities = self._topological_sort()

        for entity in sorted_entities:
            entity_name = entity['name']
            print(f"Generating {entity['row_count']} records for {entity_name}...")
            self._generate_entity_data(entity)
            print(f"  ✓ Generated {len(self.generated_data[entity_name])} records")

        return self.generated_data

    def _topological_sort(self) -> List[Dict[str, Any]]:
        """Sort entities by FK dependencies."""
        dependencies = defaultdict(set)
        entity_map = {e['name']: e for e in self.template['entities']}

        # Build dependency graph
        for rel in self.template['relationships']:
            from_entity = rel['from'].split('.')[0]
            to_entity = rel['to'].split('.')[0]
            if from_entity != to_entity:
                dependencies[from_entity].add(to_entity)

        # Calculate in-degree
        in_degree = {e['name']: 0 for e in self.template['entities']}
        for entity_name, deps in dependencies.items():
            in_degree[entity_name] = len(deps)

        # Kahn's algorithm
        queue = deque([
            entity for entity in self.template['entities']
            if in_degree[entity['name']] == 0
        ])

        sorted_entities = []
        while queue:
            entity = queue.popleft()
            sorted_entities.append(entity)

            for other_name, deps in dependencies.items():
                if entity['name'] in deps:
                    in_degree[other_name] -= 1
                    if in_degree[other_name] == 0:
                        queue.append(entity_map[other_name])

        if len(sorted_entities) != len(self.template['entities']):
            raise ValueError("Circular dependency detected")

        return sorted_entities

    def _generate_entity_data(self, entity: Dict[str, Any]):
        """Generate data for a single entity."""
        entity_name = entity['name']
        records = []

        for i in range(entity['row_count']):
            record = {}

            for field in entity['fields']:
                value = self._generate_field_value(field, entity_name)
                record[field['name']] = value

                # Track PKs
                if field.get('primary_key'):
                    if entity_name not in self.primary_keys:
                        self.primary_keys[entity_name] = []
                    self.primary_keys[entity_name].append(value)

            records.append(record)

        self.generated_data[entity_name] = records

    def _generate_field_value(self, field: Dict[str, Any], entity_name: str) -> Any:
        """Generate a single field value."""
        # Handle FKs
        if field.get('foreign_key'):
            fk_entity = field['foreign_key'].split('.')[0]
            if fk_entity not in self.primary_keys:
                raise ValueError(f"FK reference to {fk_entity} not yet generated")
            return self.fake.random_element(self.primary_keys[fk_entity])

        # Handle PKs
        if field.get('primary_key'):
            return str(uuid.uuid4())

        # Use Faker method
        if field.get('faker_method'):
            method = getattr(self.fake, field['faker_method'], None)
            if method:
                args = field.get('faker_args', {})
                return method(**args) if args else method()

        # Fallback by type
        field_type = field.get('type', 'string')
        if field_type == 'string':
            return self.fake.word()
        elif field_type == 'int':
            return self.fake.random_int(1, 1000)
        elif field_type == 'float':
            return round(self.fake.random.random() * 1000, 2)
        elif field_type == 'bool':
            return self.fake.boolean()
        elif field_type in ['date', 'datetime']:
            return str(self.fake.date_time())
        else:
            return self.fake.word()

# %% Generate Data
print("\n" + "="*60)
print("GENERATING SYNTHETIC DATA")
print("="*60 + "\n")

generator = MockDataGenerator(template)
generated_data = generator.generate_all()

# Print summary
print("\n" + "="*60)
print("GENERATION SUMMARY")
print("="*60)
for entity_name, records in generated_data.items():
    print(f"  {entity_name}: {len(records)} records")

# %% Convert to DataFrames and Save
print("\n" + "="*60)
print("SAVING TO ONELAKE")
print("="*60 + "\n")

if IN_FABRIC:
    # Save as Delta tables in Fabric
    for entity_name, records in generated_data.items():
        if not records:
            print(f"  ⚠ Skipping {entity_name}: No records")
            continue

        # Get bronze table name from template
        entity_meta = next(
            (e for e in template['entities'] if e['name'] == entity_name),
            None
        )
        if not entity_meta or not entity_meta.get('bronze_table'):
            print(f"  ⚠ Skipping {entity_name}: No bronze_table specified")
            continue

        bronze_table = entity_meta['bronze_table']

        # Create DataFrame
        df = spark.createDataFrame(records)

        # Add metadata columns
        from pyspark.sql.functions import current_timestamp, lit
        df = df.withColumn("_ingested_at", current_timestamp())
        df = df.withColumn("_source_system", lit(f"{source_name}_mock"))
        df = df.withColumn("_environment", lit("dev"))

        # Write to Bronze table
        df.write.format("delta").mode("overwrite").saveAsTable(bronze_table)

        print(f"  ✓ Saved {len(records)} records to {bronze_table}")

else:
    # Save as JSON files for local testing
    import os
    os.makedirs(output_path, exist_ok=True)

    for entity_name, records in generated_data.items():
        file_path = f"{output_path}/{entity_name}.json"
        with open(file_path, 'w') as f:
            json.dump(records, f, indent=2, default=str)
        print(f"  ✓ Saved {len(records)} records to {file_path}")

print("\n" + "="*60)
print("MOCK DATA GENERATION COMPLETE")
print("="*60)
