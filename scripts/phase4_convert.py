#!/usr/bin/env python3
"""Phase 4: Convert governance pages to HTML and draft improved versions."""

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from lib.wikitext_converter import convert_wikitext

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PAGES_DIR = DATA_DIR / "pages"
CONVERTED_DIR = DATA_DIR / "converted"
IMPROVED_DIR = DATA_DIR / "improved"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def convert_governance_pages():
    """Convert all governance pages from wikitext to HTML."""
    gov_pages = load_json(DATA_DIR / "governance_pages.json")
    converted = 0

    for entry in gov_pages:
        slug = entry["slug"]
        page_path = PAGES_DIR / f"{slug}.json"
        if not page_path.exists():
            continue

        page = load_json(page_path)
        text = page["latest_revision"]["text"]
        title = page["title"]

        html = convert_wikitext(text, title)

        # Wrap in a document fragment with title
        full_html = f'<article class="wiki-content">\n<h1>{title}</h1>\n{html}\n</article>'

        out_path = CONVERTED_DIR / f"{slug}.html"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(full_html)
        converted += 1

    return converted


# Improved document drafts
IMPROVEMENTS = {
    "Bylaws": {
        "changes": [
            "Restructured into lean 10-article legal framework",
            "Moved Card Access, Proposal Process, and Code of Conduct to separate Community Policies and Community Standards documents",
            "Added Article III: Board Member Standards with anti-discrimination/inclusion requirements",
            "Added Article IV: Member-Called Special Elections (petition mechanism for 8+ members)",
            "Added Article VIII: Community Governance (do-ocracy principle, policy hierarchy)",
            "Added dissolution clause (required for 501(c)(3) compliance)",
            "Added explicit fiscal year definition (January 1 - December 31)",
            "Added virtual/remote meeting provisions",
            "Added clear officer removal process",
            "Added board member indemnification provisions",
        ],
        "rationale": (
            "The previous Bylaws embedded operational policies (card access, proposal process, code of conduct) "
            "directly in the bylaws document. This makes iteration slow because amending bylaws requires a "
            "formal process, while community policies should be adaptable by simple HYH vote. The restructured "
            "bylaws are a lean legal framework that references separate Community Standards and Community Policies "
            "documents, adds member empowerment mechanisms (special elections), and includes anti-discrimination "
            "requirements for board members."
        ),
        "content": """\
# HeatSync Labs Bylaws (Improved Draft)

## Table of Contents

1. [Name and Purpose](#name-and-purpose)
2. [Organization](#organization)
3. [Interested Persons](#interested-persons)
4. [Membership](#membership)
5. [Card Access](#card-access)
6. [Proposal Process](#proposal-process)
7. [Code of Conduct](#code-of-conduct)
8. [Community Relations](#community-relations)
9. [Meetings](#meetings)
10. [Dissolution](#dissolution)
11. [Amendments](#amendments)

---

## I. NAME AND PURPOSE

1. The name of the organization is HeatSync Labs, Inc. ("HeatSync Labs" or "the Organization").
2. HeatSync Labs is organized exclusively for educational and charitable purposes within the meaning of Section 501(c)(3) of the Internal Revenue Code. The Organization provides a physical environment for mutual self-education and mutual self-enrichment in the areas of technology, science, and art.
3. **Fiscal Year.** The fiscal year of the Organization shall be January 1 through December 31.

## II. ORGANIZATION

1. HeatSync Labs shall have a Board of Directors ("the Board") consisting of the following officer positions: Champion, Treasurer, Secretary, and Operations.
2. All Board positions shall have equal authority. No single position carries executive power over the others.
3. Board decisions shall be made by majority vote of the Board members present, provided a quorum exists. A quorum shall consist of at least three (3) Board members.
4. For decisions regarding member termination, Code of Conduct enforcement, or other sensitive matters, a two-thirds (2/3) vote of the full Board shall be required.
5. Board members shall serve one-year terms beginning at the annual meeting. There are no term limits.
6. In the event of a vacancy, the remaining Board members may appoint an interim officer to serve until the next annual election.

### Officer Removal

7. Any officer may be removed from office by a two-thirds (2/3) vote of the other Board members, for cause including but not limited to: failure to fulfill duties, violation of the Code of Conduct, or conduct detrimental to the Organization.
8. The officer subject to removal shall be given at least fourteen (14) days written notice and an opportunity to be heard before the Board.

### Indemnification

9. The Organization shall indemnify any Board member or officer against expenses actually and necessarily incurred in connection with the defense of any action, suit, or proceeding in which they are made a party by reason of being or having been such Board member or officer, except in relation to matters as to which they shall be adjudged to be liable for negligence or misconduct in the performance of duty.

## III. INTERESTED PERSONS

1. Any Board member who has a financial, personal, or official interest in, or conflict (or appearance of conflict) with any matter pending before the Board, of such nature that it prevents or may prevent that member from acting on the matter in an impartial manner, shall disclose the nature of the interest to the Board.
2. After disclosure, that member shall not vote or use their personal influence on the matter, and shall not be counted as part of the quorum for the vote on the matter.
3. The minutes of the meeting shall reflect the disclosure, the abstention from voting, and the quorum situation.

## IV. MEMBERSHIP

*(Retained from current bylaws with formatting improvements)*

1. Membership is open to any individual who supports the mission of HeatSync Labs.
2. **Membership Tiers:**
   - **Associate** ($25/month): Access during staffed hours, participation in events and classes
   - **Basic** ($50/month): Full access during staffed hours, eligible for card access
   - **Plus** ($100/month): Full access, card access eligibility, supports community growth
3. Members in good standing may participate in HYH meetings and vote on proposals.
4. A member is in good standing if current on dues payments. Members more than 30 days past due will receive notice; members more than 60 days past due may have membership suspended.

## V. CARD ACCESS

*(Retained from current bylaws - this section was well-crafted in the 2025 overhaul)*

1. **Eligibility:** Members must have maintained at least Basic ($50/month) membership for a minimum of two (2) consecutive months.
2. **Nomination:** An existing card access member must nominate the candidate and serve as their mentor for six (6) months. Each card member may nominate only one candidate per calendar year.
3. **Proposal:** The nomination shall be submitted as a public proposal on the organization's communication channels, including an introduction of the candidate to the community.
4. **Approval:** Card access is granted by majority vote at an HYH meeting with a minimum of five (5) card access members present.
5. **Revocation:** Card access may be revoked by a two-thirds (2/3) vote of card access members present at an HYH meeting (minimum five present), or immediately by the Board in emergency situations involving safety concerns.

## VI. PROPOSAL PROCESS

*(Retained from current bylaws)*

1. Any member in good standing may submit a proposal for consideration.
2. **Timeline:**
   - Days 1-2: Submission and initial review
   - Days 3-7: Community discussion period
   - Days 8-9: Voting period at HYH meeting
3. A minimum of five (5) voting members must be present for a valid vote.
4. Proposals that fail may not be resubmitted for six (6) months unless substantially modified (as determined by the Board).

## VII. CODE OF CONDUCT

*(Retained from current bylaws - based on Geek Feminism community standards)*

1. All members, visitors, and guests are expected to treat each other with respect and courtesy.
2. Harassment, discrimination, and intimidation in any form are prohibited.
3. **Enforcement** follows an escalating process: verbal warning, written warning, temporary suspension, permanent ban.
4. **Grievance Process:** Any member may file a written grievance with the Board. The Board shall respond within fourteen (14) days.

## VIII. COMMUNITY RELATIONS

1. Members speaking publicly on behalf of HeatSync Labs must accurately represent the organization's positions and values.
2. The Champion serves as the primary public spokesperson; other members should coordinate with the Champion before making official statements.

## IX. MEETINGS

### Regular Meetings

1. **Hack Your Hackerspace (HYH):** Regular community meetings shall be held at least monthly for the conduct of organizational business, proposals, and community discussion.
2. **Annual Meeting:** The Board shall convene the first member meeting in April for annual business, including Board elections.

### Virtual Participation

3. Members may participate in HYH meetings and vote on proposals via approved electronic communication platforms (currently Slack), provided the meeting facilitator can verify participant identity.
4. Board meetings may be conducted virtually, provided all participants can communicate simultaneously.
5. Votes conducted electronically shall have the same force as in-person votes, provided the voting period and notification requirements are met.

## X. DISSOLUTION

1. The Organization may be dissolved by a two-thirds (2/3) vote of the membership at a meeting called for that purpose, with at least thirty (30) days advance written notice to all members.
2. Upon dissolution, after paying or making provision for the payment of all liabilities, the Board shall distribute remaining assets to one or more organizations organized exclusively for charitable, educational, or scientific purposes and which qualify as exempt organizations under Section 501(c)(3) of the Internal Revenue Code, or to a federal, state, or local government for a public purpose.
3. No part of the net earnings of the Organization shall inure to the benefit of any private individual.

## XI. AMENDMENTS

1. These Bylaws may be amended by a two-thirds (2/3) vote of members present at an HYH meeting, provided the proposed amendment has been submitted as a proposal following the standard Proposal Process (Article VI).
2. Amendments shall take effect immediately upon ratification unless otherwise specified.

---

*This improved draft preserves the strong governance framework established in the December 2025 overhaul while adding standard nonprofit provisions for IRS compliance and operational clarity.*
""",
    },

    "Rules": {
        "changes": [
            "Added enforcement ladder (verbal warning -> written warning -> suspension -> termination)",
            "Added equipment damage reporting procedure",
            "Consolidated scattered safety rules into unified structure",
            "Added cross-references to Bylaws for membership and card access",
            "Improved table of contents and navigation",
        ],
        "rationale": (
            "The Rules document is comprehensive (116 revisions of organic growth) but lacks "
            "a clear enforcement mechanism and damage reporting procedure. The enforcement ladder "
            "provides consistent, fair consequences while the damage reporting encourages "
            "transparency rather than hiding accidents."
        ),
        "content": """\
# HeatSync Labs Rules (Improved Draft)

## Table of Contents

1. [Membership Guidelines](#membership-guidelines)
2. [General Safety Rules](#general-safety-rules)
3. [Equipment Rules](#equipment-rules)
4. [Workshop-Specific Rules](#workshop-specific-rules)
5. [Enforcement](#enforcement)

---

## 1. Membership Guidelines

Membership tiers and eligibility are defined in the [Bylaws](Bylaws.html). Key points:

- **Associate** ($25/month): Access during staffed hours
- **Basic** ($50/month): Full access, card access eligible
- **Plus** ($100/month): Full access, enhanced support

### Good Standing

A member is in good standing when current on dues. Late payment process:
- 30 days past due: Reminder notice from Treasurer
- 60 days past due: Card access suspended; formal notice sent
- 90+ days past due: Membership terminated; may re-apply after settling balance

### Teacher Discount

Members who teach regular classes receive a 50% membership discount for the months they teach.

---

## 2. General Safety Rules

### Core Principles

- **You are responsible for your own safety.** Verify all equipment setup personally before use.
- **If you don't know how to use it, don't use it.** Ask for training first.
- **Clean up after yourself.** Leave the space better than you found it.
- **Report all accidents and near-misses** to the Board (see Enforcement section).

### Personal Protective Equipment

- Closed-toe shoes required in all workshop areas
- Safety glasses required when operating any power tool
- Hearing protection recommended for sustained loud operations
- No loose clothing, jewelry, or unsecured long hair near rotating equipment
- Long sleeves and welding gloves required for all welding operations

### General Rules

- No working alone on dangerous equipment (lathe, mill, welder) without another person present
- No alcohol or drug impairment while operating equipment
- Know the location of fire extinguishers, first aid kits, and emergency exits
- Minors must be supervised by a parent/guardian at all times

---

## 3. Equipment Rules

### Certification Requirements

**All dangerous tools require HeatSync Labs certification**, even if you have outside experience. Our equipment may have specific quirks, limitations, or procedures.

Certification is earned by:
1. Attending a scheduled training class, OR
2. Receiving one-on-one training from a certified member

Certified members are tracked on equipment-specific wiki pages.

### Equipment Damage and Reporting

If you damage equipment:
1. **Stop using the equipment immediately**
2. **Post to Slack (#general)** describing what happened
3. **Tag the equipment** with an "OUT OF ORDER" note including your name and date
4. **Notify the Board** via board@heatsynclabs.org

Honest reporting is valued. Accidents happen; hiding damage puts others at risk and is a more serious violation than the accident itself.

### Consumables

Members provide their own consumables (material, drill bits, sandpaper, etc.). Membership does not include supplies unless explicitly donated to the community.

---

## 4. Workshop-Specific Rules

### Laser Cutters

- See [Laser FAQ](Laser_FAQ.html) for detailed materials guide
- Never leave the laser unattended while operating
- Only approved materials (check the FAQ for the approved/banned list)
- Clean the bed and lens after use

### Metal Lathe & Mill

- No gloves while operating rotating equipment
- Secure workpiece properly; verify before starting
- Use appropriate speeds and feeds for material
- Remove chuck key before starting machine

### CNC Mill / CNC Router

- Certification required for each specific machine
- Verify tool paths in software before running
- Secure workpiece and verify zero positions
- Stay present during entire operation

### Welding

- Long sleeves, welding gloves, and welding helmet required
- Ensure adequate ventilation
- Check for flammable materials in the area before striking an arc
- Allow hot work to cool before leaving the area

### Woodshop

- Use push sticks on the table saw
- Never reach over a running blade
- Check for nails/metal before cutting reclaimed wood
- Use dust collection when available

### 3D Printers

- Check printer condition before starting a print
- Remove completed prints and clean the bed
- Report failed prints or maintenance issues to Slack
- Standard filament provided; specialty materials may be personal supply

---

## 5. Enforcement

### Enforcement Ladder

Violations are addressed through progressive enforcement:

1. **Verbal Warning:** Informal correction for minor or first-time issues
2. **Written Warning:** Documented notice from the Board for repeated or moderate violations
3. **Temporary Suspension:** 1-30 day suspension of membership and access for serious or repeated violations
4. **Membership Termination:** Permanent removal for severe violations or pattern of behavior

The Board may skip steps for severe safety violations or Code of Conduct breaches.

### Appeals

Members may appeal enforcement actions to the Board in writing within fourteen (14) days. The Board shall respond within fourteen (14) days of receiving the appeal.

---

*See also: [Bylaws](Bylaws.html) | [Operational Policies](Operational_Policies.html) | [Procedures](Procedures.html)*
""",
    },

    "How_to_Run_HeatSync_Labs": {
        "changes": [
            "Restructured as onboarding guide for new board members",
            "Added 'First 30 Days' checklist for each role",
            "Added institutional knowledge notes (accounting, banking, insurance)",
            "Preserved treasurer notes from Eric Wood (August 2023)",
            "Added section on community governance philosophy",
        ],
        "rationale": (
            "The current document mixes role definitions with accumulated institutional knowledge. "
            "Restructuring as an onboarding guide makes it more useful for incoming board members "
            "who need both the 'what' and the 'how' of their new roles."
        ),
        "content": """\
# How to Run HeatSync Labs: Board Member Onboarding Guide

## Philosophy

HeatSync Labs operates on a community governance model. The Board exists to:

1. **Guide the community** - facilitate decisions, don't dictate them
2. **Represent externally** - be the public face and legal representatives
3. **Empower individuals** - help members take ownership of projects and improvements

The Hack Your Hackerspace (HYH) meeting is the primary decision-making venue. The Board executes community decisions rather than making unilateral ones.

## Everyone on the Board Should...

- Attend every HYH meeting (or send a proxy with updates)
- Convert visitors into members through welcoming and engagement
- Support fundraising efforts
- Model the Code of Conduct
- Respond to board@heatsynclabs.org within 48 hours

---

## Champion

The Champion is the primary external contact and vision keeper.

### Responsibilities
- Primary point of contact for external inquiries
- Maintains relationships with the City of Mesa, landlord, and community partners
- Holds other Board members accountable to their commitments
- Facilitates HYH meetings (or delegates)
- Signs legal documents on behalf of the organization

### First 30 Days
- [ ] Get added to all official accounts and contacts
- [ ] Meet with outgoing Champion for knowledge transfer
- [ ] Review current lease, insurance, and key vendor relationships
- [ ] Introduce yourself to city/landlord contacts

---

## Treasurer

The Treasurer manages all financial operations.

### Responsibilities
- Manage banking (checking and savings accounts)
- Process membership dues and track payments
- Handle accounts payable (rent, utilities, insurance, accounting)
- File taxes and work with CPA
- Maintain budget and financial reports
- Manage building-related expenses

### Institutional Knowledge (as of 2023)
- **Accounting:** ~$300/month for external accounting service
- **Auto-pay bills:** Rent, utilities, insurance are on auto-pay
- **Manual bills:** Some vendor invoices arrive irregularly
- **Software:** QuickBooks for bookkeeping
- **Savings strategy:** CD ladder for interest optimization
- **Major expenses:** Rent (~$1/sqft/month), electricity is #2
- **Instructor payments:** Collected via PayPal, transferred by Treasurer, 1099s by accountant
- **Reimbursements:** Photos stored in Dropbox, tracked in QuickBooks

### First 30 Days
- [ ] Get added to bank accounts (signatory change at the bank)
- [ ] Get access to QuickBooks and PayPal
- [ ] Get access to Dropbox for financial records
- [ ] Review current budget and recurring expenses
- [ ] Confirm auto-pay bills are active and correct
- [ ] Quarterly audit: reconcile member payments with Square records

---

## Secretary

The Secretary manages communications and compliance.

### Responsibilities
- Send thank-you notes to donors and supporters
- Prepare presentations for events and meetings
- Take and publish meeting minutes
- Send reminders for upcoming events and deadlines
- Maintain compliance filings (state nonprofit annual report)
- Manage official communications

### First 30 Days
- [ ] Get access to official email and communication channels
- [ ] Review annual filing calendar (state report, IRS)
- [ ] Set up recurring reminders for compliance deadlines
- [ ] Review and update wiki documentation

---

## Operations

Operations manages the physical space and member experience.

### Responsibilities
- Inspire and coordinate volunteers (the "Welcoming Team")
- Manage membership onboarding and offboarding
- Oversee IT infrastructure (wifi, servers, access control)
- Marketing and social media
- Facility maintenance and safety
- Equipment maintenance coordination

### Key Principle
> Inspire volunteers, don't dictate. Mediate consensus, don't command.

### First 30 Days
- [ ] Get access to access control system and member database
- [ ] Tour the entire space with outgoing Operations lead
- [ ] Identify any immediate maintenance or safety issues
- [ ] Meet active volunteers and understand current projects
- [ ] Review and update the Walk Through Orientation

---

## Annual Calendar

| Month | Key Activities |
|-------|---------------|
| January | New year budget review |
| February | Prepare for annual meeting |
| March | Annual filing prep |
| **April** | **Annual Meeting & Board Elections** |
| May | New board transition |
| June-August | Summer planning |
| September | Fall events planning |
| October-November | End-of-year fundraising |
| December | Annual review, tax prep handoff to CPA |

---

*See also: [Bylaws](Bylaws.html) | [Procedures](Procedures.html) | [Board Members](Board_Members.html)*
""",
    },

    "Operational_Policies": {
        "changes": [
            "Expanded from 1.4KB to comprehensive operational policy document",
            "Added guest policy",
            "Added storage policy with timeline",
            "Added noise/hours guidelines",
            "Preserved existing policies (sleeping, tools, public space)",
        ],
        "rationale": (
            "The current Operational Policies page is extremely brief (1,426 bytes, 4 sections). "
            "Expanding it provides clear operational expectations without requiring members to "
            "hunt through multiple documents."
        ),
        "content": """\
# HeatSync Labs Operational Policies (Improved Draft)

## Public Space

- The lab is a shared space. Clean up after yourself when done working.
- Do not leave personal projects on shared work surfaces overnight.
- Large equipment must be stored in designated areas only.
- Food and drinks are allowed in the lounge area; keep them away from equipment.

## Tools and Equipment

- All dangerous tools require HeatSync Labs certification, regardless of outside experience.
- Return all tools to their designated storage locations after use.
- Report any equipment issues or damage immediately (see Rules for reporting procedure).
- Personal tools may be used but must be clearly labeled and stored separately.

## Guest Policy

- Members may bring guests at any time during staffed hours.
- Guests must be accompanied by their sponsoring member at all times.
- Guests must sign a liability waiver before using any equipment.
- Frequent guests should be encouraged to become members.

## Storage

- Members may store personal projects in designated member storage areas.
- All stored items must be labeled with the member's name and date.
- Items stored more than 90 days without activity may be moved or disposed of after notice.
- No hazardous materials may be stored without Board approval.

## Sleeping in the Lab

- Members may sleep in the lab a maximum of two (2) nights per week.
- Sleeping areas must be cleaned and cleared by 9:00 AM.
- This privilege may be revoked if it interferes with lab operations.

## Hours and Noise

- The lab is accessible to card-holding members 24/7.
- Staffed hours are posted on the website and Slack.
- Loud operations (grinding, hammering, etc.) should be limited to reasonable hours.
- Be considerate of neighbors and adjacent businesses.

## Card Access

- Card access voting and eligibility are governed by the [Bylaws](Bylaws.html).
- Lost or damaged cards should be reported immediately.
- Do not share your access card or let others use it to enter.
- Do not prop doors open or bypass security systems.

---

*See also: [Rules](Rules.html) | [Procedures](Procedures.html) | [Bylaws](Bylaws.html)*
""",
    },

    "Procedures": {
        "changes": [
            "Modernized payment processing section",
            "Added onboarding checklist format",
            "Integrated with current tools (Square, Slack, Dropbox)",
            "Updated 'Operations Team' -> 'Welcoming Team' throughout",
            "Added equipment certification tracking procedure",
        ],
        "rationale": (
            "The Procedures document is the practical companion to Rules and Policies. "
            "Formatting as checklists makes it actionable for volunteers handling these tasks."
        ),
        "content": """\
# HeatSync Labs Procedures (Improved Draft)

## New Member Onboarding

### When a new person wants to join:

- [ ] Welcome them and explain membership tiers (Associate $25, Basic $50, Plus $100)
- [ ] Process first payment via Square (record: name, email, amount, tier)
- [ ] Add them to Slack workspace
- [ ] Add them to Google Group (heatsynclabs@googlegroups.com)
- [ ] Give them a brief orientation (or schedule one)
- [ ] Explain the HYH meeting schedule and how proposals work
- [ ] If Basic/Plus: explain card access eligibility (after 2 months + nomination)

### Payment Processing

- All payments processed through Square
- Required fields: member name, email, item description, amount
- Recurring payments highly encouraged (reduces volunteer workload)
- Payment records reconciled quarterly by Treasurer

## Member Non-Payment / Cancellation

### Quarterly Audit (Treasurer responsibility):

1. Review all member payments for the quarter
2. Identify members more than 30 days past due
3. Send reminder notices to past-due members
4. For members 60+ days past due:
   - Suspend card access (update access control system)
   - Send formal written notice
5. For members 90+ days past due:
   - Terminate membership
   - Remove from access control system
   - Send final notice

### Voluntary Cancellation

1. Member notifies any Board member or posts to Slack
2. Welcoming Team updates records and cancels recurring payment
3. If card access holder: deactivate card in access control system
4. Send thank-you message and note they're welcome back anytime

## Equipment Certification

### Scheduling a Class

1. Certified member volunteers to teach (or Board recruits)
2. Post class to Slack and events calendar with date/time
3. After class: add attendee names to the equipment's certification list on the wiki

### Impromptu Training

1. Certified member may train individuals one-on-one
2. After training: add the person to the certification list
3. Both parties should sign/acknowledge the training was completed

## Sales and Donations

### Processing a Sale or Donation

1. Process payment through Square
2. Record: donor/buyer name, email, item/description, amount
3. For donations over $250: provide written acknowledgment (required by IRS)
4. Treasurer records in QuickBooks

## Purchase Requests

1. Post request to Slack (#general or #purchases) with item, estimated cost, and justification
2. For items under $100: any Board member may approve
3. For items $100-$500: requires two Board member approval
4. For items over $500: requires community proposal (see Bylaws, Proposal Process)
5. Save receipt photo to Dropbox and notify Treasurer for reimbursement

## Tool Acquisition

1. Donated tools: inspect for safety, add to inventory, update wiki
2. Purchased tools: follow Purchase Request procedure above
3. All new tools: determine if certification is required and schedule initial training

---

*See also: [Rules](Rules.html) | [Operational Policies](Operational_Policies.html) | [Bylaws](Bylaws.html)*
""",
    },

    "Proposals": {
        "changes": [
            "Updated to reference current Bylaws proposal process",
            "Added proposal template",
            "Preserved historical proposal links",
            "Added guidance on what requires a proposal vs. Board approval",
        ],
        "rationale": (
            "The current Proposals page is outdated (last updated 2020) and doesn't reference "
            "the detailed Proposal Process now in the Bylaws. This update bridges that gap and "
            "provides a practical template for members."
        ),
        "content": """\
# Proposals

## When is a Proposal Required?

Per the [Bylaws](Bylaws.html), formal proposals are required for:

- **Card access nominations** (new member card access)
- **Major equipment purchases** (over $500)
- **Permanent space modifications** (installations, layout changes)
- **Policy changes** (amendments to Rules, Policies, or Procedures)
- **Bylaw amendments** (follow the Amendments process in the Bylaws)

## Proposal Process

The full proposal process is defined in the Bylaws, Article VI. Summary:

1. **Days 1-2:** Submit proposal to Slack and/or Google Group
2. **Days 3-7:** Community discussion period
3. **Days 8-9:** Vote at HYH meeting (minimum 5 voting members)
4. **Result:** Majority vote to pass; failed proposals cannot be resubmitted for 6 months

## Proposal Template

```
PROPOSAL: [Title]
DATE: [Submission date]
PROPOSER: [Your name]
TYPE: [Equipment / Space Modification / Policy / Card Access / Other]

DESCRIPTION:
[What you're proposing, in detail]

COST: [If applicable]
FUNDING: [How it will be paid for]

BENEFIT:
[Why this benefits the community]

DISCUSSION PERIOD: [Date range]
VOTE DATE: [Planned HYH meeting date]
```

## Historic Proposals

- Ultimaker Complete Kit (2012)
- Ultimaker 2 (2015)
- Vinyl Cutter (2015)
- Laptop Purchases (2011-2015)

---

*See also: [Bylaws](Bylaws.html) | [How to Run HeatSync Labs](How_to_Run_HeatSync_Labs.html)*
""",
    },

    "Access_Card_Procedure": {
        "changes": [
            "Updated to reference Community Policies for card access process",
            "Preserved historical technical procedure as appendix",
            "Added modern access control workflow",
            "Noted transition from manual minicom/SSH to current system",
        ],
        "rationale": (
            "The current Access Card Procedure (2014) documents a legacy SSH/minicom "
            "process that may no longer be in use. The governance process for card access "
            "is now in the Community Policies; this document should focus on the technical execution."
        ),
    },

    "Community_Standards": {
        "changes": [
            "New document replacing the Code of Conduct previously embedded in Bylaws",
            "Structured around do-ocracy principles: handle it yourself, escalate when needed",
            "Comprehensive protected characteristics list",
            "Clear tiered consequences (A-D: warning through permanent ban)",
            "Grievance committee preserved from current bylaws (1 board + 3 random HYH members)",
            "Detailed reporting and investigation process with timelines",
            "Weapons policy retained from current Code of Conduct",
            "No waiting for multiple complaints language",
            "Confidentiality and documentation requirements",
        ],
        "rationale": (
            "The previous Code of Conduct was embedded in the Bylaws, making it difficult to amend "
            "without the formal bylaws amendment process. This standalone Community Standards document "
            "is more comprehensive, includes a clear do-ocracy response framework, preserves the "
            "grievance committee structure from the current bylaws, and can be amended by simple HYH "
            "majority vote per the policy hierarchy defined in the Bylaws."
        ),
    },

    "Community_Policies": {
        "changes": [
            "New document absorbing Card Access and Proposal Process from Bylaws",
            "Reformed card access: 1-month cooldown on failed nomination instead of 6-12 month lockout",
            "Reformed card access: nominator not locked out on failed nomination",
            "Reformed card access: removed 1 nomination per year per card member restriction",
            "Added clear guidance on what a no vote should be based on",
            "Added nominee feedback mechanism for failed nominations",
            "Reduced proposal resubmission lockout from 6 months to 3 months",
            "Amendable by simple HYH majority vote (no Board ratification required)",
        ],
        "rationale": (
            "The previous Bylaws embedded operational policies (card access, proposal process) directly, "
            "requiring the formal bylaws amendment process to change them. Moving these to a separate "
            "Community Policies document allows the community to iterate on these processes by simple "
            "HYH majority vote. The card access reforms address punitive nomination rules that locked "
            "both nominator and nominee for 6-12 months on a failed vote."
        ),
    },

    "Board_Members": {
        "changes": [
            "Added role descriptions for each position",
            "Improved historical record formatting",
            "Added notes on role evolution (obsolete positions)",
            "Cross-referenced with How to Run HeatSync Labs for role details",
        ],
        "rationale": (
            "The Board Members page serves as both current reference and historical record. "
            "Adding role descriptions and cross-references makes it more useful for members "
            "trying to understand the governance structure."
        ),
        "content": """\
# Board Members

## Current Board (2024-2025)

| Position | Member(s) | Since |
|----------|-----------|-------|
| Co-Champions | David Lang & Landon | 2024 |
| Secretary | Brett Neese | 2024 |
| Treasurer | Shaundra Newstead & David Flores | 2022 (Shaundra), 2024 (David) |
| Operations | *Open Position* | -- |

For detailed role descriptions, see [How to Run HeatSync Labs](How_to_Run_HeatSync_Labs.html).

## Board Elections

- Elections are held annually at the April HYH meeting
- Any member in good standing may run for any position
- Voting is by show of hands (or electronic if virtual)
- Terms are one year; no term limits
- Vacancies may be filled by Board appointment until the next election

## Past Board Members (2022-Present)

| Year | Champion(s) | Treasurer | Secretary | Operations |
|------|-------------|-----------|-----------|------------|
| 2024-25 | David Lang, Landon | Shaundra Newstead, David Flores | Brett Neese | Open |
| 2023-24 | Darrell Wertz, David Lang | Shaundra Newstead | Brett Neese | Jeff Sittler |
| 2022-23 | Darrell Wertz (interim) | Shaundra Newstead | -- | Jeff Sittler |

## Obsolete Positions

The following positions existed historically but have been consolidated:

- **PR/Marketing** → absorbed into Operations
- **Event Coordinator** → community-driven
- **Fundraising Coordinator** → shared Board responsibility
- **Editor** → community wiki contributions
- **Resource Manager** → absorbed into Operations

## External Services

- **Legal Counsel:** Retained (paid)
- **Accountant/CPA:** Retained (paid, ~$300/month)

---

*See also: [Bylaws](Bylaws.html) | [Board Elections](Board_Elections.html) | [How to Run HeatSync Labs](How_to_Run_HeatSync_Labs.html)*
""",
    },
}


