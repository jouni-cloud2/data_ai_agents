"""
Metadata extraction utilities for various source types.

Supports:
- REST APIs
- SQL databases (JDBC)
- SaaS platforms with metadata APIs
"""

import json
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class FieldMetadata:
    """Metadata for a single field."""
    name: str
    type: str
    pii: bool = False
    primary_key: bool = False
    foreign_key: Optional[str] = None
    faker_method: Optional[str] = None
    faker_args: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class EntityMetadata:
    """Metadata for a single entity (table/endpoint)."""
    name: str
    api_endpoint: Optional[str] = None
    table_name: Optional[str] = None
    bronze_table: Optional[str] = None
    row_count: int = 100
    fields: List[FieldMetadata] = None

    def __post_init__(self):
        if self.fields is None:
            self.fields = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "name": self.name,
            "row_count": self.row_count,
            "fields": [f.to_dict() for f in self.fields]
        }
        if self.api_endpoint:
            result["api_endpoint"] = self.api_endpoint
        if self.table_name:
            result["table_name"] = self.table_name
        if self.bronze_table:
            result["bronze_table"] = self.bronze_table
        return result


@dataclass
class Relationship:
    """Foreign key relationship between entities."""
    from_field: str  # e.g., "employees.teamId"
    to_field: str    # e.g., "teams.id"

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary."""
        return {"from": self.from_field, "to": self.to_field}


class MetadataTemplate:
    """Complete metadata template for a source system."""

    def __init__(
        self,
        source: str,
        source_type: str,
        base_url: Optional[str] = None,
        database_name: Optional[str] = None
    ):
        self.source = source
        self.source_type = source_type
        self.base_url = base_url
        self.database_name = database_name
        self.extracted_at = datetime.utcnow().isoformat() + "Z"
        self.entities: List[EntityMetadata] = []
        self.relationships: List[Relationship] = []

    def add_entity(self, entity: EntityMetadata):
        """Add an entity to the template."""
        self.entities.append(entity)

    def add_relationship(self, relationship: Relationship):
        """Add a relationship to the template."""
        self.relationships.append(relationship)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "source": self.source,
            "source_type": self.source_type,
            "extracted_at": self.extracted_at,
            "entities": [e.to_dict() for e in self.entities],
            "relationships": [r.to_dict() for r in self.relationships]
        }
        if self.base_url:
            result["base_url"] = self.base_url
        if self.database_name:
            result["database_name"] = self.database_name
        return result

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def save(self, file_path: str):
        """Save template to file."""
        with open(file_path, 'w') as f:
            f.write(self.to_json())
        print(f"Template saved to {file_path}")

    @classmethod
    def load(cls, file_path: str) -> 'MetadataTemplate':
        """Load template from file."""
        with open(file_path, 'r') as f:
            data = json.load(f)

        template = cls(
            source=data["source"],
            source_type=data["source_type"],
            base_url=data.get("base_url"),
            database_name=data.get("database_name")
        )
        template.extracted_at = data["extracted_at"]

        # Load entities
        for entity_data in data["entities"]:
            entity = EntityMetadata(
                name=entity_data["name"],
                api_endpoint=entity_data.get("api_endpoint"),
                table_name=entity_data.get("table_name"),
                bronze_table=entity_data.get("bronze_table"),
                row_count=entity_data.get("row_count", 100),
                fields=[
                    FieldMetadata(**field_data)
                    for field_data in entity_data["fields"]
                ]
            )
            template.add_entity(entity)

        # Load relationships
        for rel_data in data["relationships"]:
            relationship = Relationship(
                from_field=rel_data["from"],
                to_field=rel_data["to"]
            )
            template.add_relationship(relationship)

        return template


class RestApiExtractor:
    """Extract metadata from REST APIs."""

    # Common PII field name patterns
    PII_PATTERNS = [
        'email', 'phone', 'ssn', 'social', 'personal', 'firstname',
        'lastname', 'name', 'address', 'birth', 'salary', 'compensation'
    ]

    # Python type to Faker method mapping
    TYPE_TO_FAKER = {
        'string': 'word',
        'int': 'random_int',
        'float': 'random_number',
        'bool': 'boolean',
        'date': 'date',
        'datetime': 'date_time'
    }

    # Field name to Faker method mapping
    FIELD_TO_FAKER = {
        'email': 'email',
        'firstname': 'first_name',
        'lastname': 'last_name',
        'name': 'name',
        'phone': 'phone_number',
        'phonenumber': 'phone_number',
        'address': 'address',
        'city': 'city',
        'country': 'country',
        'countrycode': 'country_code',
        'zipcode': 'zipcode',
        'postalcode': 'postcode',
        'ssn': 'ssn',
        'personalnumber': 'ssn',
        'socialsecurity': 'ssn',
        'salary': 'random_int',
        'compensation': 'random_int',
        'currency': 'currency_code',
        'currencycode': 'currency_code',
        'company': 'company',
        'job': 'job',
        'jobtitle': 'job',
        'department': 'job',
        'url': 'url',
        'username': 'user_name',
        'description': 'text',
        'bio': 'text'
    }

    def __init__(self, base_url: str, api_token: str):
        """Initialize REST API extractor."""
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }

    def extract_entity(
        self,
        endpoint: str,
        entity_name: str,
        bronze_table: str,
        row_count: int = 100,
        query_params: Optional[Dict[str, Any]] = None
    ) -> EntityMetadata:
        """
        Extract metadata for a single entity by calling the API.

        Args:
            endpoint: API endpoint path (e.g., '/employee')
            entity_name: Entity name (e.g., 'employees')
            bronze_table: Target bronze table name
            row_count: Desired row count for synthetic data
            query_params: Optional query parameters for the API call

        Returns:
            EntityMetadata object
        """
        # Make API call to get sample data
        url = f"{self.base_url}{endpoint}"
        params = query_params or {"limit": 1}

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch {endpoint}: {e}")

        # Extract sample record
        if isinstance(data, list):
            sample = data[0] if data else {}
        elif isinstance(data, dict):
            # Handle different response structures
            if 'results' in data:
                sample = data['results'][0] if data['results'] else {}
            elif 'data' in data:
                sample = data['data'][0] if isinstance(data['data'], list) else data['data']
            else:
                sample = data
        else:
            sample = {}

        # Create entity
        entity = EntityMetadata(
            name=entity_name,
            api_endpoint=endpoint,
            bronze_table=bronze_table,
            row_count=row_count
        )

        # Extract fields from sample
        entity.fields = self._extract_fields(sample, entity_name)

        return entity

    def _extract_fields(
        self,
        sample: Dict[str, Any],
        entity_name: str,
        prefix: str = ""
    ) -> List[FieldMetadata]:
        """Extract field metadata from sample JSON object."""
        fields = []

        for key, value in sample.items():
            field_name = f"{prefix}{key}" if prefix else key

            # Skip nested objects for now (could be relationships)
            if isinstance(value, dict):
                # Could be a FK relationship - let user confirm
                continue

            # Skip arrays
            if isinstance(value, list):
                continue

            # Infer type
            field_type = self._infer_type(value)

            # Detect PII
            is_pii = self._is_pii_field(field_name)

            # Detect primary key
            is_pk = field_name.lower() in ['id', f'{entity_name}_id']

            # Map to Faker method
            faker_method = self._get_faker_method(field_name, field_type)
            faker_args = self._get_faker_args(field_name, field_type)

            field = FieldMetadata(
                name=key,  # Use original key name (not prefixed)
                type=field_type,
                pii=is_pii,
                primary_key=is_pk,
                faker_method=faker_method,
                faker_args=faker_args
            )

            fields.append(field)

        return fields

    def _infer_type(self, value: Any) -> str:
        """Infer field type from value."""
        if value is None:
            return 'string'
        elif isinstance(value, bool):
            return 'bool'
        elif isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, str):
            # Try to detect date/datetime
            if 'T' in value and ('Z' in value or '+' in value or '-' in value):
                return 'datetime'
            elif len(value) == 10 and value.count('-') == 2:
                return 'date'
            return 'string'
        else:
            return 'string'

    def _is_pii_field(self, field_name: str) -> bool:
        """Check if field name suggests PII."""
        field_lower = field_name.lower().replace('_', '')
        return any(pattern in field_lower for pattern in self.PII_PATTERNS)

    def _get_faker_method(self, field_name: str, field_type: str) -> str:
        """Get appropriate Faker method for field."""
        field_lower = field_name.lower().replace('_', '')

        # Check field name mapping first
        for pattern, faker_method in self.FIELD_TO_FAKER.items():
            if pattern in field_lower:
                return faker_method

        # Check if it's an ID field
        if field_name.lower() == 'id' or field_name.lower().endswith('id'):
            return 'uuid4'

        # Fallback to type-based mapping
        return self.TYPE_TO_FAKER.get(field_type, 'word')

    def _get_faker_args(self, field_name: str, field_type: str) -> Optional[Dict[str, Any]]:
        """Get Faker method arguments for special cases."""
        field_lower = field_name.lower().replace('_', '')

        # Salary/compensation - reasonable range
        if 'salary' in field_lower or 'compensation' in field_lower:
            return {"min": 30000, "max": 150000}

        # Random int - default range
        if field_type == 'int' and 'id' not in field_lower:
            return {"min": 1, "max": 1000}

        # Random float - default precision
        if field_type == 'float':
            return {"digits": 2}

        return None


class SqlExtractor:
    """Extract metadata from SQL databases via JDBC."""

    def __init__(self, connection_string: str):
        """Initialize SQL extractor."""
        self.connection_string = connection_string
        # Note: Actual JDBC implementation would require py4j or similar
        # This is a placeholder for the pattern

    def extract_entity(self, table_name: str, bronze_table: str) -> EntityMetadata:
        """Extract metadata for a SQL table."""
        # Placeholder - would query INFORMATION_SCHEMA.COLUMNS
        raise NotImplementedError("SQL extraction not implemented in v1")

    def extract_relationships(self) -> List[Relationship]:
        """Extract FK relationships from INFORMATION_SCHEMA."""
        # Placeholder - would query INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        raise NotImplementedError("SQL extraction not implemented in v1")
