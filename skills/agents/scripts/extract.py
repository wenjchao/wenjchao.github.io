#!/usr/bin/env python3
"""
Build a coordinate-bearing document representation from an academic PDF.

The script has two internal responsibilities:

1. raw evidence extraction
   - recover words, chars, and geometry from the PDF
   - apply narrow mechanical normalization such as PUA mapping

2. canonical representation building
   - assign stable IDs
   - build candidate blocks and artifact regions
   - write the canonical `extracted.json` schema used downstream

This script should not become a hidden paragraph assembler. Any structure
fields it emits are candidates for downstream use, not final semantic truth.

Usage:
    python3 extract.py input.pdf output.json [options]

Options:
    --sidebar-filter N   Remove words with x0 > N (auto-detect if omitted)
"""

# -- PUA → Unicode mapping ----------------------------------------------------
# Covers common publisher fonts (SymbolGreek, MathematicalPi,
# MinionPro-Italic for numbers, etc.).
PUA_MAP = {
    # Lowercase Greek
    '\uf061': '\u03b1',  # α
    '\uf062': '\u03b2',  # β
    '\uf063': '\u03c7',  # χ (chi, often encoded here in SymbolGreek)
    '\uf064': '\u03b4',  # δ
    '\uf065': '\u03b5',  # ε
    '\uf066': '\u03c6',  # φ (phi)
    '\uf067': '\u03b3',  # γ
    '\uf068': '\u03b7',  # η
    '\uf069': '\u03b9',  # ι
    '\uf06a': '\u03d5',  # ϕ
    '\uf06b': '\u03ba',  # κ
    '\uf06c': '\u03bb',  # λ
    '\uf06d': '\u00b5',  # µ (micro sign)
    '\uf06e': '\u03bd',  # ν
    '\uf06f': '\u03bf',  # ο
    '\uf070': '\u03c0',  # π
    '\uf071': '\u03b8',  # θ
    '\uf072': '\u03c1',  # ρ
    '\uf073': '\u03c3',  # σ
    '\uf074': '\u03c4',  # τ
    '\uf075': '\u03c5',  # υ
    '\uf076': '\u03d6',  # ϖ
    '\uf077': '\u03c9',  # ω
    '\uf078': '\u03be',  # ξ
    '\uf079': '\u03c8',  # ψ
    '\uf07a': '\u03b6',  # ζ
    # Uppercase Greek
    '\uf041': '\u0391',  # Α
    '\uf042': '\u0392',  # Β
    '\uf043': '\u03a7',  # Χ
    '\uf044': '\u0394',  # Δ
    '\uf045': '\u0395',  # Ε
    '\uf046': '\u03a6',  # Φ
    '\uf047': '\u0393',  # Γ
    '\uf048': '\u0397',  # Η
    '\uf049': '\u0399',  # Ι
    '\uf04b': '\u039a',  # Κ
    '\uf04c': '\u039b',  # Λ
    '\uf04d': '\u039c',  # Μ
    '\uf04e': '\u039d',  # Ν
    '\uf04f': '\u039f',  # Ο
    '\uf050': '\u03a0',  # Π
    '\uf051': '\u0398',  # Θ
    '\uf052': '\u03a1',  # Ρ
    '\uf053': '\u03a3',  # Σ
    '\uf054': '\u03a4',  # Τ
    '\uf055': '\u03a5',  # Υ
    '\uf057': '\u03a9',  # Ω
    '\uf058': '\u039e',  # Ξ
    '\uf059': '\u03a8',  # Ψ
    '\uf05a': '\u0396',  # Ζ
    # Math / special (common MathematicalPi / Symbol codepoints)
    '\uf0b1': '\u00b1',  # ±
    '\uf0b2': '\u2264',  # ≤
    '\uf0b3': '\u2265',  # ≥
    '\uf0b4': '\u00d7',  # ×
    '\uf0b8': '\u00f7',  # ÷
    '\uf0d7': '\u00d7',  # ×
    '\uf0b0': '\u00b0',  # °
    '\uf0a2': '\u2032',  # ′ prime
    '\uf0a3': '\u2033',  # ″ double prime
    '\uf0d1': '\u2192',  # →
    '\uf0de': '\u21d2',  # ⇒
    '\uf0ae': '\u2192',  # →
    # Publisher-specific PUA (Wiley, Elsevier, Springer)
    '\uf6d9': '\u00a9',  # © copyright (Wiley journals)
    '\uf6da': '\u00ae',  # ® registered
    '\uf6e8': '\u00a9',  # © copyright (alternate Wiley encoding)
    '\uf0a7': '\u2022',  # bullet
    '\uf0e0': '\u2190',  # ← leftarrow
    '\uf0a5': '\u221e',  # infinity
    '\uf0b6': '\u2202',  # partial differential
    '\uf0b9': '\u2260',  # not equal
    '\uf0b5': '\u221d',  # proportional to
    '\uf0c5': '\u2245',  # approximately equal
    '\uf0ba': '\u2026',  # ellipsis
    '\uf0bb': '\u2194',  # left-right arrow
    '\uf020': ' ',       # space (some fonts encode space as PUA)
}

# Common digit super/subscript Unicode
SUPERSCRIPT_DIGITS = {'0': '\u2070', '1': '\u00b9', '2': '\u00b2', '3': '\u00b3',
                      '4': '\u2074', '5': '\u2075', '6': '\u2076', '7': '\u2077',
                      '8': '\u2078', '9': '\u2079',
                      '+': '\u207a', '-': '\u207b', '(': '\u207d', ')': '\u207e',
                      'n': '\u207f', 'i': '\u2071'}
SUBSCRIPT_DIGITS = {'0': '\u2080', '1': '\u2081', '2': '\u2082', '3': '\u2083',
                    '4': '\u2084', '5': '\u2085', '6': '\u2086', '7': '\u2087',
                    '8': '\u2088', '9': '\u2089',
                    '+': '\u208a', '-': '\u208b', '(': '\u208d', ')': '\u208e'}

import argparse
import json
import os
import re
from collections import Counter

import pdfplumber


# ---------------------------------------------------------------------------
# v9: Glyph resolution from page.chars
# ---------------------------------------------------------------------------

def _map_pua_string(s: str) -> str:
    """Apply PUA_MAP character-by-character."""
    if not s:
        return s
    return ''.join(PUA_MAP.get(ch, ch) for ch in s)


