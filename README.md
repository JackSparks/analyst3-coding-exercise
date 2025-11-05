# Deal Sourcing Agent - Coding Exercise

## Overview

Build a mini deal sourcing outreach agent that scrapes company data and generates personalized M&A outreach emails.

Time: 60 minutes

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add provided OpenAI API key

---

## Task 1: Review Web Scraping Pipeline (10 min)

### Problem

The scraping pipeline in `src/scraper.py` is implemented but may have bugs/issues.

Run the scraper on the test companies provided in `data/companies.csv`, review outputs, identify bugs/issues, and rectify as necessary.

Scraped company data will be saved and used as inputs to the next task.

---

## Task 2: Build Personalized Outreach Agent (30 min)

### Context

You're building this for M&A advisors reaching out to business owners who might want to sell. The objective is to create a personalized outreach email draft for the initial first outreach.

**Advisor Profile:**

see `data/advisor_profile.txt`

### Requirements

Build `generate_personalized_email()` in `src/agent.py` that creates email drafts that outputs at least for each of the test companies:

1. Email subject
2. Email body

For the purpose of this exercise, we can assume that we are reaching out to the owner of the business and if needed, use a placeholder for their name in the email draft.

### Email Requirements

#### Email content

- clear CTA - i.e. request for exploratory conversation
- start with a hook about the company that is either recent (e.g. recent news of product launches, funding, leadership appointments...etc) or relevant (e.g. shares location)
- match advisor's expertise to company to highlight relevant deal experience if applicable
- incl. specific industry reference - e.g. "buyers interested in Healthtech companies"

#### Formatting

- email body is properly formatted (i.e. can be sent as is)
- leverage the advisor's writing styles and guidelines as per advisor profile provided
- company name is clean - not the company's legal name but how a company would refer to itself as (i.e. "Apple Inc" vs "Apple")
- use standard industry terminology, in a way that should be easy to understand
- should be around 150-250 words
- Professional, consultative tone

### Other Requirements

You can structure this agent however you see fit, consider how well the agent handles the following:

- varying industries and industry scopes (some industries can be super niche or super technical - e.g. Thermoplastic Piping Distribution)
- some industries receive a lot of spam (e.g. marketing agencies)
- varying sizes of companies
- where advisor has no relevant experience in the industry being targeted

### Helper Functions Available

Use the `call_llm()` function from `src/utils.py` for LLM completion. You can change the function if required.

```python
from src.utils import call_llm

# Simple text response
response = call_llm(
    prompt="Your prompt here",
    system_message="You are a helpful assistant"
)

# Structured output with Pydantic
from pydantic import BaseModel

class EmailOutput(BaseModel):
    email_body: str
    reasoning: str

result = call_llm(
    prompt="Generate an email...",
    response_schema=EmailOutput
)
```

---

## Task 3: Add Feedback Mechanism (15min)

Add feedback mechanism through the CLI that either:

- allows the user to provide explicit text feedback (i.e. "Make it more professional")
- allows the user to pick and rank from multiple variations their top drafts

The feedback received should then be used to update context & instructions for future draft creation. How that context is updated or structured is up to you. What things would you consider when designing this solution?

---

## Running Your Solution

### Step 1: Run the scraper

```bash
python src/scraper.py
```

This will:

- Load companies from `data/companies.csv`
- Scrape each company's website
- Save results to `output/scraped_companies_[timestamp].csv`

### Step 2: Generate emails

```bash
python src/agent.py
```

This will:

- Load the most recent scraped data CSV
- Generate personalized emails for each company
- Display results in the terminal
