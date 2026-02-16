#!/usr/bin/env python3
"""Phase 2: Classify every page and generate analysis documents."""

import json
import os
import sys
import re
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from lib.classify import classify_page, is_governance_page

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PAGES_DIR = DATA_DIR / "pages"
ANALYSIS_DIR = BASE_DIR / "analysis"


def load_manifest():
    with open(DATA_DIR / "pages_all.json") as f:
        return json.load(f)


def load_page(slug):
    path = PAGES_DIR / f"{slug}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def extract_sections(text):
    """Extract section headers from wikitext."""
    sections = []
    for match in re.finditer(r'^(={2,6})\s*(.+?)\s*\1\s*$', text, re.MULTILINE):
        level = len(match.group(1))
        sections.append({"level": level, "title": match.group(2)})
    return sections


def generate_page_catalog(pages_classified, categories_grouped):
    """Generate analysis/page_catalog.md."""
    lines = [
        "# HeatSync Labs Wiki: Complete Page Catalog",
        "",
        f"**Total Pages:** {len(pages_classified)}",
        "",
        "## Category Summary",
        "",
        "| Category | Count | Description |",
        "|----------|-------|-------------|",
    ]

    cat_descriptions = {
        "governance": "Core governance documents (bylaws, rules, policies)",
        "board": "Board meeting minutes and elections",
        "meetings": "Community meeting notes",
        "legal": "Legal/nonprofit documents",
        "operations": "Operational procedures and logistics",
        "membership": "Membership-related pages",
        "projects": "Maker projects and builds",
        "events": "Events, workshops, classes",
        "community": "Community outreach and communication",
        "infrastructure": "Space infrastructure, equipment, tools",
        "corp": "Corporate namespace documents",
        "file": "Uploaded files and media",
        "meta": "Wiki infrastructure (templates, categories, mediawiki)",
        "talk": "Discussion/talk pages",
        "user": "User pages and profiles",
        "redirect": "Redirect pages",
        "other": "Uncategorized pages",
    }

    for cat in sorted(categories_grouped.keys(), key=lambda c: (-len(categories_grouped[c]), c)):
        count = len(categories_grouped[cat])
        desc = cat_descriptions.get(cat, "")
        lines.append(f"| {cat} | {count} | {desc} |")

    lines.append("")

    # List pages by category
    for cat in sorted(categories_grouped.keys()):
        pages = sorted(categories_grouped[cat], key=lambda p: p["title"].lower())
        lines.append(f"## {cat.title()} ({len(pages)} pages)")
        lines.append("")

        if cat == "file":
            # Just list filenames compactly
            lines.append("| Title | Revisions | Last Updated |")
            lines.append("|-------|-----------|--------------|")
            for p in pages:
                ts = p["latest_timestamp"][:10]
                lines.append(f"| {p['title']} | {p['revision_count']} | {ts} |")
            lines.append("")
            continue

        lines.append("| Title | Size | Revisions | Last Updated | Redirect |")
        lines.append("|-------|------|-----------|--------------|----------|")
        for p in pages:
            ts = p["latest_timestamp"][:10]
            size = f"{p['bytes']:,}B" if p['bytes'] else "0B"
            redir = "Yes" if p["is_redirect"] else ""
            lines.append(f"| {p['title']} | {size} | {p['revision_count']} | {ts} | {redir} |")
        lines.append("")

    return "\n".join(lines)


