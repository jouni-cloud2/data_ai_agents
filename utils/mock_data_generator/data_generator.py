"""
Synthetic data generation from metadata templates.

Handles:
- Topological sorting for FK dependencies
- Faker-based data generation
- Referential integrity preservation
"""

import uuid
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
from faker import Faker
from .metadata_extractor import MetadataTemplate, EntityMetadata, FieldMetadata


class SyntheticDataGenerator:
    """Generate synthetic data from metadata templates."""

    def __init__(self, template: MetadataTemplate, seed: Optional[int] = None):
        """
        Initialize generator.

        Args:
            template: MetadataTemplate to generate from
            seed: Random seed for reproducibility (optional)
        """
        self.template = template
        self.fake = Faker()
        if seed:
            Faker.seed(seed)
        self.generated_data: Dict[str, List[Dict[str, Any]]] = {}
        self.primary_keys: Dict[str, List[Any]] = {}

    def generate_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate synthetic data for all entities in dependency order.

        Returns:
            Dictionary mapping entity names to lists of records
        """
        # Build dependency graph and perform topological sort
        sorted_entities = self._topological_sort()

        # Generate data for each entity in order
        for entity in sorted_entities:
            self._generate_entity_data(entity)

        return self.generated_data

    def _topological_sort(self) -> List[EntityMetadata]:
        """
        Sort entities by FK dependencies (independent entities first).

        Returns:
            List of entities in dependency order
        """
        # Build dependency graph
        dependencies = defaultdict(set)
        entity_map = {e.name: e for e in self.template.entities}

        for relationship in self.template.relationships:
            # Parse "employees.teamId" -> ("employees", "teamId")
            from_entity, _ = relationship.from_field.split('.')
            to_entity, _ = relationship.to_field.split('.')

            # from_entity depends on to_entity
            if from_entity != to_entity:  # Skip self-references
                dependencies[from_entity].add(to_entity)

        # Kahn's algorithm for topological sort
        in_degree = {entity.name: 0 for entity in self.template.entities}
        for entity_name, deps in dependencies.items():
            in_degree[entity_name] = len(deps)

        # Queue of entities with no dependencies
        queue = deque([
            entity for entity in self.template.entities
            if in_degree[entity.name] == 0
        ])

        sorted_entities = []
        while queue:
            entity = queue.popleft()
            sorted_entities.append(entity)

            # Reduce in-degree for dependent entities
            for other_name, deps in dependencies.items():
                if entity.name in deps:
                    in_degree[other_name] -= 1
                    if in_degree[other_name] == 0:
                        queue.append(entity_map[other_name])

        if len(sorted_entities) != len(self.template.entities):
            # Circular dependency detected
            raise ValueError("Circular dependency detected in relationships")

        return sorted_entities

    def _generate_entity_data(self, entity: EntityMetadata):
        """Generate synthetic data for a single entity."""
        records = []

        for i in range(entity.row_count):
            record = {}

            for field in entity.fields:
                # Generate field value
                value = self._generate_field_value(field, entity.name)
                record[field.name] = value

                # Track primary keys for FK references
                if field.primary_key:
                    if entity.name not in self.primary_keys:
                        self.primary_keys[entity.name] = []
                    self.primary_keys[entity.name].append(value)

            records.append(record)

        self.generated_data[entity.name] = records

    def _generate_field_value(self, field: FieldMetadata, entity_name: str) -> Any:
        """Generate a single field value."""
        # Handle foreign keys
        if field.foreign_key:
            return self._generate_fk_value(field.foreign_key)

        # Handle primary keys (UUID by default)
        if field.primary_key:
            return str(uuid.uuid4())

        # Use Faker method if specified
        if field.faker_method:
            return self._call_faker_method(field.faker_method, field.faker_args)

        # Fallback to type-based generation
        return self._generate_by_type(field.type)

    def _generate_fk_value(self, foreign_key: str) -> Any:
        """
        Generate foreign key value by referencing existing primary keys.

        Args:
            foreign_key: FK reference in format "entity.field"

        Returns:
            Random value from referenced entity's primary keys
        """
        entity_name, _ = foreign_key.split('.')

        if entity_name not in self.primary_keys or not self.primary_keys[entity_name]:
            raise ValueError(
                f"Cannot generate FK for {foreign_key}: "
                f"Entity {entity_name} has no primary keys generated yet"
            )

        # Randomly select from available primary keys
        return self.fake.random_element(self.primary_keys[entity_name])

    def _call_faker_method(
        self,
        method_name: str,
        args: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Call Faker method with optional arguments.

        Args:
            method_name: Faker method name (e.g., 'email', 'first_name')
            args: Optional keyword arguments for the method

        Returns:
            Generated value
        """
        if not hasattr(self.fake, method_name):
            # Fallback if method doesn't exist
            return self.fake.word()

        method = getattr(self.fake, method_name)

        if args:
            return method(**args)
        else:
            return method()

    def _generate_by_type(self, field_type: str) -> Any:
        """Generate value based on field type."""
        if field_type == 'string':
            return self.fake.word()
        elif field_type == 'int':
            return self.fake.random_int(min=1, max=1000)
        elif field_type == 'float':
            return round(self.fake.random.random() * 1000, 2)
        elif field_type == 'bool':
            return self.fake.boolean()
        elif field_type == 'date':
            return self.fake.date()
        elif field_type == 'datetime':
            return self.fake.date_time()
        else:
            return self.fake.word()

    def export_to_dict(self) -> Dict[str, List[Dict[str, Any]]]:
        """Export generated data as dictionary."""
        return self.generated_data

    def export_to_json(self) -> str:
        """Export generated data as JSON string."""
        import json
        return json.dumps(self.generated_data, indent=2, default=str)

    def get_entity_data(self, entity_name: str) -> List[Dict[str, Any]]:
        """Get generated data for a specific entity."""
        return self.generated_data.get(entity_name, [])

    def get_summary(self) -> Dict[str, int]:
        """Get summary of generated records per entity."""
        return {
            entity_name: len(records)
            for entity_name, records in self.generated_data.items()
        }
