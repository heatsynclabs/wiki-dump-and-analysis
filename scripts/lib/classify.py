"""Page classification for HeatSync Labs wiki pages."""

# Category definitions with namespace and keyword rules
# "keywords" match against title only; "content_keywords" match text (weaker)
CATEGORIES = {
    "governance": {
        "titles": {"bylaws", "rules", "operational policies", "procedures",
                   "how to run heatsync labs", "code of conduct",
                   "how to hackerspace", "membership guidelines",
                   "lab incident report"},
        "keywords": ["governance", "bylaw", "amendment"],
    },
    "board": {
        "ns": {102},
        "title_prefixes": ["board:"],
        "titles": {"board members", "board elections", "2012 board elections"},
        "keywords": [],
    },
    "meetings": {
        "keywords": ["meeting minutes", "meeting notes", "monthly meeting",
                     "hyh meeting"],
        "titles": {"meetings"},
    },
    "legal": {
        "titles": {"501c3", "501(c)3 filings", "articles of incorporation",
                   "insurance", "liability waiver", "nonprofit annual filings",
                   "starting a non-profit", "501c3 narrative", "3yrfinancial",
                   "forms", "secretary howto"},
        "keywords": ["501c3", "articles of incorporation", "non-profit",
                     "nonprofit annual"],
    },
    "operations": {
        "titles": {"access card procedure", "card access", "proposals",
                   "proposal process", "donation policy", "cleanup",
                   "hours", "space layout", "2kproposal",
                   "108 moving needs", "walk through orientation"},
        "keywords": ["procedure", "access card", "proposal",
                     "cleanup day"],
    },
    "membership": {
        "keywords": ["membership", "dues"],
        "titles": {"membership guidelines", "members"},
    },
    "projects": {
        "keywords": ["project", "printer", "cnc", "laser",
                     "arduino", "raspberry", "robot", "reprap", "3d print",
                     "fakerbot", "quadcopter", "drone", "woodshop",
                     "wood shop", "breadboard", "circuits"],
        "titles": {"business plan", "projects", "woodshop", "wood shop"},
    },
    "events": {
        "keywords": ["event", "workshop", "hackathon", "party",
                     "maker faire", "open house", "grand opening",
                     "first friday"],
        "titles": {"events", "classes", "first friday"},
    },
    "community": {
        "keywords": ["community", "outreach", "press", "social",
                     "web presence", "donation", "fundrais", "sponsor",
                     "marketing", "media coverage"],
        "titles": {"marketing", "web presence", "an idea for tempe migration"},
    },
    "infrastructure": {
        "keywords": ["network", "wifi", "server", "internet", "electrical",
                     "hvac", "plumbing", "construction", "renovation",
                     "equipment", "inventory", "space layout",
                     "location search"],
        "titles": {"1page"},
    },
    "corp": {
        "ns": {100},
        "title_prefixes": ["corp:"],
    },
}

# Namespace-based classification
NS_CATEGORIES = {
    1: "talk",       # Talk
    2: "user",       # User
    3: "user",       # User talk
    4: "meta",       # Project (HeatSync Labs Wiki)
    5: "meta",       # Project talk
    6: "file",       # File
    7: "file",       # File talk
    8: "meta",       # MediaWiki
    9: "meta",       # MediaWiki talk
    10: "meta",      # Template
    11: "meta",      # Template talk
    12: "meta",      # Help
    13: "meta",      # Help talk
    14: "meta",      # Category
    15: "meta",      # Category talk
}


def classify_page(title: str, ns: int, text: str = "", is_redirect: bool = False) -> str:
    """Classify a wiki page into a category.

    Priority: redirect > namespace mapping > exact title > title prefix > keyword in title > keyword in text > other.
    """
    if is_redirect:
        return "redirect"

    # Namespace-based (non-main, non-governance namespaces)
    if ns in NS_CATEGORIES:
        return NS_CATEGORIES[ns]

    title_lower = title.lower()

    # Check each category
    scores = {}
    for cat, rules in CATEGORIES.items():
        score = 0

        # Namespace match
        if "ns" in rules and ns in rules["ns"]:
            score += 100

        # Exact title match
        if "titles" in rules and title_lower in rules["titles"]:
            score += 50

        # Title prefix
        for prefix in rules.get("title_prefixes", []):
            if title_lower.startswith(prefix):
                score += 40

        # Keyword in title
        for kw in rules.get("keywords", []):
            if kw in title_lower:
                score += 20

        if score > 0:
            scores[cat] = score

    if scores:
        return max(scores, key=scores.get)

    return "other"


def is_governance_page(title: str, ns: int, category: str, text: str = "") -> bool:
    """Determine if a page is a governance document (for deep analysis)."""
    # Core governance categories
    if category == "governance":
        return True

    # Board meeting minutes are governance
    if category == "board":
        return True

    # Corp namespace
    if ns == 100:
        return True

    # Specific pages from various categories that are governance-related
    governance_titles = {
        # Operations
        "access card procedure", "card access", "proposals", "proposal process",
        "2kproposal", "walk through orientation",
        # Board
        "board members", "board elections", "2012 board elections",
        # Membership
        "membership guidelines",
        # Legal
        "501c3", "501(c)3 filings", "nonprofit annual filings",
        "starting a non-profit", "insurance", "liability waiver",
        "501c3 narrative", "3yrfinancial", "forms", "secretary howto",
        # Projects (but governance-relevant)
        "business plan",
        # Meetings
        "meetings", "hyh meeting 2012-12-13", "hyh meeting 2013-02-14",
        "2012 september 27 hack your hackerspace",
    }
    if title.lower() in governance_titles:
        return True

    return False
