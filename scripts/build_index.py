#!/usr/bin/env python3
"""Update papers/index.html cards section from <folder>/<folder>_summary.md.

papers/index.html is hand-maintained (layout, CSS, header, etc. all yours).
This script only replaces content between the markers:

    <!-- BEGIN PAPERS -->
    ...cards generated from each paper folder's _summary.md...
    <!-- END PAPERS -->
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPERS_DIR = ROOT / "papers"
INDEX_HTML = PAPERS_DIR / "index.html"

BEGIN = "<!-- BEGIN PAPERS -->"
END = "<!-- END PAPERS -->"

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
TITLE_RE = re.compile(r"^title\s*:\s*(.+?)\s*$", re.MULTILINE)


def parse_summary(md_path: Path):
    text = md_path.read_text(encoding="utf-8")
    title = None
    body = text
    fm = FRONTMATTER_RE.match(text)
    if fm:
        body = text[fm.end():]
        tm = TITLE_RE.search(fm.group(1))
        if tm:
            title = tm.group(1).strip().strip('"').strip("'")
    return title, extract_section(body, "主線")


def extract_section(md: str, heading: str) -> str:
    pattern = re.compile(
        r"^#\s+" + re.escape(heading) + r"\s*$(.*?)(?=^#\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(md)
    if not m:
        return ""
    text = m.group(1).strip()
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", text)
    text = re.sub(r"\[(.+?)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def find_papers():
    items = []
    if not PAPERS_DIR.is_dir():
        return items
    for sub in sorted(PAPERS_DIR.iterdir()):
        if not sub.is_dir():
            continue
        summary_path = sub / f"{sub.name}_summary.md"
        html_path = sub / f"{sub.name}.html"
        if not html_path.exists():
            print(f"skip {sub.name}: missing {html_path.name}", file=sys.stderr)
            continue
        if not summary_path.exists():
            print(f"skip {sub.name}: missing {summary_path.name}", file=sys.stderr)
            continue
        title, main_line = parse_summary(summary_path)
        items.append({
            "href": html_path.relative_to(PAPERS_DIR).as_posix(),
            "title": title or sub.name,
            "summary": main_line,
        })
    return items


def render_cards(items, indent="      "):
    if not items:
        return f'{indent}<li class="empty">尚未有 paper。</li>'
    cards = []
    for it in items:
        title_h = html.escape(it["title"])
        href_h = html.escape(it["href"])
        summary_block = ""
        if it["summary"]:
            summary_block = (
                f'{indent}    <p class="summary">'
                f'{html.escape(it["summary"])}</p>\n'
            )
        cards.append(
            f'{indent}<li class="paper">\n'
            f'{indent}  <a href="{href_h}">\n'
            f'{indent}    <h2>{title_h}</h2>\n'
            f'{summary_block}'
            f'{indent}  </a>\n'
            f'{indent}</li>'
        )
    return "\n".join(cards)


def main():
    items = find_papers()

    if not INDEX_HTML.exists():
        sys.exit(
            f"error: {INDEX_HTML.relative_to(ROOT)} does not exist.\n"
            f"Create it with {BEGIN} and {END} markers where the paper list should go."
        )

    text = INDEX_HTML.read_text(encoding="utf-8")
    if BEGIN not in text or END not in text:
        sys.exit(
            f"error: {INDEX_HTML.relative_to(ROOT)} is missing the {BEGIN} or {END} marker."
        )

    cards = render_cards(items)
    pattern = re.compile(
        re.escape(BEGIN) + r".*?" + re.escape(END),
        re.DOTALL,
    )
    # Match the indent that precedes the END marker so it stays aligned.
    m = re.search(r"([ \t]*)" + re.escape(END), text)
    end_indent = m.group(1) if m else "    "
    replacement = f"{BEGIN}\n{cards}\n{end_indent}{END}"
    new_text = pattern.sub(replacement, text, count=1)

    if new_text == text:
        print(f"no change ({len(items)} paper(s))")
        return

    INDEX_HTML.write_text(new_text, encoding="utf-8")
    print(f"updated {INDEX_HTML.relative_to(ROOT)} ({len(items)} paper(s))")


if __name__ == "__main__":
    main()
