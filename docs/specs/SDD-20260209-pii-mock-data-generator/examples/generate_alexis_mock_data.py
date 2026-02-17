#!/usr/bin/env python3
"""
Example: Generate mock data for Alexis HR

This script demonstrates the PII mock data generation pattern for Alexis HR.
It can be run standalone or adapted to a Fabric notebook.

Usage:
    python generate_alexis_mock_data.py

Output:
    - Console: Summary of generated data
    - Files: JSON files in ./output/ directory (for local testing)
    - Fabric: Delta tables in dev Bronze layer (when IN_FABRIC=True)
"""

import sys
import json
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "utils"))

from mock_data_generator import MetadataTemplate, SyntheticDataGenerator


def main():
    """Generate mock data for Alexis HR."""

    print("="*70)
    print("ALEXIS HR MOCK DATA GENERATION")
    print("="*70)
    print()

    # Step 1: Load metadata template
    print("Step 1: Loading metadata template...")
    template_path = Path(__file__).parent / "alexis-metadata-template.json"
    template = MetadataTemplate.load(str(template_path))

    print(f"  ✓ Loaded template for source: {template.source}")
    print(f"  ✓ Entities: {len(template.entities)}")
    print(f"  ✓ Relationships: {len(template.relationships)}")
    print()

    # Step 2: Generate synthetic data
    print("Step 2: Generating synthetic data...")
    print()

    generator = SyntheticDataGenerator(template, seed=42)
    data = generator.generate_all()

    print()

    # Step 3: Verify data integrity
    print("Step 3: Verifying data integrity...")
    summary = generator.get_summary()

    print()
    print("  Generation Summary:")
    for entity_name, count in summary.items():
        print(f"    - {entity_name}: {count} records")

    # Verify FK integrity
    print()
    print("  FK Integrity Checks:")

    # Check teams -> departments
    teams_data = generator.get_entity_data("teams")
    dept_ids = set(generator.primary_keys.get("departments", []))
    teams_dept_ids = set(team["departmentId"] for team in teams_data)
    if teams_dept_ids.issubset(dept_ids):
        print("    ✓ All teams.departmentId exist in departments.id")
    else:
        print("    ✗ FK violation: teams.departmentId")

    # Check employees -> teams, departments, offices
    employees_data = generator.get_entity_data("employees")
    team_ids = set(generator.primary_keys.get("teams", []))
    office_ids = set(generator.primary_keys.get("offices", []))

    emp_team_ids = set(emp["teamId"] for emp in employees_data)
    emp_dept_ids = set(emp["departmentId"] for emp in employees_data)
    emp_office_ids = set(emp["officeId"] for emp in employees_data)

    if emp_team_ids.issubset(team_ids):
        print("    ✓ All employees.teamId exist in teams.id")
    else:
        print("    ✗ FK violation: employees.teamId")

    if emp_dept_ids.issubset(dept_ids):
        print("    ✓ All employees.departmentId exist in departments.id")
    else:
        print("    ✗ FK violation: employees.departmentId")

    if emp_office_ids.issubset(office_ids):
        print("    ✓ All employees.officeId exist in offices.id")
    else:
        print("    ✗ FK violation: employees.officeId")

    # Check compensation -> employees
    comp_data = generator.get_entity_data("compensation")
    employee_ids = set(generator.primary_keys.get("employees", []))
    comp_emp_ids = set(comp["employeeId"] for comp in comp_data)

    if comp_emp_ids.issubset(employee_ids):
        print("    ✓ All compensation.employeeId exist in employees.id")
    else:
        print("    ✗ FK violation: compensation.employeeId")

    print()

    # Step 4: Save data (local mode)
    print("Step 4: Saving data...")
    output_dir = Path("./output")
    output_dir.mkdir(exist_ok=True)

    for entity_name, records in data.items():
        file_path = output_dir / f"{entity_name}.json"
        with open(file_path, 'w') as f:
            json.dump(records, f, indent=2, default=str)
        print(f"  ✓ Saved {len(records)} records to {file_path}")

    print()
    print("="*70)
    print("MOCK DATA GENERATION COMPLETE")
    print("="*70)
    print()
    print("Next Steps:")
    print("  1. Review generated data in ./output/")
    print("  2. Adapt this script for Fabric notebook execution")
    print("  3. Load to dev Bronze Delta tables")
    print("  4. Develop Silver transformation notebooks")
    print()


if __name__ == "__main__":
    main()
