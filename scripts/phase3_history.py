#!/usr/bin/env python3
"""Phase 3: Reconstruct history from revision data and generate narratives."""

import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PAGES_DIR = DATA_DIR / "pages"
REVISION_DIR = DATA_DIR / "revision_history"
ANALYSIS_DIR = BASE_DIR / "analysis"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_timeline(manifest, contributors):
    """Build a chronological timeline from all available data."""
    events = []

    # Track first page creation per year
    yearly_firsts = defaultdict(list)

    for page in manifest:
        ts = page.get("first_timestamp") or page["latest_timestamp"]
        year = ts[:4]
        yearly_firsts[year].append(page)

        # Major page creations
        if page["title"] in (
            "Bylaws", "Rules", "Main Page", "How to Run HeatSync Labs",
            "Board Members", "Business Plan", "Operational Policies",
            "Procedures", "Proposals", "Access Card Procedure",
            "501(c)3 Filings", "Walk Through Orientation",
        ):
            events.append({
                "date": ts[:10],
                "type": "page_created",
                "title": f"'{page['title']}' page created",
                "detail": f"First revision of {page['title']} ({page['bytes']:,} bytes latest)",
            })

    # Board meeting dates from Board: namespace pages
    for page in manifest:
        if page["title"].startswith("Board:"):
            ts = page.get("first_timestamp") or page["latest_timestamp"]
            events.append({
                "date": ts[:10],
                "type": "board_meeting",
                "title": page["title"],
                "detail": f"Board meeting documented ({page['revision_count']} revisions)",
            })

    # Track revision history for key governance docs
    key_docs = ["Bylaws", "Rules", "How_to_Run_HeatSync_Labs", "Operational_Policies"]
    for slug in key_docs:
        rev_path = REVISION_DIR / f"{slug}_revisions.json"
        if rev_path.exists():
            rev_data = load_json(rev_path)
            for rev in rev_data["revisions"]:
                if rev["comment"] and any(kw in rev["comment"].lower() for kw in
                    ["ratified", "approved", "major", "overhaul", "rewrite", "created page"]):
                    events.append({
                        "date": rev["timestamp"][:10],
                        "type": "governance_milestone",
                        "title": f"{rev_data['title']}: {rev['comment'][:100]}",
                        "detail": f"Size: {rev['bytes']} bytes",
                    })

    # Wiki activity milestones
    for year in sorted(yearly_firsts.keys()):
        pages = yearly_firsts[year]
        events.append({
            "date": f"{year}-01-01",
            "type": "activity_summary",
            "title": f"{year}: {len(pages)} pages created or first edited",
            "detail": "",
        })

    # Contributor milestones
    top_contribs = sorted(contributors.items(), key=lambda x: x[1]["edit_count"], reverse=True)[:10]
    for uname, data in top_contribs:
        events.append({
            "date": data["first_edit"][:10],
            "type": "contributor_joined",
            "title": f"Contributor {uname} first edit",
            "detail": f"Total edits: {data['edit_count']}, pages: {data['page_count']}",
        })

    events.sort(key=lambda e: e["date"])
    return events


def get_bylaws_size_over_time():
    """Track Bylaws document size across all revisions."""
    rev_path = REVISION_DIR / "Bylaws_revisions.json"
    if not rev_path.exists():
        return []
    data = load_json(rev_path)
    points = []
    for rev in sorted(data["revisions"], key=lambda r: r["timestamp"]):
        who = rev["contributor"].get("username") or rev["contributor"].get("ip") or "?"
        points.append({
            "date": rev["timestamp"][:10],
            "bytes": rev["bytes"],
            "contributor": who,
            "comment": rev["comment"][:120],
        })
    return points


