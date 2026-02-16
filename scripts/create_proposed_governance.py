#!/usr/bin/env python3
"""Transform data/improved/*.md files into proposed-governance/ for GitHub browsing.

Transformations:
1. Convert YAML frontmatter to visible blockquote callout
2. Fix cross-references: .html -> .md (for files in this folder)
3. Remove "(Improved Draft)" from titles
4. Keep all content intact
"""

import os
import re
import yaml

IMPROVED_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'improved')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'proposed-governance')

# Files that exist in proposed-governance/ (for link rewriting)
KNOWN_FILES = {
    'Bylaws', 'Community_Standards', 'Community_Policies', 'Rules',
    'Operational_Policies', 'Procedures', 'Board_Members',
    'How_to_Run_HeatSync_Labs', 'Access_Card_Procedure', 'Proposals'
}


def parse_frontmatter(text):
    """Parse YAML frontmatter from markdown text. Returns (metadata_dict, body)."""
    if not text.startswith('---'):
        return {}, text

    # Find the closing ---
    end = text.find('\n---', 3)
    if end == -1:
        return {}, text

    yaml_str = text[4:end]  # skip opening ---\n
    body = text[end + 4:]   # skip closing ---\n

    try:
        metadata = yaml.safe_load(yaml_str)
    except yaml.YAMLError:
        return {}, text

    return metadata or {}, body


def frontmatter_to_callout(metadata):
    """Convert frontmatter metadata to a GitHub-flavored blockquote callout."""
    lines = []
    lines.append('> [!NOTE]')
    lines.append('> **Proposed Changes**')
    lines.append('>')

    changes = metadata.get('changes', [])
    for change in changes:
        lines.append(f'> - {change}')

    rationale = metadata.get('rationale', '').strip()
    if rationale:
        lines.append('>')
        lines.append(f'> **Rationale:** {rationale}')

    return '\n'.join(lines)


def fix_cross_references(text):
    """Replace .html links with .md for known files in this folder."""
    def replace_link(match):
        name = match.group(1)
        if name in KNOWN_FILES:
            return f'{name}.md)'
        # Not a file we have -- leave the .html link as-is
        return match.group(0)

    # Match patterns like Something.html) in markdown links
    text = re.sub(r'(\w+)\.html\)', replace_link, text)
    return text


def remove_improved_draft(text):
    """Remove '(Improved Draft)' from headings."""
    text = re.sub(r'\s*\(Improved Draft\)', '', text)
    return text


def transform_file(input_path, output_path):
    """Transform a single improved markdown file."""
    with open(input_path, 'r') as f:
        content = f.read()

    metadata, body = parse_frontmatter(content)

    # Build callout from frontmatter
    callout = frontmatter_to_callout(metadata)

    # Clean up body
    body = body.lstrip('\n')
    body = remove_improved_draft(body)
    body = fix_cross_references(body)

    # Assemble output
    output = callout + '\n\n' + body

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(output)

    print(f"  {os.path.basename(output_path)}")


def main():
    print("Creating proposed-governance/ files...")
    print()

    for filename in sorted(os.listdir(IMPROVED_DIR)):
        if not filename.endswith('.md'):
            continue
        input_path = os.path.join(IMPROVED_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)
        transform_file(input_path, output_path)

    print()
    print(f"Done. {len(os.listdir(OUTPUT_DIR))} files in proposed-governance/")


if __name__ == '__main__':
    main()
