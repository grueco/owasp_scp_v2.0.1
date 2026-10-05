# Extracts all checklist items from the OWASP SCP V2.0.1 (Dec 15, 2022)

from pathlib import Path
import csv
import json
import pymupdf


# Config
BASE_DIR = Path(__file__).resolve().parent.parent

PDF_PATH = BASE_DIR / "data" / "raw" / "owasp_scp_v2.0.1.pdf"
EXTRACTED_DIR = BASE_DIR / "data" / "extracted"

CSV_PATH = EXTRACTED_DIR / "owasp_scp_all.csv"
JSONL_PATH = EXTRACTED_DIR / "owasp_scp_all.jsonl"
REVIEW_PATH = EXTRACTED_DIR / "extraction_review.txt"


CATEGORIES = [
    "Input Validation",
    "Output Encoding",
    "Authentication and Password Management",
    "Session Management",
    "Access Control",
    "Cryptographic Practices",
    "Error Handling and Logging",
    "Data Protection",
    "Communication Security",
    "System Configuration",
    "Database Security",
    "File Management",
    "Memory Management",
    "General Coding Practices",
]


CATEGORY_CODES = {
    "Input Validation": "IV",
    "Output Encoding": "OE",
    "Authentication and Password Management": "AP",
    "Session Management": "SM",
    "Access Control": "AC",
    "Cryptographic Practices": "CP",
    "Error Handling and Logging": "EL",
    "Data Protection": "DP",
    "Communication Security": "CS",
    "System Configuration": "SC",
    "Database Security": "DB",
    "File Management": "FM",
    "Memory Management": "MM",
    "General Coding Practices": "GC",
}


# Helper funcs
def is_category(line):
    """Check whether a line is one of the SCP category headings."""
    cleaned = line.strip().rstrip(":")

    for category in CATEGORIES:
        if cleaned.lower() == category.lower():
            return category

    return None


def is_checkbox(line):
    """Check whether a line starts with the SCP checkbox character."""
    return line.strip().startswith("□")


def clean_checkbox_text(line):
    """Remove the checkbox from the beginning of a practice."""
    text = line.strip()

    if text.startswith("□"):
        text = text[1:]

    return text.strip()


def is_page_number(line):
    """Check for standalone page numbers."""
    return line.strip().isdigit()