def get_rules_size_over_time():
    """Track Rules document size across all revisions."""
    rev_path = REVISION_DIR / "Rules_revisions.json"
    if not rev_path.exists():
        return []
    data = load_json(rev_path)
    points = []
    for rev in sorted(data["revisions"], key=lambda r: r["timestamp"]):
        who = rev["contributor"].get("username") or rev["contributor"].get("ip") or "?"
        points.append({
            "date": rev["timestamp"][:10],
            "bytes": rev["bytes"],
            "contributor": who,
            "comment": rev["comment"][:120],
        })
    return points


def generate_history_of_space(manifest, contributors, timeline):
    """Generate analysis/history_of_space.md narrative."""
    # Group pages by year of creation
    year_pages = defaultdict(list)
    for p in manifest:
        ts = p.get("first_timestamp") or p["latest_timestamp"]
        year_pages[ts[:4]].append(p)

    # Count revisions per year
    all_revision_years = defaultdict(int)
    for p in manifest:
        # Approximate: assume revisions spread between first and latest
        first = p.get("first_timestamp") or p["latest_timestamp"]
        last = p["latest_timestamp"]
        for year in range(int(first[:4]), int(last[:4]) + 1):
            all_revision_years[str(year)] += 1

    lines = [
        "# History of HeatSync Labs",
        "",
        "A narrative history of HeatSync Labs (Phoenix/Tempe, AZ hackerspace) reconstructed",
        "from 939 wiki pages spanning 2009-2026, with 5,419 revisions by 263 contributors.",
        "",
        "---",
        "",
        "## Founding Era (2009-2010)",
        "",
        "HeatSync Labs traces its origins to late 2009, emerging from the Phoenix maker community.",
        "The wiki's earliest content dates from December 2009, when the Bylaws were first drafted",
        "at 9,300 bytes by an anonymous contributor (IP 65.103.203.33). This founding document",
        "established HeatSync Labs as an Arizona nonprofit corporation with a mission to provide",
        "\"a physical environment for mutual self-education and mutual self-enrichment.\"",
        "",
        "The earliest board meetings on record begin with the **November 19, 2009 Meeting**,",
        "suggesting formal organizational structure was being established even before the wiki.",
        "Through early 2010, board meetings occurred frequently (roughly biweekly), documenting",
        "decisions on space location, finances, and community building.",
        "",
    ]

    # Count board meetings
    board_meetings = [p for p in manifest if p["title"].startswith("Board:")]
    lines.extend([
        f"The wiki records **{len(board_meetings)} board meeting pages** in the Board: namespace,",
        "spanning 2009-2013. The meeting frequency suggests an actively governed organization",
        "from its earliest days.",
        "",
        "Key early milestones:",
        "- **December 2009**: Bylaws drafted, wiki established",
        "- **Early 2010**: Regular board meetings begin (biweekly schedule)",
        "- **2010**: Location search documented (86 revisions to '2010 Location Search' page)",
        "- **Mid-2010**: First space secured in Mesa/Tempe area",
        "",
        "The founding group included contributors who would shape the organization for years:",
    ])

    # Find earliest contributors
    early_contribs = [(u, d) for u, d in contributors.items()
                      if d["first_edit"] and d["first_edit"][:4] in ("2009", "2010")]
    early_contribs.sort(key=lambda x: x[1]["first_edit"])
    for uname, data in early_contribs[:10]:
        lines.append(f"- **{uname}**: {data['edit_count']} total edits, "
                     f"active {data['first_edit'][:4]}-{data['last_edit'][:4]}")
    lines.append("")

    lines.extend([
        "## Growth and Formalization (2011-2012)",
        "",
        "2011 saw rapid wiki growth with extensive documentation efforts:",
        "",
    ])

    pages_2011 = year_pages.get("2011", [])
    pages_2012 = year_pages.get("2012", [])
    lines.extend([
        f"- **{len(pages_2011)} pages** created/first-edited in 2011",
        f"- **{len(pages_2012)} pages** created/first-edited in 2012",
        "",
        "The **Rules** page was created in November 2010 and quickly became one of the most",
        "revised documents in the wiki (116 revisions total). The initial 2,097-byte document",
        "covering basic safety rules grew to cover membership guidelines, equipment procedures,",
        "and detailed workshop safety requirements.",
        "",
        "The **Business Plan** emerged as the most-revised document (132 revisions, 40KB),",
        "reflecting extensive planning for the space's sustainability.",
        "",
        "Board elections were formalized, with the **2012 Board Elections** page documenting",
        "the transition to regular election cycles. Board member tracking became systematic.",
        "",
        "The **Hack Your Hackerspace (HYH)** process emerged as a community governance",
        "mechanism - regular meetings where members could propose changes, discuss operations,",
        "and make collective decisions. A September 2012 meeting specifically focused on",
        "\"How to Hack Your Hackerspace\" governance.",
        "",
        "## Maturation (2013-2016)",
        "",
        "This period saw governance systems solidify:",
        "",
        "- The **How to Run HeatSync Labs** guide (42 revisions) codified board member",
        "  responsibilities across Champion, Treasurer, Secretary, and Operations roles",
        "- **Operational Policies** formalized day-to-day rules (sleeping in lab: max 2 nights/week;",
        "  tool certification requirements)",
        "- **Procedures** documented step-by-step processes for membership, payments, and equipment",
        "- The **Walk Through Orientation** (121 revisions, 9.5KB) became a comprehensive",
        "  onboarding document for new visitors and members",
        "",
        "The Board: namespace meetings taper off after mid-2013, suggesting a shift from",
        "board-centric governance toward the HYH community model.",
        "",
        "## Steady State Operations (2017-2023)",
        "",
        "Wiki activity settled into maintenance mode, with ongoing updates to:",
        "",
        "- Equipment documentation (Laser FAQ: 119 revisions, workshop rules)",
        "- Safety procedures and equipment-specific guidelines",
        "- Membership management and payment processing",
        "",
        "Board leadership saw regular turnover with annual elections. The Treasurer role",
        "showed particular continuity, with Shaundra Newstead serving continuously from 2022.",
        "",
        "The space continued to operate from its Mesa location, maintaining diverse",
        "capabilities: 3D printing, laser cutting, metalworking, woodworking, electronics,",
        "sewing, jewelry making, and more - documented across dozens of wiki pages.",
        "",
        "## Major Governance Overhaul (2024-2026)",
        "",
        "The most significant period of governance change since founding occurred in 2024-2025:",
        "",
    ])

    # Get recent bylaws changes
    bylaws_evolution = get_bylaws_size_over_time()
    recent_bylaws = [p for p in bylaws_evolution if p["date"] >= "2024-01-01"]

    lines.extend([
        "### Bylaws Modernization",
        "",
        f"The Bylaws underwent extensive revision, growing from their original 9.3KB (2009)",
        f"to **30.6KB** (2025). Key additions in 2024-2025:",
        "",
        "- **Card Access** section: Detailed eligibility, nomination, approval, and revocation",
        "  procedures (previously scattered across separate wiki pages)",
        "- **Proposal Process**: Formal 9-day discussion period, voting rules, 6-month",
        "  resubmission restrictions for failed proposals",
        "- **Code of Conduct**: Comprehensive behavioral standards based on Geek Feminism",
        "  model, with enforcement procedures and grievance processes",
        "- **Community Relations**: Standards for public representation",
        "- **Amendments** clause: Formal process for changing the bylaws themselves",
        "",
        "These changes were ratified via Slack vote in December 2025, with Brett Neese",
        "(Secretary) recording the formal amendments.",
        "",
        "### Operational Updates",
        "",
        "- **Rules** updated through October 2025 (19.7KB, 116 revisions) to align with",
        "  new membership tiers (Associate $25, Basic $50, Plus $100)",
        "- **Procedures** updated November 2024, renaming \"Operations Team\" to \"Welcoming Team\"",
        "- **How to Run HeatSync Labs** updated January 2026 with current board responsibilities",
        "",
        "### Current Board (2024-2025)",
        "",
        "- **Co-Champions**: David Lang & Landon",
        "- **Secretary**: Brett Neese",
        "- **Treasurer**: Shaundra Newstead & David Flores",
        "- **Operations**: Open position",
        "",
        "---",
        "",
        "## Wiki Statistics",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total pages | {len(manifest)} |",
        f"| Total revisions | 5,419 |",
        f"| Unique contributors | {len(contributors)} |",
        f"| Content pages (non-redirect) | {sum(1 for p in manifest if not p['is_redirect'])} |",
        f"| File pages | {sum(1 for p in manifest if p['ns'] == 6)} |",
        f"| Board meeting pages | {len(board_meetings)} |",
        "| Time span | Dec 2009 - Feb 2026 |",
        "",
        "## Pages by Year of Creation",
        "",
        "| Year | Pages Created |",
        "|------|--------------|",
    ])
    for year in sorted(year_pages.keys()):
        lines.append(f"| {year} | {len(year_pages[year])} |")
    lines.append("")

    return "\n".join(lines)


