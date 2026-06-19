#!/usr/bin/env python3
"""Deterministic mapping_merger — implements Step 1-9 of subagent_prompts/mapping_merger.md.

Usage:
    python3 agents/scripts/mapping_merger_script.py <paper_dir> [--out <output_html_path>]

If --out is omitted, writes to <paper_dir>/mapping/canonical/paper.html
(the original mapping_merger behavior).
"""

import argparse
import glob
import html
import json
import os
import re
import sys
from collections import defaultdict, OrderedDict

# Path constants — populated in main() based on CLI args.
PAPER_DIR = None
SRC_HTML = None
OUT_HTML = None
MAPPING_DIR = None
METHOD_JSON = None
SUMMARY_JSON = None
METHOD_MD = None

# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------
COLORS = OrderedDict([
    ("summary", {"fill": "#FFF3B0", "ink": "#7a5a00", "ring": "#E8C75A"}),
    ("m1",  {"fill": "#FFB3BA", "ink": "#8a2330", "ring": "#E08594"}),
    ("m2",  {"fill": "#C8E6C9", "ink": "#1f5c2e", "ring": "#88BF8B"}),
    ("m3",  {"fill": "#B3D9FF", "ink": "#1b4d80", "ring": "#7AB2E0"}),
    ("m4",  {"fill": "#FFD9B3", "ink": "#7a3d00", "ring": "#E0A66E"}),
    ("m5",  {"fill": "#E1BEE7", "ink": "#5a2a6e", "ring": "#B287B9"}),
    ("m6",  {"fill": "#B2EBF2", "ink": "#1d5d68", "ring": "#7DC6CF"}),
    ("m7",  {"fill": "#EFC1CD", "ink": "#6C1329", "ring": "#D2798F"}),
    ("m8",  {"fill": "#EFDCC1", "ink": "#6C4613", "ring": "#D2AC79"}),
    ("m9",  {"fill": "#DDEFC1", "ink": "#486C13", "ring": "#AED279"}),
    ("m10", {"fill": "#C1EFCB", "ink": "#136C26", "ring": "#79D28C"}),
    ("m11", {"fill": "#C1EDEF", "ink": "#13686C", "ring": "#79CED2"}),
    ("m12", {"fill": "#C1C8EF", "ink": "#131F6C", "ring": "#7985D2"}),
    ("m13", {"fill": "#E1C1EF", "ink": "#50136C", "ring": "#B679D2"}),
    ("m14", {"fill": "#EFC1D8", "ink": "#6C133F", "ring": "#D279A5"}),
    ("m15", {"fill": "#EFD0C1", "ink": "#6C3013", "ring": "#D29679"}),
    ("m16", {"fill": "#E8EFC1", "ink": "#5E6C13", "ring": "#C4D279"}),
    ("m17", {"fill": "#C2EFC1", "ink": "#156C13", "ring": "#7BD279"}),
    ("m18", {"fill": "#C1EFE6", "ink": "#136C5A", "ring": "#79D2C0"}),
    ("m19", {"fill": "#C1D3EF", "ink": "#13356C", "ring": "#799BD2"}),
    ("m20", {"fill": "#D5C1EF", "ink": "#3A136C", "ring": "#A079D2"}),
    ("m21", {"fill": "#EFC1E3", "ink": "#6C1354", "ring": "#D279BA"}),
    ("m22", {"fill": "#EFC5C1", "ink": "#6C1A13", "ring": "#D28079"}),
    ("m23", {"fill": "#EFEBC1", "ink": "#6C6313", "ring": "#D2C979"}),
    ("m24", {"fill": "#CEEFC1", "ink": "#2B6C13", "ring": "#91D279"}),
    ("m25", {"fill": "#C1EFDB", "ink": "#136C44", "ring": "#79D2AA"}),
    ("m26", {"fill": "#C1DEEF", "ink": "#134B6C", "ring": "#79B1D2"}),
    ("m27", {"fill": "#CAC1EF", "ink": "#24136C", "ring": "#8A79D2"}),
    ("m28", {"fill": "#EFC1EE", "ink": "#6C136A", "ring": "#D279D0"}),
    ("m29", {"fill": "#EFC1C9", "ink": "#6C1321", "ring": "#D27987"}),
    ("m30", {"fill": "#EFE0C1", "ink": "#6C4E13", "ring": "#D2B479"}),
])

COLOR_KEYS = list(COLORS.keys())


# ---------------------------------------------------------------------------
# Math wrappers (Step 6)
# ---------------------------------------------------------------------------

UNICODE_MAP = {
    "−": "-", "×": "\\times", "·": "\\cdot",
    "≤": "\\le", "≥": "\\ge", "≠": "\\neq", "∈": "\\in", "∉": "\\notin",
    "α": "\\alpha", "β": "\\beta", "γ": "\\gamma", "δ": "\\delta",
    "λ": "\\lambda", "μ": "\\mu", "σ": "\\sigma", "Π": "\\Pi", "Σ": "\\Sigma",
}
GREEK_RE = re.compile(r"[αβγδλμσΠΣ]")
DEFINITE_RE = re.compile(r"[_^]|\\[a-zA-Z]+|[αβγδλμσΠΣ]")
MATH_RUN_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 \t+-−*·/=<>≤≥≠^_(){}[],.\\αβγδλμσΠΣ∈∉")


def _unicode_to_latex(s):
    out = []
    for i, ch in enumerate(s):
        mapped = UNICODE_MAP.get(ch, ch)
        out.append(mapped)
        # TeX commands like \beta consume following letters; if we just inserted
        # \something and the next source char is an ASCII letter, append a space
        # so MathJax sees `\beta R2` not `\betaR2` (undefined command).
        if mapped.startswith("\\") and len(mapped) > 1 and mapped[1:].isalpha():
            nxt = s[i + 1] if i + 1 < len(s) else ""
            if nxt and nxt.isascii() and nxt.isalpha():
                out.append(" ")
    return "".join(out)


def _find_math_runs(text):
    """Return list of (start, end) ranges to wrap, after trimming, prefix/suffix
    word stripping, and paren balancing. End exclusive."""
    runs = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] in MATH_RUN_CHARS:
            j = i
            while j < n and text[j] in MATH_RUN_CHARS:
                j += 1
            # check definite
            seg = text[i:j]
            if DEFINITE_RE.search(seg):
                runs.append((i, j))
            i = j
        else:
            i += 1
    # post-process: trim whitespace/punctuation, strip word prefix/suffix, balance parens
    fixed = []
    for s, e in runs:
        # Trim leading/trailing whitespace, comma, period
        while s < e and text[s] in " \t,.":
            s += 1
        while e > s and text[e - 1] in " \t,.":
            e -= 1
        if s >= e:
            continue
        # Re-check definite after trim
        if not DEFINITE_RE.search(text[s:e]):
            continue
        # Strip word prefix: ([a-zA-Z]{2,}\s+)+ with no _^0-9
        seg = text[s:e]
        m = re.match(r"((?:[a-zA-Z]{2,}\s+)+)", seg)
        if m:
            prefix = m.group(1)
            if not re.search(r"[_^0-9]", prefix):
                s += len(prefix)
                seg = text[s:e]
        # Strip word suffix
        m = re.search(r"(\s+[a-zA-Z]{2,})+$", seg)
        if m:
            suffix = m.group(0)
            if not re.search(r"[_^0-9]", suffix):
                e -= len(suffix)
                seg = text[s:e]
        if s >= e:
            continue
        if not DEFINITE_RE.search(text[s:e]):
            continue
        # Balance parens
        seg = text[s:e]
        op = seg.count("(")
        cp = seg.count(")")
        if op > cp:
            # cut unmatched ( from right - drop from end while ( count > ) count
            new_seg = seg
            while new_seg.count("(") > new_seg.count(")") and new_seg:
                # find last "(" and trim from there onwards
                idx = new_seg.rfind("(")
                if idx < 0:
                    break
                new_seg = new_seg[:idx].rstrip()
            if new_seg and DEFINITE_RE.search(new_seg):
                e = s + len(new_seg)
            else:
                continue
        elif cp > op:
            new_seg = seg
            while new_seg.count(")") > new_seg.count("(") and new_seg:
                idx = new_seg.find(")")
                if idx < 0:
                    break
                new_seg = new_seg[idx + 1:].lstrip()
                s_offset = e - s - len(new_seg)
                s = s + s_offset
            if new_seg and DEFINITE_RE.search(new_seg):
                pass
            else:
                continue
        # Final trim
        while s < e and text[s] in " \t,.":
            s += 1
        while e > s and text[e - 1] in " \t,.":
            e -= 1
        if s < e and DEFINITE_RE.search(text[s:e]):
            fixed.append((s, e))
    return fixed


def _mask_math_regions(text, placeholders):
    """Mask $$...$$, $...$, \\(...\\) regions in text. Returns masked text."""
    out_parts = []
    i = 0
    n = len(text)
    while i < n:
        # $$...$$
        if text[i:i + 2] == "$$":
            end = text.find("$$", i + 2)
            if end < 0:
                out_parts.append(text[i:])
                break
            content = text[i:end + 2]
            ph = f"\x05M{len(placeholders)}\x05"
            placeholders.append(content)
            out_parts.append(ph)
            i = end + 2
            continue
        # \(...\)
        if text[i:i + 2] == "\\(":
            end = text.find("\\)", i + 2)
            if end < 0:
                out_parts.append(text[i:])
                break
            content = text[i:end + 2]
            ph = f"\x05M{len(placeholders)}\x05"
            placeholders.append(content)
            out_parts.append(ph)
            i = end + 2
            continue
        # $...$ (not $$)
        if text[i] == "$" and (i == 0 or text[i - 1] != "\\"):
            end = -1
            j = i + 1
            while j < n:
                if text[j] == "$" and text[j - 1] != "\\" and (j + 1 >= n or text[j + 1] != "$"):
                    end = j
                    break
                j += 1
            if end > 0:
                content = text[i:end + 1]
                if "\n" not in content:
                    ph = f"\x05M{len(placeholders)}\x05"
                    placeholders.append(content)
                    out_parts.append(ph)
                    i = end + 1
                    continue
        out_parts.append(text[i])
        i += 1
    return "".join(out_parts)


def _unmask(text, placeholders):
    for idx, content in enumerate(placeholders):
        text = text.replace(f"\x05M{idx}\x05", content)
    return text


def greedy_wrap_math(text, delim="paren"):
    """Greedy wrap math runs in text. delim='paren' uses \\(...\\), delim='dollar' uses $...$.

    1) Unwrap existing \\(...\\) and $...$ first.
    2) Find runs, wrap with selected delim.
    3) Inside wrapped runs, replace unicode->latex.
    """
    if not text:
        return text
    # Unwrap existing
    text = re.sub(r"\\\((.+?)\\\)", r"\1", text)
    text = re.sub(r"(?<!\$)\$([^$\n]+?)\$(?!\$)", r"\1", text)

    runs = _find_math_runs(text)
    if not runs:
        return text
    # Build output
    out = []
    last = 0
    for s, e in runs:
        out.append(text[last:s])
        inner = _unicode_to_latex(text[s:e])
        if delim == "paren":
            out.append("\\(" + inner + "\\)")
        else:
            out.append("$" + inner + "$")
        last = e
    out.append(text[last:])
    return "".join(out)