def generate_governance_inventory(governance_pages):
    """Generate analysis/governance_inventory.md."""
    lines = [
        "# HeatSync Labs Governance Document Inventory",
        "",
        f"**Total governance-related pages:** {len(governance_pages)}",
        "",
        "This document provides a detailed analysis of each governance document in the wiki,",
        "including section structure, key provisions, and identified gaps.",
        "",
    ]

    # Core docs first, then board minutes, then others
    core = []
    board_minutes = []
    other_gov = []
    for p in governance_pages:
        if p["title"].startswith("Board:"):
            board_minutes.append(p)
        elif p["category"] == "governance" or p["title"] in (
            "Proposals", "Access Card Procedure", "Business Plan", "Board Members",
            "Board Elections", "Membership Guidelines",
        ):
            core.append(p)
        else:
            other_gov.append(p)

    core.sort(key=lambda p: p["title"].lower())
    board_minutes.sort(key=lambda p: p["title"])
    other_gov.sort(key=lambda p: p["title"].lower())

    lines.append("## Core Governance Documents")
    lines.append("")
    for p in core:
        lines.extend(_governance_page_detail(p))

    if board_minutes:
        lines.append("## Board Meeting Minutes")
        lines.append("")
        lines.append(f"**{len(board_minutes)} meeting records found** (Board namespace)")
        lines.append("")
        lines.append("Note: The original wiki reportedly had ~37 board meeting pages;")
        lines.append(f"this dump contains {len(board_minutes)}, suggesting some were deleted.")
        lines.append("")
        lines.append("| Meeting | Revisions | Last Updated | Size |")
        lines.append("|---------|-----------|--------------|------|")
        for p in board_minutes:
            ts = p["latest_timestamp"][:10]
            lines.append(f"| {p['title']} | {p['revision_count']} | {ts} | {p['bytes']:,}B |")
        lines.append("")

    if other_gov:
        lines.append("## Other Governance-Related Pages")
        lines.append("")
        for p in other_gov:
            lines.extend(_governance_page_detail(p))

    return "\n".join(lines)


def _governance_page_detail(p):
    """Generate detail block for a single governance page."""
    lines = [
        f"### {p['title']}",
        "",
        f"- **Size:** {p['bytes']:,} bytes",
        f"- **Revisions:** {p['revision_count']}",
        f"- **Created:** {p.get('first_timestamp', 'unknown')[:10]}",
        f"- **Last updated:** {p['latest_timestamp'][:10]}",
        f"- **Category:** {p['category']}",
        "",
    ]

    if p.get("sections"):
        lines.append("**Sections:**")
        lines.append("")
        for s in p["sections"]:
            indent = "  " * (s["level"] - 2)
            lines.append(f"{indent}- {s['title']}")
        lines.append("")

    # Key observations
    text = p.get("text_preview", "")
    observations = []

    title_lower = p["title"].lower()
    if "bylaws" in title_lower:
        if "dissolution" not in text.lower():
            observations.append("Missing dissolution clause (required for 501(c)(3))")
        if "conflict of interest" not in text.lower():
            observations.append("No explicit conflict of interest policy")
        if "fiscal year" not in text.lower():
            observations.append("No fiscal year definition found")
        if p["bytes"] > 25000:
            observations.append(f"Document is very long ({p['bytes']:,} bytes) - may benefit from restructuring")

    if "rules" in title_lower and p["revision_count"] > 100:
        observations.append(f"Heavily revised ({p['revision_count']} revisions) - suggests ongoing refinement")

    if p["revision_count"] == 1:
        observations.append("Only 1 revision - may be incomplete or abandoned")

    if observations:
        lines.append("**Observations:**")
        lines.append("")
        for obs in observations:
            lines.append(f"- {obs}")
        lines.append("")

    lines.append("---")
    lines.append("")
    return lines


