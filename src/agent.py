"""
AI agent for generating personalized M&A outreach emails.
"""

import csv
import json
import sys
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv
from utils import call_llm

# Increase CSV field size limit to handle large scraped content
csv.field_size_limit(sys.maxsize)

load_dotenv()

# Constants
ADVISOR_PROFILE_PATH = "data/advisor_profile.txt"
SCRAPED_CONTENT_LIMIT = 1500  # Token management
DEFAULT_MODEL = "gpt-4o"
MIN_WORD_COUNT = 150
MAX_WORD_COUNT = 250


def load_advisor_profile() -> str:
    """
    Load advisor profile from data directory.
    
    Returns:
        str: Advisor profile content, or fallback message if not found
    """
    try:
        profile_path = Path(ADVISOR_PROFILE_PATH)
        if not profile_path.exists():
            print(f"Warning: Advisor profile not found at {ADVISOR_PROFILE_PATH}")
            return "Experienced M&A advisor with diverse deal experience across multiple industries."
        
        with open(profile_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                print("Warning: Advisor profile is empty")
                return "Experienced M&A advisor with diverse deal experience across multiple industries."
            return content
            
    except Exception as e:
        print(f"Error loading advisor profile: {e}")
        return "Experienced M&A advisor with diverse deal experience across multiple industries."


def build_email_prompt(company_data: Dict[str, str], advisor_profile: str) -> str:
    """
    Construct the prompt for email generation.
    
    Args:
        company_data: Company information including scraped content
        advisor_profile: Advisor's profile and experience
        
    Returns:
        str: Formatted prompt for LLM
    """
    # Truncate scraped content to manage token usage
    scraped_snippet = company_data.get('scraped_content', '')[:SCRAPED_CONTENT_LIMIT]
    
    prompt = f"""You are an expert M&A advisor assistant drafting a personalized outreach email to a business owner.

## Context

**Advisor Profile:**
{advisor_profile}

**Target Company (from web scraping):**
- Company Name: {company_data['company_name']}
- Industry: {company_data['industry']}
- Revenue: {company_data['revenue']}
- Website: {company_data['website']}
- Company Intelligence: {scraped_snippet if scraped_snippet else 'Limited data available'}

## Your Task

Create a highly personalized email that:

### Content Structure
1. **Opening Hook**: Reference something specific from the scraped content—recent news, product launches, company achievements, or shared location. Be concrete, not generic.

2. **Value Proposition**: Connect the advisor's specific deal experience to this company's industry ({company_data['industry']}). Mention relevant buyer interest (e.g., "strategic buyers focused on {company_data['industry']} businesses").

3. **Call-to-Action**: Professional request for a 15-minute exploratory conversation.

### Strict Requirements
- **Length**: {MIN_WORD_COUNT}-{MAX_WORD_COUNT} words for email body (count carefully)
- **Tone**: Professional and consultative—not salesy
- **Company Name**: Use brand name as they'd refer to themselves, not legal entity name
- **Recipient**: Address as "[Company Owner]" 
- **Formatting**: Production-ready—proper paragraphs, no signature block
- **Language**: Industry-standard terminology, accessible to non-experts

### Critical Rules
- DO NOT include sender signature or contact details
- DO NOT be generic—every sentence must reflect this specific company
- DO NOT exceed word count
- Use insights from scraped content to demonstrate research

## Output Format

Return ONLY valid JSON (no markdown, no extra text):

{{
  "email_subject": "Engaging subject under 60 characters",
  "email_body": "Complete email body text"
}}
"""
    return prompt


def validate_email_output(email: Dict[str, str], company_name: str) -> bool:
    """
    Validate generated email meets basic requirements.
    
    Args:
        email: Generated email dict
        company_name: Company name for logging
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not email or not isinstance(email, dict):
        print(f"Warning [{company_name}]: Invalid email format")
        return False
    
    if 'email_subject' not in email or 'email_body' not in email:
        print(f"Warning [{company_name}]: Missing required email fields")
        return False
    
    # Check word count
    body = email.get('email_body', '')
    word_count = len(body.split())
    
    if word_count < MIN_WORD_COUNT or word_count > MAX_WORD_COUNT:
        print(f"Warning [{company_name}]: Email body is {word_count} words (target: {MIN_WORD_COUNT}-{MAX_WORD_COUNT})")
        # Don't fail, just warn
    
    return True


def generate_personalized_email(
    company_data: Dict[str, str],
    model: str = DEFAULT_MODEL
) -> Optional[Dict[str, str]]:
    """
    Generate a personalized email for M&A outreach using LLM.

    Args:
        company_data: Dict with keys: company_name, website, industry, revenue, scraped_content
        model: LLM model to use (default: gpt-4o). Configurable for future flexibility.

    Returns:
        Dict with keys:
            - email_subject: The generated email subject
            - email_body: The generated email text
        Returns None if generation fails.
    """
    try:
        # Load advisor profile (cached in memory for performance)
        if not hasattr(generate_personalized_email, '_advisor_profile'):
            generate_personalized_email._advisor_profile = load_advisor_profile()
        
        advisor_profile = generate_personalized_email._advisor_profile
        
        # Build prompt
        prompt = build_email_prompt(company_data, advisor_profile)
        
        # System message for model behavior
        system_message = (
            "You are an expert M&A advisor assistant. Your emails are known for being "
            "highly personalized, consultative, and demonstrating thorough research. "
            "Always return valid JSON with email_subject and email_body fields."
        )
        
        # Call LLM
        response = call_llm(
            prompt=prompt,
            system_message=system_message,
            model=model
        )
        
        # Parse JSON response - strip markdown code blocks if present
        cleaned_response = response.strip()
        
        # Remove markdown code block delimiters
        if "```json" in cleaned_response:
            # Extract content between ```json and ```
            start = cleaned_response.find("```json") + 7
            end = cleaned_response.rfind("```")
            if end > start:
                cleaned_response = cleaned_response[start:end].strip()
        elif cleaned_response.startswith("```") and cleaned_response.endswith("```"):
            # Generic code block
            cleaned_response = cleaned_response[3:-3].strip()
        
        email = json.loads(cleaned_response)
        
        # Validate output
        if not validate_email_output(email, company_data['company_name']):
            return None
        
        return email
        
    except json.JSONDecodeError as e:
        print(f"Error [{company_data['company_name']}]: Failed to parse JSON response - {e}")
        print(f"Raw response: {response[:200]}...")
        return None
        
    except Exception as e:
        print(f"Error [{company_data['company_name']}]: Email generation failed - {e}")
        return None


def load_scraped_data_from_csv(csv_path):
    """
    Load scraped company data from CSV file.

    Args:
        csv_path: Path to the CSV file with scraped data

    Returns:
        List of dicts with keys: company_name, website, industry, revenue, scraped_content
    """
    companies = []

    with open(csv_path, "r", encoding="utf-8") as f:
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


if __name__ == "__main__":
    import glob

    # Find the most recent scraped CSV file
    csv_files = glob.glob("output/scraped_companies_*.csv")
    
    if not csv_files:
        print("Error: No scraped company data found.")
        print("Please run: python src/scraper.py")
        sys.exit(1)

    # Use the most recent file
    latest_csv = sorted(csv_files)[-1]
    print(f"Loading scraped data from: {latest_csv}\n")

    companies = load_scraped_data_from_csv(latest_csv)
    
    print(f"Generating emails for {len(companies)} companies using {DEFAULT_MODEL}...\n")

    # Generate emails for all companies
    successful = 0
    failed = 0
    
    for company in companies:
        email = generate_personalized_email(company, model=DEFAULT_MODEL)

        print(f"\n{'='*60}")
        print(f"EMAIL FOR: {company['company_name']}")
        print(f"{'='*60}")

        if email:
            print(f"Subject: {email.get('email_subject', 'Not generated')}")
            print()
            print(email.get("email_body", "Not generated"))
            print()
            successful += 1
        else:
            print("❌ Failed to generate email")
            print()
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Summary: {successful} successful, {failed} failed")
    print(f"{'='*60}")
