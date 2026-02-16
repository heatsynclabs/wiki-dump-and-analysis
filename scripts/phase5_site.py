#!/usr/bin/env python3
"""Phase 5: Generate static governance site from converted pages and improvements."""

import json
import os
import re
import sys
import time
from pathlib import Path

import jinja2

sys.path.insert(0, os.path.dirname(__file__))
from lib.diff_generator import generate_diff_html, generate_inline_diff, generate_change_summary
from lib.wikitext_converter import convert_wikitext

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CONVERTED_DIR = DATA_DIR / "converted"
IMPROVED_DIR = DATA_DIR / "improved"
SITE_DIR = BASE_DIR / "site"
PAGES_DIR = SITE_DIR / "pages"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def markdown_to_html(md_text: str) -> str:
    """Simple markdown to HTML converter for improved docs."""
    lines = md_text.split("\n")
    html_parts = []
    in_list = None  # 'ul' or 'ol'
    in_code = False
    in_table = False

    for line in lines:
        # Skip YAML frontmatter
        if line.strip() == "---":
            continue
        if line.startswith("title:") or line.startswith("type:") or \
           line.startswith("changes:") or line.startswith("rationale:") or \
           line.startswith("  -") and not in_list:
            continue

        # Code blocks
        if line.strip().startswith("```"):
            if in_code:
                html_parts.append("</pre>")
                in_code = False
            else:
                html_parts.append("<pre>")
                in_code = True
            continue
        if in_code:
            html_parts.append(_escape(line))
            continue

        # Tables
        if "|" in line and line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            # Skip separator rows
            if all(re.match(r'^[-:]+$', c) for c in cells):
                continue
            if not in_table:
                html_parts.append("<table>")
                in_table = True
                # First row is header
                html_parts.append("<tr>" + "".join(f"<th>{_inline_md(c)}</th>" for c in cells) + "</tr>")
                continue
            html_parts.append("<tr>" + "".join(f"<td>{_inline_md(c)}</td>" for c in cells) + "</tr>")
            continue
        elif in_table:
            html_parts.append("</table>")
            in_table = False

        # Headers
        m = re.match(r'^(#{1,6})\s+(.+)', line)
        if m:
            if in_list:
                html_parts.append(f"</{in_list}>")
                in_list = None
            level = len(m.group(1))
            text = _inline_md(m.group(2))
            anchor = re.sub(r'[^a-zA-Z0-9_-]', '-', m.group(2).lower()).strip('-')
            html_parts.append(f'<h{level} id="{anchor}">{text}</h{level}>')
            continue

        # Horizontal rule
        if re.match(r'^---+\s*$', line):
            if in_list:
                html_parts.append(f"</{in_list}>")
                in_list = None
            html_parts.append("<hr>")
            continue

        # Unordered list
        m = re.match(r'^(\s*)[-*]\s+(.+)', line)
        if m:
            if not in_list:
                html_parts.append("<ul>")
                in_list = "ul"
            content = _inline_md(m.group(2))
            # Checkbox
            content = content.replace("[ ]", "&#9744;").replace("[x]", "&#9745;")
            html_parts.append(f"<li>{content}</li>")
            continue

        # Ordered list
        m = re.match(r'^(\s*)\d+\.\s+(.+)', line)
        if m:
            if in_list != "ol":
                if in_list:
                    html_parts.append(f"</{in_list}>")
                html_parts.append("<ol>")
                in_list = "ol"
            html_parts.append(f"<li>{_inline_md(m.group(2))}</li>")
            continue

        # Close list if not continuing
        if in_list and line.strip() == "":
            html_parts.append(f"</{in_list}>")
            in_list = None
            continue

        # Blockquote
        if line.startswith("> "):
            if in_list:
                html_parts.append(f"</{in_list}>")
                in_list = None
            html_parts.append(f"<blockquote>{_inline_md(line[2:])}</blockquote>")
            continue

        # Regular paragraph
        if line.strip():
            if in_list:
                html_parts.append(f"</{in_list}>")
                in_list = None
            html_parts.append(f"<p>{_inline_md(line)}</p>")

    if in_list:
        html_parts.append(f"</{in_list}>")
    if in_table:
        html_parts.append("</table>")

    return "\n".join(html_parts)