def enrich_words_with_glyphs(words: list, page_chars: list) -> list:
    """Re-insert PUA glyphs that `extract_words()` dropped, and convert
    super/subscripts to Unicode. Also tag each word with a dominant fontname
    (used downstream to detect bold subheadings).

    Strategy:
      1. Index page chars by (x0, top) so we can find them fast.
      2. For every word, compute its line-median font size.
      3. Re-scan page chars that fall within the word's bbox:
         - Map PUA codepoints to Unicode via PUA_MAP.
         - Detect super/subscripts by size (< 0.75× median) and vertical
           offset (above or below baseline).
         - Rebuild the word's text from the enriched chars, preserving
           left-to-right order.
         - Record the most common fontname among the word's chars.
    """
    if not words or not page_chars:
        return words

    # Pre-filter chars to speed things up: drop whitespace.
    valid_chars = [c for c in page_chars
                   if c.get('text') and not c['text'].isspace()]

    # Group chars by approximate y-band (tolerance 3 px) so we can find
    # line-median font size cheaply.
    by_y = {}
    for c in valid_chars:
        band = round(c['top'] / 3) * 3
        by_y.setdefault(band, []).append(c)

    def _line_median_size(top):
        # Merge three y-bands to be robust to baseline wobble.
        buckets = []
        for delta in (-3, 0, 3):
            buckets.extend(by_y.get(round(top / 3) * 3 + delta, []))
        sizes = [c.get('size', 0) for c in buckets if c.get('size')]
        if not sizes:
            return 9.0
        sizes.sort()
        return sizes[len(sizes) // 2]

    for w in words:
        wx0, wx1 = float(w['x0']), float(w['x1'])
        wtop, wbottom = float(w['top']), float(w['bottom'])

        # Gather all chars whose center is strictly inside the word's bbox.
        # A too-loose tolerance pulls in chars from adjacent lines; tight
        # containment is safer.
        matched = []
        for c in valid_chars:
            cx = (float(c['x0']) + float(c['x1'])) / 2
            cy = (float(c['top']) + float(c['bottom'])) / 2
            if (wx0 <= cx <= wx1
                    and wtop <= cy <= wbottom):
                matched.append(c)
        if not matched:
            continue
        matched.sort(key=lambda c: float(c['x0']))

        median_size = _line_median_size(wtop)
        # Use the word's own chars' median if it's more reliable.
        own_sizes = sorted(c.get('size', 0) for c in matched if c.get('size'))
        if own_sizes:
            self_med = own_sizes[len(own_sizes) // 2]
            # For short words (< 4 chars), line-median is more reliable.
            median_size = self_med if len(matched) >= 4 else max(median_size, self_med)
            w['size'] = round(float(self_med), 2)
        elif w.get('height'):
            w['size'] = round(float(w['height']), 2)

        # Rebuild the word's text from matched chars with PUA mapping only.
        # Super/subscript detection during this per-char rebuild is fragile
        # (a small digit that belongs to an adjacent word gets pulled in by
        # the bbox overlap and reordered). Instead, we do a targeted regex
        # post-pass on the full text below for safe cases (cm²/cm³/H₂O etc.).
        rebuilt = []
        for c in matched:
            t = c.get('text', '')
            if not t:
                continue
            t = _map_pua_string(t)
            if t:
                rebuilt.append(t)

        # Record dominant fontname (used downstream to detect bold headings).
        fnames = [c.get('fontname') for c in matched if c.get('fontname')]
        if fnames:
            w['fontname'] = Counter(fnames).most_common(1)[0][0]

        new_text = ''.join(rebuilt)
        if not new_text or new_text == w['text']:
            continue
        # Guardrail: rebuild must preserve the ASCII-letter sequence of the
        # original. Otherwise we're likely pulling chars from adjacent words.
        def _letters(s):
            return ''.join(ch for ch in s if ch.isalpha() and ord(ch) < 128)
        if _letters(new_text) != _letters(w['text']):
            continue
        # Require rebuild to ADD at least one non-ASCII char (otherwise it's
        # not useful and could be spurious).
        if not any(ord(ch) > 127 for ch in new_text):
            continue
        w['text'] = new_text

    return words


# ---------------------------------------------------------------------------
# v11: Reattach orphan punctuation from page.chars
# ---------------------------------------------------------------------------
# pdfplumber's extract_words() sometimes splits trailing punctuation (periods,
# commas) from a word when the punctuation is rendered in a different font
# subset (common in italic journal abbreviations like "Front." where the
# period is in the roman font but the word is italic). The period becomes an
# invisible orphan character that doesn't appear in any word.
#
# This function finds period/comma chars that aren't covered by any extracted
# word and attaches them to the immediately preceding word if they are
# spatially adjacent (within 2px gap).

def reattach_orphan_punctuation(words: list, page_chars: list) -> list:
    """Find period/comma chars not covered by any word and attach to the
    preceding word."""
    if not words or not page_chars:
        return words

    # Collect all punctuation chars (periods, commas) from page_chars
    punct_chars = [c for c in page_chars
                   if c.get('text') in ('.', ',')
                   and not c['text'].isspace()]
    if not punct_chars:
        return words

    # For each punct char, check if it falls inside any word's bbox
    def _inside_word(pc, w):
        cx = (float(pc['x0']) + float(pc['x1'])) / 2
        cy = (float(pc['top']) + float(pc['bottom'])) / 2
        return (float(w['x0']) - 1 <= cx <= float(w['x1']) + 1
                and float(w['top']) - 2 <= cy <= float(w['bottom']) + 2)

    orphans = []
    for pc in punct_chars:
        covered = any(_inside_word(pc, w) for w in words)
        if not covered:
            orphans.append(pc)

    if not orphans:
        return words

    # Sort words by (top, x0) for spatial matching
    sorted_words = sorted(words, key=lambda w: (float(w['top']), float(w['x0'])))

    for pc in orphans:
        pc_x0 = float(pc['x0'])
        pc_top = float(pc['top'])
        pc_bottom = float(pc['bottom'])
        pc_text = pc['text']

        # Find the nearest preceding word on the same line
        best_word = None
        best_gap = float('inf')
        for w in sorted_words:
            w_x1 = float(w['x1'])
            w_top = float(w['top'])
            w_bottom = float(w['bottom'])
            # Must be on the same line (vertical overlap)
            y_overlap = min(pc_bottom, w_bottom) - max(pc_top, w_top)
            if y_overlap <= 0:
                continue
            # Punctuation must be immediately after the word (gap < 2px)
            gap = pc_x0 - w_x1
            if 0 <= gap <= 2.0 and gap < best_gap:
                # Also verify the word doesn't already end with this punctuation
                if not w['text'].endswith(pc_text):
                    best_word = w
                    best_gap = gap

        if best_word is not None:
            best_word['text'] = best_word['text'] + pc_text
            best_word['x1'] = max(float(best_word['x1']),
                                  float(pc['x1']))

    return words


# ---------------------------------------------------------------------------
# Targeted super/subscript post-substitution on extracted text units
# ---------------------------------------------------------------------------
# Applied after word extraction. Only substitutes in unambiguous scientific-
# unit patterns (cm²/cm³, mm²/mm³, H₂O, CO₂) so author-name affiliations and
# other digits are left alone.

_SUPERSCRIPT_SAFE_PATTERNS = [
    # Area / volume units
    (re.compile(r'\b(cm|mm|km|nm|µm|μm|m)([23])\b'),
     lambda m: m.group(1) + SUPERSCRIPT_DIGITS[m.group(2)]),
    # Nanogram per mg^2 style typically stays 2D; skip
]

_SUBSCRIPT_SAFE_PATTERNS = [
    (re.compile(r'\bH([23])O\b'),
     lambda m: 'H' + SUBSCRIPT_DIGITS[m.group(1)] + 'O'),
    (re.compile(r'\bCO([23])\b'),
     lambda m: 'CO' + SUBSCRIPT_DIGITS[m.group(1)]),
    (re.compile(r'\bN([23])\b(?=\s+[A-Za-z])'),
     lambda m: 'N' + SUBSCRIPT_DIGITS[m.group(1)]),
]


def apply_superscript_subscript_substitutions(text: str) -> str:
    """Safe regex-based super/subscript fixes for common scientific units."""
    if not text:
        return text
    for pattern, sub in _SUPERSCRIPT_SAFE_PATTERNS:
        text = pattern.sub(sub, text)
    for pattern, sub in _SUBSCRIPT_SAFE_PATTERNS:
        text = pattern.sub(sub, text)
    return text


# ---------------------------------------------------------------------------
# PDF-ToUnicode-CMap error correction
# ---------------------------------------------------------------------------
# Some PDFs silently lose diacritics via broken ToUnicode CMap entries.
# This is not recoverable from per-char metadata. We keep the mechanism
# but leave the list empty — downstream LLM agents can fix these using
# contextual knowledge of the paper's reference list.
_TOUNICODE_SURNAME_FIXES = []


def apply_tounicode_surname_fixes(text: str) -> str:
    """Restore diacritics that the PDF's ToUnicode CMap silently dropped."""
    if not text or not _TOUNICODE_SURNAME_FIXES:
        return text
    for pattern, repl in _TOUNICODE_SURNAME_FIXES:
        text = pattern.sub(repl, text)
    return text


# ---------------------------------------------------------------------------
# Sidebar / watermark detection (unchanged from v5)
# ---------------------------------------------------------------------------

def detect_sidebar_filter(all_words: list, page_width: float) -> int:
    """Detect publisher sidebar/watermark text at the right edge."""
    far_right = [w for w in all_words if w["x0"] > page_width * 0.93
                 and (w["x1"] - w["x0"]) < 15]
    if len(far_right) > 10:
        x0_buckets = Counter(int(w["x0"]) for w in far_right)
        most_common_x0, count = x0_buckets.most_common(1)[0]
        if count > 5:
            return int(most_common_x0 - 5)
    return int(page_width)


# ---------------------------------------------------------------------------
# Line grouping (unchanged from v5)
# ---------------------------------------------------------------------------

def detect_gutters(all_words: list, page_width: float) -> list:
    """Find persistent vertical column gutters from word positions.

    Uses two complementary strategies:

    1. **Valley detection** (best for non-concatenated text): builds a
       fine-grained x0 histogram and finds valleys where very few words
       start.

    2. **Peak clustering** (best for concatenated text): finds dominant
       x0 peaks (column left-margins) and places gutters in the gaps
       between clusters.

    Returns a list of gutter x-coordinates.
    """
    if len(all_words) < 40:
        return []

    bucket = 5
    n_buckets = int(page_width / bucket) + 1
    hist = [0] * n_buckets

    for w in all_words:
        idx = min(int(w["x0"] / bucket), n_buckets - 1)
        hist[idx] += 1

    margin_buckets = max(3, int(page_width * 0.05 / bucket))

    # --- Strategy 1: Valley detection ---
    gutters = _detect_gutters_valley(hist, n_buckets, margin_buckets,
                                     bucket, page_width)
    if gutters:
        return gutters

    # --- Strategy 2: Peak clustering ---
    gutters = _detect_gutters_peaks(all_words, page_width)

    # Filter out gutters too close to the page edges (< 15% from either side)
    min_x = page_width * 0.15
    max_x = page_width * 0.85
    gutters = [g for g in gutters if min_x < g < max_x]

    return gutters


def _detect_gutters_valley(hist, n_buckets, margin_buckets, bucket, page_width):
    """Valley-based gutter detection (for non-concatenated text)."""
    interior = hist[margin_buckets:n_buckets - margin_buckets]
    if not interior or max(interior) < 5:
        return []

    hw = 10  # half-window in buckets (50px)
    baseline = [0.0] * n_buckets
    for i in range(hw, n_buckets - hw):
        window = hist[i - hw:i + hw + 1]
        baseline[i] = sorted(window)[len(window) // 2]

    min_baseline = max(interior) * 0.15

    gutters = []
    in_valley = False
    valley_start = 0

    for i in range(margin_buckets, n_buckets - margin_buckets):
        is_valley = (baseline[i] > min_baseline and
                     hist[i] < baseline[i] * 0.25)
        if is_valley:
            if not in_valley:
                in_valley = True
                valley_start = i
        else:
            if in_valley:
                valley_end = i
                valley_width_px = (valley_end - valley_start) * bucket
                if valley_width_px >= 5:
                    left_max = max(hist[max(0, valley_start - 4):valley_start]) if valley_start > 0 else 0
                    right_max = max(hist[valley_end:min(n_buckets, valley_end + 4)]) if valley_end < n_buckets else 0
                    if left_max > min_baseline and right_max > min_baseline:
                        center = (valley_start + valley_end) / 2.0 * bucket
                        gutters.append(center)
                in_valley = False

    return gutters


def _detect_gutters_peaks(all_words, page_width):
    """Peak-clustering gutter detection (for concatenated text)."""
    total = len(all_words)
    bucket = 3
    x0_counts = Counter(int(w["x0"] / bucket) * bucket for w in all_words)

    # Collect peaks above low threshold (>= 1% of total)
    min_peak = max(total * 0.01, 5)
    peaks = [(x, cnt) for x, cnt in x0_counts.items() if cnt >= min_peak]
    if len(peaks) < 2:
        return []

    # Merge nearby peaks (within 15px)
    peaks.sort(key=lambda p: p[0])
    clusters = []
    cur_xs = [peaks[0][0]]
    cur_cnts = [peaks[0][1]]

    for x, cnt in peaks[1:]:
        if x - cur_xs[-1] <= 15:
            cur_xs.append(x)
            cur_cnts.append(cnt)
        else:
            total_cnt = sum(cur_cnts)
            center = sum(x * c for x, c in zip(cur_xs, cur_cnts)) / total_cnt
            clusters.append((center, total_cnt))
            cur_xs = [x]
            cur_cnts = [cnt]

    total_cnt = sum(cur_cnts)
    center = sum(x * c for x, c in zip(cur_xs, cur_cnts)) / total_cnt
    clusters.append((center, total_cnt))

    if len(clusters) < 2:
        return []

    # Keep significant clusters (>= 3% of total)
    sig = [(x, cnt) for x, cnt in clusters if cnt >= total * 0.03]
    if len(sig) < 2:
        return []

    sig.sort(key=lambda c: c[0])

    # Place gutters between adjacent clusters that are far apart
    gutters = []
    x1_counts = Counter(int(w["x1"] / bucket) * bucket for w in all_words)

    for i in range(len(sig) - 1):
        left_margin = sig[i][0]
        right_margin = sig[i + 1][0]

        if right_margin - left_margin < 30:
            continue

        # Find the right-edge peak between the two margins
        search_lo = int(left_margin + (right_margin - left_margin) * 0.3)
        search_hi = int(right_margin)
        best_x1 = 0
        best_x1_cnt = 0
        for x in range(search_lo, search_hi, bucket):
            cnt = x1_counts.get(x, 0)
            if cnt > best_x1_cnt:
                best_x1_cnt = cnt
                best_x1 = x

        if best_x1 > 0 and best_x1_cnt >= 3:
            gutter = (best_x1 + right_margin) / 2.0
        else:
            gutter = (left_margin + right_margin) / 2.0

        gutters.append(gutter)

    return gutters


def group_into_lines(words: list, tol: float = 4.0) -> list:
    """Group words into lines by approximate y-coordinate.

    Returns a list of lines.  Each line is a list of word dicts sorted by x0.
    NOTE: Does NOT split lines at column gutters.  Call split_lines_at_gutters
    separately after gutter detection.

    Tolerance is bounded so that the running line span stays below tol.

    Post-pass: reassign any word that is spatially discontiguous from its
    assigned line — i.e., its x-position sits way past the rest of the
    line's x-range AND it is as close in y to a neighboring line. This
    catches wrap-artifact units like "cells/cm³," that get pulled into a
    nearby caption line by the chain heuristic but actually belong to a
    following body line whose x-range they continue.
    """
    if not words:
        return []
    sorted_w = sorted(words, key=lambda w: (w["top"], w["x0"]))
    lines = []
    cur = [sorted_w[0]]
    cur_min_top = sorted_w[0]["top"]
    cur_max_top = sorted_w[0]["top"]

    for w in sorted_w[1:]:
        wt = w["top"]
        new_span = max(cur_max_top, wt) - min(cur_min_top, wt)
        if new_span < tol:
            cur.append(w)
            cur_min_top = min(cur_min_top, wt)
            cur_max_top = max(cur_max_top, wt)
        else:
            cur.sort(key=lambda w2: w2["x0"])
            lines.append(cur)
            cur = [w]
            cur_min_top = wt
            cur_max_top = wt
    cur.sort(key=lambda w2: w2["x0"])
    lines.append(cur)

    # --- Post-pass: rescue spatially discontiguous trailing words ---
    # For each line, check whether its RIGHTMOST word is far to the right
    # of the rest of the line AND the rest of the line's x-range is clearly
    # separate. If so, and a neighboring line's x-range is near-adjacent to
    # the trailing word, move it.
    if len(lines) < 2:
        return lines

    idx_by_y = sorted(range(len(lines)),
                      key=lambda i: min(w["top"] for w in lines[i]))

    def _x_range_without(line, exclude_word):
        others = [w for w in line if w is not exclude_word]
        if not others:
            return None
        return (min(w["x0"] for w in others),
                max(w["x1"] for w in others))

    # Simple single-pass rescue.
    moves = []  # (src_line_idx, word, dst_line_idx)
    for pos, i in enumerate(idx_by_y):
        line = lines[i]
        if len(line) < 2:
            continue
        # Look at the rightmost word.
        rightmost = max(line, key=lambda w: w["x0"])
        remainder = _x_range_without(line, rightmost)
        if remainder is None:
            continue
        rem_x0, rem_x1 = remainder
        gap_to_rest = rightmost["x0"] - rem_x1
        # Only a significantly-detached trailing word is a candidate (>25px
        # clear separation from the main line body, to leave normal prose
        # untouched).
        if gap_to_rest < 25.0:
            continue
        wy = rightmost["top"]
        # Check both y-neighbors.
        for nb_pos in (pos - 1, pos + 1):
            if nb_pos < 0 or nb_pos >= len(idx_by_y):
                continue
            nb_i = idx_by_y[nb_pos]
            nb_line = lines[nb_i]
            nb_x0 = min(w["x0"] for w in nb_line)
            nb_x1 = max(w["x1"] for w in nb_line)
            nb_top_min = min(w["top"] for w in nb_line)
            nb_top_max = max(w["top"] for w in nb_line)
            y_dist = min(abs(wy - nb_top_min), abs(wy - nb_top_max))
            # Must be within tol * 1.5 in y, and the trailing word's x must
            # be within 6px of the neighbor's right edge (natural trailing
            # position).
            if y_dist > tol * 1.5:
                continue
            if abs(rightmost["x0"] - nb_x1) > 6.0:
                continue
            moves.append((i, rightmost, nb_i))
            break

    if not moves:
        return lines

    for src_i, word, dst_i in moves:
        if word in lines[src_i]:
            lines[src_i] = [w for w in lines[src_i] if w is not word]
        lines[dst_i].append(word)
        lines[dst_i].sort(key=lambda w: w["x0"])

    return [l for l in lines if l]


def split_lines_at_gutters(lines: list, gutters: list) -> list:
    """Split lines at detected column gutters.

    For each gutter, check whether a line has an actual inter-word gap near
    that gutter position.  If yes, split the line there.  If no (the line
    has continuous text across the gutter, e.g. a full-width title), leave
    it intact.  This naturally handles mixed layouts.
    """
    if not gutters:
        return lines

    result = lines
    for gutter_x in sorted(gutters):
        new_result = []
        for line in result:
            parts = _split_line_at_one_gutter(line, gutter_x)
            new_result.extend(parts)
        result = new_result
    return result


def _split_line_at_one_gutter(line: list, gutter_x: float) -> list:
    """Split a single line at one gutter position if there's a real gap.

    A split only happens if the gutter falls WITHIN (or very close to) an
    inter-word gap, AND that gap is wider than typical word spacing.
    """
    if len(line) < 2:
        return [line]

    line_x0 = line[0]["x0"]
    line_x1 = line[-1]["x1"]

    # Does this line span the gutter?
    if line_x0 >= gutter_x or line_x1 <= gutter_x:
        return [line]

    # Compute all inter-word gaps and find median
    all_gaps = []
    for i in range(len(line) - 1):
        g = line[i + 1]["x0"] - line[i]["x1"]
        if g > 0:
            all_gaps.append(g)

    median_gap = sorted(all_gaps)[len(all_gaps) // 2] if all_gaps else 0

    # Find the best gap that contains or is very near the gutter
    MARGIN = 15  # gutter can be up to 15px outside the gap edges
    best_split = None
    best_gap_width = -1

    for i in range(len(line) - 1):
        gap_left = line[i]["x1"]
        gap_right = line[i + 1]["x0"]
        gap_width = gap_right - gap_left

        if gap_width < 3:
            continue

        # Does the gutter fall within (or very near) this gap?
        if not (gap_left - MARGIN <= gutter_x <= gap_right + MARGIN):
            continue

        # The gap must be wider than typical word spacing
        if len(all_gaps) > 1:
            if gap_width < median_gap * 2.0 and gap_width < 10:
                continue
        else:
            # Single gap in line — use absolute threshold
            if gap_width < 8:
                continue

        # Among multiple candidates, prefer the widest gap
        if gap_width > best_gap_width:
            best_gap_width = gap_width
            best_split = i + 1

    if best_split is not None:
        return [line[:best_split], line[best_split:]]
    return [line]


def split_lines_at_large_gaps(lines: list, min_absolute: float = 20,
                              min_ratio: float = 4.0) -> list:
    """Split lines at anomalously large inter-word gaps.

    After gutter-based splitting, some lines may still contain words from
    different page regions that happen to share the same y-coordinate (e.g.,
    a full-width title line at y=82 and copyright sidebar text at y=83).
    Gutter splitting won't catch these if the gap doesn't align with any
    detected gutter.

    This function finds inter-word gaps that are far larger than the line's
    typical word spacing and splits the line there.  This naturally handles
    publisher sidebars, margin notes, and any text that spatially doesn't
    belong to the adjacent words on the same y-band.

    Parameters:
        min_absolute: Minimum absolute gap (px) to consider a split.
        min_ratio: Minimum ratio of gap to median gap to consider a split.
    """
    result = []
    for line in lines:
        result.extend(_split_line_large_gaps(line, min_absolute, min_ratio))
    return result


def _split_line_large_gaps(line: list, min_absolute: float = 20,
                           min_ratio: float = 4.0) -> list:
    """Split one line at any anomalously large gap."""
    if len(line) < 2:
        return [line]

    # Compute all inter-word gaps
    gaps = []
    for i in range(len(line) - 1):
        g = line[i + 1]["x0"] - line[i]["x1"]
        gaps.append((i, g))

    positive_gaps = [g for _, g in gaps if g > 0]
    if not positive_gaps:
        return [line]

    median_gap = sorted(positive_gaps)[len(positive_gaps) // 2]

    split_indices = []
    for i, g in gaps:
        if g >= min_absolute and (median_gap < 1.0 or g >= median_gap * min_ratio):
            split_indices.append(i + 1)

    if not split_indices:
        return [line]

    # Split the line at all identified points
    parts = []
    prev = 0
    for idx in split_indices:
        parts.append(line[prev:idx])
        prev = idx
    parts.append(line[prev:])

    return [p for p in parts if p]


# ---------------------------------------------------------------------------
# Column-aware line grouping (Bug 2 fix: prevents cross-column merging)
# ---------------------------------------------------------------------------

def group_into_lines_column_aware(words: list, gutters: list,
                                  tol: float = 4.0) -> list:
    """Column-aware line grouping that prevents cross-column text merging.

    BUG FIX: The old approach grouped ALL words at the same y-coordinate
    into one line, then tried to split at column gutters.  This failed
    when a full-width element (figure caption) and narrow-column body text
    coexisted at the same y-level -- the caption's continuous text across
    the gutter prevented the split, so body text got merged into the
    caption line.

    New approach:
      1. Partition words into column zones using detected gutters (by x0).
      2. Within each zone, group words into lines by y-proximity.
      3. Within each zone, split lines at large gaps (using tighter
         thresholds than the page-level splitter, since intra-column gaps
         are smaller).  This separates caption-continuation fragments from
         body text fragments that happen to share the same zone + y.
      4. Across adjacent zones, merge lines at the same y that have a small
         inter-word gap (< MERGE_GAP_THRESHOLD), reconstructing genuine
         full-width text (titles, abstracts, captions).

    This replaces the old group_into_lines() + split_lines_at_gutters() +
    split_lines_at_large_gaps() three-step pipeline.
    """
    if not gutters:
        # No gutters = single-column document; use original logic
        lines = group_into_lines(words, tol)
        return split_lines_at_large_gaps(lines)

    sorted_gutters = sorted(gutters)
    n_zones = len(sorted_gutters) + 1

    # ------------------------------------------------------------------
    # Step 1: Assign each word to a column zone based on x0
    # ------------------------------------------------------------------
    zone_words: dict[int, list] = {}
    for w in words:
        zone = 0
        for g in sorted_gutters:
            if w["x0"] >= g:
                zone += 1
        zone_words.setdefault(zone, []).append(w)

    # ------------------------------------------------------------------
    # Step 2 + 3: Per-zone line assembly + intra-zone large-gap splitting
    # Use tighter thresholds (12px, 3x) than the page-level splitter
    # (20px, 4x) because within a single column, legitimate word gaps
    # are smaller, so we can detect smaller anomalous gaps.
    # ------------------------------------------------------------------
    ZONE_GAP_ABSOLUTE = 10   # px  (page-level: 20)
    ZONE_GAP_RATIO = 3.0     #     (page-level: 4.0)
    # v11 tuning: lowered from 12 → 10 so a caption fragment ending at the
    # gutter edge (e.g. "SMA" at x=396) + body text starting just past the
    # gutter ("was" at x=408, gap=11.98) actually gets split apart.
    # 11.98 < 12 previously let them be fused into one line, causing body
    # prose to leak into figure captions.

    zone_lines: dict[int, list] = {}
    for z in range(n_zones):
        zw = zone_words.get(z, [])
        if zw:
            raw = group_into_lines(zw, tol)
            zone_lines[z] = split_lines_at_large_gaps(
                raw, min_absolute=ZONE_GAP_ABSOLUTE, min_ratio=ZONE_GAP_RATIO)
        else:
            zone_lines[z] = []

    # ------------------------------------------------------------------
    # Step 4: Cross-zone merging for genuine full-width text
    #
    # For each gutter boundary, look for line pairs (left-zone line,
    # right-zone line) at the same y.  If the gap between the last word
    # of the left line and the first word of the right line is small
    # (consistent with normal word spacing), merge them into a single
    # full-width line.
    #
    # The merge threshold is computed DYNAMICALLY from the actual column
    # gap in the document (median right-zone x0 minus median left-zone
    # x1).  We merge only when the gap is less than half the typical
    # column gap (min 5px).  This correctly handles narrow gutters
    # (e.g., 12px) that a fixed threshold would miss.
    # ------------------------------------------------------------------
    merged_ids: set = set()      # id() of lines consumed by merging
    extra_merged: list = []      # newly created merged lines

    for gz_idx in range(len(sorted_gutters)):
        left_z = gz_idx
        right_z = gz_idx + 1

        # --- Dynamic merge threshold from actual column geometry ---
        left_ends = [max(w["x1"] for w in line)
                     for line in zone_lines[left_z] if line]
        right_starts = [min(w["x0"] for w in line)
                        for line in zone_lines[right_z] if line]

        if left_ends and right_starts:
            typical_left_end = sorted(left_ends)[len(left_ends) // 2]
            typical_right_start = sorted(right_starts)[len(right_starts) // 2]
            typical_col_gap = typical_right_start - typical_left_end
            # CAP the threshold at 8px. Rationale: legitimate full-width text
            # (titles, abstracts, single-line captions) has word gaps of
            # 2-5px; anything beyond ~8px is a column separator, not natural
            # word spacing. Previously we capped at 15px, but that merged
            # genuine two-column body text where the inter-column gap was
            # 12px (e.g. page 3 lines had "...fatigue" at x1=291 and "racic"
            # at x0=303, gap=12) into a single line containing words from
            # both columns — producing spliced prose in downstream assembly.
            # Two-column bodies in modern typesetting have gaps of 10-30px;
            # dropping the cap to 8px excludes those unambiguously.
            merge_threshold = max(min(typical_col_gap * 0.5, 8.0), 4.0)
        else:
            typical_left_end = 0
            typical_right_start = 0
            typical_col_gap = 0
            merge_threshold = 6.0

        # --- Build y-index for both zones (quantized by tolerance) ---
        def _y_key(line):
            return round(min(w["top"] for w in line) / tol)

        left_by_y: dict[int, list] = {}
        for line in zone_lines[left_z]:
            if id(line) not in merged_ids:
                left_by_y.setdefault(_y_key(line), []).append(line)
        # Also consider previously merged lines whose right extent may
        # reach into this zone (needed for 3+ column cascading)
        for line in extra_merged:
            if id(line) not in merged_ids:
                left_by_y.setdefault(_y_key(line), []).append(line)

        right_by_y: dict[int, list] = {}
        for line in zone_lines[right_z]:
            if id(line) not in merged_ids:
                right_by_y.setdefault(_y_key(line), []).append(line)

        for yk, left_list in left_by_y.items():
            # Check exact and adjacent y-keys (tolerance overlap)
            for yk_r in [yk - 1, yk, yk + 1]:
                right_list = right_by_y.get(yk_r, [])
                if not right_list:
                    continue

                for l_line in left_list:
                    if id(l_line) in merged_ids:
                        continue
                    l_top = min(w["top"] for w in l_line)
                    l_last_x1 = max(w["x1"] for w in l_line)

                    best_r = None
                    best_gap = float('inf')

                    for r_line in right_list:
                        if id(r_line) in merged_ids:
                            continue
                        r_top = min(w["top"] for w in r_line)

                        # Actual y must be close
                        if abs(l_top - r_top) > tol:
                            continue

                        r_first_x0 = min(w["x0"] for w in r_line)
                        gap = r_first_x0 - l_last_x1

                        # Merge if gap is within word-spacing range
                        # (negative gaps = overlapping/continuous text)
                        if gap < merge_threshold and gap < best_gap:
                            best_r = r_line
                            best_gap = gap

                    if best_r is not None:
                        new_line = list(l_line) + list(best_r)
                        new_line.sort(key=lambda w: w["x0"])
                        merged_ids.add(id(l_line))
                        merged_ids.add(id(best_r))
                        extra_merged.append(new_line)

    # ------------------------------------------------------------------
    # Collect all lines: unmerged zone lines + newly merged full-width lines
    # ------------------------------------------------------------------
    all_lines = []
    for z in range(n_zones):
        for line in zone_lines[z]:
            if id(line) not in merged_ids:
                all_lines.append(line)
    for line in extra_merged:
        # extra_merged lines that were consumed by a later cascade merge
        # are already in merged_ids; skip them
        if id(line) not in merged_ids:
            all_lines.append(line)

    return all_lines


# ---------------------------------------------------------------------------
# Line annotation helpers
# ---------------------------------------------------------------------------

def annotate_line(words: list) -> dict:
    """Compute bounding-box metadata for a line of words."""
    x0 = min(w["x0"] for w in words)
    x1 = max(w["x1"] for w in words)
    top = min(w["top"] for w in words)
    bottom = max(w["bottom"] for w in words)
    return {
        "x0": x0, "x1": x1, "top": top, "bottom": bottom,
        "width": x1 - x0,
        "center_x": (x0 + x1) / 2.0,
        "words": words,
    }


# ---------------------------------------------------------------------------
# Union-Find (Disjoint Set)
# ---------------------------------------------------------------------------

class UnionFind:
    """Simple union-find with path compression and union by rank."""

    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, i: int) -> int:
        while self.parent[i] != i:
            self.parent[i] = self.parent[self.parent[i]]
            i = self.parent[i]
        return i

    def union(self, i: int, j: int):
        ri, rj = self.find(i), self.find(j)
        if ri == rj:
            return
        if self.rank[ri] < self.rank[rj]:
            ri, rj = rj, ri
        self.parent[rj] = ri
        if self.rank[ri] == self.rank[rj]:
            self.rank[ri] += 1


# ---------------------------------------------------------------------------
# Text-block detection via spatial clustering
# ---------------------------------------------------------------------------

def find_text_blocks(annotated_lines: list, page_width: float) -> list:
    """Cluster annotated lines into text blocks.

    Two lines are in the same block if:
      - They are vertically close  (y-gap < vertical_threshold)
      - They are horizontally aligned (mutual overlap > 50% of the
        narrower line's width)

    The mutual-overlap criterion means that a full-width abstract line will
    NOT bridge two narrow body-text columns below it, because the overlap
    with each narrow column is < 50% of the wide line's width.

    Returns a list of blocks.  Each block is a list of annotated lines
    sorted by y-position.
    """
    n = len(annotated_lines)
    if n == 0:
        return []

    # Compute adaptive vertical threshold based on actual inter-line gaps
    # (bottom of line i to top of line j), not top-to-top spacing.
    # This handles mixed font sizes (e.g. 18pt title above 9pt body).
    sorted_by_y = sorted(annotated_lines, key=lambda a: a["top"])
    true_gaps = []
    for i in range(1, len(sorted_by_y)):
        gap = sorted_by_y[i]["top"] - sorted_by_y[i - 1]["bottom"]
        if 0 < gap < 30:
            true_gaps.append(gap)
    if true_gaps:
        median_gap = sorted(true_gaps)[len(true_gaps) // 2]
        vert_threshold = max(median_gap * 3.0, 15.0)
    else:
        vert_threshold = 20.0

    uf = UnionFind(n)

    # Build index sorted by y for efficient neighbor search
    idx_by_y = sorted(range(n), key=lambda i: annotated_lines[i]["top"])

    for a_pos in range(len(idx_by_y)):
        i = idx_by_y[a_pos]
        ai = annotated_lines[i]

        for b_pos in range(a_pos + 1, len(idx_by_y)):
            j = idx_by_y[b_pos]
            aj = annotated_lines[j]

            # Use actual gap (bottom-to-top), not top-to-top spacing
            y_gap = aj["top"] - ai["bottom"]
            if y_gap > vert_threshold:
                break  # no more candidates

            # Horizontal overlap check
            overlap = min(ai["x1"], aj["x1"]) - max(ai["x0"], aj["x0"])
            if overlap <= 0:
                continue

            w_narrow = min(ai["width"], aj["width"])
            w_wide = max(ai["width"], aj["width"])

            if w_narrow < 1:
                continue

            # Both ratios must exceed threshold
            ratio_narrow = overlap / w_narrow  # always <= 1.0
            ratio_wide = overlap / w_wide

            # Bug 1 fix: containment-based merging for paragraph-final
            # short lines.  A short line at the end of a paragraph is
            # much narrower than the preceding full-width lines (e.g.,
            # "tube design." is only ~48px vs ~255px column width).
            # The standard ratio_wide threshold (0.45) rejects it because
            # 48/255 = 0.19.  But the short line is geometrically
            # CONTAINED within the wide line's x-range -- it shares the
            # same left margin and its right edge doesn't exceed the
            # wide line's right edge.  This is a reliable signal that
            # the short line belongs to the same text block (paragraph
            # continuation, centered title, etc.).
            #
            # Containment check: the narrow line's [x0, x1] is a subset
            # of the wide line's [x0, x1] (with 5px tolerance for
            # rounding / slight misalignment).
            if ai["width"] <= aj["width"]:
                narrow_line, wide_line = ai, aj
            else:
                narrow_line, wide_line = aj, ai
            contained = (narrow_line["x0"] >= wide_line["x0"] - 5 and
                         narrow_line["x1"] <= wide_line["x1"] + 5)

            if ratio_narrow > 0.3 and (ratio_wide > 0.45 or contained):
                uf.union(i, j)

    # Collect blocks
    blocks_map: dict[int, list] = {}
    for i in range(n):
        root = uf.find(i)
        blocks_map.setdefault(root, []).append(annotated_lines[i])

    # Sort lines within each block by y, tie-breaking by x0 so two lines at
    # the same y (e.g. a bare "µm" glyph floating at the same baseline as the
    # main caption line) render in geometric reading order. Without the x0
    # tie-break, a stray small fragment could get emitted BEFORE the main-line
    # text that precedes it in the same baseline — producing splices like
    # "SMA µm stain in (E)..." where "µm" belonged after "0.5" further right.
    blocks = []
    for lines in blocks_map.values():
        lines.sort(key=lambda a: (a["top"], a["x0"]))
        blocks.append(lines)

    return blocks


def split_blocks_at_gutters(blocks: list, gutters: list) -> list:
    """Post-process blocks: split any block that spans across a detected gutter.

    When the block-clustering union-find merges lines from different columns
    (because a full-width header or caption bridges them), the resulting block
    contains interleaved lines from multiple columns. This function detects
    such blocks and splits them at the gutter boundaries.

    For each gutter, if a block's x-range spans both sides of the gutter AND
    it has lines predominantly on each side, split it into separate blocks.
    """
    if not gutters or not blocks:
        return blocks

    result = blocks
    for gutter_x in sorted(gutters):
        new_result = []
        for block_lines in result:
            split = _split_block_at_gutter(block_lines, gutter_x)
            new_result.extend(split)
        result = new_result
    return result


def _split_block_at_gutter(block_lines: list, gutter_x: float) -> list:
    """Split a single block at a gutter if it spans both sides.

    A line is assigned to the left or right column based on its center_x
    relative to the gutter. Lines whose center is within 10px of the gutter
    are assigned based on where most of their text mass lies.
    """
    if len(block_lines) < 2:
        return [block_lines]

    # Check if block spans the gutter
    block_x0 = min(a["x0"] for a in block_lines)
    block_x1 = max(a["x1"] for a in block_lines)

    if block_x1 <= gutter_x + 10 or block_x0 >= gutter_x - 10:
        return [block_lines]  # Block doesn't span the gutter

    # Classify each line as left, right, or spanning
    left_lines = []
    right_lines = []
    spanning_lines = []

    for aline in block_lines:
        cx = aline["center_x"]
        line_x0 = aline["x0"]
        line_x1 = aline["x1"]

        # Line is entirely on one side
        if line_x1 <= gutter_x + 5:
            left_lines.append(aline)
        elif line_x0 >= gutter_x - 5:
            right_lines.append(aline)
        else:
            # Line spans the gutter -- check where the text mass lies
            # If most words are on one side, assign to that side
            left_words = [w for w in aline["words"] if w["x1"] <= gutter_x + 5]
            right_words = [w for w in aline["words"] if w["x0"] >= gutter_x - 5]
            if left_words and not right_words:
                left_lines.append(aline)
            elif right_words and not left_words:
                right_lines.append(aline)
            else:
                spanning_lines.append(aline)

    # Need at least 3 lines on each side to justify a split
    if len(left_lines) < 3 or len(right_lines) < 3:
        return [block_lines]

    # For spanning lines, split them at the gutter into left and right halves
    for aline in spanning_lines:
        left_words = [w for w in aline["words"] if w["x1"] <= gutter_x + 10]
        right_words = [w for w in aline["words"] if w["x0"] >= gutter_x - 10]
        # Words that straddle the gutter go to whichever side has more of the word
        for w in aline["words"]:
            if w["x1"] > gutter_x + 10 and w["x0"] < gutter_x - 10:
                mid = (w["x0"] + w["x1"]) / 2
                if mid < gutter_x:
                    left_words.append(w)
                else:
                    right_words.append(w)
        if left_words:
            left_lines.append(annotate_line(left_words))
        if right_words:
            right_lines.append(annotate_line(right_words))

    # Sort each column's lines by y-position
    left_lines.sort(key=lambda a: (a["top"], a["x0"]))
    right_lines.sort(key=lambda a: (a["top"], a["x0"]))

    result = []
    if left_lines:
        result.append(left_lines)
    if right_lines:
        result.append(right_lines)

    return result if result else [block_lines]


# ---------------------------------------------------------------------------
# Candidate reading-order construction
# ---------------------------------------------------------------------------

def order_blocks_by_candidate_reading(blocks: list) -> list:
    """Sort text blocks into a coarse reading-order candidate.

    Strategy: sort by the block's starting y-position.  For blocks whose
    y-ranges overlap significantly, sort left-to-right.  This handles
    side-by-side columns correctly: the left column block reads before the
    right column block.
    """
    if not blocks:
        return []

    # Compute block bounding boxes
    block_info = []
    for block in blocks:
        y_min = block[0]["top"]
        y_max = block[-1]["top"]
        x_min = min(a["x0"] for a in block)
        x_max = max(a["x1"] for a in block)
        block_info.append({
            "block": block,
            "y_min": y_min, "y_max": y_max,
            "x_min": x_min, "x_max": x_max,
            "y_mid": (y_min + y_max) / 2.0,
        })

    # Sort: primary by y_min, secondary by x_min for overlapping blocks
    # Two blocks "overlap vertically" if neither ends before the other starts
    # Use a simple approach: sort by (y_min, x_min)
    # This naturally puts the top-left block first, then top-right, etc.
    # For true column detection, we group blocks with overlapping y-ranges.

    # Step 1: group blocks into "rows" where y-ranges overlap
    sorted_blocks = sorted(block_info, key=lambda b: b["y_min"])
    rows = []
    current_row = [sorted_blocks[0]]
    row_y_max = sorted_blocks[0]["y_max"]

    for bi in sorted_blocks[1:]:
        # Does this block overlap with the current row's y-range?
        # Overlap means: the block starts before the row ends AND
        # has substantial vertical overlap
        row_y_min = min(b["y_min"] for b in current_row)
        row_height = row_y_max - row_y_min
        bi_height = bi["y_max"] - bi["y_min"]

        overlap_top = max(row_y_min, bi["y_min"])
        overlap_bottom = min(row_y_max, bi["y_max"])
        overlap_amount = max(0, overlap_bottom - overlap_top)

        # Blocks are in the same "row" if they overlap > 40% of the
        # shorter block's height
        min_height = min(row_height, bi_height) if min(row_height, bi_height) > 0 else 1
        if overlap_amount / min_height > 0.4:
            current_row.append(bi)
            row_y_max = max(row_y_max, bi["y_max"])
        else:
            rows.append(current_row)
            current_row = [bi]
            row_y_max = bi["y_max"]
    rows.append(current_row)

    # Step 2: within each row, sort blocks left-to-right. Then, within the
    # row, group adjacent blocks that belong to the SAME column (their
    # centers are close in x) and sort those by y_min. This fixes cases
    # like page 14 of Syedain-2021 where a full-height left-column block
    # pulled two right-column blocks (refs-tail y=64..586 and
    # Acknowledgments-head y=618..701) into one row; without the secondary
    # y-sort they were emitted in x-order (~303 vs ~305), producing
    # refs 18-36 AFTER the Acknowledgments instead of BEFORE.
    ordered = []
    for row in rows:
        row.sort(key=lambda b: b["x_min"])
        # Split row into horizontal column groups using block x-centers:
        # two blocks are in the same column if their centers are within a
        # small fraction of each block's width of each other. Using center
        # distance (not just x-range overlap) is robust to full-width
        # captions that extend past a gutter and spuriously overlap the
        # opposite column.
        col_groups = []
        current_col = [row[0]]
        for b in row[1:]:
            prev = current_col[-1]
            prev_center = (prev["x_min"] + prev["x_max"]) / 2.0
            b_center = (b["x_min"] + b["x_max"]) / 2.0
            prev_width = prev["x_max"] - prev["x_min"]
            b_width = b["x_max"] - b["x_min"]
            # Blocks are same-column iff centers are within 35% of the
            # narrower block's width. This keeps two right-column refs
            # blocks together (centers nearly identical) but separates a
            # left-column block from a right-column block (centers
            # differ by >> narrower width).
            narrower = min(prev_width, b_width)
            if narrower > 0 and abs(prev_center - b_center) <= narrower * 0.35:
                current_col.append(b)
            else:
                col_groups.append(current_col)
                current_col = [b]
        col_groups.append(current_col)

        for cg in col_groups:
            cg.sort(key=lambda b: b["y_min"])
            for bi in cg:
                ordered.append(bi["block"])

    return ordered


# ---------------------------------------------------------------------------
# Canonical representation building
# ---------------------------------------------------------------------------

_CAPTION_PREFIX_RE = re.compile(r'^(fig(?:ure)?|table)\.?\s*\d+', re.I)
_REFERENCE_PREFIX_RE = re.compile(r'^\s*(references?|bibliography)\b', re.I)
_HEADING_RE = re.compile(
    r'^(abstract|introduction|methods?|materials?|results?|discussion|'
    r'conclusion|acknowledg(?:e)?ments?|supplementary)\b', re.I)
_JOURNAL_HEADER_RE = re.compile(
    r'(science translational medicine|research article)', re.I)
_COPYRIGHT_RE = re.compile(
    r'(copyright|rights reserved|exclusive licensee|no claim to original)', re.I)
_DOWNLOAD_STAMP_RE = re.compile(r'\bdownloaded\b', re.I)
_PAGE_COUNT_RE = re.compile(r'^\s*\d+\s+of\s+\d+\s*$')
_FOOTER_CITATION_RE = re.compile(
    r'\bet al\.,?\s+sci\.\s+transl\.\s+med\..*\b\d{4}\b', re.I)
_TOP_SECTION_LABEL_RE = re.compile(r'^[A-Z][A-Z\s&/-]{4,}$')


def _round_bbox_list(x0: float, top: float, x1: float, bottom: float) -> list:
    return [round(float(x0), 1), round(float(top), 1),
            round(float(x1), 1), round(float(bottom), 1)]


def _normalize_word_text(text: str) -> str:
    text = apply_superscript_subscript_substitutions(text)
    text = apply_tounicode_surname_fixes(text)
    return text


def _should_attach_chars(text: str) -> bool:
    if not text:
        return False
    return any(ord(ch) > 127 for ch in text)


def _build_word_entries(words: list, page_chars: list, page_num: int) -> list:
    """Assign stable IDs and build word entries for the canonical schema."""
    sorted_words = sorted(words, key=lambda w: (float(w["top"]), float(w["x0"])))
    valid_chars = [c for c in page_chars
                   if c.get("text") and not c["text"].isspace()]
    word_entries = []

    for idx, w in enumerate(sorted_words, start=1):
        word_id = f"p{page_num:03d}_w{idx:06d}"
        w["_word_id"] = word_id
        w["text"] = _normalize_word_text(w.get("text", ""))
        entry = {
            "id": word_id,
            "text": w["text"],
            "bbox": _round_bbox_list(w["x0"], w["top"], w["x1"], w["bottom"]),
        }
        if w.get("fontname"):
            entry["font_name"] = w["fontname"]
        size = w.get("size") or w.get("height")
        if size:
            entry["font_size"] = round(float(size), 2)

        if _should_attach_chars(w["text"]):
            chars = []
            wx0, wx1 = float(w["x0"]), float(w["x1"])
            wtop, wbottom = float(w["top"]), float(w["bottom"])
            for c in valid_chars:
                cx = (float(c["x0"]) + float(c["x1"])) / 2.0
                cy = (float(c["top"]) + float(c["bottom"])) / 2.0
                if wx0 <= cx <= wx1 and wtop <= cy <= wbottom:
                    ch = _normalize_word_text(_map_pua_string(c.get("text", "")))
                    if ch and not ch.isspace():
                        chars.append({
                            "char": ch,
                            "bbox": _round_bbox_list(
                                c["x0"], c["top"], c["x1"], c["bottom"]),
                        })
            if chars:
                entry["chars"] = chars

        word_entries.append(entry)

    return word_entries


def _block_text(block_lines: list) -> str:
    return " ".join(
        " ".join(w["text"] for w in aline["words"])
        for aline in block_lines
    ).strip()


def _infer_block_type_hint(block_lines: list, block_text: str) -> str:
    """Return a cheap candidate label only; never semantic truth."""
    text = block_text.strip()
    if not text:
        return "unknown"
    if _CAPTION_PREFIX_RE.match(text):
        return "caption"
    if _REFERENCE_PREFIX_RE.match(text):
        return "reference_section"
    if _HEADING_RE.match(text):
        return "heading"

    line_fonts = []
    for aline in block_lines:
        line_fonts.extend(
            w.get("fontname", "").lower() for w in aline["words"]
            if w.get("fontname"))
    boldish = sum(("bold" in f or "black" in f or "semibold" in f)
                  for f in line_fonts)
    if len(block_lines) <= 2 and boldish >= max(1, len(line_fonts) // 2):
        return "heading_candidate"
    return "unknown"


def _artifact_line_type(line_text: str, top: float, page_height: float):
    text = line_text.strip()
    if not text:
        return None

    near_top = top <= max(90.0, page_height * 0.14)
    near_bottom = top >= page_height * 0.84

    if near_top and _JOURNAL_HEADER_RE.search(text):
        return "journal_header_candidate"
    if near_top and len(text.split()) <= 4 and _TOP_SECTION_LABEL_RE.match(text):
        return "top_section_label_candidate"
    if near_top and _COPYRIGHT_RE.search(text):
        return "copyright_candidate"
    if near_top and _DOWNLOAD_STAMP_RE.search(text):
        return "download_stamp_candidate"
    if near_bottom and _FOOTER_CITATION_RE.search(text):
        return "footer_citation_candidate"
    if near_bottom and _PAGE_COUNT_RE.match(text):
        return "page_count_candidate"
    return None


def _build_artifact_regions(page_obj, page_num: int, page_width: float,
                            page_height: float, words: list,
                            ordered_blocks: list,
                            sidebar_filter: int) -> list:
    regions = []
    region_idx = 1

    figures = detect_figures(page_obj, words)
    for fig in figures:
        regions.append({
            "id": f"p{page_num:03d}_a{region_idx:05d}",
            "bbox": _round_bbox_list(
                fig["bbox"]["x0"], fig["bbox"]["y0"],
                fig["bbox"]["x1"], fig["bbox"]["y1"]),
            "type": "figure_candidate",
        })
        region_idx += 1

    if sidebar_filter is not None and sidebar_filter < page_width:
        regions.append({
            "id": f"p{page_num:03d}_a{region_idx:05d}",
            "bbox": _round_bbox_list(sidebar_filter, 0.0, page_width, page_height),
            "type": "right_margin_candidate",
        })
        region_idx += 1

    seen_regions = set()
    for block_lines in ordered_blocks:
        for aline in block_lines:
            line_text = " ".join(w["text"] for w in aline["words"]).strip()
            region_type = _artifact_line_type(
                line_text, float(aline["top"]), float(page_height))
            if not region_type:
                continue
            bbox = _round_bbox_list(aline["x0"], aline["top"],
                                    aline["x1"], aline["bottom"])
            key = (region_type, *bbox)
            if key in seen_regions:
                continue
            seen_regions.add(key)
            regions.append({
                "id": f"p{page_num:03d}_a{region_idx:05d}",
                "bbox": bbox,
                "type": region_type,
            })
            region_idx += 1

    return regions


def build_page_representation(page_obj, page_num: int, page_width: float,
                              page_height: float, words: list,
                              ordered_blocks: list, sidebar_filter: int) -> dict:
    """Build the canonical page representation for extracted.json."""
    word_entries = _build_word_entries(words, page_obj.chars, page_num)
    blocks = []

    for block_idx, block_lines in enumerate(ordered_blocks, start=1):
        block_words = []
        seen_word_ids = set()
        for aline in block_lines:
            for w in aline["words"]:
                word_id = w.get("_word_id")
                if word_id and word_id not in seen_word_ids:
                    block_words.append(w)
                    seen_word_ids.add(word_id)
        if not block_words:
            continue

        block_text = _block_text(block_lines)
        blocks.append({
            "id": f"p{page_num:03d}_b{block_idx:05d}",
            "bbox": _round_bbox_list(
                min(w["x0"] for w in block_words),
                min(w["top"] for w in block_words),
                max(w["x1"] for w in block_words),
                max(w["bottom"] for w in block_words),
            ),
            "word_ids": [w["_word_id"] for w in block_words],
            "reading_order_candidate": block_idx,
            "block_type_hint": _infer_block_type_hint(block_lines, block_text),
        })

    qc_notes = []
    if not word_entries:
        qc_notes.append("No words were extracted for this page.")
    elif len(blocks) == 0:
        qc_notes.append("Words were extracted but no candidate blocks were built.")

    return {
        "page": page_num,
        "width_pt": round(page_width, 1),
        "height_pt": round(page_height, 1),
        "rotation": int(getattr(page_obj, "rotation", 0) or 0),
        "words": word_entries,
        "blocks": blocks,
        "artifact_regions": _build_artifact_regions(
            page_obj, page_num, page_width, page_height, words, ordered_blocks,
            sidebar_filter),
        "qc_notes": qc_notes,
    }


def build_document_representation(input_path: str, pages_output: list,
                                  sidebar_filter: int,
                                  encoding_profile: dict) -> dict:
    """Build the top-level extracted.json payload."""
    return {
        "source_pdf": os.path.basename(input_path),
        "total_pages": len(pages_output),
        "pages": pages_output,
        "metadata": {
            "sidebar_filter": sidebar_filter,
            "encoding_profile": encoding_profile,
        },
    }


# ---------------------------------------------------------------------------
# Encoding profile detection (unchanged from v5)
# ---------------------------------------------------------------------------

def detect_encoding_profile(all_text: str) -> dict:
    """Analyze extracted text to determine encoding conventions."""
    total_chars = len(all_text)
    if total_chars == 0:
        return {"words_concatenated": False, "space_ratio": 0.0,
                "quote_style": "unknown", "has_emdash": False,
                "hyphen_pattern": "unknown", "sample_chars": {}}

    space_count = all_text.count(' ')
    space_ratio = space_count / total_chars
    words_concatenated = space_ratio < 0.05

    count_2018 = all_text.count('\u2018')
    count_2019 = all_text.count('\u2019')
    count_201c = all_text.count('\u201c')
    count_201d = all_text.count('\u201d')
    count_straight_double = all_text.count('"')

    if count_201c > 5 or count_201d > 5:
        quote_style = "standard"
        open_dq, close_dq = '\u201c', '\u201d'
    elif count_2018 > 10:
        quote_style = "curly_single_as_double"
        open_dq, close_dq = '\u2018\u2018', '\u2019\u2019'
    elif count_straight_double > 5:
        quote_style = "straight"
        open_dq, close_dq = '"', '"'
    else:
        quote_style = "minimal"
        open_dq, close_dq = '', ''

    apostrophe = '\u2019' if count_2019 > 0 else "'"
    has_emdash = '\u2014' in all_text

    hyph_space = len(re.findall(r'\w- \w', all_text))
    hyph_nospace = len(re.findall(r'\w-\w', all_text))
    if hyph_space > hyph_nospace and hyph_space > 5:
        hyphen_pattern = "word- continuation"
    elif hyph_nospace > 5:
        hyphen_pattern = "word-continuation"
    else:
        hyphen_pattern = "none_detected"

    sample_chars = {
        "apostrophe": apostrophe,
        "open_double_quote": open_dq,
        "close_double_quote": close_dq,
    }
    if has_emdash:
        sample_chars["emdash"] = '\u2014'

    return {
        "words_concatenated": words_concatenated,
        "space_ratio": round(space_ratio, 4),
        "quote_style": quote_style,
        "has_emdash": has_emdash,
        "hyphen_pattern": hyphen_pattern,
        "sample_chars": sample_chars,
    }


# ---------------------------------------------------------------------------
# Figure detection (unchanged from v5)
# ---------------------------------------------------------------------------

def detect_figures(page, words: list) -> list:
    """Detect figure regions by finding image objects and nearby captions."""
    figures = []
    try:
        images = page.images
    except Exception:
        images = []

    if not images:
        return figures

    for img in images:
        bbox = {
            "x0": round(float(img.get("x0", 0)), 1),
            "y0": round(float(img.get("top", 0)), 1),
            "x1": round(float(img.get("x1", 0)), 1),
            "y1": round(float(img.get("bottom", 0)), 1),
        }
        width = bbox["x1"] - bbox["x0"]
        height = bbox["y1"] - bbox["y0"]
        if width < 50 or height < 50:
            continue

        caption = ""
        caption_words = [w for w in words
                         if w["top"] > bbox["y1"]
                         and w["top"] < bbox["y1"] + 40
                         and w["x0"] >= bbox["x0"] - 20
                         and w["x1"] <= bbox["x1"] + 20]
        if caption_words:
            caption_words.sort(key=lambda w: (w["top"], w["x0"]))
            first_word = caption_words[0]["text"].lower()
            if first_word.startswith("fig") or first_word.startswith("figure"):
                caption = " ".join(w["text"] for w in caption_words)

        if not caption:
            above_words = [w for w in words
                           if w["bottom"] < bbox["y0"]
                           and w["bottom"] > bbox["y0"] - 40
                           and w["x0"] >= bbox["x0"] - 20
                           and w["x1"] <= bbox["x1"] + 20]
            if above_words:
                above_words.sort(key=lambda w: (w["top"], w["x0"]))
                first_word = above_words[0]["text"].lower()
                if first_word.startswith("fig") or first_word.startswith("figure"):
                    caption = " ".join(w["text"] for w in above_words)

        figures.append({"bbox": bbox, "caption": caption})

    return figures



# ---------------------------------------------------------------------------
# v14: Adaptive x_tolerance for word extraction
# ---------------------------------------------------------------------------
# pdfplumber's extract_words() uses x_tolerance (default 3.0) to decide
# whether adjacent characters belong to the same word. Some PDFs (e.g.
# Science/AAAS journals) have very tight inter-word spacing (2-3px) that
# falls below the default threshold, causing entire lines to merge into
# single "words". This function analyzes character-level gaps to compute
# the optimal x_tolerance for each page.

def compute_adaptive_x_tolerance(page_chars, default=3.0):
    """Compute optimal x_tolerance from character gap distribution.

    Analyzes gaps between consecutive characters on the same line to find
    the valley between intra-word gaps (characters within a word) and
    inter-word gaps (spaces between words). Returns a tolerance value
    positioned in that valley.

    Works for any PDF: tight-spacing journals (Science/AAAS with 1-3px
    word gaps) get a lower tolerance; normal PDFs keep the default.

    Handles two cases:
    1. Standard valley: non-zero minimum between two populated clusters.
    2. Void valley: a complete gap (zero-count region) between intra-word
       and inter-word clusters -- common in PDFs where the inter-word gap
       is distinctly larger than intra-word gaps (e.g., 0px intra vs 2.4px
       inter with nothing in between).
    """
    if not page_chars:
        return default

    # Collect ALL gaps between consecutive chars on same line
    sorted_chars = sorted(page_chars,
                          key=lambda c: (round(float(c['top'])), float(c['x0'])))
    gaps = []
    for i in range(1, len(sorted_chars)):
        c0, c1 = sorted_chars[i - 1], sorted_chars[i]
        if abs(float(c0['top']) - float(c1['top'])) > 3:
            continue
        gap = float(c1['x0']) - float(c0['x1'])
        if -2 < gap < 20:
            gaps.append(gap)

    if len(gaps) < 50:
        return default

    # Build histogram with 0.25px bins from -0.5 to 6.0
    from collections import Counter
    bins = Counter()
    for g in gaps:
        b = round(g * 4) / 4  # 0.25 resolution
        bins[b] += 1

    # --- Strategy 1: Void-valley detection ---
    # Check for a clear void (zero-count region) between an intra-word
    # cluster near 0 and an inter-word cluster further right.
    # Scan ALL bins from 0.25 to default in 0.25 steps (including empty ones).
    all_scan_bins = [round(i * 0.25, 2) for i in range(1, int(default / 0.25) + 1)]
    void_start = None
    void_end = None
    for b in all_scan_bins:
        count = bins.get(b, 0)
        if count == 0:
            if void_start is None:
                void_start = b
            void_end = b
        else:
            if void_start is not None:
                # Found populated bin after a void
                void_width = void_end - void_start + 0.25
                # Check that there's significant mass on both sides
                below = sum(bins.get(bb, 0) for bb in bins if bb < void_start and bb >= -1)
                above = sum(bins.get(bb, 0) for bb in bins if bb > void_end and bb <= default + 2)
                if below >= 30 and above >= 20 and void_width >= 0.5:
                    # Place tolerance in the middle of the void
                    result = (void_start + void_end + 0.25) / 2.0
                    return max(0.5, min(result, default))
                void_start = None
                void_end = None

    # --- Strategy 2: Standard valley detection ---
    # Find the valley between intra-word cluster (near 0) and inter-word
    # cluster (typically 1.5-4px). Scan bins from 0.25 up to default,
    # looking for the minimum-density region.
    scan_bins = [b for b in sorted(bins.keys()) if 0.25 <= b <= default]
    if len(scan_bins) < 3:
        return default

    # Find the bin with minimum count in [0.25, default]
    min_count = float('inf')
    min_bin = None
    for b in scan_bins:
        count = bins.get(b, 0)
        if count < min_count:
            min_count = count
            min_bin = b

    if min_bin is None:
        return default

    # Verify this is a real valley: there should be substantially more
    # entries below it (intra-word) and above it (inter-word)
    below_total = sum(bins.get(b, 0) for b in bins if b < min_bin and b >= -1)
    above_total = sum(bins.get(b, 0) for b in bins if b > min_bin and b <= default + 2)

    # Both clusters should have significant mass
    if below_total < 30 or above_total < 20:
        return default

    # The valley should be significantly lower than both peaks
    if min_count > 0.1 * below_total:
        return default  # No clear valley

    result = max(0.5, min(min_bin, default))
    return result




# ---------------------------------------------------------------------------
# Raw evidence extraction
# ---------------------------------------------------------------------------

def _merge_drop_cap_words(words: list, page_num: int) -> list:
    """Merge obvious drop-cap words into the following lowercase word."""
    if not words:
        return words

    median_h = sorted(w['bottom'] - w['top'] for w in words)[len(words) // 2]
    drop_cap_indices = set()
    for wi, w in enumerate(words):
        wh = w['bottom'] - w['top']
        wtext = w.get('text', '').strip()
        if not (len(wtext) == 1 and wtext.isupper()
                and wh >= median_h * 1.8 and wh >= 15):
            continue
        wx0 = w['x0']
        wy_bottom = w['bottom']
        for wj, w2 in enumerate(words):
            if wj == wi:
                continue
            w2text = w2.get('text', '').strip()
            w2h = w2['bottom'] - w2['top']
            if (w2text and w2text[0].islower()
                    and w2h < wh * 0.7
                    and abs(w2['x0'] - wx0) < 30
                    and w2['top'] >= w['top'] - 5
                    and w2['top'] <= wy_bottom + 10):
                w2['text'] = wtext + w2text
                w2['x0'] = min(w['x0'], w2['x0'])
                w2['top'] = min(w['top'], w2['top'])
                w2['bottom'] = max(w['bottom'], w2['bottom'])
                drop_cap_indices.add(wi)
                print(f"  [info] page {page_num}: merged drop-cap '{wtext}' into "
                      f"'{w2text}' -> '{w2['text']}'")
                break
    if drop_cap_indices:
        return [w for i, w in enumerate(words) if i not in drop_cap_indices]
    return words


def extract_raw_page_evidence(pdf) -> tuple:
    """Extract raw words and page objects before canonical schema building."""
    all_words_flat = []
    raw_pages = []
    page_objects = []

    for page in pdf.pages:
        try:
            xtol = compute_adaptive_x_tolerance(page.chars)
            if xtol < 3.0:
                print(f"  [info] page {page.page_number}: adaptive x_tolerance = {xtol:.2f}")
        except Exception:
            xtol = 3.0
        words = page.extract_words(
            keep_blank_chars=False,
            use_text_flow=False,
            x_tolerance=xtol,
        )
        try:
            words = enrich_words_with_glyphs(words, page.chars)
        except Exception as e:
            print(f"  [warn] glyph enrichment failed on page {page.page_number}: {e}")
        try:
            words = reattach_orphan_punctuation(words, page.chars)
        except Exception as e:
            print(f"  [warn] orphan punctuation reattach failed on page {page.page_number}: {e}")
        raw_pages.append(words)
        all_words_flat.extend(words)
        page_objects.append(page)

    return raw_pages, page_objects, all_words_flat


# ---------------------------------------------------------------------------
# Main extraction
# ---------------------------------------------------------------------------

def extract_pdf(input_path: str, sidebar_filter: int = None,
                no_gutters: bool = False) -> dict:
    """Extract raw evidence, then build the canonical extracted.json output."""

    with pdfplumber.open(input_path) as pdf:
        raw_pages, page_objects, all_words_flat = extract_raw_page_evidence(pdf)

        if not page_objects:
            return {
                "source_pdf": os.path.basename(input_path),
                "total_pages": 0,
                "pages": [],
                "metadata": {},
            }

        page_width = page_objects[0].width

        if sidebar_filter is None:
            sidebar_filter = detect_sidebar_filter(all_words_flat, page_width)
            print(f"  Auto-detected sidebar filter: x0 > {sidebar_filter}")

        clean_words = [w for w in all_words_flat if w["x0"] < sidebar_filter]
        if no_gutters:
            gutters = []
            print("  Gutter detection disabled (--no-gutters)")
        else:
            gutters = detect_gutters(clean_words, page_width)
        if gutters:
            print(f"  Detected gutters at x = {[round(g, 1) for g in gutters]}")
        elif not no_gutters:
            print("  No column gutters detected (single-column document)")

        pages_output = []
        all_word_texts = []

        for page_idx, words_raw in enumerate(raw_pages):
            page_num = page_idx + 1
            page_obj = page_objects[page_idx]
            width = page_obj.width
            height = page_obj.height

            words = [w for w in words_raw if w["x0"] < sidebar_filter]
            words = _merge_drop_cap_words(words, page_num)

            lines = group_into_lines_column_aware(words, gutters)
            annotated = [annotate_line(line) for line in lines if line]
            blocks = find_text_blocks(annotated, width)
            if gutters:
                blocks = split_blocks_at_gutters(blocks, gutters)
            ordered = order_blocks_by_candidate_reading(blocks)

            page_representation = build_page_representation(
                page_obj=page_obj,
                page_num=page_num,
                page_width=width,
                page_height=height,
                words=words,
                ordered_blocks=ordered,
                sidebar_filter=sidebar_filter,
            )
            pages_output.append(page_representation)
            all_word_texts.extend(w["text"] for w in page_representation["words"])

            n_blocks = len(page_representation["blocks"])
            n_words = sum(len(line) for line in lines)
            print(f"  Page {page_num}: {n_words} words, {len(lines)} lines, {n_blocks} blocks")

        combined_text = "\n".join(all_word_texts)
        encoding_profile = detect_encoding_profile(combined_text)
        print(f"  Encoding: concatenated={encoding_profile['words_concatenated']}, "
              f"quotes={encoding_profile['quote_style']}, "
              f"emdash={encoding_profile['has_emdash']}")

        return build_document_representation(
            input_path=input_path,
            pages_output=pages_output,
            sidebar_filter=sidebar_filter,
            encoding_profile=encoding_profile,
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Build canonical extracted.json evidence from an academic PDF")
    parser.add_argument("input", help="Input PDF path")
    parser.add_argument("output", help="Output JSON path")
    parser.add_argument("--sidebar-filter", type=int, default=None,
                        help="Remove words with x0 above this value")
    parser.add_argument("--no-gutters", action="store_true",
                        help="Disable column gutter detection (single-column documents)")
    args = parser.parse_args()

    print(f"Extracting: {args.input}")
    result = extract_pdf(args.input, args.sidebar_filter, no_gutters=args.no_gutters)
    print(f"  Pages: {result['total_pages']}")

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"  Saved to: {args.output}")


if __name__ == "__main__":
    main()
