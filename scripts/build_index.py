#!/usr/bin/env python3
"""Build index.html from papers/<folder>/<folder>_summary.md files.

Each paper folder must contain:
  - <folder>.html          the paper HTML (link target)
  - <folder>_summary.md    YAML frontmatter with `title:` + a `# 主線` section
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPERS_DIR = ROOT / "papers"

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


def render(items):
    if items:
        cards = []
        for it in items:
            title_h = html.escape(it["title"])
            href_h = html.escape(it["href"])
            summary_block = ""
            if it["summary"]:
                summary_block = f'        <p class="summary">{html.escape(it["summary"])}</p>\n'
            cards.append(
                f'    <li class="paper">\n'
                f'      <a href="{href_h}">\n'
                f'        <h2>{title_h}</h2>\n'
                f'{summary_block}'
                f'      </a>\n'
                f'    </li>'
            )
        body = "\n".join(cards)
    else:
        body = '    <li class="empty">尚未有 paper。</li>'

    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Papers — wenjchao</title>
  <style>
    :root {{ --ink:#1f252b; --muted:#5c6670; --rule:#d8dde3; }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", Arial, sans-serif;
      color: var(--ink);
      background: #fff;
      line-height: 1.55;
    }}
    main {{ max-width: 760px; margin: 0 auto; padding: 64px 24px 96px; }}
    header h1 {{ font-size: 28px; margin: 0 0 8px; letter-spacing: -0.01em; }}
    header p {{ color: var(--muted); margin: 0 0 40px; font-size: 14px; }}
    ul.papers {{ list-style: none; padding: 0; margin: 0; }}
    li.paper {{ border-top: 1px solid var(--rule); }}
    li.paper:last-child {{ border-bottom: 1px solid var(--rule); }}
    li.paper a {{ display: block; padding: 22px 4px; color: inherit; text-decoration: none; }}
    li.paper a:hover {{ background: #f6f8fa; }}
    li.paper h2 {{ font-size: 17px; font-weight: 600; margin: 0 0 6px; line-height: 1.35; }}
    li.paper .summary {{ margin: 0; color: var(--muted); font-size: 14px; }}
    li.empty {{ color: var(--muted); padding: 22px 4px; }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Papers</h1>
      <p>Reading notes by wenjchao.</p>
    </header>
    <ul class="papers">
{body}
    </ul>
  </main>
</body>
</html>
"""


def main():
    items = find_papers()
    out = PAPERS_DIR / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(items), encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)} ({len(items)} paper(s))")


if __name__ == "__main__":
    main()
