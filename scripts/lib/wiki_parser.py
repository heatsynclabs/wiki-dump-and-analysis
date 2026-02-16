"""Memory-efficient MediaWiki XML dump parser using iterparse."""

import xml.etree.ElementTree as ET
import re
from typing import Iterator


NS = "{http://www.mediawiki.org/xml/export-0.6/}"


def slugify(title: str) -> str:
    """Convert a page title to a filesystem-safe slug."""
    slug = title.replace(" ", "_").replace("/", "_-_")
    slug = re.sub(r'[<>:"|?*]', "_", slug)
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug[:200] if slug else "untitled"


def parse_pages(xml_path: str) -> Iterator[dict]:
    """Stream pages from a MediaWiki XML dump.

    Yields dicts with keys: title, ns, id, revisions (list of dicts).
    Each revision has: id, parent_id, timestamp, contributor, comment, text, bytes, sha1.
    Uses iterparse + elem.clear() for constant memory usage.
    """
    context = ET.iterparse(xml_path, events=("end",))
    page_data = None

    for event, elem in context:
        tag = elem.tag.replace(NS, "")

        if tag == "page":
            if page_data and page_data.get("revisions"):
                yield page_data
            page_data = None
            elem.clear()

        elif tag == "title" and elem.text is not None:
            # We're inside a <page>
            if page_data is None:
                page_data = {"revisions": []}
            page_data["title"] = elem.text

        elif tag == "ns" and elem.text is not None:
            if page_data is not None:
                page_data["ns"] = int(elem.text)

        elif tag == "id":
            parent = None
            # id can belong to page, revision, or contributor
            # We handle this by checking context
            if page_data is not None and "id" not in page_data:
                page_data["id"] = int(elem.text)

        elif tag == "revision":
            if page_data is not None:
                rev = {}
                for child in elem:
                    ctag = child.tag.replace(NS, "")
                    if ctag == "id":
                        rev["id"] = int(child.text) if child.text else 0
                    elif ctag == "parentid":
                        rev["parent_id"] = int(child.text) if child.text else None
                    elif ctag == "timestamp":
                        rev["timestamp"] = child.text or ""
                    elif ctag == "contributor":
                        username = child.find(f"{NS}username")
                        ip = child.find(f"{NS}ip")
                        uid = child.find(f"{NS}id")
                        rev["contributor"] = {
                            "username": username.text if username is not None else None,
                            "ip": ip.text if ip is not None else None,
                            "id": int(uid.text) if uid is not None and uid.text else None,
                        }
                    elif ctag == "comment":
                        rev["comment"] = child.text or ""
                    elif ctag == "text":
                        rev["text"] = child.text or ""
                        rev["bytes"] = int(child.get("bytes", 0))
                    elif ctag == "sha1":
                        rev["sha1"] = child.text or ""
                # Defaults
                rev.setdefault("parent_id", None)
                rev.setdefault("comment", "")
                rev.setdefault("contributor", {"username": None, "ip": None, "id": None})
                rev.setdefault("text", "")
                rev.setdefault("bytes", 0)
                rev.setdefault("sha1", "")
                page_data["revisions"].append(rev)
            elem.clear()

    # Don't forget the last page if the file doesn't end cleanly
    if page_data and page_data.get("revisions"):
        yield page_data