def generate_improvements():
    """Generate improved versions of governance documents.

    If an improved markdown file already exists on disk, it is preserved as the
    authoritative source.  Only entries with a 'content' key whose file does not
    yet exist will be generated from the inline content in this script.
    """
    count = 0
    for slug, improvement in IMPROVEMENTS.items():
        out_path = IMPROVED_DIR / f"{slug}.md"

        # Preserve existing improved documents (they may have been edited)
        if out_path.exists() and out_path.stat().st_size > 0:
            count += 1
            continue

        # Only generate if the entry has inline content
        if "content" not in improvement:
            print(f"  WARNING: No content for {slug} and no existing file")
            continue

        # Build frontmatter
        frontmatter = [
            "---",
            f"title: {slug.replace('_', ' ')}",
            f"type: improved_draft",
            f"changes:",
        ]
        for change in improvement["changes"]:
            frontmatter.append(f"  - \"{change}\"")
        frontmatter.extend([
            f"rationale: >",
            f"  {improvement['rationale']}",
            "---",
            "",
        ])

        content = "\n".join(frontmatter) + improvement["content"]

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        count += 1

    return count


def main():
    start = time.time()
    print("Phase 4: Converting and improving governance pages...")

    os.makedirs(CONVERTED_DIR, exist_ok=True)
    os.makedirs(IMPROVED_DIR, exist_ok=True)

    print("  Converting governance pages to HTML...")
    converted = convert_governance_pages()
    print(f"  Converted {converted} pages")

    print("  Generating improved versions...")
    improved = generate_improvements()
    print(f"  Generated {improved} improved documents")

    elapsed = time.time() - start
    print(f"\nPhase 4 complete in {elapsed:.1f}s")

    with open(BASE_DIR / ".phase4_complete", "w") as f:
        f.write(f"Completed at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Converted: {converted}, Improved: {improved}\n")


if __name__ == "__main__":
    main()
