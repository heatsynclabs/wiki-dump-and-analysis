"""Convert MediaWiki wikitext to clean HTML.

Handles the subset of markup used in HeatSync Labs wiki:
- Headers (== to ======)
- Bold/italic (''' and '')
- Wiki links ([[target]] and [[target|label]])
- External links ([url label] and bare URLs)
- Bullet lists (* ** ***)
- Numbered lists (# ## ###)
- Tables ({| |+ |- | !! |})
- Inline HTML passthrough (ol, li, br, etc.)
- Horizontal rules (----)
"""

import re


def convert_wikitext(text: str, page_title: str = "") -> str:
    """Convert wikitext to HTML."""
    if not text:
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n")

    # Handle redirect
    if text.strip().upper().startswith("#REDIRECT"):
        match = re.match(r'#REDIRECT\s*\[\[(.+?)\]\]', text, re.IGNORECASE)
        if match:
            target = match.group(1)
            return f'<p class="redirect">Redirects to: <a href="{_page_link(target)}">{target}</a></p>'
        return '<p class="redirect">Redirect page</p>'

    lines = text.split("\n")
    html_parts = []
    i = 0
    in_list = []  # stack of list types ('ul' or 'ol')

    while i < len(lines):
        line = lines[i]

        # Blank line - close lists, add paragraph break
        if not line.strip():
            html_parts.extend(_close_lists(in_list))
            html_parts.append("")
            i += 1
            continue

        # Horizontal rule
        if line.strip().startswith("----"):
            html_parts.extend(_close_lists(in_list))
            html_parts.append("<hr>")
            i += 1
            continue

        # Wiki table
        if line.strip().startswith("{|"):
            html_parts.extend(_close_lists(in_list))
            table_lines = [line]
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("|}"):
                table_lines.append(lines[i])
                i += 1
            if i < len(lines):
                table_lines.append(lines[i])
                i += 1
            html_parts.append(_convert_table(table_lines))
            continue

        # Headers
        header_match = re.match(r'^(={2,6})\s*(.+?)\s*\1\s*$', line)
        if header_match:
            html_parts.extend(_close_lists(in_list))
            level = len(header_match.group(1))
            content = _inline_convert(header_match.group(2))
            anchor = re.sub(r'[^a-zA-Z0-9_-]', '_', header_match.group(2).strip())
            html_parts.append(f'<h{level} id="{anchor}">{content}</h{level}>')
            i += 1
            continue

        # Bullet lists
        if line.startswith("*") and not line.startswith("**") or line.startswith("*"):
            depth = 0
            while depth < len(line) and line[depth] == '*':
                depth += 1
            content = _inline_convert(line[depth:].strip())

            # Adjust list nesting
            while len(in_list) < depth:
                html_parts.append("<ul>")
                in_list.append("ul")
            while len(in_list) > depth:
                html_parts.append(f"</{in_list.pop()}>")

            html_parts.append(f"<li>{content}</li>")
            i += 1
            continue

        # Numbered lists (wiki syntax)
        if line.startswith("#") and not line.startswith("#REDIRECT"):
            depth = 0
            while depth < len(line) and line[depth] == '#':
                depth += 1
            content = _inline_convert(line[depth:].strip())

            while len(in_list) < depth:
                html_parts.append("<ol>")
                in_list.append("ol")
            while len(in_list) > depth:
                html_parts.append(f"</{in_list.pop()}>")

            html_parts.append(f"<li>{content}</li>")
            i += 1
            continue

        # Lines starting with HTML tags - pass through
        if re.match(r'^\s*<(ol|ul|li|div|blockquote|pre|table|tr|td|th|p|br|hr|h[1-6])', line, re.I):
            html_parts.extend(_close_lists(in_list))
            html_parts.append(_inline_convert(line))
            i += 1
            continue

        # Lines that are closing HTML tags
        if re.match(r'^\s*</(ol|ul|li|div|blockquote|pre|table|tr|td|th|p)', line, re.I):
            html_parts.append(line)
            i += 1
            continue

        # Definition lists (; term : definition)
        if line.startswith(";"):
            html_parts.extend(_close_lists(in_list))
            if ":" in line[1:]:
                term, defn = line[1:].split(":", 1)
                html_parts.append(f"<dl><dt>{_inline_convert(term.strip())}</dt>"
                                f"<dd>{_inline_convert(defn.strip())}</dd></dl>")
            else:
                html_parts.append(f"<p><strong>{_inline_convert(line[1:].strip())}</strong></p>")
            i += 1
            continue

        # Preformatted text (leading space)
        if line.startswith(" ") and not line.startswith("  ") and not re.match(r'^\s*<', line):
            html_parts.extend(_close_lists(in_list))
            pre_lines = []
            while i < len(lines) and lines[i].startswith(" ") and not re.match(r'^\s*<', lines[i]):
                pre_lines.append(lines[i][1:])
                i += 1
            html_parts.append(f"<pre>{chr(10).join(pre_lines)}</pre>")
            continue

        # Regular paragraph text
        html_parts.extend(_close_lists(in_list))
        para_lines = [line]
        i += 1
        while i < len(lines):
            next_line = lines[i]
            if (not next_line.strip() or
                next_line.startswith("=") or
                next_line.startswith("*") or
                next_line.startswith("#") or
                next_line.startswith("{|") or
                next_line.startswith("----") or
                next_line.startswith(";") or
                re.match(r'^\s*<(ol|ul|li|div|table|h[1-6]|br|hr)', next_line, re.I)):
                break
            para_lines.append(next_line)
            i += 1

        content = " ".join(_inline_convert(l) for l in para_lines)
        html_parts.append(f"<p>{content}</p>")

    # Close any remaining lists
    html_parts.extend(_close_lists(in_list))

    return "\n".join(html_parts)