def _inline_md(text: str) -> str:
    """Convert inline markdown to HTML."""
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Code
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    # Links [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    return text


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_nav(gov_pages):
    """Build sidebar navigation structure from governance pages.

    The 'governance' section follows the policy hierarchy defined in
    Bylaws Article VIII: Bylaws > Community Standards > Community Policies >
    Rules / Operational Policies / Procedures / Access Card Procedure.
    """
    # Governance docs in hierarchy order (matching Bylaws Article VIII)
    governance_order = [
        "Bylaws",
        "Community Standards",
        "Community Policies",
        "Rules",
        "Operational Policies",
        "Procedures",
        "Access Card Procedure",
        "Proposals",
    ]
    governance_set = set(governance_order)

    guides_titles = {"How to Run HeatSync Labs", "How To Hackerspace",
                     "Walk Through Orientation", "2kproposal"}
    board_titles = {"Board Members", "Board Elections", "2012 Board Elections"}
    legal_titles = {"501(c)3 Filings", "501c3", "501c3 narrative", "Insurance",
                    "Nonprofit Annual Filings", "Starting a Non-Profit",
                    "3yrfinancial", "Forms", "Secretary HowTo", "Liability Waiver"}
    meeting_titles_prefix = {"Board:", "HYH Meeting", "Meetings",
                             "2012 September 27 Hack Your Hackerspace"}

    nav = {"governance": [], "guides": [], "board": [], "legal": [], "meetings": []}

    # Build slug lookup
    slug_by_title = {}
    for page in gov_pages:
        slug_by_title[page["title"]] = page["slug"]

    # Add governance docs in explicit hierarchy order
    for title in governance_order:
        if title in slug_by_title:
            nav["governance"].append({"title": title, "slug": slug_by_title[title]})

    # Sort remaining pages into categories
    for page in sorted(gov_pages, key=lambda p: p["title"].lower()):
        title = page["title"]
        if title in governance_set:
            continue  # already added in order
        entry = {"title": title, "slug": page["slug"]}

        if title in guides_titles:
            nav["guides"].append(entry)
        elif title in board_titles or title.startswith("Board:"):
            nav["board"].append(entry)
        elif title in legal_titles:
            nav["legal"].append(entry)
        elif any(title.startswith(p) or title == p for p in meeting_titles_prefix):
            nav["meetings"].append(entry)
        else:
            nav["guides"].append(entry)

    return nav


def filesizeformat(value):
    """Jinja2 filter: format bytes as human-readable."""
    for unit in ('B', 'KB', 'MB', 'GB'):
        if abs(value) < 1024.0:
            return f"{value:.1f} {unit}"
        value /= 1024.0
    return f"{value:.1f} TB"


def parse_frontmatter(md_text: str) -> dict:
    """Parse YAML-like frontmatter from improved markdown files."""
    meta = {"changes": [], "rationale": ""}
    in_frontmatter = False
    frontmatter_done = False
    content_lines = []
    current_key = None

    for line in md_text.split("\n"):
        if not frontmatter_done and line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                in_frontmatter = False
                frontmatter_done = True
                continue

        if in_frontmatter:
            if line.startswith("  - "):
                val = line.strip()[2:].strip().strip('"')
                if current_key == "changes":
                    meta["changes"].append(val)
            elif line.startswith("  "):
                if current_key == "rationale":
                    meta["rationale"] += " " + line.strip()
            elif ":" in line:
                key, _, val = line.partition(":")
                current_key = key.strip()
                val = val.strip()
                if val == ">":
                    val = ""
                if current_key == "rationale":
                    meta["rationale"] = val
        else:
            content_lines.append(line)

    meta["content"] = "\n".join(content_lines)
    meta["rationale"] = meta["rationale"].strip()
    return meta


