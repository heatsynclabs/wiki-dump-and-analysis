#!/usr/bin/env python3
"""Phase 1: Parse MediaWiki XML dump into structured JSON files."""

import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

# Add scripts dir to path
sys.path.insert(0, os.path.dirname(__file__))
from lib.wiki_parser import parse_pages, slugify

BASE_DIR = Path(__file__).resolve().parent.parent
DUMP_PATH = BASE_DIR / "dumps" / "wiki.heatsynclabs.org_w-20260215-history.xml"
DATA_DIR = BASE_DIR / "data"
PAGES_DIR = DATA_DIR / "pages"
REVISION_DIR = DATA_DIR / "revision_history"

# Keywords that suggest governance content - used to decide which pages get full revision history
GOVERNANCE_KEYWORDS = {
    "bylaws", "rules", "policy", "policies", "procedure", "procedures",
    "governance", "board", "membership", "code of conduct", "proposal",
    "how to run", "operational", "elections", "meeting minutes",
    "card access", "access card", "how to hackerspace", "guidelines",
    "corp:", "board:",
}


def is_governance_candidate(title: str, ns: int) -> bool:
    """Check if a page should get full revision history saved."""
    title_lower = title.lower()
    # Board namespace (102) always qualifies
    if ns == 102:
        return True
    # Corp namespace (100)
    if ns == 100:
        return True
    # Keyword match
    for kw in GOVERNANCE_KEYWORDS:
        if kw in title_lower:
            return True
    return False


def main():
    start = time.time()
    print(f"Phase 1: Parsing {DUMP_PATH.name}...")

    os.makedirs(PAGES_DIR, exist_ok=True)
    os.makedirs(REVISION_DIR, exist_ok=True)

    manifest = []
    contributors = defaultdict(lambda: {
        "edit_count": 0,
        "first_edit": None,
        "last_edit": None,
        "pages_touched": set(),
    })
    total_revisions = 0
    total_pages = 0
    redirect_count = 0
    ns_counts = defaultdict(int)
    governance_revision_count = 0

    for page in parse_pages(str(DUMP_PATH)):
        total_pages += 1
        title = page["title"]
        ns = page.get("ns", 0)
        page_id = page.get("id", 0)
        slug = slugify(title)
        revisions = page["revisions"]
        total_revisions += len(revisions)
        ns_counts[ns] += 1

        # Sort revisions by timestamp (newest first)
        revisions.sort(key=lambda r: r["timestamp"], reverse=True)
        latest = revisions[0]
        oldest = revisions[-1]

        # Check if redirect
        is_redirect = latest["text"].strip().upper().startswith("#REDIRECT")

        # Track contributors
        for rev in revisions:
            contrib = rev.get("contributor", {})
            uname = contrib.get("username") or contrib.get("ip") or "anonymous"
            c = contributors[uname]
            c["edit_count"] += 1
            c["pages_touched"].add(title)
            ts = rev["timestamp"]
            if c["first_edit"] is None or ts < c["first_edit"]:
                c["first_edit"] = ts
            if c["last_edit"] is None or ts > c["last_edit"]:
                c["last_edit"] = ts

        # Write per-page JSON (latest revision + metadata)
        page_json = {
            "title": title,
            "ns": ns,
            "id": page_id,
            "slug": slug,
            "latest_revision": {
                "id": latest["id"],
                "timestamp": latest["timestamp"],
                "contributor": latest["contributor"],
                "comment": latest["comment"],
                "text": latest["text"],
                "bytes": latest["bytes"],
            },
            "revision_count": len(revisions),
            "first_revision_timestamp": oldest["timestamp"],
            "is_redirect": is_redirect,
        }
        page_path = PAGES_DIR / f"{slug}.json"
        with open(page_path, "w", encoding="utf-8") as f:
            json.dump(page_json, f, ensure_ascii=False, indent=2)

        # Manifest entry
        manifest.append({
            "title": title,
            "ns": ns,
            "id": page_id,
            "slug": slug,
            "latest_timestamp": latest["timestamp"],
            "first_timestamp": oldest["timestamp"],
            "bytes": latest["bytes"],
            "revision_count": len(revisions),
            "is_redirect": is_redirect,
        })

        # Full revision history for governance pages
        if is_governance_candidate(title, ns):
            governance_revision_count += len(revisions)
            rev_data = {
                "title": title,
                "slug": slug,
                "ns": ns,
                "revision_count": len(revisions),
                "revisions": [
                    {
                        "id": r["id"],
                        "parent_id": r["parent_id"],
                        "timestamp": r["timestamp"],
                        "contributor": r["contributor"],
                        "comment": r["comment"],
                        "text": r["text"],
                        "bytes": r["bytes"],
                    }
                    for r in revisions
                ],
            }
            rev_path = REVISION_DIR / f"{slug}_revisions.json"
            with open(rev_path, "w", encoding="utf-8") as f:
                json.dump(rev_data, f, ensure_ascii=False, indent=2)

        if total_pages % 100 == 0:
            print(f"  Processed {total_pages} pages...")

        if is_redirect:
            redirect_count += 1

    # Write manifest
    manifest.sort(key=lambda p: p["title"].lower())
    with open(DATA_DIR / "pages_all.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    # Write contributors
    contrib_out = {}
    for uname, data in sorted(contributors.items(), key=lambda x: x[1]["edit_count"], reverse=True):
        contrib_out[uname] = {
            "edit_count": data["edit_count"],
            "first_edit": data["first_edit"],
            "last_edit": data["last_edit"],
            "pages_touched": sorted(data["pages_touched"]),
            "page_count": len(data["pages_touched"]),
        }
    with open(DATA_DIR / "contributors.json", "w", encoding="utf-8") as f:
        json.dump(contrib_out, f, ensure_ascii=False, indent=2)

    # Write statistics
    stats = {
        "total_pages": total_pages,
        "total_revisions": total_revisions,
        "redirect_count": redirect_count,
        "content_pages": total_pages - redirect_count,
        "unique_contributors": len(contributors),
        "namespace_counts": dict(ns_counts),
        "governance_revision_files": len(list(REVISION_DIR.glob("*.json"))),
        "governance_total_revisions": governance_revision_count,
        "xml_size_bytes": DUMP_PATH.stat().st_size,
        "parse_time_seconds": round(time.time() - start, 2),
    }
    with open(DATA_DIR / "statistics.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    elapsed = time.time() - start
    print(f"\nPhase 1 complete in {elapsed:.1f}s")
    print(f"  Pages: {total_pages}")
    print(f"  Revisions: {total_revisions}")
    print(f"  Redirects: {redirect_count}")
    print(f"  Contributors: {len(contributors)}")
    print(f"  Namespace breakdown: {dict(ns_counts)}")
    print(f"  Governance revision files: {stats['governance_revision_files']}")

    # Write phase marker
    with open(BASE_DIR / ".phase1_complete", "w") as f:
        f.write(f"Completed at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Pages: {total_pages}, Revisions: {total_revisions}\n")


if __name__ == "__main__":
    main()