def _close_lists(in_list: list) -> list:
    """Close all open list tags."""
    parts = []
    while in_list:
        parts.append(f"</{in_list.pop()}>")
    return parts


def _inline_convert(text: str) -> str:
    """Convert inline wikitext markup to HTML."""
    # Bold+italic (must come before bold and italic)
    text = re.sub(r"'''''(.+?)'''''", r"<strong><em>\1</em></strong>", text)

    # Bold
    text = re.sub(r"'''(.+?)'''", r"<strong>\1</strong>", text)

    # Italic
    text = re.sub(r"''(.+?)''", r"<em>\1</em>", text)

    # Wiki links [[target|label]] and [[target]]
    text = re.sub(r'\[\[([^|\]]+)\|([^\]]+)\]\]',
                  lambda m: f'<a href="{_page_link(m.group(1))}">{m.group(2)}</a>', text)
    text = re.sub(r'\[\[([^\]]+)\]\]',
                  lambda m: f'<a href="{_page_link(m.group(1))}">{m.group(1)}</a>', text)

    # External links [url label]
    text = re.sub(r'\[(\S+?)\s+(.+?)\]',
                  lambda m: f'<a href="{m.group(1)}" rel="nofollow">{m.group(2)}</a>', text)

    # Bare external links [url]
    text = re.sub(r'\[(https?://\S+?)\]',
                  lambda m: f'<a href="{m.group(1)}" rel="nofollow">{m.group(1)}</a>', text)

    return text


def _page_link(title: str) -> str:
    """Generate a link path for a wiki page title."""
    slug = title.replace(" ", "_").replace("/", "_-_")
    return f"{slug}.html"


def _convert_table(lines: list) -> str:
    """Convert wiki table markup to HTML table."""
    html = ['<table class="wiki-table">']
    in_row = False

    for line in lines:
        line = line.strip()

        if line.startswith("{|"):
            # Table start, might have class/style
            attrs = line[2:].strip()
            if attrs:
                html[0] = f'<table class="wiki-table" {attrs}>'
            continue

        if line.startswith("|}"):
            if in_row:
                html.append("</tr>")
            html.append("</table>")
            continue

        if line.startswith("|+"):
            # Caption
            html.append(f"<caption>{_inline_convert(line[2:].strip())}</caption>")
            continue

        if line.startswith("|-"):
            if in_row:
                html.append("</tr>")
            html.append("<tr>")
            in_row = True
            continue

        if line.startswith("!"):
            if not in_row:
                html.append("<tr>")
                in_row = True
            cells = re.split(r'\s*!!\s*', line[1:])
            for cell in cells:
                html.append(f"<th>{_inline_convert(cell.strip())}</th>")
            continue

        if line.startswith("|"):
            if not in_row:
                html.append("<tr>")
                in_row = True
            cells = re.split(r'\s*\|\|\s*', line[1:])
            for cell in cells:
                html.append(f"<td>{_inline_convert(cell.strip())}</td>")
            continue

    if in_row:
        html.append("</tr>")
    if not any("</table>" in h for h in html):
        html.append("</table>")

    return "\n".join(html)