def generate_contributor_analysis(contributors_data):
    """Generate analysis/contributor_analysis.md."""
    lines = [
        "# HeatSync Labs Wiki: Contributor Analysis",
        "",
        f"**Total unique contributors:** {len(contributors_data)}",
        "",
    ]

    # Sort by edit count
    sorted_contribs = sorted(contributors_data.items(), key=lambda x: x[1]["edit_count"], reverse=True)

    # Top contributors
    lines.append("## Top 30 Contributors by Edit Count")
    lines.append("")
    lines.append("| Rank | Username | Edits | Pages | First Edit | Last Edit |")
    lines.append("|------|----------|-------|-------|------------|-----------|")
    for i, (uname, data) in enumerate(sorted_contribs[:30], 1):
        first = data["first_edit"][:10] if data["first_edit"] else "?"
        last = data["last_edit"][:10] if data["last_edit"] else "?"
        lines.append(f"| {i} | {uname} | {data['edit_count']} | {data['page_count']} | {first} | {last} |")
    lines.append("")

    # Activity distribution
    edit_brackets = {"1 edit": 0, "2-5": 0, "6-20": 0, "21-50": 0, "51-100": 0, "100+": 0}
    for uname, data in contributors_data.items():
        n = data["edit_count"]
        if n == 1:
            edit_brackets["1 edit"] += 1
        elif n <= 5:
            edit_brackets["2-5"] += 1
        elif n <= 20:
            edit_brackets["6-20"] += 1
        elif n <= 50:
            edit_brackets["21-50"] += 1
        elif n <= 100:
            edit_brackets["51-100"] += 1
        else:
            edit_brackets["100+"] += 1

    lines.append("## Contributor Activity Distribution")
    lines.append("")
    lines.append("| Edit Range | Contributors |")
    lines.append("|------------|-------------|")
    for bracket, count in edit_brackets.items():
        lines.append(f"| {bracket} | {count} |")
    lines.append("")

    # Year-based activity
    year_activity = defaultdict(set)
    for uname, data in contributors_data.items():
        if data["first_edit"]:
            year = data["first_edit"][:4]
            year_activity[year].add(uname)
        if data["last_edit"]:
            year = data["last_edit"][:4]
            year_activity[year].add(uname)

    lines.append("## Contributors Active by Year (first/last edit)")
    lines.append("")
    lines.append("| Year | Active Contributors |")
    lines.append("|------|-------------------|")
    for year in sorted(year_activity.keys()):
        lines.append(f"| {year} | {len(year_activity[year])} |")
    lines.append("")

    return "\n".join(lines)


def generate_statistics(stats, pages_classified, categories_grouped):
    """Generate analysis/statistics.md."""
    lines = [
        "# HeatSync Labs Wiki: Statistics",
        "",
        "## Aggregate Numbers",
        "",
        f"- **Total pages:** {stats['total_pages']}",
        f"- **Content pages (non-redirect):** {stats['content_pages']}",
        f"- **Redirect pages:** {stats['redirect_count']}",
        f"- **Total revisions:** {stats['total_revisions']}",
        f"- **Unique contributors:** {stats['unique_contributors']}",
        f"- **XML dump size:** {stats['xml_size_bytes']:,} bytes ({stats['xml_size_bytes']/1048576:.1f} MB)",
        "",
        "## Pages by Namespace",
        "",
        "| NS | Name | Count |",
        "|-----|------|-------|",
    ]

    ns_names = {
        0: "Main", 1: "Talk", 2: "User", 3: "User talk",
        4: "Project", 6: "File", 8: "MediaWiki", 10: "Template",
        12: "Help", 14: "Category", 100: "Corp", 102: "Board",
    }
    for ns, count in sorted(stats["namespace_counts"].items(), key=lambda x: int(x[0])):
        name = ns_names.get(int(ns), f"NS {ns}")
        lines.append(f"| {ns} | {name} | {count} |")
    lines.append("")

    lines.append("## Pages by Category")
    lines.append("")
    lines.append("| Category | Count |")
    lines.append("|----------|-------|")
    for cat in sorted(categories_grouped.keys(), key=lambda c: (-len(categories_grouped[c]), c)):
        lines.append(f"| {cat} | {len(categories_grouped[cat])} |")
    lines.append("")

    # Revision stats
    rev_counts = [p["revision_count"] for p in pages_classified]
    lines.append("## Revision Statistics")
    lines.append("")
    lines.append(f"- **Average revisions per page:** {sum(rev_counts)/len(rev_counts):.1f}")
    lines.append(f"- **Max revisions:** {max(rev_counts)} (Main Page)")
    lines.append(f"- **Pages with 1 revision:** {sum(1 for r in rev_counts if r == 1)}")
    lines.append(f"- **Pages with 10+ revisions:** {sum(1 for r in rev_counts if r >= 10)}")
    lines.append(f"- **Pages with 50+ revisions:** {sum(1 for r in rev_counts if r >= 50)}")
    lines.append("")

    # Size stats
    sizes = [p["bytes"] for p in pages_classified if p["bytes"] > 0]
    if sizes:
        lines.append("## Size Statistics")
        lines.append("")
        lines.append(f"- **Total content:** {sum(sizes):,} bytes ({sum(sizes)/1048576:.1f} MB)")
        lines.append(f"- **Average page size:** {sum(sizes)//len(sizes):,} bytes")
        lines.append(f"- **Largest page:** {max(sizes):,} bytes")
        lines.append(f"- **Pages over 10KB:** {sum(1 for s in sizes if s > 10000)}")
        lines.append("")

    return "\n".join(lines)


