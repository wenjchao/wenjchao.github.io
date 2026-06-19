#!/usr/bin/env python3
"""Convert canonical tables.json to a single HTML file with all tables.

Usage:
    python tables_to_html.py <tables.json> <output.html>
"""

import json
import sys
from pathlib import Path


def table_to_html(table: dict) -> str:
    sd = table["structured_data"]
    headers = sd["headers"]
    rows = sd["rows"]
    footnotes = sd.get("footnotes", [])

    parts = []
    parts.append(f'<div class="table-block" id="{table["table_id"]}">')

    caption = table.get("caption_text", "")
    if caption:
        parts.append(f"<p class=\"caption\">{esc(caption)}</p>")

    parts.append("<table>")

    if headers:
        parts.append("<thead>")
        for level in headers:
            parts.append("<tr>")
            for cell in level:
                parts.append(f"<th>{esc(cell)}</th>")
            parts.append("</tr>")
        parts.append("</thead>")

    parts.append("<tbody>")
    for row in rows:
        parts.append("<tr>")
        for cell in row:
            parts.append(f"<td>{esc(cell)}</td>")
        parts.append("</tr>")
    parts.append("</tbody>")

    parts.append("</table>")

    if footnotes:
        parts.append('<div class="footnotes">')
        for fn in footnotes:
            parts.append(f"<p>{esc(fn)}</p>")
        parts.append("</div>")

    parts.append("</div>")
    return "\n".join(parts)


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <tables.json> <output.html>")
        sys.exit(1)

    tables_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    with open(tables_path) as f:
        data = json.load(f)

    tables_html = []
    for t in data["tables"]:
        tables_html.append(table_to_html(t))

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Tables</title>
<style>
body {{
  font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 1rem;
  color: #1a1a1a;
  background: #fdfdfd;
}}
.table-block {{
  margin-bottom: 3rem;
}}
.caption {{
  font-weight: 600;
  margin-bottom: 0.5rem;
  line-height: 1.4;
}}
table {{
  border-collapse: collapse;
  width: 100%;
  font-size: 0.85rem;
  line-height: 1.3;
}}
thead th {{
  background: #f0f0f0;
  border-bottom: 2px solid #333;
  padding: 6px 8px;
  text-align: left;
  font-weight: 600;
}}
tbody td {{
  border-bottom: 1px solid #ddd;
  padding: 5px 8px;
  vertical-align: top;
}}
tbody tr:hover {{
  background: #f8f8f8;
}}
.footnotes {{
  margin-top: 0.4rem;
  font-size: 0.8rem;
  color: #555;
}}
.footnotes p {{
  margin: 0.15rem 0;
}}
</style>
</head>
<body>
<h1>Tables</h1>
{chr(10).join(tables_html)}
</body>
</html>"""

    output_path.write_text(html, encoding="utf-8")
    print(f"Written {len(data['tables'])} tables to {output_path}")


if __name__ == "__main__":
    main()