# Conservative per-token wrapper for body text nodes
ATOM_RE = re.compile(
    r"(?<![A-Za-z\\])"
    r"(?:\\(?:alpha|beta|gamma|delta|lambda|mu|sigma|Pi|Sigma|times|cdot|le|ge|neq|in|notin)"
    r"(?:_[A-Za-z0-9]+|\^[A-Za-z0-9]+|\^\{[^}]+\}|_\{[^}]+\})*"
    r"|[A-Za-z](?:_[A-Za-z0-9]+|\^[A-Za-z0-9]+|\^\{[^}]+\}|_\{[^}]+\})+)"
)


def conservative_wrap_math(text):
    """Per-token wrap; do NOT unwrap existing \\(...\\) / $...$ / $$...$$.
    Caller is responsible for masking those regions before calling.
    """
    if not text:
        return text

    def repl(m):
        token = m.group(0)
        # Skip if obvious non-math identifier
        return "\\(" + token + "\\)"

    return ATOM_RE.sub(repl, text)


# ---------------------------------------------------------------------------
# Step 1: discover maps
# ---------------------------------------------------------------------------

def discover_maps():
    maps = []
    for f in sorted(glob.glob(os.path.join(MAPPING_DIR, "mapping.*.json"))):
        base = os.path.basename(f)
        m = re.match(r"mapping\.([a-z0-9_]+)\.json$", base)
        if not m:
            continue
        key = m.group(1)
        if key == "l1":
            color_key = "summary"
            kind = "l1"
            lane = "l1"
        elif key.startswith("l2_m"):
            color_key = key[3:]  # mN
            kind = key
            lane = "detail"
        elif key.startswith("method_m"):
            color_key = key[7:]  # mN
            kind = key
            lane = "method"
        else:
            continue
        with open(f) as fh:
            data = json.load(fh)
        maps.append({
            "path": f,
            "key": key,
            "kind": kind,
            "color_key": color_key,
            "lane": lane,
            "data": data,
        })
    return maps


# ---------------------------------------------------------------------------
# Step 2: collect snippets, dedup
# ---------------------------------------------------------------------------

def build_snippet_index(maps):
    # All snippets: snippet_id -> {text, phrase_id, color_key, kind}
    raw_snippets = OrderedDict()
    phrase_text = {}  # phrase_id -> summary_text
    phrase_color = {}  # phrase_id -> color_key
    phrase_kind = {}  # phrase_id -> kind
    phrase_loc = {}

    for mp in maps:
        ck = mp["color_key"]
        kd = mp["kind"]
        for ph in mp["data"].get("phrases", []):
            pid = ph["id"]
            phrase_text[pid] = ph.get("summary_text", "")
            phrase_color[pid] = ck
            phrase_kind[pid] = kd
            phrase_loc[pid] = ph.get("summary_location", "")
            for s in ph.get("paper_snippets", []) or []:
                sid = s.get("snippet_id")
                txt = s.get("text", "")
                if not sid or not txt:
                    continue
                raw_snippets[sid] = {
                    "text": txt,
                    "phrase_id": pid,
                    "color_key": ck,
                    "kind": kd,
                }

    # (2a) text-equality dedup
    text_to_canon = {}  # text -> canonical snippet_id (first seen)
    canonical_id_of = {}  # snippet_id -> canonical_id
    for sid, info in raw_snippets.items():
        t = info["text"]
        if t in text_to_canon:
            canonical_id_of[sid] = text_to_canon[t]
        else:
            text_to_canon[t] = sid
            canonical_id_of[sid] = sid

    # unique texts: canonical_id -> text
    unique_texts = OrderedDict()
    for t, sid in text_to_canon.items():
        unique_texts[sid] = t

    # (2b) containment alias: sort by length descending, check substring
    sorted_canons = sorted(unique_texts.keys(), key=lambda s: -len(unique_texts[s]))
    # For each shorter canon, see if its text is a substring of any longer canon
    alias_map = {}  # canon -> longer canon
    for i, c_short in enumerate(sorted_canons):
        t_short = unique_texts[c_short]
        for j in range(i):
            c_long = sorted_canons[j]
            if c_long in alias_map:
                continue
            t_long = unique_texts[c_long]
            if len(t_long) > len(t_short) and t_short in t_long:
                alias_map[c_short] = c_long
                break

    # Resolve alias chains (in case)
    def resolve_alias(c):
        seen = set()
        while c in alias_map and c not in seen:
            seen.add(c)
            c = alias_map[c]
        return c

    # Translate canonical_id_of through alias
    for sid in list(canonical_id_of.keys()):
        canonical_id_of[sid] = resolve_alias(canonical_id_of[sid])

    # Remove aliased shorts from unique_texts
    final_texts = OrderedDict()
    for c, t in unique_texts.items():
        if c in alias_map:
            continue
        final_texts[c] = t

    # Build phrases_at and phrases_at_by_color
    phrases_at = defaultdict(list)  # canon -> [phrase_id list, preserving insertion order, deduped]
    phrases_at_by_color = defaultdict(lambda: defaultdict(list))  # canon -> color -> [phrase_id list]
    seen_pair = set()
    seen_color_pair = set()
    for sid, info in raw_snippets.items():
        canon = canonical_id_of[sid]
        pid = info["phrase_id"]
        ck = info["color_key"]
        if (canon, pid) not in seen_pair:
            phrases_at[canon].append(pid)
            seen_pair.add((canon, pid))
        if (canon, ck, pid) not in seen_color_pair:
            phrases_at_by_color[canon][ck].append(pid)
            seen_color_pair.add((canon, ck, pid))

    return {
        "unique_texts": final_texts,  # canon -> text
        "canonical_id_of": canonical_id_of,
        "phrases_at": phrases_at,
        "phrases_at_by_color": phrases_at_by_color,
        "phrase_text": phrase_text,
        "phrase_color": phrase_color,
        "phrase_kind": phrase_kind,
        "phrase_loc": phrase_loc,
    }


# ---------------------------------------------------------------------------
# Step 3: strip prior injections
# ---------------------------------------------------------------------------

def strip_prior(html_text):
    # Style block + adjacent panel
    html_text = re.sub(
        r'<style id="reader-panel-style">.*?</style>\s*<aside class="reader-panel">.*?</aside>',
        "",
        html_text,
        flags=re.DOTALL,
    )
    # Style block alone
    html_text = re.sub(
        r'<style id="reader-panel-style">.*?</style>',
        "",
        html_text,
        flags=re.DOTALL,
    )
    # Panel alone
    html_text = re.sub(
        r'<aside class="reader-panel">.*?</aside>',
        "",
        html_text,
        flags=re.DOTALL,
    )
    # JS block
    html_text = re.sub(
        r'<script id="reader-panel-js">.*?</script>',
        "",
        html_text,
        flags=re.DOTALL,
    )
    # Margin rail
    html_text = re.sub(
        r'<div class="margin-rail">.*?</div>',
        "",
        html_text,
        flags=re.DOTALL,
    )
    # Strip existing marks (idempotent). Use generic pattern that tolerates extra attrs.
    mark_re = re.compile(
        r'<mark class="hl hl-[^"]+" id="[^"]+" data-back="[^"]+"[^>]*>(.*?)</mark>',
        flags=re.DOTALL,
    )
    while True:
        new = mark_re.sub(r"\1", html_text)
        if new == html_text:
            break
        html_text = new
    # Drop any stragglers
    html_text = re.sub(r'<mark class="hl[^"]*"[^>]*>', "", html_text)
    html_text = re.sub(r'</mark>', "", html_text)
    return html_text


# ---------------------------------------------------------------------------
# Step 3.5: patch MathJax config (no-op if already correct)
# ---------------------------------------------------------------------------

def patch_mathjax_config(html_text):
    # Source HTML often writes `inlineMath: [['\(', '\)']]` — single-backslash
    # form. JS strings collapse the unknown `\(` escape to just `(`, so MathJax
    # ends up treating any `(...)` as inline math (garbling all parenthetical
    # text). Rewrite to double-backslash so JS evaluates to `\(`.
    # NOTE: regex `\\\(` in raw string = literal `\(` (backslash + paren).
    return re.sub(
        r"inlineMath\s*:\s*\[\s*\['\\\(',\s*'\\\)'\]\s*\]",
        "inlineMath: [['\\\\\\\\(', '\\\\\\\\)']]",
        html_text,
    )


# ---------------------------------------------------------------------------
# Step 4: wrap snippets
# ---------------------------------------------------------------------------

# We need to:
#  - mask <script>, <style>, attribute values, $$...$$ and \(...\) regions
#  - for each unique text (longest first), find token-safe occurrence, replace with placeholder
#  - if no clean spot, detect partial overlap with existing tokens -> alias to the longest-overlap canon
#  - after all replacements, unmask attributes/math, then replace placeholders with full <mark>

ATTR_VALUE_RE = re.compile(r'="([^"<>]*)"')


def mask_attribute_values(html_text):
    placeholders = []

    def repl(m):
        idx = len(placeholders)
        placeholders.append(m.group(1))
        return f'="\x01ATTR_{idx}\x01"'

    # mask attribute values in all tags
    masked = re.sub(r'="([^"<>]*)"', repl, html_text)
    return masked, placeholders


def unmask_attribute_values(html_text, placeholders):
    def repl(m):
        idx = int(m.group(1))
        return f'="{placeholders[idx]}"'

    return re.sub(r'="\x01ATTR_(\d+)\x01"', repl, html_text)


def mask_script_style(html_text):
    placeholders = []

    def make_repl(tag):
        def repl(m):
            idx = len(placeholders)
            placeholders.append(m.group(0))
            return f"\x04SS_{idx}\x04"
        return repl

    masked = re.sub(r"<script\b[^>]*>.*?</script>", make_repl("script"), html_text, flags=re.DOTALL)
    masked = re.sub(r"<style\b[^>]*>.*?</style>", make_repl("style"), masked, flags=re.DOTALL)
    return masked, placeholders


def unmask_script_style(html_text, placeholders):
    def repl(m):
        idx = int(m.group(1))
        return placeholders[idx]

    return re.sub(r"\x04SS_(\d+)\x04", repl, html_text)


def mask_math_blocks(html_text):
    placeholders = []

    def add(s):
        idx = len(placeholders)
        placeholders.append(s)
        return f"\x02MATH_{idx}\x02"

    # $$...$$
    def repl_dd(m):
        return add(m.group(0))
    html_text = re.sub(r"\$\$.*?\$\$", repl_dd, html_text, flags=re.DOTALL)

    # \(...\)
    def repl_par(m):
        return add(m.group(0))
    html_text = re.sub(r"\\\(.*?\\\)", repl_par, html_text, flags=re.DOTALL)

    return html_text, placeholders


def unmask_math_blocks(html_text, placeholders):
    def repl(m):
        idx = int(m.group(1))
        return placeholders[idx]

    return re.sub(r"\x02MATH_(\d+)\x02", repl, html_text)


