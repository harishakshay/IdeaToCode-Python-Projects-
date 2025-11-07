	import argparse
import json
import sys
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup

# Default sample HTML used when no URL is supplied (for demonstration/testing)
_SAMPLE_HTML = """
<html>
  <body>
    <div class='job'>
      <h2 class='title'>Software Engineer</h2>
      <span class='location'>New York, NY</span>
      <div class='description'>Develop and maintain web applications.</div>
      <span class='experience'>2</span>
      <ul class='skills'>
        <li>Python</li>
        <li>JavaScript</li>
      </ul>
    </div>
    <div class='job'>
      <h2 class='title'>Data Analyst</h2>
      <span class='location'>Remote</span>
      <div class='description'>Analyze datasets to drive business decisions.</div>
      <span class='experience'>4</span>
      <ul class='skills'>
        <li>SQL</li>
        <li>Python</li>
        <li>Tableau</li>
      </ul>
    </div>
  </body>
</html>
"""


def _fetch_html(url: str) -> str:
    """Retrieve raw HTML from a URL with basic error handling."""
    headers = {
        "User-Agent": "JobScraper/1.0 (+https://example.com/job-scraper)"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as exc:
        sys.stderr.write(f"Error fetching URL '{url}': {exc}\n")
        sys.exit(1)


def parse_jobs(html: str) -> List[Dict]:
    """Parse job postings from HTML and return a list of job dictionaries."""
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    for job_div in soup.select("div.job"):
        title_el = job_div.select_one("h2.title")
        location_el = job_div.select_one("span.location")
        desc_el = job_div.select_one("div.description")
        exp_el = job_div.select_one("span.experience")
        skill_els = job_div.select("ul.skills li")
        if not (title_el and location_el and desc_el and exp_el):
            continue  # Skip malformed entries
        job = {
            "title": title_el.get_text(strip=True),
            "location": location_el.get_text(strip=True),
            "description": desc_el.get_text(strip=True),
            "experience": int(exp_el.get_text(strip=True)),
            "skills": [s.get_text(strip=True) for s in skill_els],
        }
        jobs.append(job)
    return jobs


def filter_jobs(jobs: List[Dict], skill: Optional[str] = None, min_experience: Optional[int] = None) -> List[Dict]:
    """Return jobs that match the optional skill and experience criteria."""
    filtered = []
    for job in jobs:
        if skill and skill.lower() not in (s.lower() for s in job["skills"]):
            continue
        if min_experience is not None and job["experience"] < min_experience:
            continue
        filtered.append(job)
    return filtered


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape job postings and filter by skill or experience.")
    parser.add_argument("--url", type=str, help="URL of the job listings page. If omitted, a built‑in sample is used.")
    parser.add_argument("--skill", type=str, help="Skill that must be present in the job's skill list.")
    parser.add_argument("--experience", type=int, help="Minimum years of experience required.")
    args = parser.parse_args()

    if args.url:
        html = _fetch_html(args.url)
    else:
        html = _SAMPLE_HTML
        sys.stderr.write("No URL provided – using built‑in sample data.\n")

    jobs = parse_jobs(html)
    if not jobs:
        sys.stderr.write("No job postings found.\n")
        sys.exit(0)

    filtered = filter_jobs(jobs, skill=args.skill, min_experience=args.experience)
    output = {
        "total_found": len(jobs),
        "total_filtered": len(filtered),
        "jobs": filtered,
    }
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
