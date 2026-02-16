---
title: Access Card Procedure
type: improved_draft
changes:
  - "Updated to reference current Bylaws card access process"
  - "Preserved historical technical procedure as appendix"
  - "Added modern access control workflow"
  - "Noted transition from manual minicom/SSH to current system"
rationale: >
  The current Access Card Procedure (2014) documents a legacy SSH/minicom process that may no longer be in use. The governance process for card access is now in the Bylaws; this document should focus on the technical execution.
---
# Access Card Procedure

## Governance Process

The eligibility and approval process for card access is defined in the [Community Policies](Community_Policies.html), Section 1: Card Access. In summary:

1. Member must have 2+ months of Basic ($50+) membership
2. Existing card member nominates the candidate
3. Public proposal submitted to community
4. Vote at HYH meeting (5+ card members present, majority)
5. Upon approval, Operations processes the card (see below)

## Card Issuance (Technical)

After a card access proposal is approved:

1. **Operations** or designated volunteer accesses the card management system
2. Assign a new user number to the member
3. Program the RFID card with the member's credentials
4. Set user mask to full access (1)
5. Test the card at all entry points
6. Update the member database with card number and activation date
7. Notify the member and their nominator

## Card Deactivation

When card access is revoked (non-payment, voluntary cancellation, or community vote):

1. Update user mask to no-access (255) in the access control system
2. Update the member database with deactivation date and reason
3. Notify the member of deactivation

## Appendix: Legacy Procedure (2014)

The original access control system used SSH to hsl-access server with minicom serial interface:
- Users 0-9: reserved for testing
- Real users: #10 onwards
- UserMask 1: full access
- UserMask 255: no access
- Card database maintained in Dropbox text file

---

*See also: [Community Policies](Community_Policies.html) | [Bylaws](Bylaws.html) | [Procedures](Procedures.html)*
