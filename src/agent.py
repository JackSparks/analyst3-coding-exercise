"""
AI agent for generating personalized M&A outreach emails.
"""

import csv
import os
from dotenv import load_dotenv
from src.utils import call_llm

load_dotenv()


def load_scraped_data_from_csv(csv_path):
    """
    Load scraped company data from CSV file.

    Args:
        csv_path: Path to the CSV file with scraped data

    Returns:
        List of dicts with keys: company_name, website, industry, revenue, scraped_content
    """
    companies = []

    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            companies.append(
                {
                    "company_name": row["company_name"],
                    "website": row["website"],
                    "industry": row.get("industry", ""),
                    "revenue": row.get("revenue", ""),
                    "scraped_content": row.get("scraped_content", ""),
                }
            )

    return companies


# TODO: IMPLEMENT THIS
def generate_personalized_email(company_data):
    """
    Generate a personalized email for M&A outreach.

    Args:
        company_data: Dict with keys: company_name, website, industry, revenue, scraped_content

    Returns:
        Dict with keys:
            - email_subject: The generated email subject
            - email_body: The generated email text
    """

    pass


if __name__ == "__main__":
    # Example: Load most recent scraped data
    import glob

    # Find the most recent scraped CSV file
    csv_files = glob.glob("output/scraped_companies_*.csv")

    # Use the most recent file
    latest_csv = sorted(csv_files)[-1]
    print(f"Loading scraped data from: {latest_csv}\n")

    companies = load_scraped_data_from_csv(latest_csv)

    # Generate emails for all companies
    for company in companies:
        email = generate_personalized_email(company)

        print(f"\n{'='*60}")
        print(f"EMAIL FOR: {company['company_name']}")
        print(f"{'='*60}")

        if email:
            print(email.get("email_subject", "Not implemented yet"))
            print()
            print(email.get("email_body", "Not implemented yet"))
            print()