def generate_history_of_governance(manifest, contributors):
    """Generate analysis/history_of_governance.md."""
    bylaws_evolution = get_bylaws_size_over_time()
    rules_evolution = get_rules_size_over_time()

    lines = [
        "# History of HeatSync Labs Governance",
        "",
        "An analysis of how HeatSync Labs' governance structures evolved from 2009 to 2026,",
        "traced through 63 Bylaws revisions, 116 Rules revisions, and dozens of supporting",
        "governance documents.",
        "",
        "---",
        "",
        "## Phase 1: Founder-Driven (2009-2010)",
        "",
        "### Initial Structure",
        "",
        "The original Bylaws (December 28, 2009, 9,300 bytes) established:",
        "",
        "- Arizona nonprofit corporation",
        "- Board of Directors governance",
        "- Basic membership structure",
        "- Purpose: mutual self-education and enrichment",
        "",
        "The founding document was drafted by an anonymous contributor (IP 65.103.203.33),",
        "suggesting an informal founding group working from shared internet access (likely",
        "at Gangplank, the Phoenix coworking space where early maker meetups were held).",
        "",
        "### Board-Heavy Governance",
        "",
        "Board meetings were frequent and documented:",
        "",
    ]

    board_pages = sorted(
        [p for p in manifest if p["title"].startswith("Board:")],
        key=lambda p: p.get("first_timestamp", p["latest_timestamp"])
    )
    for bp in board_pages:
        ts = bp.get("first_timestamp", bp["latest_timestamp"])[:10]
        lines.append(f"- {bp['title']} ({ts})")
    lines.append("")

    lines.extend([
        "The biweekly meeting cadence and detailed minutes suggest a traditional",
        "board-of-directors model with formal decision-making processes.",
        "",
        "## Phase 2: Community Governance Emerges (2011-2013)",
        "",
        "### Rules Explosion",
        "",
        "The Rules page was created November 17, 2010 with basic safety rules (2,097 bytes).",
        "It underwent rapid expansion:",
        "",
    ])

    # Rules growth milestones
    if rules_evolution:
        prev_size = 0
        for point in rules_evolution:
            if point["bytes"] > prev_size * 1.5 and point["bytes"] > prev_size + 1000:
                lines.append(f"- **{point['date']}**: Grew to {point['bytes']:,}B "
                           f"({point['contributor']}) - {point['comment'][:60]}")
                prev_size = point["bytes"]
            elif point == rules_evolution[-1]:
                lines.append(f"- **{point['date']}**: Final state {point['bytes']:,}B "
                           f"({point['contributor']})")

    lines.extend([
        "",
        "### Hack Your Hackerspace (HYH)",
        "",
        "The HYH process emerged as a defining governance innovation. Rather than top-down",
        "board decisions, HYH meetings allowed any member to propose changes. This shifted",
        "decision-making from the board to the community.",
        "",
        "Key HYH milestones:",
        "- **September 2012**: Dedicated \"Hack Your Hackerspace\" governance discussion",
        "- **December 2012**: HYH Meeting documented community governance processes",
        "- **February 2013**: Continued HYH development",
        "",
        "The \"How to Run HeatSync Labs\" guide (created around 2012) explicitly states the",
        "board's role is to \"guide the community\" and \"empower individuals,\" not to dictate.",
        "",
        "### Board Meeting Decline",
        "",
        "Board: namespace pages end in mid-2013, coinciding with the HYH process maturing.",
        "This suggests governance successfully transitioned from board-centric to community-centric.",
        "",
        "**Note:** The wiki reportedly had ~37 board meeting pages; only",
        f"{len(board_pages)} survive in this dump, suggesting some institutional memory was lost",
        "to page deletions.",
        "",
        "## Phase 3: Operational Maturity (2014-2020)",
        "",
        "### Policy Documentation",
        "",
        "This period saw governance shift from structural questions to operational detail:",
        "",
        "- **Operational Policies** (2014): Formalized day-to-day rules",
        "  - Public space cleanliness standards",
        "  - Tool certification requirements",
        "  - Sleeping policy (max 2 nights/week)",
        "  - Card access voting rules",
        "",
        "- **Procedures** (2016+): Step-by-step administrative guides",
        "  - New member onboarding",
        "  - Payment processing (Square)",
        "  - Equipment certification tracking",
        "  - Purchase request workflow",
        "",
        "- **Access Card Procedure** (2014): Technical documentation for RFID access",
        "  management, showing the nuts-and-bolts of physical access control via",
        "  SSH/minicom serial interface",
        "",
        "### Stable Board Structure",
        "",
        "Board positions consolidated into four roles:",
        "1. **Champion** (later Co-Champions) - primary contact, vision keeper",
        "2. **Treasurer** - finances, banking, taxes, building management",
        "3. **Secretary** - communications, compliance, documentation",
        "4. **Operations** - volunteers, membership, facilities, safety",
        "",
        "Earlier specialized roles (PR/Marketing, Event Coordinator, Fundraising Coordinator,",
        "Editor, Resource Manager) were marked obsolete, reflecting a move toward broader",
        "role definitions.",
        "",
        "## Phase 4: Major Overhaul (2024-2026)",
        "",
        "### Bylaws Growth",
        "",
        "The most significant governance changes since founding:",
        "",
    ])

    # Bylaws size milestones
    if bylaws_evolution:
        key_sizes = []
        prev = 0
        for point in bylaws_evolution:
            if point["bytes"] > prev + 2000:
                key_sizes.append(point)
                prev = point["bytes"]
        for point in key_sizes:
            lines.append(f"- **{point['date']}**: {point['bytes']:,}B "
                       f"({point['contributor']}) - {point['comment'][:80]}")

    lines.extend([
        "",
        "### New Sections Added (2024-2025)",
        "",
        "The Bylaws grew from ~9KB to **30.6KB** with major new sections:",
        "",
        "#### Card Access (new section)",
        "- Eligibility: 2+ months membership at $50+/month level",
        "- Nomination: existing card member sponsors candidate",
        "- Public proposal period with community introduction",
        "- Vote: minimum 5 card members present, majority required",
        "- Mentor system: nominators responsible for nominees for 6 months",
        "- One nomination per year per member",
        "- Revocation process with 2/3 card access member majority",
        "",
        "#### Proposal Process (new section)",
        "- 9-day discussion period: 2 days submission, 5 days discussion, 2 days voting",
        "- Voting at HYH meetings with minimum 5 voting members",
        "- Failed proposals: 6-month waiting period before resubmission",
        "- Temporary measures during discussion period",
        "",
        "#### Code of Conduct (new section)",
        "- Based on Geek Feminism community standards",
        "- Defines acceptable and unacceptable behavior",
        "- Enforcement procedures with escalating consequences",
        "- Grievance process for disputes",
        "- Addresses weapons policy (Arizona state law compliance)",
        "",
        "#### Amendments Process",
        "- Formal procedure for changing bylaws",
        "- Ratification via community vote (December 2025 via Slack)",
        "",
        "### Identified Governance Gaps",
        "",
        "Despite the comprehensive 2025 overhaul, several governance best practices",
        "are still missing from the current bylaws:",
        "",
        "1. **Dissolution clause**: Required for 501(c)(3) status - must specify",
        "   asset distribution to another exempt organization upon dissolution",
        "2. **Fiscal year definition**: Not explicitly stated",
        "3. **Virtual meeting provisions**: No provisions for remote participation",
        "   (despite the Slack ratification precedent)",
        "4. **Officer removal process**: No clear process for removing board members",
        "   mid-term beyond the general termination provisions",
        "5. **Insurance/indemnification**: No provisions for board member indemnification",
        "",
        "---",
        "",
        "## Governance Document Evolution Summary",
        "",
        "| Document | Created | Revisions | Size (Current) | Key Role |",
        "|----------|---------|-----------|----------------|----------|",
        "| Bylaws | Dec 2009 | 63 | 30,634B | Constitutional document |",
        "| Rules | Nov 2010 | 116 | 19,673B | Safety & membership rules |",
        "| How to Run HSL | ~2012 | 42 | 5,988B | Board role guide |",
        "| Operational Policies | ~2014 | 13 | 1,426B | Day-to-day policies |",
        "| Procedures | ~2016 | 17 | 2,604B | Administrative processes |",
        "| Proposals | ~2011 | 6 | 1,598B | Equipment/change proposals |",
        "| Access Card Procedure | 2014 | 6 | 2,440B | Physical access mgmt |",
        "| Board Members | ~2010 | 40 | 3,693B | Leadership tracking |",
        "",
        "## Governance Model Diagram",
        "",
        "```",
        "Community (HYH Meetings)",
        "    |",
        "    +-- Proposals --> Discussion (9 days) --> Vote",
        "    |",
        "    +-- Card Access Nominations --> Vote",
        "    |",
        "Board of Directors",
        "    |",
        "    +-- Champion (external face, vision)",
        "    +-- Treasurer (money, building, taxes)",
        "    +-- Secretary (comms, compliance)",
        "    +-- Operations (volunteers, facilities)",
        "    |",
        "    +-- Annual elections (HYH meeting in April)",
        "```",
        "",
    ])

    return "\n".join(lines)