# Main extraction logic
def main():

    print()
    print("OWASP Secure Coding Practices PDF Extractor")
    print("Version 2.0.1")
    print()

    print("Reading PDF:")
    print(PDF_PATH)
    print()

    if not PDF_PATH.exists():
        print("ERROR: PDF file not found.")
        print(f"Expected: {PDF_PATH}")
        return

    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)

    doc = pymupdf.open(PDF_PATH)

    print(f"PDF pages: {len(doc)}")
    print()
    print("Locating SCP checklist...")

    # Find the checklist page
    start_page = None

    for page_index in range(len(doc)):
        text = doc[page_index].get_text("text")

        if "Secure Coding Practices Checklist" in text and "□" in text:
            start_page = page_index
            break

    if start_page is None:
        print("ERROR: Could not find the SCP checklist.")
        doc.close()
        return

    print(
        f"Checklist found on PDF page {start_page + 1}."
    )
    print()

    # Extract checklist items
    print("Extracting SCP checklist...")
    print()

    practices = []

    current_category = None
    current_practice = None
    current_page = None

    category_counts = {
        category: 0
        for category in CATEGORIES
    }

    checkbox_count = 0

    extraction_started = False

    for page_index in range(start_page, len(doc)):

        page_number = page_index + 1
        text = doc[page_index].get_text("text")

        lines = text.splitlines()

        for raw_line in lines:

            line = raw_line.strip()

            if not line:
                continue

            # Ignore document metadata
            if line == "December 2022":
                continue

            if line == "Version 2.0.1":
                continue

            if is_page_number(line):
                continue

            # Stop at the appendix
            if extraction_started:
                if line.startswith("Appendix A"):
                    print(
                        f"Appendix detected on page {page_number}. "
                        "Stopping extraction."
                    )

                    extraction_started = False
                    break

                if line.startswith("Appendix B"):
                    print(
                        f"Appendix detected on page {page_number}. "
                        "Stopping extraction."
                    )

                    extraction_started = False
                    break

            # Detect category headings
            category = is_category(line)

            if category is not None:

                # Save previous practice before changing category
                if current_practice is not None and current_category is not None:

                    practice_id = (
                        f"SCP-{CATEGORY_CODES[current_category]}"
                        f"-{category_counts[current_category] + 1:03d}"
                    )

                    practices.append({
                        "id": practice_id,
                        "category": current_category,
                        "practice": current_practice.strip(),
                        "source_page": current_page,
                        "source": "OWASP Secure Coding Practices - Quick Reference Guide",
                        "source_version": "2.0.1",
                        "source_date": "December 2022",
                    })

                    category_counts[current_category] += 1
                    current_practice = None

                current_category = category
                extraction_started = True

                print(
                    f"  Category detected: {category} "
                    f"(page {page_number})"
                )

                continue

            # Detect checkbox items
            if extraction_started and is_checkbox(line):

                # Save previous practice
                if current_practice is not None and current_category is not None:

                    practice_id = (
                        f"SCP-{CATEGORY_CODES[current_category]}"
                        f"-{category_counts[current_category] + 1:03d}"
                    )

                    practices.append({
                        "id": practice_id,
                        "category": current_category,
                        "practice": current_practice.strip(),
                        "source_page": current_page,
                        "source": "OWASP Secure Coding Practices - Quick Reference Guide",
                        "source_version": "2.0.1",
                        "source_date": "December 2022",
                    })

                    category_counts[current_category] += 1

                current_practice = clean_checkbox_text(line)
                current_page = page_number

                checkbox_count += 1

                continue

            if (
                extraction_started
                and current_practice is not None
                and current_category is not None
            ):

                # Ignore common document footer text
                if line in {
                    "Secure Coding Practices Checklist",
                    "OWASP Secure Coding Practices - Quick Reference Guide",
                }:
                    continue

                current_practice += " " + line

        # Stop processing pages after Appendix
        if not extraction_started and page_index > start_page:
            break

    if current_practice is not None and current_category is not None:

        practice_id = (
            f"SCP-{CATEGORY_CODES[current_category]}"
            f"-{category_counts[current_category] + 1:03d}"
        )

        practices.append({
            "id": practice_id,
            "category": current_category,
            "practice": current_practice.strip(),
            "source_page": current_page,
            "source": "OWASP Secure Coding Practices - Quick Reference Guide",
            "source_version": "2.0.1",
            "source_date": "December 2022",
        })

        category_counts[current_category] += 1

    doc.close()

    # Print extraction statistics
    print()
    print(f"Checkbox items detected: {checkbox_count}")
    print(f"Practices reconstructed: {len(practices)}")
    print()

    print("Practices by category:")

    for category in CATEGORIES:
        print(
            f"  {category}: "
            f"{category_counts[category]}"
        )

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
        CSV_PATH,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(practices)

    # Write JSONL
    with open(
        JSONL_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        for practice in practices:
            file.write(
                json.dumps(
                    practice,
                    ensure_ascii=False,
                )
                + "\n"
            )

    # Write review file for manual checking
    with open(
        REVIEW_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        file.write(
            "OWASP Secure Coding Practices Extraction Review\n"
        )
        file.write(
            "================================================\n\n"
        )

        file.write(
            f"Source PDF: {PDF_PATH.name}\n"
        )
        file.write(
            "Version: 2.0.1\n"
        )
        file.write(
            "Date: December 2022\n"
        )
        file.write(
            f"Checklist start page: {start_page + 1}\n"
        )
        file.write(
            f"Total practices: {len(practices)}\n\n"
        )

        file.write("Practices by category:\n")

        for category in CATEGORIES:
            file.write(
                f"{category}: "
                f"{category_counts[category]}\n"
            )

        file.write("\n")
        file.write("Extracted practices:\n\n")

        for practice in practices:

            file.write(
                f"{practice['id']} | "
                f"{practice['category']} | "
                f"Page {practice['source_page']}\n"
            )

            file.write(
                f"{practice['practice']}\n\n"
            )

    # Print the file directories of the outputs
    print()
    print("Extraction complete.")
    print()

    print(f"CSV: {CSV_PATH}")
    print(f"JSONL: {JSONL_PATH}")
    print(f"Review: {REVIEW_PATH}")


if __name__ == "__main__":
    main()