def main():
    start = time.time()
    print("Phase 5: Building static governance site...")

    os.makedirs(PAGES_DIR, exist_ok=True)

    # Load data
    gov_pages = load_json(DATA_DIR / "governance_pages.json")
    stats = load_json(DATA_DIR / "statistics.json")

    # Map of slug -> improved file content
    improved_files = {}
    for f in IMPROVED_DIR.glob("*.md"):
        slug = f.stem
        with open(f, encoding="utf-8") as fh:
            improved_files[slug] = fh.read()

    # Build nav
    nav = build_nav(gov_pages)

    # Setup Jinja2
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=False,
    )
    env.filters["filesizeformat"] = filesizeformat

    common_ctx = {
        "nav_governance": nav["governance"],
        "nav_guides": nav["guides"],
        "nav_board": nav["board"],
        "nav_legal": nav["legal"],
        "nav_meetings": nav["meetings"],
    }

    # Generate index page
    print("  Generating index.html...")
    core_order = ["Bylaws", "Community Standards", "Community Policies",
                  "Rules", "How to Run HeatSync Labs",
                  "Operational Policies", "Procedures", "Proposals",
                  "Access Card Procedure", "How To Hackerspace"]
    core_pages = []
    for title in core_order:
        for p in gov_pages:
            if p["title"] == title:
                page_info = dict(p)
                page_info["has_improved"] = p["slug"] in improved_files
                core_pages.append(page_info)
                break

    board_pages = [p for p in gov_pages if p["title"].startswith("Board") or
                   p["title"] == "2012 Board Elections"]

    index_tmpl = env.get_template("index.html")
    index_html = index_tmpl.render(
        title="Home",
        stats=stats,
        governance_count=len(gov_pages),
        core_pages=core_pages,
        board_pages=board_pages,
        root_path="",
        css_path="",
        js_path="",
        **common_ctx,
    )
    with open(SITE_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    # Generate governance pages
    print("  Generating governance pages...")
    page_tmpl = env.get_template("governance_page.html")

    for entry in gov_pages:
        slug = entry["slug"]
        title = entry["title"]

        # Load converted HTML
        converted_path = CONVERTED_DIR / f"{slug}.html"
        if not converted_path.exists():
            continue
        with open(converted_path, encoding="utf-8") as f:
            current_html = f.read()

        has_improved = slug in improved_files
        improved_html = ""
        diff_html = ""
        change_summary = ""

        if has_improved:
            meta = parse_frontmatter(improved_files[slug])
            improved_html = markdown_to_html(meta["content"])
            change_summary = generate_change_summary(meta["changes"], meta["rationale"])

            # Generate diff from original wiki text to improved markdown
            page_path = DATA_DIR / "pages" / f"{slug}.json"
            if page_path.exists():
                page_data = load_json(page_path)
                orig_text = page_data["latest_revision"]["text"]
                diff_html = generate_inline_diff(orig_text, meta["content"])

        page_html = page_tmpl.render(
            title=title,
            page_title=title,
            revision_count=entry["revision_count"],
            bytes=entry["bytes"],
            first_timestamp=entry.get("first_timestamp", entry["latest_timestamp"]),
            latest_timestamp=entry["latest_timestamp"],
            category=entry["category"],
            has_improved=has_improved,
            current_html=current_html,
            improved_html=improved_html,
            diff_html=diff_html,
            change_summary=change_summary,
            root_path="../",
            css_path="../",
            js_path="../",
            **common_ctx,
        )

        with open(PAGES_DIR / f"{slug}.html", "w", encoding="utf-8") as f:
            f.write(page_html)

    # Generate history pages
    print("  Generating history pages...")
    history_tmpl = env.get_template("history_page.html")

    for md_file, out_name, page_title in [
        ("history_of_space.md", "history_space.html", "History of HeatSync Labs"),
        ("history_of_governance.md", "history_governance.html", "History of Governance"),
    ]:
        md_path = BASE_DIR / "analysis" / md_file
        if md_path.exists():
            with open(md_path, encoding="utf-8") as f:
                md_content = f.read()
            html_content = markdown_to_html(md_content)
            page_html = history_tmpl.render(
                title=page_title,
                content=html_content,
                root_path="../",
                css_path="../",
                js_path="../",
                **common_ctx,
            )
            with open(PAGES_DIR / out_name, "w", encoding="utf-8") as f:
                f.write(page_html)

    elapsed = time.time() - start
    page_count = len(list(PAGES_DIR.glob("*.html")))
    print(f"\nPhase 5 complete in {elapsed:.1f}s")
    print(f"  Site pages: {page_count}")
    print(f"  Site dir: {SITE_DIR}")
    print(f"  Preview: python -m http.server 8000 --directory site/")

    with open(BASE_DIR / ".phase5_complete", "w") as f:
        f.write(f"Completed at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Pages: {page_count}\n")


if __name__ == "__main__":
    main()