def main():
    start = time.time()
    print("Phase 3: Reconstructing history...")

    manifest = load_json(DATA_DIR / "pages_all.json")
    contributors = load_json(DATA_DIR / "contributors.json")

    # Build timeline
    print("  Building timeline...")
    timeline = build_timeline(manifest, contributors)
    with open(DATA_DIR / "timeline.json", "w", encoding="utf-8") as f:
        json.dump(timeline, f, ensure_ascii=False, indent=2)
    print(f"  Timeline: {len(timeline)} events")

    # Generate history of space
    print("  Generating history_of_space.md...")
    history = generate_history_of_space(manifest, contributors, timeline)
    with open(ANALYSIS_DIR / "history_of_space.md", "w", encoding="utf-8") as f:
        f.write(history)

    # Generate history of governance
    print("  Generating history_of_governance.md...")
    gov_history = generate_history_of_governance(manifest, contributors)
    with open(ANALYSIS_DIR / "history_of_governance.md", "w", encoding="utf-8") as f:
        f.write(gov_history)

    elapsed = time.time() - start
    print(f"\nPhase 3 complete in {elapsed:.1f}s")

    with open(BASE_DIR / ".phase3_complete", "w") as f:
        f.write(f"Completed at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")


if __name__ == "__main__":
    main()
