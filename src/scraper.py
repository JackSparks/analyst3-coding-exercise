"""
Web scraper for company websites using Jina AI.
"""

import csv
import requests
from datetime import datetime


def scrape_company_website(url):
    """
    Scrape a company website using Jina AI and return its content.
    """
    headers = {
        "X-Return-Format": "html",
        "X-Locale": "en-US",
    }

    # Bug: No timeout parameter, no error handling
    response = requests.get(f"https://r.jina.ai/{url}", headers=headers)
    return response.text


def load_companies_from_csv(filepath):
    """Load company data from CSV file."""
    companies = []

    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            companies.append(
                {
                    "company_name": row["company_name"],
                    "website": row["website"],
                    "industry": row.get("industry", ""),
                    "revenue": row.get("revenue", ""),
                }
            )

    return companies


def save_results_to_csv(results, output_dir="output"):
    """
    Save scraped results to CSV file with timestamp.

    Args:
        results: List of dicts with company data and scraped content
        output_dir: Directory to save the output file

    Returns:
        str: Path to the saved CSV file
    """
    import os

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_dir, f"scraped_companies_{timestamp}.csv")

    if not results:
        print("No results to save")
        return None

    # Define fields to save
    fieldnames = ["company_name", "website", "industry", "revenue", "scraped_content"]

    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            writer.writerow(
                {
                    "company_name": result["company_name"],
                    "website": result["website"],
                    "industry": result["industry"],
                    "revenue": result["revenue"],
                    "scraped_content": result["raw_content"],
                }
            )

    print(f"Saved {len(results)} companies to {filename}")
    return filename


def scrape_all_companies(csv_path):
    """
    Main pipeline function that loads companies, scrapes their websites,
    and saves results to a CSV file.

    Returns:
        str: Path to the saved CSV file with scraped data
    """
    companies = load_companies_from_csv(csv_path)
    results = []

    for company in companies:
        print(f"Scraping {company['company_name']}...")
        raw_content = scrape_company_website(company["website"])

        results.append(
            {
                "company_name": company["company_name"],
                "website": company["website"],
                "industry": company["industry"],
                "revenue": company["revenue"],
                "raw_content": raw_content,
            }
        )

    # Save results to CSV
    output_file = save_results_to_csv(results)

    return output_file


if __name__ == "__main__":
    # Test the scraper
    output_file = scrape_all_companies("data/companies.csv")

    if output_file:
        print(f"\nSuccessfully scraped companies!")
        print(f"Results saved to: {output_file}")
        print("\nUse this file as input for the email generation agent.")