def main():
    start = time.time()
    print("Phase 2: Classifying and analyzing pages...")

    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    manifest = load_manifest()

    with open(DATA_DIR / "statistics.json") as f:
        stats = json.load(f)

    with open(DATA_DIR / "contributors.json") as f:
        contributors_data = json.load(f)

    # Classify every page
    pages_classified = []
    categories_grouped = defaultdict(list)
    governance_pages = []

    for entry in manifest:
        slug = entry["slug"]
        page = load_page(slug)
        text = page["latest_revision"]["text"] if page else ""

        category = classify_page(
            entry["title"], entry["ns"], text, entry["is_redirect"]
        )

        classified = {
            **entry,
            "category": category,
        }
        pages_classified.append(classified)
        categories_grouped[category].append(classified)

        if is_governance_page(entry["title"], entry["ns"], category, text):
            sections = extract_sections(text)
            classified["sections"] = sections
            classified["text_preview"] = text[:3000]
            governance_pages.append(classified)

    print(f"  Classified {len(pages_classified)} pages into {len(categories_grouped)} categories")

    # Save governance pages list
    gov_out = []
    for p in sorted(governance_pages, key=lambda x: x["title"].lower()):
        gov_entry = {k: v for k, v in p.items() if k != "text_preview"}
        gov_out.append(gov_entry)
    with open(DATA_DIR / "governance_pages.json", "w", encoding="utf-8") as f:
        json.dump(gov_out, f, ensure_ascii=False, indent=2)
    print(f"  Governance pages: {len(gov_out)}")

    # Generate analysis documents
    print("  Generating page_catalog.md...")
    catalog = generate_page_catalog(pages_classified, categories_grouped)
    with open(ANALYSIS_DIR / "page_catalog.md", "w", encoding="utf-8") as f:
        f.write(catalog)

    print("  Generating governance_inventory.md...")
    inventory = generate_governance_inventory(governance_pages)
    with open(ANALYSIS_DIR / "governance_inventory.md", "w", encoding="utf-8") as f:
        f.write(inventory)

    print("  Generating contributor_analysis.md...")
    contrib = generate_contributor_analysis(contributors_data)
    with open(ANALYSIS_DIR / "contributor_analysis.md", "w", encoding="utf-8") as f:
        f.write(contrib)

    print("  Generating statistics.md...")
    stats_md = generate_statistics(stats, pages_classified, categories_grouped)
    with open(ANALYSIS_DIR / "statistics.md", "w", encoding="utf-8") as f:
        f.write(stats_md)

    # Generate README
    readme = [
        "# HeatSync Labs Wiki Dump: Analysis",
        "",
        "Comprehensive analysis of the HeatSync Labs (Phoenix/Tempe AZ) MediaWiki dump.",
        "",
        f"- **{stats['total_pages']}** pages, **{stats['total_revisions']}** revisions",
        f"- **{stats['unique_contributors']}** contributors spanning 2009-2026",
        f"- **{len(governance_pages)}** governance-related documents identified",
        "",
        "## Documents",
        "",
        "- [Page Catalog](page_catalog.md) - Every page classified and cataloged",
        "- [Governance Inventory](governance_inventory.md) - Deep dive on governance documents",
        "- [Contributor Analysis](contributor_analysis.md) - Who built this wiki",
        "- [Statistics](statistics.md) - Aggregate numbers",
        "- [History of the Space](history_of_space.md) - Narrative history (Phase 3)",
        "- [History of Governance](history_of_governance.md) - Governance evolution (Phase 3)",
        "",
    ]
    with open(ANALYSIS_DIR / "README.md", "w", encoding="utf-8") as f:
        f.write("\n".join(readme))

    elapsed = time.time() - start
    print(f"\nPhase 2 complete in {elapsed:.1f}s")

    # Phase marker
    with open(BASE_DIR / ".phase2_complete", "w") as f:
        f.write(f"Completed at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Categories: {len(categories_grouped)}, Governance pages: {len(governance_pages)}\n")


if __name__ == "__main__":
    main()
