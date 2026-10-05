# Filters the extracted SCP checklist to the categories in-scope of our research

from pathlib import Path
import csv
import json

# Config
BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_CSV = (
    BASE_DIR
    / "data"
    / "extracted"
    / "owasp_scp_all.csv"
)

OUTPUT_CSV = (
    BASE_DIR
    / "data"
    / "processed"
    / "owasp_scp_filtered_scope.csv"
)

OUTPUT_JSONL = (
    BASE_DIR
    / "data"
    / "processed"
    / "owasp_scp_filtered_scope.jsonl"
)


# Research scope
RESEARCH_CATEGORIES = {
    "Input Validation",
    "Authentication and Password Management",
    "Access Control",
}


# Main filter logic
def main():

    print()
    print("OWASP SCP Research Dataset Filter")
    print()

    if not INPUT_CSV.exists():
        print("ERROR: Extracted CSV not found.")
        print(f"Expected: {INPUT_CSV}")
        return

    # Read the extracted SCP practices
    with open(
        INPUT_CSV,
        "r",
        encoding="utf-8",
        newline=""
    ) as file:

        reader = csv.DictReader(file)
        rows = list(reader)

    print(
        f"Extracted practices loaded: {len(rows)}"
    )
    print()

    # Filter research categories
    research_rows = []

    for row in rows:

        if row["category"] in RESEARCH_CATEGORIES:
            research_rows.append(row)

    # Count by category
    category_counts = {}

    for row in research_rows:

        category = row["category"]

        if category not in category_counts:
            category_counts[category] = 0

        category_counts[category] += 1

    # Write CSV
    fieldnames = [
        "id",
        "category",
        "practice",
        "source_page",
        "source",
        "source_version",
        "source_date",
    ]

    with open(
        OUTPUT_CSV,
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(research_rows)

    # Write JSONL
    with open(
        OUTPUT_JSONL,
        "w",
        encoding="utf-8"
    ) as file:

        for row in research_rows:

            file.write(
                json.dumps(
                    row,
                    ensure_ascii=False
                )
                + "\n"
            )

    # Prints summary of filtered categories
    print("Research categories:")

    for category in [
        "Input Validation",
        "Authentication and Password Management",
        "Access Control",
    ]:

        print(
            f"  {category}: "
            f"{category_counts.get(category, 0)}"
        )

    print()
    print(
        f"Research practices: {len(research_rows)}"
    )

    print()
    print("Output:")
    print(f"CSV: {OUTPUT_CSV}")
    print(f"JSONL: {OUTPUT_JSONL}")


if __name__ == "__main__":
    main()