def find_token_safe_position(text, needle, start=0):
    """Find first position where needle occurs and is NOT inside an existing
    MARK token (\x00MARK_<id>\x00). Inside-token is detected by counting \x00
    chars before the position (odd count -> inside)."""
    while True:
        idx = text.find(needle, start)
        if idx < 0:
            return -1
        # count \x00 before idx
        n0 = text.count("\x00", 0, idx)
        if n0 % 2 == 0:
            # also check inside that needle doesn't contain a partial token
            # Specifically, if needle text contains a \x00 it's already inside a token
            if "\x00" not in needle:
                return idx
        start = idx + 1


def find_overlap_canon(text, needle):
    """When needle can't be placed safely, locate the area where needle WOULD go
    (by finding the longest matching prefix or suffix in text) and return the
    nearest overlapping token's canonical id.

    Strategy:
    - Try longest matching prefix of needle in text (>= 20 chars).
    - Try longest matching suffix in text.
    - From the matched anchor position, scan nearby tokens; pick the one whose
      replaced text (looked up via original_unique_texts) has the largest
      substring overlap with needle.
    """
    # Helper: find longest prefix p such that text.find(needle[:p]) succeeds, p>=10
    MIN_OVERLAP = 10

    def longest_prefix_match(s):
        # binary search
        lo, hi = MIN_OVERLAP, len(s)
        best = -1
        best_pos = -1
        while lo <= hi:
            mid = (lo + hi) // 2
            pos = text.find(s[:mid])
            if pos >= 0:
                best = mid
                best_pos = pos
                lo = mid + 1
            else:
                hi = mid - 1
        return best, best_pos

    def longest_suffix_match(s):
        lo, hi = MIN_OVERLAP, len(s)
        best = -1
        best_pos = -1
        while lo <= hi:
            mid = (lo + hi) // 2
            pos = text.find(s[len(s) - mid:])
            if pos >= 0:
                best = mid
                best_pos = pos
                lo = mid + 1
            else:
                hi = mid - 1
        return best, best_pos

    # Always scan ALL tokens in the document for maximum chunk overlap with the
    # needle. This is O(num_tokens * len(needle)) per missed snippet but only
    # runs for snippets that fail token-safe placement.
    window = text
    best_canon = None
    best_overlap = 0
    for m in re.finditer(r"\x00MARK_([^\x00]+)\x00", window):
        tok_text = _overlap_canon_texts.get(m.group(1), "")
        # compute substring overlap with needle: largest common substring length
        # cheap approach: use longest matching prefix/suffix of tok_text within needle
        # First try is tok_text a substring of needle? (containment)
        if tok_text and tok_text in needle:
            ov = len(tok_text)
            if ov > best_overlap:
                best_overlap = ov
                best_canon = m.group(1)
            continue
        if not tok_text:
            continue
        # Find longest common region: try prefixes/suffixes of needle inside tok_text
        # Simpler heuristic: scan for any common 20+ char chunk
        L = len(needle)
        for chunk_len in (120, 80, 60, 40, 20):
            if chunk_len > L:
                continue
            found = False
            for i in range(0, L - chunk_len + 1, max(1, chunk_len // 4)):
                if needle[i:i + chunk_len] in tok_text:
                    if chunk_len > best_overlap:
                        best_overlap = chunk_len
                        best_canon = m.group(1)
                    found = True
                    break
            if found:
                break
    return best_canon, best_overlap


# Populated in apply_marks
_overlap_canon_texts = {}


def html_escape_attr(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


def wrap_bare_math_tokens_for_attr(text):
    """Add $...$ around bare math tokens in summary_text before writing to data-zh-*."""
    if not text:
        return text
    return greedy_wrap_math(text, delim="dollar")


def apply_marks(html_text, index):
    """Returns (new_html, marks_applied, total_unique, missed_list)."""
    # Mask script/style first
    html_masked, ss_phs = mask_script_style(html_text)
    # Mask attribute values
    html_masked, attr_phs = mask_attribute_values(html_masked)
    # Mask math blocks
    html_masked, math_phs = mask_math_blocks(html_masked)

    unique_texts = index["unique_texts"]
    canonical_id_of = index["canonical_id_of"]
    phrases_at = index["phrases_at"]
    phrases_at_by_color = index["phrases_at_by_color"]

    # Populate global for find_overlap_canon
    global _overlap_canon_texts
    _overlap_canon_texts = dict(unique_texts)

    # Sort canons by text length desc
    sorted_canons = sorted(unique_texts.keys(), key=lambda c: -len(unique_texts[c]))

    missed = []
    applied = 0

    for canon in sorted_canons:
        needle = unique_texts[canon]
        if not needle:
            missed.append((canon, "empty"))
            continue
        pos = find_token_safe_position(html_masked, needle)
        if pos < 0:
            # Try partial overlap alias
            overlap_canon, overlap_sz = find_overlap_canon(html_masked, needle)
            if overlap_canon and overlap_sz > 0:
                # Alias canon -> overlap_canon
                # Translate canonical_id_of: any snippet_id mapping to canon now -> overlap_canon
                for sid, c in list(canonical_id_of.items()):
                    if c == canon:
                        canonical_id_of[sid] = overlap_canon
                # Move phrases_at[canon] into phrases_at[overlap_canon]
                for pid in phrases_at.get(canon, []):
                    if pid not in phrases_at[overlap_canon]:
                        phrases_at[overlap_canon].append(pid)
                phrases_at.pop(canon, None)
                # Move phrases_at_by_color
                for ck, pids in phrases_at_by_color.get(canon, {}).items():
                    for pid in pids:
                        if pid not in phrases_at_by_color[overlap_canon][ck]:
                            phrases_at_by_color[overlap_canon][ck].append(pid)
                phrases_at_by_color.pop(canon, None)
                continue
            # Truly missed
            missed.append((canon, needle[:80]))
            continue
        # Replace at pos with token placeholder
        token = f"\x00MARK_{canon}\x00"
        html_masked = html_masked[:pos] + token + html_masked[pos + len(needle):]
        applied += 1

    # Now unmask math then attributes then script/style
    html_masked = unmask_math_blocks(html_masked, math_phs)
    html_masked = unmask_attribute_values(html_masked, attr_phs)
    html_masked = unmask_script_style(html_masked, ss_phs)

    # Build mark replacements
    # Decide base color per canon
    def choose_base(canon):
        by_color = phrases_at_by_color.get(canon, {})
        if not by_color:
            return None
        if by_color.get("summary"):
            return "summary"
        # L2: max phrase count, tie -> earliest mN
        best = None
        best_count = -1
        for ck in COLOR_KEYS:
            if ck == "summary":
                continue
            if ck in by_color:
                cnt = len(by_color[ck])
                if cnt > best_count:
                    best_count = cnt
                    best = ck
        return best

    # Replace each token with the full <mark>
    # We need to find all tokens (some may have been duplicated? No - token-safe insertion ensures only inserted ones).
    token_re = re.compile(r"\x00MARK_([^\x00]+)\x00")

    # Also we need original snippet text for the mark content
    canon_text = {c: unique_texts[c] for c in unique_texts}

    def build_mark(canon):
        base = choose_base(canon)
        if not base:
            base = "summary"
        text = canon_text.get(canon, "")
        # data-back: union of phrase ids across all colors
        back_ids = phrases_at.get(canon, [])
        data_back = " ".join(f"sum-{pid}" for pid in back_ids)
        # data-zh-<color> and data-pids-<color>
        zh_attrs = []
        by_color = phrases_at_by_color.get(canon, {})
        for ck in COLOR_KEYS:
            if ck not in by_color:
                continue
            pids = by_color[ck]
            # build zh text: join summary_text via ' / '
            zh_parts = []
            for pid in pids:
                stext = index["phrase_text"].get(pid, "")
                # Auto-add $...$ to bare math tokens
                stext = wrap_bare_math_tokens_for_attr(stext)
                zh_parts.append(stext)
            zh = " ／ ".join(zh_parts)
            zh_esc = html_escape_attr(zh)
            zh_attrs.append(f' data-zh-{ck}="{zh_esc}"')
            zh_attrs.append(f' data-pids-{ck}="{" ".join(pids)}"')
        attr_blob = "".join(zh_attrs)
        return (f'<mark class="hl hl-{base}" id="{canon}" data-back="{data_back}"'
                f'{attr_blob}>{text}</mark>')

    def token_repl(m):
        canon = m.group(1)
        return build_mark(canon)

    new_html = token_re.sub(token_repl, html_masked)

    return new_html, applied, len(unique_texts), missed


# ---------------------------------------------------------------------------
# Step 5: CSS
# ---------------------------------------------------------------------------

def build_css():
    rules = []
    rules.append("""
/* Layout override */
/* Some source papers set `main { width: min(1120px, …) }` (a fixed width, not max-width).
   Plain `max-width` doesn't override that — we'd end up with a 1120px main minus 340px
   rail padding = narrow content. Set both width and max-width to win in either case. */
main { width: min(1320px, calc(100vw - 40px)) !important; max-width: 1320px !important; padding-right: 340px !important; position: relative !important; box-sizing: border-box !important; margin: 0 auto !important; }
@media (max-width: 1100px) {
  main { padding-right: 28px !important; }
  .margin-rail { position: absolute !important; left:0; top:0; width:100%; height:0; overflow:visible; background:transparent; border:0; box-shadow:none; }
}

/* Reader panel */
.reader-panel { background: rgba(255,255,255,0.85); border: 1px solid rgba(0,0,0,0.08); border-radius: 12px; padding: 14px 16px; margin: 0 0 24px; font-family: "PingFang TC", "Noto Sans TC", "Microsoft JhengHei", sans-serif; line-height: 1.7; }
.reader-panel .layer-title { font-size: 1.5em; font-weight: 700; margin: 0.7em 0 0.4em; color: #1f2428; }
.reader-panel .layer-title:first-child { margin-top: 0; }
.reader-panel .module-block { padding: 10px 12px; border-radius: 8px; margin: 0 0 12px; border: 1px solid rgba(0,0,0,0.06); }
.reader-panel .module-thesis { margin: 0 0 8px; font-size: 0.98em; color: #1f2428; line-height: 1.75; }
.reader-panel details.version { margin: 6px 0; border-radius: 6px; padding: 2px 0; border: 1px solid rgba(0,0,0,0.05); }
.reader-panel details.version > summary { cursor: pointer; list-style: none; font-weight: 500; padding: 6px 8px; border-radius: 6px; }
.reader-panel details.version > summary::-webkit-details-marker { display: none; }
.reader-panel details.version > summary::before { content: "▸"; display: inline-block; margin-right: 6px; transition: transform 0.2s; }
.reader-panel details.version[open] > summary::before { transform: rotate(90deg); }
.reader-panel .hdr { display: inline-flex; align-items: baseline; gap: 8px; flex-wrap: wrap; }
.reader-panel .rank-badge { font-size: 12px; padding: 1px 6px; border-radius: 4px; background: rgba(0,0,0,0.08); }
.reader-panel .vote { font-size: 12px; color: #555; }
.reader-panel .panel-body { padding: 8px 12px 10px; font-size: 0.95em; }
.reader-panel .panel-body p { margin: 6px 0; line-height: 1.85; }
.reader-panel .main-line-inline { font-weight: 600; margin-left: 4px; }
.reader-panel .main-line { margin: 6px 0; line-height: 1.7; padding: 0 12px; }
.reader-panel .terms-list { padding-left: 1.2em; margin: 0; }
.reader-panel .terms-list li { margin: 4px 0; line-height: 1.6; }
.reader-panel a.hl { padding: 0 1px; border-radius: 3px; cursor: pointer; text-decoration: none; }

/* Margin rail / notes */
.margin-rail { position: absolute; top: 0; right: 16px; width: 308px; pointer-events: none; }
body.notes-closed .margin-note { display:none !important; }
.margin-note { display:block; position: absolute; right: 0; width: 296px; box-sizing: border-box; pointer-events: auto; cursor: pointer; padding: 8px 10px; border-radius: 6px; font-family: "PingFang TC", "Noto Sans TC", "Microsoft JhengHei", sans-serif; font-size: 13px; line-height: 1.55; transition: top 0.2s ease; background: #fff; border: 1px solid rgba(0,0,0,0.08); }
.margin-note.is-active { box-shadow: 0 0 0 1px rgba(0,0,0,0.15); }
.margin-note.is-selected { box-shadow: 0 6px 18px rgba(0,0,0,0.2); z-index: 5; }
.mobile-note-slot { display:none; }
@media (max-width: 1100px) {
  .mobile-note-slot { display:block; clear:both; }
  body.notes-closed .mobile-note-slot { display:none !important; }
  .margin-note { position: static !important; right:auto; width:min(300px, calc(100vw - 28px)); max-width:calc(100vw - 28px); margin:5px 0 9px; font-size:12.5px; box-shadow:0 6px 20px rgba(0,0,0,0.18); }
}
.note-next { display: inline-block; margin-left: 6px; padding: 1px 8px; border-radius: 999px; background: rgba(0,0,0,0.06); font-size: 11.5px; color: #444; cursor: pointer; }
.note-next:hover { background: rgba(0,0,0,0.12); }

/* Generic selected outline */
mark.hl.is-selected { outline: 2.5px solid var(--sel-color, #444); outline-offset: 1px; border-radius: 2px; }
a.hl.is-selected { box-shadow: 0 0 0 2.5px var(--sel-color, #444), 0 4px 12px rgba(0,0,0,0.18); border-radius: 3px; position: relative; z-index: 2; }
mark.hl.hl-none { background: transparent !important; box-shadow: none !important; outline: none !important; cursor: text !important; padding: 0 !important; }

/* Floating toggle */
.color-toggle { position: fixed; top: 16px; right: 16px; z-index: 100; background: #fff; border: 1px solid rgba(0,0,0,0.12); border-radius: 8px; box-shadow: 0 4px 14px rgba(0,0,0,0.15); padding: 8px 10px; font-family: "PingFang TC", "Noto Sans TC", "Microsoft JhengHei", sans-serif; font-size: 12px; max-height: 80vh; overflow-y: auto; }
.color-toggle .ct-title { cursor: pointer; display: flex; align-items: center; justify-content: space-between; gap: 10px; user-select: none; font-weight: 700; margin-bottom: 6px; }
.color-toggle .ct-caret { transition: transform 0.15s ease; font-size: 11px; color: #666; }
.color-toggle.is-collapsed .ct-items { display: none; }
.color-toggle.is-collapsed .ct-caret { transform: rotate(-90deg); }
.color-toggle .ct-items { display: flex; flex-direction: column; gap: 4px; }
.color-toggle .ct-item { display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 2px 4px; border-radius: 4px; }
.color-toggle .ct-item:hover { background: rgba(0,0,0,0.04); }
.color-toggle .ct-swatch { width: 14px; height: 14px; border-radius: 3px; flex-shrink: 0; border: 1px solid rgba(0,0,0,0.15); }
.color-toggle .ct-swatch-notes { background: #30363d; border-color: #1a1d22; }
.color-toggle .ct-item.is-off { color: #888; }
.color-toggle .ct-item.is-off .ct-swatch { background: transparent !important; border-style: dashed !important; }

/* Synthesis module-block */
.module-block.c-synth { background: #f5f5f560; border-left: 4px solid #909090; }
.synth-body h4 { font-size: 0.95em; margin: 14px 0 6px; color: #303030; }
.synth-body h4:first-child { margin-top: 4px; }
.synth-body p { margin: 6px 0; }
.synth-body ul { padding-left: 1.4em; margin: 4px 0; }
.synth-body li { margin: 4px 0; line-height: 1.65; }
""")

    # Per-color rules
    for key, c in COLORS.items():
        fill = c["fill"]
        ink = c["ink"]
        ring = c["ring"]
        rules.append(f"""
.reader-panel details.version.c-{key} > summary {{ background: {fill}33; border-left: 3px solid {ring}; }}
.reader-panel details.version.c-{key}[open] > summary {{ background: {fill}55; }}
.reader-panel .module-block.c-{key} {{ background: {fill}26; border-left: 4px solid {ring}; }}
.hl-{key} {{ background: {fill}; box-shadow: inset 0 -2px 0 0 {ring}; border-radius: 2px; padding: 0 2px; cursor: pointer; }}
a.hl.hl-{key} {{ color: {ink}; text-decoration: none; }}
mark.hl.is-selected.sel-{key} {{ --sel-color: {ink}; }}
a.hl.is-selected.sel-{key} {{ --sel-color: {ink}; }}
.margin-note.n-{key} {{ background: {fill}40; border-left: 3px solid {ring}; color: {ink}; }}
.margin-note.n-{key}.is-selected {{ background: {fill}80; outline: 2.5px solid {ink}; outline-offset: 1px; }}
.color-toggle .ct-swatch-{key} {{ background: {fill}; border-color: {ring}; }}
body.off-{key} .margin-note.n-{key} {{ display: none; }}
""")
    return "\n".join(rules)


# ---------------------------------------------------------------------------
# Step 6: panel construction
# ---------------------------------------------------------------------------

_SUBSUP_RE = re.compile(r"&lt;(/?)(sub|sup)&gt;")

def esc(s):
    out = html.escape(s or "", quote=False)
    # Authors sometimes write <sub>...</sub> / <sup>...</sup> literally in
    # JSON fields (thesis, summary_text, refined_final_output) when math
    # delimiters would be awkward. Preserve those two specific tags after
    # general escaping so they render instead of showing as raw "<sub>X</sub>".
    return _SUBSUP_RE.sub(lambda m: f"<{m.group(1)}{m.group(2)}>", out)


def transform_panel_math(text):
    """Apply greedy wrapping with \\(...\\) on panel text (already escaped HTML).

    Splits on HTML tags so that attribute values inside tags are NEVER touched
    by the math wrapper. Only text between tags (and tag-free strings) get math
    transformation.
    """
    if not text:
        return text
    # Split into tag and non-tag segments
    parts = re.split(r"(<[^>]*>)", text)
    out = []
    for i, part in enumerate(parts):
        if part.startswith("<") and part.endswith(">"):
            out.append(part)
        else:
            # First, convert $...$ -> \(...\)
            p = re.sub(r"(?<!\\)\$(.+?)(?<!\\)\$", r"\\(\1\\)", part)
            # Then greedy wrap
            p = greedy_wrap_math(p, delim="paren")
            out.append(p)
    return "".join(out)


def wrap_summary_text(text, phrase_idx, canonical_id_of, color_key):
    """Build panel text where each phrase's summary_text is wrapped as <a class="hl hl-<color>">.

    phrase_idx: list of (phrase_id, summary_text). We iterate by summary_text length desc.
    """
    # Step: panel text gets greedy math wrap (\(...\))
    # But we need to wrap anchors AFTER escaping. Strategy: escape -> math wrap -> insert anchors.
    # Anchors are HTML, so we must wrap BEFORE escaping breaks them.
    # Simpler approach: escape, then for each phrase do str.replace(escaped_needle, anchor + escaped_needle + '</a>')
    # then transform math afterwards
    escaped_text = esc(text)

    sorted_phrases = sorted(phrase_idx, key=lambda p: -len(p[1]))
    for pid, summary_text in sorted_phrases:
        if not summary_text:
            continue
        # Compute canonical ids
        canon_ids = []
        seen = set()
        for sid in phrase_idx_to_snippets.get(pid, []):
            c = canonical_id_of.get(sid, sid)
            if c not in seen:
                seen.add(c)
                canon_ids.append(c)
        if not canon_ids:
            # No anchor for this phrase
            continue
        needle = esc(summary_text)
        if needle not in escaped_text:
            continue
        targets = " ".join(canon_ids)
        anchor_open = f'<a class="hl hl-{color_key}" id="sum-{pid}" data-id="{pid}" data-targets="{targets}">'
        replacement = anchor_open + needle + "</a>"
        escaped_text = escaped_text.replace(needle, replacement, 1)

    # Now transform math
    return transform_panel_math(escaped_text)


# Global phrase_id -> snippet ids (populated below)
phrase_idx_to_snippets = {}


def collect_phrase_snippets(maps):
    """Build phrase_id -> [snippet_id list]."""
    d = defaultdict(list)
    for mp in maps:
        for ph in mp["data"].get("phrases", []):
            pid = ph["id"]
            for s in ph.get("paper_snippets", []) or []:
                sid = s.get("snippet_id")
                if sid:
                    d[pid].append(sid)
    return d


def build_l1_panel(summary_data, l1_phrases, canonical_id_of):
    """l1_phrases: list of phrase dicts from l1 mapping (in order)."""
    # Build map: phrase_id -> phrase data; group by location
    p_by_id = {p["id"]: p for p in l1_phrases}
    main_line_phrases = [p for p in l1_phrases if p.get("summary_location") == "main_line"]
    refined_phrases = defaultdict(list)
    for p in l1_phrases:
        loc = p.get("summary_location", "")
        m = re.match(r"refined_final_output\[(\d+)\]", loc) or re.match(r"refined_(\d+)$", loc)
        if m:
            refined_phrases[int(m.group(1))].append(p)

    items = summary_data.get("items", [])
    items_sorted = sorted(items, key=lambda x: x.get("rank", 99))
    parts = ['<div class="layer-title">全文摘要</div>']

    for it in items_sorted:
        rank = it.get("rank", 0)
        vote = it.get("vote_total", 0)
        is_best = (rank == 1)
        open_attr = " open" if is_best else ""
        label = "最佳版本" if rank == 1 else "次佳版本"
        main_line = it.get("main_line", "")
        refined = it.get("refined_final_output", []) or []

        if is_best:
            # Build inline summary header with wrapped main_line, panel-body holds refined
            phrase_idx = [(p["id"], p["summary_text"]) for p in main_line_phrases]
            ml_html = wrap_summary_text(main_line, phrase_idx, canonical_id_of, "summary")
            summary_block = (
                f'<summary><span class="hdr">'
                f'<span class="rank-badge">{label}</span>'
                f'<span class="vote">vote {vote}</span>'
                f'</span><span class="main-line-inline">{ml_html}</span></summary>'
            )
            body_parts = []
            for i, para in enumerate(refined):
                phrase_idx_p = [(p["id"], p["summary_text"]) for p in refined_phrases.get(i, [])]
                p_html = wrap_summary_text(para, phrase_idx_p, canonical_id_of, "summary")
                body_parts.append(f"<p>{p_html}</p>")
            body = '<div class="panel-body">' + "".join(body_parts) + "</div>"
            parts.append(f'<details class="version c-summary"{open_attr}>{summary_block}{body}</details>')
        else:
            # Collapsed, main_line in main-line div, refined plain
            ml_html = transform_panel_math(esc(main_line))
            summary_block = (
                f'<summary><span class="hdr">'
                f'<span class="rank-badge">{label}</span>'
                f'<span class="vote">vote {vote}</span>'
                f'</span></summary>'
            )
            body_parts = [f'<div class="main-line">{ml_html}</div>']
            for para in refined:
                p_html = transform_panel_math(esc(para))
                body_parts.append(f"<p>{p_html}</p>")
            body = '<div class="panel-body">' + "".join(body_parts) + "</div>"
            parts.append(f'<details class="version c-summary"{open_attr}>{summary_block}{body}</details>')

    return "".join(parts)


CHINESE_NUM = ["", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十",
               "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
               "二十一", "二十二", "二十三", "二十四", "二十五", "二十六", "二十七", "二十八", "二十九", "三十"]


def extract_chinese_heading(text):
    """Extract Chinese portion from heading.

    If text is 'English (中文)' or '中文 (English)', take the Chinese part.
    If purely English, return as-is.
    """
    if not text:
        return text
    text = text.strip()
    # Check for parentheses
    m = re.match(r"^(.+?)\s*[（(](.+?)[)）]\s*$", text)
    if m:
        a, b = m.group(1).strip(), m.group(2).strip()
        a_has_cjk = re.search(r"[一-鿿]", a)
        b_has_cjk = re.search(r"[一-鿿]", b)
        if a_has_cjk and not b_has_cjk:
            return a
        if b_has_cjk and not a_has_cjk:
            return b
    return text


def build_method_panel(method_data, all_method_phrases_by_module, canonical_id_of):
    """Build the 技術及材料 section from method.json modules."""
    modules = method_data.get("modules", [])
    parts = ['<div class="layer-title">技術及材料</div>']

    for idx, mod in enumerate(modules):
        m_num = idx + 1
        cn_num = CHINESE_NUM[m_num] if m_num < len(CHINESE_NUM) else str(m_num)
        color_key = f"m{m_num}"
        items = mod.get("items", [])
        if not items:
            continue
        best = items[0]
        thesis = mod.get("thesis", "")
        heading_raw = mod.get("subitem_heading") or best.get("outline") or ""
        heading = extract_chinese_heading(heading_raw)

        # Wrap main_line phrases onto thesis (since thesis = main_line)
        module_phrases_all = all_method_phrases_by_module.get(color_key, [])
        main_line_phrases_m = [p for p in module_phrases_all if p.get("summary_location") == "main_line"]
        phrase_idx_main = [(p["id"], p["summary_text"]) for p in main_line_phrases_m]
        thesis_html_inner = wrap_summary_text(thesis, phrase_idx_main, canonical_id_of, color_key)

        # Module thesis line
        if heading:
            thesis_html = (
                f'<p class="module-thesis"><strong>主題{cn_num}：{esc(heading)}</strong><br>'
                f'{thesis_html_inner}</p>'
            )
        else:
            thesis_html = (
                f'<p class="module-thesis"><strong>主題{cn_num}</strong>：'
                f'{thesis_html_inner}</p>'
            )

        # Build versions: items[0] (best, wrapped), items[1] (次佳, plain) if present
        version_blocks = []
        for i, item in enumerate(items):
            rank = i + 1
            label = "最佳版本" if rank == 1 else "次佳版本"
            vote = item.get("vote_total", 0)
            refined = item.get("refined_final_output", []) or []
            summary_block = (
                f'<summary><span class="hdr">'
                f'<span class="rank-badge">{label}</span>'
                f'<span class="vote">vote {vote}</span>'
                f'</span></summary>'
            )
            body_parts = []
            if rank == 1:
                # Wrap with phrases from mapping (this module's color)
                module_phrases = all_method_phrases_by_module.get(color_key, [])
                refined_phrases = defaultdict(list)
                for p in module_phrases:
                    loc = p.get("summary_location", "")
                    m = re.match(r"refined_final_output\[(\d+)\]", loc) or re.match(r"refined_(\d+)$", loc)
                    if m:
                        refined_phrases[int(m.group(1))].append(p)
                for j, para in enumerate(refined):
                    phrase_idx = [(p["id"], p["summary_text"]) for p in refined_phrases.get(j, [])]
                    p_html = wrap_summary_text(para, phrase_idx, canonical_id_of, color_key)
                    body_parts.append(f"<p>{p_html}</p>")
            else:
                for para in refined:
                    body_parts.append(f"<p>{transform_panel_math(esc(para))}</p>")
            body = '<div class="panel-body">' + "".join(body_parts) + "</div>"
            version_blocks.append(f'<details class="version c-{color_key}">{summary_block}{body}</details>')

        # Toolchain terms block (best version's items[0].toolchain_terms)
        tc_terms = best.get("toolchain_terms", []) or []
        if tc_terms:
            terms_li = []
            for tc in tc_terms:
                term = transform_panel_math(esc(tc.get("term", "")))
                desc = transform_panel_math(esc(tc.get("description", "")))
                terms_li.append(f"<li><strong>{term}</strong>：{desc}</li>")
            terms_block = (
                f'<details class="version c-{color_key}">'
                f'<summary><span class="hdr"><span class="rank-badge">工具與材料</span></span></summary>'
                f'<div class="panel-body"><ul class="terms-list">{"".join(terms_li)}</ul></div>'
                f'</details>'
            )
            version_blocks.append(terms_block)

        block_html = (
            f'<div class="module-block c-{color_key}">'
            f'{thesis_html}'
            f'{"".join(version_blocks)}'
            f'</div>'
        )
        parts.append(block_html)

    return "".join(parts)


def md_to_html_synth(md_text):
    """Minimal markdown -> HTML for synthesis section."""
    lines = md_text.split("\n")
    out = []
    in_ul_stack = []  # list of indent depths
    para_lines = []

    def flush_para():
        nonlocal para_lines
        if para_lines:
            txt = " ".join(para_lines).strip()
            if txt:
                txt = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", esc(txt))
                out.append(f"<p>{txt}</p>")
            para_lines = []

    def close_uls(target_depth=0):
        while in_ul_stack and len(in_ul_stack) > target_depth:
            out.append("</ul>")
            in_ul_stack.pop()

    for line in lines:
        if not line.strip():
            flush_para()
            close_uls(0)
            continue
        # heading
        m = re.match(r"^#### (.+)$", line)
        if m:
            flush_para()
            close_uls(0)
            text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", esc(m.group(1).strip()))
            out.append(f"<h4>{text}</h4>")
            continue
        # bullet item
        m = re.match(r"^(\s*)\* (.+)$", line)
        if m:
            flush_para()
            indent = len(m.group(1))
            depth = 1 if indent < 2 else 2
            # adjust ul stack
            while in_ul_stack and in_ul_stack[-1] > depth:
                out.append("</ul>")
                in_ul_stack.pop()
            if not in_ul_stack or in_ul_stack[-1] < depth:
                out.append("<ul>")
                in_ul_stack.append(depth)
            text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", esc(m.group(2).strip()))
            out.append(f"<li>{text}</li>")
            continue
        # plain paragraph line
        para_lines.append(line.strip())

    flush_para()
    close_uls(0)
    return "\n".join(out)


def build_synth_block(md_path):
    if not os.path.exists(md_path):
        return ""
    with open(md_path) as f:
        text = f.read()
    # Find ### 4 and ### 5
    sections = []
    for header_re, label in [(r"### 4\. 方法組合策略", "方法組合策略"), (r"### 5\. 借鑑價值", "借鑑價值")]:
        m = re.search(header_re, text)
        if not m:
            continue
        start = m.end()
        # find next ### or eof
        m2 = re.search(r"\n### ", text[start:])
        if m2:
            content = text[start:start + m2.start()]
        else:
            content = text[start:]
        sections.append((label, content.strip()))
    if not sections:
        return ""
    html_parts = []
    for label, content in sections:
        html_parts.append(f"<h4>{esc(label)}</h4>")
        html_parts.append(md_to_html_synth(content))
    inner = "\n".join(html_parts)
    return (
        '<div class="module-block c-synth">'
        '<p class="module-thesis"><strong>方法組合策略 &amp; 借鑑價值</strong></p>'
        '<details class="version c-synth">'
        '<summary><span class="hdr"><span class="rank-badge">展開</span></span></summary>'
        f'<div class="panel-body synth-body">{inner}</div>'
        '</details>'
        '</div>'
    )


# ---------------------------------------------------------------------------
# Step 7: JS
# ---------------------------------------------------------------------------

def build_color_labels(method_data):
    """Build {color_key: human label} for the toggle widget.

    summary → "全文摘要"; mN → "N-{short_label}".
    Resolution order per module:
      1. mod["short_label"]   ← preferred: hand-curated 2-4 char keyword
      2. extract_chinese_heading(mod["subitem_heading"] or best["outline"])
      3. "主題N" fallback
    Author populates `short_label` in method.json once per module.
    """
    labels = {"summary": "全文摘要"}
    modules = (method_data or {}).get("modules", [])
    for idx, mod in enumerate(modules):
        m_num = idx + 1
        ck = f"m{m_num}"
        short = (mod.get("short_label") or "").strip()
        if short:
            labels[ck] = f"{m_num}-{short}"
            continue
        best = (mod.get("items") or [{}])[0]
        heading_raw = mod.get("subitem_heading") or best.get("outline") or ""
        heading = extract_chinese_heading(heading_raw)
        labels[ck] = f"{m_num}-{heading}" if heading else f"主題{m_num}"
    return labels


def build_js(color_labels=None):
    color_keys_js = json.dumps(COLOR_KEYS)
    color_labels_js = json.dumps(color_labels or {}, ensure_ascii=False)
    js = """
(function() {
  function init() {
    var COLOR_KEYS = __COLOR_KEYS__;
    var COLOR_LABELS = __COLOR_LABELS__;
    var enabled = new Set(['summary']);
    var notesByMark = new Map();
    var phraseTargets = new Map();
    var mobileSlotByMark = new Map();
    var mainEl = document.querySelector('main');
    if (!mainEl) return;

    function isNarrowViewport() { return window.innerWidth <= 1100; }
    function colorIsOn(ck) { return enabled.has(ck) && !document.body.classList.contains('off-' + ck); }

    function clearSelection() {
      document.querySelectorAll('.margin-note.is-selected').forEach(function(n){
        n.classList.remove('is-selected');
        COLOR_KEYS.forEach(function(k){ n.classList.remove('sel-' + k); });
      });
      document.querySelectorAll('mark.hl.is-selected').forEach(function(m){
        m.classList.remove('is-selected');
        COLOR_KEYS.forEach(function(k){ m.classList.remove('sel-' + k); });
      });
      document.querySelectorAll('a.hl.is-selected').forEach(function(a){
        a.classList.remove('is-selected');
        COLOR_KEYS.forEach(function(k){ a.classList.remove('sel-' + k); });
      });
    }

    function selectPair(mark, note) {
      clearSelection();
      var colorKey = null;
      if (note) {
        note.classList.forEach(function(c){
          var m = c.match(/^n-([a-z0-9]+)$/);
          if (m) colorKey = m[1];
        });
        note.classList.add('is-selected');
      }
      if (mark) {
        mark.classList.add('is-selected');
        if (colorKey) mark.classList.add('sel-' + colorKey);
        if (colorKey) {
          var pids = (mark.getAttribute('data-pids-' + colorKey) || '').split(/\\s+/).filter(Boolean);
          pids.forEach(function(pid){
            var a = document.getElementById('sum-' + pid);
            if (a) {
              a.classList.add('is-selected');
              a.classList.add('sel-' + colorKey);
            }
          });
        }
      }
    }

    function noteForMarkColor(mark, ck) {
      var entry = notesByMark.get(mark);
      if (!entry) return null;
      return entry[ck] || null;
    }

    // Anchor click
    var anchorCycle = new Map();
    document.querySelectorAll('.reader-panel a.hl[data-targets]').forEach(function(a){
      a.addEventListener('click', function(ev){
        ev.preventDefault();
        var targets = (a.getAttribute('data-targets') || '').split(/\\s+/).filter(Boolean);
        if (!targets.length) return;
        var aid = a.getAttribute('data-id');
        var idx = anchorCycle.get(aid) || 0;
        var tid = targets[idx % targets.length];
        anchorCycle.set(aid, (idx + 1) % targets.length);
        var mark = document.getElementById(tid);
        if (!mark) return;
        mark.scrollIntoView({behavior:'smooth', block:'center'});
        // anchorColor from class
        var anchorColor = null;
        a.classList.forEach(function(c){
          var m = c.match(/^hl-([a-z0-9]+)$/);
          if (m) anchorColor = m[1];
        });
        if (anchorColor && !colorIsOn(anchorColor)) {
          clearSelection();
          return;
        }
        var note = noteForMarkColor(mark, anchorColor);
        selectPair(mark, note);
      });
    });

    // Build margin rail
    var rail = document.createElement('div');
    rail.className = 'margin-rail';
    mainEl.appendChild(rail);

    // Build phraseTargets
    document.querySelectorAll('.reader-panel a.hl[data-targets][data-id]').forEach(function(a){
      var pid = a.getAttribute('data-id');
      var targets = (a.getAttribute('data-targets') || '').split(/\\s+/).filter(Boolean);
      if (!phraseTargets.has(pid)) phraseTargets.set(pid, []);
      var arr = phraseTargets.get(pid);
      targets.forEach(function(t){ if (arr.indexOf(t) === -1) arr.push(t); });
    });

    function slotForMark(mark) {
      var existing = mobileSlotByMark.get(mark);
      if (existing) return existing;
      var slot = document.createElement('span');
      slot.className = 'mobile-note-slot';
      // find punctuation after mark
      var anchor = mark;
      var next = mark.nextSibling;
      if (next && next.nodeType === Node.TEXT_NODE) {
        var t = next.textContent;
        var m = t.match(/^([，。！？；：、,.!?;:)\\]）？」』》]+)/);
        if (m) {
          var puncLen = m[1].length;
          var before = t.slice(0, puncLen);
          var rest = t.slice(puncLen);
          var puncNode = document.createTextNode(before);
          next.textContent = rest;
          mark.parentNode.insertBefore(puncNode, next);
          anchor = puncNode;
        }
      }
      if (anchor.nextSibling) {
        anchor.parentNode.insertBefore(slot, anchor.nextSibling);
      } else {
        anchor.parentNode.appendChild(slot);
      }
      mobileSlotByMark.set(mark, slot);
      return slot;
    }

    // Helper to wrap bare math tokens in note text using greedy strategy
    // Mirror Python wrapper using simple regex (only converts $...$ to \\(...\\))
    function noteContentFromAttr(t) {
      // HTML escape
      var s = t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
      // Convert $...$ to \\(...\\)
      s = s.replace(/(?<!\\\\)\\$([^$\\n]+?)(?<!\\\\)\\$/g, '\\\\($1\\\\)');
      return s;
    }

    // For each mark, build notes
    document.querySelectorAll('mark.hl').forEach(function(mark){
      var attrs = Array.from(mark.attributes);
      var colorNotes = {};
      attrs.forEach(function(at){
        var m = at.name.match(/^data-zh-([a-z0-9]+)$/);
        if (!m) return;
        var ck = m[1];
        var note = document.createElement('span');
        note.className = 'margin-note n-' + ck;
        note.innerHTML = noteContentFromAttr(at.value);
        // Next button
        var pidsAttr = mark.getAttribute('data-pids-' + ck) || '';
        var pids = pidsAttr.split(/\\s+/).filter(Boolean);
        var union = [];
        pids.forEach(function(pid){
          var arr = phraseTargets.get(pid) || [];
          arr.forEach(function(t){ if (union.indexOf(t) === -1) union.push(t); });
        });
        if (union.length > 1) {
          var nextBtn = document.createElement('span');
          nextBtn.className = 'note-next';
          var n = union.length - 1;
          nextBtn.textContent = '→ 其他 ' + n + ' 處';
          nextBtn.title = '跳到下一處（共 ' + union.length + ' 處）';
          nextBtn.addEventListener('click', function(ev){
            ev.stopPropagation();
            var idx = union.indexOf(mark.id);
            if (idx < 0) idx = 0;
            var nextId = union[(idx + 1) % union.length];
            var nextMark = document.getElementById(nextId);
            if (!nextMark) return;
            var entry = notesByMark.get(nextMark);
            var nextNote = entry ? (entry[ck] || null) : null;
            selectPair(nextMark, nextNote);
            nextMark.scrollIntoView({behavior:'smooth', block:'center'});
          });
          note.appendChild(nextBtn);
        }
        note.addEventListener('click', function(){
          selectPair(mark, note);
          mark.scrollIntoView({behavior:'smooth', block:'center'});
        });
        rail.appendChild(note);
        colorNotes[ck] = note;
      });
      if (Object.keys(colorNotes).length) {
        notesByMark.set(mark, colorNotes);
      }
    });

    // Typeset MathJax then reposition
    function doTypeset() {
      if (window.MathJax) {
        var ready = (MathJax.startup && MathJax.startup.promise) || Promise.resolve();
        ready.then(function(){
          if (MathJax.typesetPromise) {
            return MathJax.typesetPromise([mainEl]).then(function(){ reposition(); });
          }
        });
      }
    }

    function moveNotesToFlow() {
      notesByMark.forEach(function(entry, mark){
        var slot = slotForMark(mark);
        var keys = Object.keys(entry).sort(function(a,b){
          if (a === 'summary') return -1;
          if (b === 'summary') return 1;
          var ai = parseInt(a.replace('m',''),10);
          var bi = parseInt(b.replace('m',''),10);
          return ai - bi;
        });
        keys.forEach(function(k){
          var n = entry[k];
          n.style.top = '';
          n.style.left = '';
          n.style.right = '';
          slot.appendChild(n);
        });
      });
    }

    function moveNotesToRail() {
      notesByMark.forEach(function(entry){
        Object.keys(entry).forEach(function(k){
          var n = entry[k];
          if (n.parentNode !== rail) rail.appendChild(n);
        });
      });
    }

    var inLayout = false;
    function reposition() {
      if (inLayout) return;
      inLayout = true;
      requestAnimationFrame(function(){
        try {
          // reset rail-pad
          document.querySelectorAll('[data-rail-pad]').forEach(function(el){
            el.style.marginBottom = '';
            el.removeAttribute('data-rail-pad');
          });
          if (isNarrowViewport()) {
            moveNotesToFlow();
            return;
          }
          moveNotesToRail();

          var mainRect = mainEl.getBoundingClientRect();
          // Group notes by block
          var blockEntries = new Map();
          notesByMark.forEach(function(entry, mark){
            var block = mark.closest('.table-block, .table-wrap');
            if (!block) {
              block = mark.closest('p, figcaption, .table-title, .table-caption, li, h2, h3, .equation');
            }
            if (!block) return;
            if (mark.closest('.reader-panel')) return;
            if (!blockEntries.has(block)) blockEntries.set(block, []);
            var arr = blockEntries.get(block);
            var keys = Object.keys(entry).sort(function(a,b){
              if (a === 'summary') return -1;
              if (b === 'summary') return 1;
              var ai = parseInt(a.replace('m',''),10);
              var bi = parseInt(b.replace('m',''),10);
              return ai - bi;
            });
            keys.forEach(function(k){
              arr.push({ mark: mark, note: entry[k], color: k });
            });
          });

          // process in document order
          var blocks = Array.from(blockEntries.keys());
          blocks.sort(function(a,b){
            var p = a.compareDocumentPosition(b);
            if (p & Node.DOCUMENT_POSITION_FOLLOWING) return -1;
            if (p & Node.DOCUMENT_POSITION_PRECEDING) return 1;
            return 0;
          });
          var gap = 8;
          blocks.forEach(function(block){
            var arr = blockEntries.get(block);
            arr.forEach(function(it){
              var mr = it.mark.getBoundingClientRect();
              it.desired = mr.top - mainRect.top;
            });
            arr.sort(function(a,b){ return a.desired - b.desired; });
            var prevBottom = -Infinity;
            arr.forEach(function(it){
              var top = Math.max(it.desired, prevBottom + gap);
              it.note.style.top = top + 'px';
              prevBottom = top + it.note.offsetHeight;
            });
            // check overflow
            var br = block.getBoundingClientRect();
            var blockBottom = br.bottom - mainRect.top;
            if (prevBottom > blockBottom + 4) {
              var extra = prevBottom - blockBottom + 16;
              block.style.marginBottom = extra + 'px';
              block.setAttribute('data-rail-pad', '1');
            }
          });
        } finally {
          inLayout = false;
        }
      });
    }

    // Mark click
    var markCycle = new Map();
    document.querySelectorAll('mark.hl').forEach(function(mark){
      mark.addEventListener('click', function(ev){
        ev.preventDefault();
        ev.stopPropagation();
        var ids = (mark.getAttribute('data-back') || '').split(/\\s+/).filter(Boolean);
        var pool = ids.filter(function(sid){
          var anchor = document.getElementById(sid);
          if (!anchor) return false;
          var ck = null;
          anchor.classList.forEach(function(c){
            var m = c.match(/^hl-([a-z0-9]+)$/);
            if (m) ck = m[1];
          });
          return ck && colorIsOn(ck);
        });
        if (!pool.length) { clearSelection(); return; }
        var idx = markCycle.get(mark.id) || 0;
        var sid = pool[idx % pool.length];
        markCycle.set(mark.id, (idx + 1) % pool.length);
        var anchor = document.getElementById(sid);
        if (!anchor) return;
        var p = anchor.parentElement;
        while (p) {
          if (p.tagName === 'DETAILS') p.open = true;
          p = p.parentElement;
        }
        anchor.scrollIntoView({behavior:'smooth', block:'center'});
        var ck = null;
        anchor.classList.forEach(function(c){
          var m = c.match(/^hl-([a-z0-9]+)$/);
          if (m) ck = m[1];
        });
        var note = noteForMarkColor(mark, ck);
        selectPair(mark, note);
      });
    });

    // is-active observer
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(ent){
        var mark = ent.target;
        var entry = notesByMark.get(mark);
        if (!entry) return;
        if (ent.isIntersecting) {
          Object.values(entry).forEach(function(n){ n.classList.add('is-active'); });
        } else {
          Object.values(entry).forEach(function(n){ n.classList.remove('is-active'); });
        }
      });
    }, { rootMargin: '-30% 0px -50% 0px' });
    document.querySelectorAll('mark.hl').forEach(function(m){ io.observe(m); });

    // Color toggle floating panel
    var toggle = document.createElement('div');
    toggle.className = 'color-toggle';
    var titleEl = document.createElement('div');
    titleEl.className = 'ct-title';
    titleEl.innerHTML = '<span class="ct-label">顯示</span><span class="ct-caret">▾</span>';
    titleEl.addEventListener('click', function(){
      toggle.classList.toggle('is-collapsed');
    });
    toggle.appendChild(titleEl);
    var itemsBox = document.createElement('div');
    itemsBox.className = 'ct-items';
    toggle.appendChild(itemsBox);

    // notes toggle
    var notesItem = document.createElement('div');
    notesItem.className = 'ct-item';
    notesItem.setAttribute('data-action', 'notes');
    notesItem.innerHTML = '<span class="ct-swatch ct-swatch-notes"></span><span>開啟卡片</span>';
    notesItem.addEventListener('click', function(){
      var off = document.body.classList.toggle('notes-closed');
      notesItem.classList.toggle('is-off', off);
      reposition();
    });
    itemsBox.appendChild(notesItem);

    function chooseBase(mark) {
      if (enabled.has('summary')) {
        var v = (mark.getAttribute('data-pids-summary') || '').trim();
        if (v) return 'summary';
      }
      var best = null;
      var bestCount = -1;
      for (var i = 0; i < COLOR_KEYS.length; i++) {
        var k = COLOR_KEYS[i];
        if (k === 'summary') continue;
        if (!enabled.has(k)) continue;
        var av = (mark.getAttribute('data-pids-' + k) || '').trim();
        if (!av) continue;
        var cnt = av.split(/\\s+/).length;
        if (cnt > bestCount) {
          bestCount = cnt;
          best = k;
        }
      }
      return best;
    }

    function rebaseMarks() {
      document.querySelectorAll('mark.hl').forEach(function(mark){
        var classes = mark.className.split(/\\s+/);
        var keep = classes.filter(function(c){
          return !(c.indexOf('hl-') === 0 || c.indexOf('sel-') === 0 || c === 'is-selected');
        });
        var base = chooseBase(mark);
        if (base) keep.push('hl-' + base); else keep.push('hl-none');
        mark.className = keep.join(' ');
      });
      document.querySelectorAll('.margin-note.is-selected').forEach(function(n){
        n.classList.remove('is-selected');
      });
      document.querySelectorAll('a.hl.is-selected').forEach(function(a){
        a.classList.remove('is-selected');
        COLOR_KEYS.forEach(function(k){ a.classList.remove('sel-' + k); });
      });
    }

    COLOR_KEYS.forEach(function(k){
      // Only emit toggle items for color keys this paper actually uses.
      // `summary` is always present; method colors only when COLOR_LABELS has them.
      if (k !== 'summary' && !(COLOR_LABELS && COLOR_LABELS[k])) return;
      var item = document.createElement('div');
      item.className = 'ct-item';
      item.setAttribute('data-color', k);
      var label = (COLOR_LABELS && COLOR_LABELS[k]) ? COLOR_LABELS[k] : k;
      item.innerHTML = '<span class="ct-swatch ct-swatch-' + k + '"></span><span>' + label + '</span>';
      if (k !== 'summary') {
        document.body.classList.add('off-' + k);
        item.classList.add('is-off');
      }
      item.addEventListener('click', function(){
        if (enabled.has(k)) {
          enabled.delete(k);
          document.body.classList.add('off-' + k);
          item.classList.add('is-off');
        } else {
          enabled.add(k);
          document.body.classList.remove('off-' + k);
          item.classList.remove('is-off');
        }
        rebaseMarks();
        reposition();
      });
      itemsBox.appendChild(item);
    });

    document.body.appendChild(toggle);

    // initial reposition + typeset
    rebaseMarks();
    reposition();
    doTypeset();

    window.addEventListener('resize', reposition);
    if (window.ResizeObserver) {
      var ro = new ResizeObserver(reposition);
      ro.observe(mainEl);
    } else {
      document.addEventListener('toggle', reposition, true);
    }
    document.querySelectorAll('main img').forEach(function(img){
      if (!img.complete) img.addEventListener('load', reposition);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
"""
    return js.replace("__COLOR_KEYS__", color_keys_js).replace("__COLOR_LABELS__", color_labels_js)


# ---------------------------------------------------------------------------
# Step 8: Inject and write
# ---------------------------------------------------------------------------

def inject(html_text, css, panel_html, js):
    style_block = f'<style id="reader-panel-style">\n{css}\n</style>\n'
    aside_block = f'<aside class="reader-panel">\n{panel_html}\n</aside>\n'
    js_block = f'<script id="reader-panel-js">\n{js}\n</script>\n'
    inject_blob = style_block + aside_block + js_block

    # Insert after the first <main...> tag.
    new_html, n = re.subn(r"(<main\b[^>]*>)", lambda m: m.group(1) + "\n" + inject_blob, html_text, count=1)
    if n == 0:
        # No <main> in source — wrap <body> content in <main> so the JS
        # (which queries `document.querySelector('main')`) can find it.
        # ALSO override body's width/padding (these papers cap body at
        # 880-980px, which would clamp the synthetic main below 1320px).
        synth_reset = (
            '<style id="reader-panel-synth-main-reset">\n'
            'body { max-width: none !important; padding: 0 !important; margin: 0 !important; }\n'
            'main { margin: 0 auto !important; }\n'
            '</style>\n'
        )
        new_html, n = re.subn(
            r"(<body\b[^>]*>)",
            lambda m: m.group(1) + "\n" + synth_reset + "<main>\n" + inject_blob,
            html_text, count=1,
        )
        if n == 0:
            raise RuntimeError("Could not find <main> or <body> tag")
        # Close the synthetic <main> before </body>
        new_html, n_close = re.subn(r"(</body\s*>)", r"</main>\n\1", new_html, count=1)
        if n_close == 0:
            new_html = new_html.rstrip() + "\n</main>\n"
        print("  [inject] no <main> found, wrapped <body> content in synthetic <main> (body width reset)")
    return new_html


# ---------------------------------------------------------------------------
# Step 9: self-check
# ---------------------------------------------------------------------------

def self_check(maps, final_html, missed):
    failures = []
    passes = []

    # Strip script/style blocks for tests that need to ignore them
    def strip_script_style(s):
        s = re.sub(r"<script\b[^>]*>.*?</script>", "", s, flags=re.DOTALL)
        s = re.sub(r"<style\b[^>]*>.*?</style>", "", s, flags=re.DOTALL)
        return s

    style_match = re.search(r'<style id="reader-panel-style">(.*?)</style>', final_html, re.DOTALL)
    style_block = style_match.group(1) if style_match else ""

    panel_match = re.search(r'<aside class="reader-panel">(.*?)</aside>', final_html, re.DOTALL)
    panel_block = panel_match.group(1) if panel_match else ""

    # 1. Anchor completeness per mapping
    check_ok = True
    for mp in maps:
        expected = sum(1 for p in mp["data"].get("phrases", []) if p.get("paper_snippets"))
        # Count <a class="hl hl-<ck>"
        ck = mp["color_key"]
        actual = len(re.findall(r'<a class="hl hl-' + re.escape(ck) + r'"', panel_block))
        if actual < expected:
            check_ok = False
            failures.append(f"check 1 FAIL: {mp['key']} expected {expected} anchors, got {actual}")
    if check_ok:
        print("[Step 9] check 1 PASS")
        passes.append(1)
    else:
        print(f"[Step 9] check 1 FAIL")

    # 2. Per-color six rules in style block
    check_ok = True
    for ck in COLORS.keys():
        needed = [
            f".c-{ck}",
            f".hl-{ck}",
            f".margin-note.n-{ck}",
            f".ct-swatch-{ck}",
            # .sel-<key> can be in mark.hl.is-selected.sel-K or a.hl.is-selected.sel-K
            None,  # placeholder for sel- check
            f"body.off-{ck} .margin-note.n-{ck}",
        ]
        for n in needed:
            if n is None:
                # sel- check
                if not (f"mark.hl.is-selected.sel-{ck}" in style_block or f"a.hl.is-selected.sel-{ck}" in style_block):
                    check_ok = False
                    failures.append(f"check 2 FAIL: missing .sel-{ck} for color {ck}")
                continue
            if n not in style_block:
                check_ok = False
                failures.append(f"check 2 FAIL: missing '{n}' for color {ck}")
    if check_ok:
        print("[Step 9] check 2 PASS")
        passes.append(2)
    else:
        for f in failures:
            if "check 2" in f:
                print(f"[Step 9] {f}")

    # 3. mark.hl.hl-none
    if "mark.hl.hl-none" in style_block:
        print("[Step 9] check 3 PASS")
        passes.append(3)
    else:
        print("[Step 9] check 3 FAIL: missing mark.hl.hl-none in style")

    # 4. toolchain_terms structure (method mode)
    check_ok = True
    if os.path.exists(METHOD_JSON):
        with open(METHOD_JSON) as f:
            md = json.load(f)
        for idx, mod in enumerate(md["modules"]):
            ck = f"m{idx+1}"
            best = mod["items"][0]
            tc = best.get("toolchain_terms", []) or []
            if not tc:
                continue
            # Check exactly one module-block with this c-mN containing the toolchain_terms details
            # Find the module block
            block_re = re.compile(
                r'<div class="module-block c-' + re.escape(ck) + r'">(.*?)</div>\s*(?=<div class="module-block|<div class="layer-title">|$)',
                re.DOTALL,
            )
            m = block_re.search(panel_block)
            if not m:
                # try alternate non-greedy approach: find by class then count details
                pat = re.compile(r'<div class="module-block c-' + re.escape(ck) + r'">', re.DOTALL)
                if not pat.search(panel_block):
                    check_ok = False
                    failures.append(f"check 4 FAIL: no module-block c-{ck}")
                    continue
            content = m.group(1) if m else panel_block
            # Find all <details class="version c-mN">...</details>
            details = re.findall(r'<details class="version c-' + re.escape(ck) + r'">(.*?)</details>', content, re.DOTALL)
            tc_count = 0
            for d in details:
                if "工具與材料" in d:
                    tc_count += 1
            if tc_count != 1:
                check_ok = False
                failures.append(f"check 4 FAIL: c-{ck} expected 1 toolchain details, got {tc_count}")
            # Ensure it's the LAST details (look for any 工具與材料 inside other details)
    if check_ok:
        print("[Step 9] check 4 PASS")
        passes.append(4)
    else:
        for f in failures:
            if "check 4" in f:
                print(f"[Step 9] {f}")

    # 5. terms-list format
    check_ok = True
    for ul_match in re.finditer(r'<ul class="terms-list">(.*?)</ul>', panel_block, re.DOTALL):
        ul = ul_match.group(1)
        for li in re.finditer(r"<li>(.*?)</li>", ul, re.DOTALL):
            content = li.group(1)
            if not re.match(r"^\s*<strong>.+?</strong>：", content, re.DOTALL):
                check_ok = False
                failures.append(f"check 5 FAIL: bad li format: {content[:80]}")
                break
    if "chip" in panel_block:
        check_ok = False
        failures.append("check 5 FAIL: legacy chip pattern detected")
    if check_ok:
        print("[Step 9] check 5 PASS")
        passes.append(5)
    else:
        for f in failures:
            if "check 5" in f:
                print(f"[Step 9] {f}")

    # 6. Marks idempotent: each canonical id appears exactly once
    mark_ids = re.findall(r'<mark[^>]*id="([^"]+)"', final_html)
    id_counts = defaultdict(int)
    for mid in mark_ids:
        id_counts[mid] += 1
    dups = [mid for mid, c in id_counts.items() if c >= 2]
    if dups:
        print(f"[Step 9] check 6 FAIL: duplicate mark ids: {dups[:5]}")
        failures.append(f"check 6 FAIL: dup ids {dups[:5]}")
    else:
        print("[Step 9] check 6 PASS")
        passes.append(6)
    if missed:
        print(f"Missed snippets: {missed}")
    else:
        print("Missed snippets: []")

    # 7. Section title
    has_method = any(mp["lane"] == "method" for mp in maps)
    has_detail = any(mp["lane"] == "detail" for mp in maps)
    check_ok = True
    if has_method:
        if '<div class="layer-title">技術及材料</div>' not in panel_block:
            check_ok = False
            failures.append("check 7 FAIL: missing 技術及材料 title")
        if '<div class="layer-title">分項細節</div>' in panel_block:
            check_ok = False
            failures.append("check 7 FAIL: unexpected 分項細節 title in method-only paper")
    if has_detail:
        if '<div class="layer-title">分項細節</div>' not in panel_block:
            check_ok = False
            failures.append("check 7 FAIL: missing 分項細節 title")
    if check_ok:
        print("[Step 9] check 7 PASS")
        passes.append(7)
    else:
        for f in failures:
            if "check 7" in f:
                print(f"[Step 9] {f}")

    # 8. <mark> not inside attribute value
    no_scripts = re.sub(r"<script\b[^>]*>.*?</script>", "", final_html, flags=re.DOTALL)
    m = re.search(r'"[^"<>]*<mark\b', no_scripts)
    if m:
        ctx = no_scripts[max(0, m.start() - 200):m.start() + 100]
        print(f"[Step 9] check 8 FAIL: <mark> inside attr near: {ctx[:300]!r}")
        failures.append("check 8 FAIL")
    else:
        print("[Step 9] check 8 PASS")
        passes.append(8)

    # 9. <mark> not inside $$...$$ or \(...\)
    body_only = strip_script_style(final_html)
    check_ok = True
    for mblk in re.finditer(r"\$\$(.*?)\$\$", body_only, re.DOTALL):
        inner = mblk.group(1)
        if "<mark" in inner or "</mark" in inner:
            ctx = mblk.group(0)[:200]
            print(f"[Step 9] check 9 FAIL: <mark> in $$...$$ near: {ctx!r}")
            failures.append("check 9 FAIL $$")
            check_ok = False
            break
    if check_ok:
        for mblk in re.finditer(r"\\\((.*?)\\\)", body_only, re.DOTALL):
            inner = mblk.group(1)
            if "<mark" in inner or "</mark" in inner:
                ctx = mblk.group(0)[:200]
                print(f"[Step 9] check 9 FAIL: <mark> in \\(...\\) near: {ctx!r}")
                failures.append("check 9 FAIL \\(\\)")
                check_ok = False
                break
    if check_ok:
        print("[Step 9] check 9 PASS")
        passes.append(9)

    # 10. No residual token placeholders
    check_ok = True
    if "\x00" in final_html:
        idx = final_html.find("\x00")
        ctx = final_html[max(0, idx - 80):idx + 100]
        print(f"[Step 9] check 10 FAIL: \\x00 residue near: {ctx!r}")
        failures.append("check 10 FAIL")
        check_ok = False
    # MARK_<id> literal outside data- attribute names
    # We'll scan for /MARK_[a-zA-Z]/ but exclude positions following 'data-' or 'class='
    # Simple approach: strip data-* attribute fragments first
    stripped = re.sub(r'data-[a-z-]+="[^"]*"', "", final_html)
    stripped = re.sub(r'class="[^"]*"', "", stripped)
    stripped = re.sub(r'id="[^"]*"', "", stripped)
    # Find MARK_ literal
    m = re.search(r"MARK_[a-zA-Z][a-zA-Z0-9_-]*", stripped)
    if m:
        # ensure not inside script style
        # Already stripped above we kept script/style; let's strip them too
        only_text = strip_script_style(stripped)
        m2 = re.search(r"MARK_[a-zA-Z][a-zA-Z0-9_-]*", only_text)
        if m2:
            ctx = only_text[max(0, m2.start() - 80):m2.end() + 80]
            print(f"[Step 9] check 10 FAIL: MARK_ literal near: {ctx!r}")
            failures.append("check 10 FAIL")
            check_ok = False
    if check_ok:
        print("[Step 9] check 10 PASS")
        passes.append(10)

    # 11. Bare math tokens not leaked outside math wrappers
    check_ok = True
    # Strip script/style first
    body_only = strip_script_style(final_html)
    # Strip $$...$$, \(...\), $...$ contents
    def strip_math_contents(s):
        s = re.sub(r"\$\$.*?\$\$", "", s, flags=re.DOTALL)
        s = re.sub(r"\\\(.*?\\\)", "", s, flags=re.DOTALL)
        s = re.sub(r"\$[^$\n]+?\$", "", s)
        return s

    # (a) panel text nodes
    panel_only = ""
    pm = re.search(r'<aside class="reader-panel">(.*?)</aside>', body_only, re.DOTALL)
    if pm:
        panel_only = pm.group(1)
    panel_stripped = strip_math_contents(panel_only)
    # Remove all HTML tags
    panel_text_nodes = re.sub(r"<[^>]+>", " ", panel_stripped)
    # Exemptions whitelist
    exemptions = set([
        "H3K27me3", "Cas9", "AP-1", "Cobb-Douglas", "node_modules",
    ])

    def report_bare(s, tag):
        leaks = []
        # Find sub/sup atoms
        for m in re.finditer(r"[A-Za-z][_^][A-Za-z0-9{}]+", s):
            tok = m.group(0)
            if tok in exemptions:
                continue
            leaks.append((m.start(), tok))
        for m in re.finditer(r"\\[a-zA-Z]+", s):
            tok = m.group(0)
            if tok in exemptions:
                continue
            leaks.append((m.start(), tok))
        for m in re.finditer(r"[αβγδλμσΠΣ]", s):
            tok = m.group(0)
            leaks.append((m.start(), tok))
        return leaks

    leaks_a = report_bare(panel_text_nodes, "panel")
    # (b) data-zh-* attribute values
    leaks_b = []
    for m in re.finditer(r'data-zh-[a-z0-9]+="([^"]*)"', body_only):
        v = m.group(1)
        v_stripped = strip_math_contents(v)
        for l in report_bare(v_stripped, "attr"):
            leaks_b.append(l)

    if leaks_a or leaks_b:
        check_ok = False
        sample = (leaks_a + leaks_b)[:10]
        print(f"[Step 9] check 11 FAIL: bare math leaks: {sample}")
        failures.append("check 11 FAIL")
    if check_ok:
        print("[Step 9] check 11 PASS")
        passes.append(11)

    return len(passes), failures


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _parse_args():
    p = argparse.ArgumentParser(description="Deterministic paper assembler")
    p.add_argument("paper_dir", help="Paper root (must contain reassembly/, mapping/, summary/, method/)")
    p.add_argument("--out", default=None, help="Output HTML path (default: <paper_dir>/mapping/canonical/paper.html)")
    return p.parse_args()


def _configure_paths(paper_dir, out_html=None):
    global PAPER_DIR, SRC_HTML, OUT_HTML, MAPPING_DIR, METHOD_JSON, SUMMARY_JSON, METHOD_MD
    PAPER_DIR = os.path.abspath(paper_dir)
    SRC_HTML = os.path.join(PAPER_DIR, "reassembly/canonical/paper.html")
    MAPPING_DIR = os.path.join(PAPER_DIR, "mapping/canonical")
    METHOD_JSON = os.path.join(PAPER_DIR, "method/canonical/method.json")
    SUMMARY_JSON = os.path.join(PAPER_DIR, "summary/canonical/summary.json")
    METHOD_MD = os.path.join(PAPER_DIR, "method/methodology_and_toolchain.md")
    OUT_HTML = os.path.abspath(out_html) if out_html else os.path.join(PAPER_DIR, "mapping/canonical/paper.html")


def main():
    args = _parse_args()
    _configure_paths(args.paper_dir, args.out)

    maps = discover_maps()
    print(f"Discovered {len(maps)} mappings")

    global phrase_idx_to_snippets
    phrase_idx_to_snippets = collect_phrase_snippets(maps)

    index = build_snippet_index(maps)

    with open(SRC_HTML) as f:
        html_text = f.read()

    html_text = strip_prior(html_text)
    html_text = patch_mathjax_config(html_text)

    # Step 4
    new_html, applied, total_unique, missed = apply_marks(html_text, index)
    print(f"Paper marks applied: {applied}/{total_unique}")
    if missed:
        for canon, snippet_preview in missed:
            print(f"  MISSED canon={canon} snippet={snippet_preview!r}")

    # Step 5
    css = build_css()

    # Step 6: panel
    # Load summary.json
    with open(SUMMARY_JSON) as f:
        summary_data = json.load(f)

    # Collect L1 phrases
    l1_phrases = []
    method_phrases_by_color = defaultdict(list)
    for mp in maps:
        if mp["lane"] == "l1":
            l1_phrases = mp["data"].get("phrases", [])
        elif mp["lane"] == "method":
            method_phrases_by_color[mp["color_key"]] = mp["data"].get("phrases", [])
        # detail not used here

    panel_parts = []
    if l1_phrases or True:
        panel_parts.append(build_l1_panel(summary_data, l1_phrases, index["canonical_id_of"]))
    # Method panel
    method_data = None
    if os.path.exists(METHOD_JSON):
        with open(METHOD_JSON) as f:
            method_data = json.load(f)
        panel_parts.append(build_method_panel(method_data, method_phrases_by_color, index["canonical_id_of"]))
        # Synthesis block
        synth = build_synth_block(METHOD_MD)
        if synth:
            panel_parts.append(synth)
    panel_html = "".join(panel_parts)

    # Step 7
    color_labels = build_color_labels(method_data)
    js = build_js(color_labels)

    # Step 8: inject
    final_html = inject(new_html, css, panel_html, js)

    # Write
    os.makedirs(os.path.dirname(OUT_HTML), exist_ok=True)
    with open(OUT_HTML, "w") as f:
        f.write(final_html)
    print(f"Wrote: {OUT_HTML}")

    # Step 9 self-check
    with open(OUT_HTML) as f:
        check_html = f.read()
    n_pass, failures = self_check(maps, check_html, missed)
    if n_pass == 11:
        print("Step 9 self-check: 11/11 PASS")
        sys.exit(0)
    else:
        print(f"Step 9 self-check: {n_pass}/11 PASS")
        for f in failures:
            print(f"  {f}")
        sys.exit(1)


if __name__ == "__main__":
    main()
