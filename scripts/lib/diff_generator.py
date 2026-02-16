"""Generate side-by-side diff HTML for governance page comparisons."""

import difflib
import re


def generate_diff_html(original_text: str, improved_text: str,
                       original_title: str = "Current",
                       improved_title: str = "Improved") -> str:
    """Generate a side-by-side diff view as HTML.

    Uses difflib to compare the texts and generates styled HTML
    with additions (green), deletions (red), and context lines.
    """
    # Split into lines for diffing
    orig_lines = original_text.splitlines()
    improved_lines = improved_text.splitlines()

    differ = difflib.HtmlDiff(wrapcolumn=80)
    diff_table = differ.make_table(
        orig_lines, improved_lines,
        fromdesc=original_title, todesc=improved_title,
        context=True, numlines=3,
    )

    return diff_table


def generate_inline_diff(original_text: str, improved_text: str) -> str:
    """Generate an inline unified diff as styled HTML."""
    orig_lines = original_text.splitlines(keepends=True)
    improved_lines = improved_text.splitlines(keepends=True)

    diff = difflib.unified_diff(
        orig_lines, improved_lines,
        fromfile="Current", tofile="Improved",
        lineterm="",
    )

    html_parts = ['<div class="diff-view">']
    for line in diff:
        line = line.rstrip("\n")
        escaped = _escape_html(line)
        if line.startswith("+++") or line.startswith("---"):
            html_parts.append(f'<div class="diff-header">{escaped}</div>')
        elif line.startswith("@@"):
            html_parts.append(f'<div class="diff-hunk">{escaped}</div>')
        elif line.startswith("+"):
            html_parts.append(f'<div class="diff-add">{escaped}</div>')
        elif line.startswith("-"):
            html_parts.append(f'<div class="diff-del">{escaped}</div>')
        else:
            html_parts.append(f'<div class="diff-ctx">{escaped}</div>')

    html_parts.append('</div>')
    return "\n".join(html_parts)


def generate_change_summary(changes: list, rationale: str) -> str:
    """Generate a human-readable change summary HTML block."""
    html = ['<div class="change-summary">']
    html.append('<h3>Changes in This Version</h3>')
    html.append('<ul>')
    for change in changes:
        html.append(f'<li>{_escape_html(change)}</li>')
    html.append('</ul>')
    if rationale:
        html.append('<h3>Rationale</h3>')
        html.append(f'<p>{_escape_html(rationale)}</p>')
    html.append('</div>')
    return "\n".join(html)


def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))
