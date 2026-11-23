#!/usr/bin/env python3
"""The World in One Page — Monday 23 November 2026.

A one-page newspaper front page drawn entirely by this program: 45
real, source-checked stories from Monday 23 November 2026, grouped
into 7 regions, set as a front page with a masthead, a lead story
(the Democrats' historic 258-seat House majority), four columns, a
day-in-numbers band and a source line.

Standard library only. Every glyph comes from the pre-rendered atlas
(atlas.bin, built by build_atlas.py from DejaVu fonts), so the program
needs no network and no installed fonts at run time. Two runs write
byte-identical PNG files.

Usage:  python3 main.py            # writes out/entry.png
        MAKEFUN_OUTPUT_DIR=/output python3 main.py
"""

import binascii
import hashlib
import math
import os
import struct
import sys
import zlib

# ---------------------------------------------------------------- page
W = 1024
H = 1024
MARGIN = 40
CONTENT_W = W - 2 * MARGIN          # 944
COL_W = 236
COL_GAP = 12
NCOLS = 4
BODY_TOP = 258
BODY_BOTTOM = 978

PAPER = (247, 243, 232)
INK = (24, 24, 24)
RED = (139, 26, 26)
FAINT = (178, 168, 148)

# Face ids match build_atlas.py.
F_MASTHEAD = 0   # serif bold 46
F_LEAD_HEAD = 1  # serif bold 28
F_LEAD_DECK = 2  # serif 13
F_HEAD = 3       # serif bold 13
F_SECTION = 4    # sans bold 11
F_SUMMARY = 5    # sans 10
F_FOOTER = 6     # sans 9
F_DATE = 7       # sans bold 10

# ---------------------------------------------------------------- data
# (section, headline, summary). The lead story is separate below.
STORIES = [
    ("MIDDLE EAST",
     "Hormuz attacks hit record level",
     "Attacks on shipping hit their highest since the war began: "
     "30+ in October, 22 in November."),
    ("MIDDLE EAST",
     "Iran claims control of Hormuz",
     "Tehran claims the strait after hitting US radars in Bahrain; "
     "a Houthi missile is downed."),
    ("MIDDLE EAST",
     "Trump leans to Iran strikes 2027",
     "Trump signals major new strikes after the New Year if diplomacy "
     "with Tehran fails."),
    ("MIDDLE EAST",
     "Tanker incident in Gulf of Oman",
     "UKMTO reports a tanker tangled with military forces near "
     "Chabahar; details unconfirmed."),
    ("MIDDLE EAST",
     "Settler attacks are 'terrorism'",
     "Israel's Eisenkot calls West Bank settler violence 'Jewish "
     "terrorism'."),
    ("MIDDLE EAST",
     "Pakistan FM hopeful on Iran deal",
     "Pakistan's foreign minister hopes for a US-Iran deal and warns "
     "against a long war."),
    ("EUROPE",
     "Sparta II towed out of Finland",
     "The drone-struck Russian cargo ship is towed from Finnish "
     "waters; her 16 crew are safe."),
    ("EUROPE",
     "Thousands march in Lisbon",
     "Protests over living costs sweep Lisbon, Paris and Europe, "
     "demanding higher wages."),
    ("EUROPE",
     "EU budget: €204bn cut proposed",
     "Costa's plan keeps up to €100bn for Ukraine; Czech PM Babis "
     "calls it unacceptable."),
    ("EUROPE",
     "Russia 'tried to kill rapper'",
     "Warsaw says Russia allegedly tried twice to kill a "
     "Ukrainian-American rapper."),
    ("EUROPE",
     "Denmark expels Russian attache",
     "Copenhagen expels a defence attache over a plot to kill rapper "
     "Kyivstoner."),
    ("EUROPE",
     "Macron warns of 'new level' threat",
     "Macron warns of a new level of Russian aggression after airspace "
     "violations."),
    ("RUSSIA & UKRAINE",
     "14 missing after Kyiv-region hit",
     "A drone collapses flats in Dymer; two bodies are recovered and "
     "nine people evacuated."),
    ("RUSSIA & UKRAINE",
     "Corvette capsized off Benghazi",
     "A sea drone hits the Merkury at Benghazi; 10 crew hurt and a "
     "Maltese ship also struck."),
    ("RUSSIA & UKRAINE",
     "Kryvyi Rih double-tap kills 2",
     "A missile then drones hit Kryvyi Rih; a boy of seven dies and "
     "60 are hurt."),
    ("RUSSIA & UKRAINE",
     "Russian refining cut 45% by Kyiv",
     "Ukrainian strikes have cut crude processing nearly in half since "
     "late October."),
    ("RUSSIA & UKRAINE",
     "Putin 'not America's friend'",
     "Jay Clayton says Putin is 'not America's friend in Ukraine' as "
     "Trump defends his remark."),
    ("THE AMERICAS",
     "Trump blames Democrats for $6tn",
     "Trump says markets lost $6 trillion since the Democrats' "
     "'strange win' on 3 November."),
    ("THE AMERICAS",
     "Wall Street's worst week in years",
     "The S&P falls 8.6% and the Nasdaq 10% in a week; all three post "
     "record point drops."),
    ("THE AMERICAS",
     "Delta outage delays 3,500 flights",
     "A weight-and-balance system failure forces an FAA ground stop on "
     "Atlanta-bound flights."),
    ("THE AMERICAS",
     "ICE arrests at Seattle airport",
     "Two passengers are seized boarding a flight; Governor Ferguson "
     "calls ICE 'out of control'."),
    ("THE AMERICAS",
     "Ohio baby shower shooting kills 3",
     "Gunfire in Parma kills a 17-year-old, the expectant father, 19, "
     "and the grandfather, 45."),
    ("THE AMERICAS",
     "Army to detonate 5 tons in Iowa",
     "The Army plans to blow up unstable lead azide despite a court "
     "order pausing the blast."),
    ("THE AMERICAS",
     "Trump signs law ending the penny",
     "A new law permanently ends production of the one-cent coin."),
    ("ASIA–PACIFIC",
     "Indonesia fire: 24 body bags",
     "Rescuers recover 24 body bags from the Banten candy factory; "
     "search resumes Monday."),
    ("ASIA–PACIFIC",
     "Nepal PM Shah meets Modi in Delhi",
     "Shah holds talks with Modi on his first India visit; a $2bn "
     "package is on the agenda."),
    ("ASIA–PACIFIC",
     "Myanmar calls ASEAN move unfair",
     "The army-backed government calls an ASEAN decision 'unfair and "
     "imbalanced'."),
    ("ASIA–PACIFIC",
     "Seoul education chief quits",
     "South Korea's education minister resigns amid an AI-driven exam "
     "cheating scandal."),
    ("ASIA–PACIFIC",
     "India posts record 720/9d in NZ",
     "India declare at 720/9, their best Test total in New Zealand; "
     "the hosts trail by 233."),
    ("ASIA–PACIFIC",
     "Thailand keeps Myanmar ties",
     "Bangkok keeps ties with Myanmar despite the ICJ genocide ruling, "
     "PM Anutin says."),
    ("ASIA–PACIFIC",
     "NTPC collapse kills 3 workers",
     "A conveyor collapse at an NTPC project in Jharkhand kills three "
     "workers."),
    ("ASIA–PACIFIC",
     "Tata Steel signs Rs28,000 cr deal",
     "Tata Steel signs a Rs28,000 crore deal with APL Apollo."),
    ("ASIA–PACIFIC",
     "BJP MP Wadkute dies in Delhi",
     "Rajya Sabha MP Ramrao Wadkute dies of a cardiac arrest in Delhi."),
    ("MARKETS, TECH & SPORT",
     "US still wants Nvidia answers",
     "The US still needs answers from Nvidia on its China chip sales, "
     "Bessent says on CBS."),
    ("MARKETS, TECH & SPORT",
     "Trump: Huang should say sorry",
     "Trump asks ex-Nvidia chief Jensen Huang to apologise and retake "
     "the top job."),
    ("MARKETS, TECH & SPORT",
     "Nasdaq futures rebound on Monday",
     "Futures open sharply higher in Asia after Friday's plunge, ahead "
     "of US inflation data."),
    ("MARKETS, TECH & SPORT",
     "Bitcoin rebounds above $61,000",
     "Bitcoin climbs back above $61,000, up nearly 11% from its "
     "Saturday low."),
    ("MARKETS, TECH & SPORT",
     "Liverpool thrash Man Utd 4-0",
     "Pochettino's United debut ends in a 4-0 rout at Anfield; Yoro is "
     "sent off in 8 minutes."),
    ("MARKETS, TECH & SPORT",
     "Miley Cyrus marries Maxx Morando",
     "Grammy winner Miley Cyrus, 33, weds drummer Maxx Morando, 28, "
     "in Palm Springs."),
    ("AFRICA & SCIENCE",
     "South Sudan attack kills 24",
     "SPLA-IO fighters raid a cattle camp in Warrap State; seven of "
     "the dead are children."),
    ("AFRICA & SCIENCE",
     "Fighting disrupts Ebola response",
     "Clashes near an Ituri hospital force WHO staff to shelter in a "
     "maternity ward for a day."),
    ("AFRICA & SCIENCE",
     "Ebola jab trials start next week",
     "Strain-specific jab trials begin in DR Congo as cases pass "
     "11,600 and deaths near 5,700."),
    ("AFRICA & SCIENCE",
     "BepiColombo enters Mercury orbit",
     "The ESA/JAXA mission reaches Mercury after an eight-year "
     "journey; its X-ray eye already works."),
    ("AFRICA & SCIENCE",
     "Pulsar found 1m times faster",
     "A lattice-crypto method finds pulsar PSR J1622-7204, spinning "
     "261 times a second."),
]

LEAD_KICKER = "LEAD \u2014 WASHINGTON \u2022 MIDTERMS"
LEAD_HEAD = "Democrats clinch 258 House seats"
LEAD_DECK = ("The largest House majority for either party since 1992: "
             "Chuck Hubbard beats Virginia Foxx in North Carolina as "
             "Democrats gain 44 seats. With the Senate also theirs, "
             "divided government looms.")

MASTHEAD = "THE WORLD IN ONE PAGE"
DATELINE_LEFT = "MONDAY, 23 NOVEMBER 2026"
DATELINE_RIGHT = "45 STORIES \u2022 7 REGIONS"

NUMBERS = ("THE DAY IN NUMBERS \u2014 258 House seats \u2022 24 body "
           "bags in Banten \u2022 14 missing in Dymer \u2022 3,500 "
           "flights delayed \u2022 $6tn 'lost' \u2022 720/9d in "
           "Wellington")

FOOTER_LEFT = ("Sources: AP \u2022 Reuters \u2022 CNN \u2022 BBC \u2022 "
               "Fox News \u2022 Euronews \u2022 AFP \u2022 ANTARA "
               "\u2022 People \u2022 Barron's \u2022 UKMTO")
FOOTER_RIGHT = "Compiled 23 Nov 2026 \u2022 No. 45"


# ---------------------------------------------------------------- atlas
# Binary layout written by build_atlas.py:
#   magic 8s, u32 face_count,
#   per face: u32 id, u32 size, u16 ascent, u16 descent, u32 glyphs,
#   per glyph: u32 face_id, u32 codepoint, i16 bitmap left, i16 bitmap
#              top, u16 advance, u16 width, u16 height, u32 data offset,
#              u32 data length,
#   pixel blob (8-bit grayscale).
_GLYPH = struct.Struct("<IhhHHHHII")
_FACE = struct.Struct("<IIHHI")


class Atlas(object):
    def __init__(self, path):
        with open(path, "rb") as fh:
            raw = fh.read()
        if raw[:8] != b"ATLS0002":
            raise ValueError("bad atlas magic")
        pos = 8
        (nfaces,) = struct.unpack_from("<I", raw, pos)
        pos += 4
        self.faces = {}   # face_id -> (size, ascent, descent)
        self.glyphs = {}  # (face_id, codepoint) -> glyph tuple
        counts = []
        for _ in range(nfaces):
            fid, size, asc, desc, count = _FACE.unpack_from(raw, pos)
            pos += _FACE.size
            self.faces[fid] = (size, asc, desc)
            counts.append(count)
        rows = []
        for count in counts:
            for _ in range(count):
                rows.append(_GLYPH.unpack_from(raw, pos))
                pos += _GLYPH.size
        blob_start = pos
        for fid, cp, left, top, adv, w, h, off, ln in rows:
            self.glyphs[(fid, cp)] = (
                left, top, adv, w, h,
                raw[blob_start + off: blob_start + off + ln])

    def glyph(self, face, ch):
        found = self.glyphs.get((face, ord(ch)))
        if found is None:
            found = self.glyphs.get((face, ord("?")))
        return found

    def text_width(self, face, text):
        return sum(self.glyph(face, ch)[2] for ch in text)

    def wrap(self, face, text, max_w, max_lines=None):
        """Greedy word wrap; optionally cap lines, ending with …."""
        lines = []
        current = ""
        for word in text.split(" "):
            trial = word if not current else current + " " + word
            if self.text_width(face, trial) <= max_w or not current:
                current = trial
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        # Hard-split any line that is still too wide.
        fixed = []
        for line in lines:
            while self.text_width(face, line) > max_w and len(line) > 1:
                cut = len(line) - 1
                while cut > 0 and self.text_width(face, line[:cut]) > max_w:
                    cut -= 1
                fixed.append(line[:max(cut, 1)])
                line = line[max(cut, 1):]
            fixed.append(line)
        lines = fixed
        if max_lines is not None and len(lines) > max_lines:
            lines = lines[:max_lines]
            last = lines[-1]
            while last and self.text_width(face, last + "…") > max_w:
                last = last[:-1]
            lines[-1] = last + "…"
        return lines


# ---------------------------------------------------------------- canvas
class Page(object):
    def __init__(self, atlas):
        self.atlas = atlas
        self.buf = bytearray(PAPER * (W * H))

    def _set(self, x, y, color, alpha=255):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            if alpha >= 255:
                self.buf[i:i + 3] = bytes(color)
            elif alpha > 0:
                for c in range(3):
                    base = self.buf[i + c]
                    self.buf[i + c] = (
                        color[c] * alpha + base * (255 - alpha)) // 255

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(W, x + w), min(H, y + h)
        for yy in range(y0, y1):
            base = (yy * W + x0) * 3
            self.buf[base:base + (x1 - x0) * 3] = bytes(color) * (x1 - x0)

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def draw_text(self, x, y_top, face, text, color=INK):
        """Draw text anchored at (x, y_top): y_top is the ascender top."""
        cx = x
        for ch in text:
            left, top, adv, w, h, data = self.atlas.glyph(face, ch)
            if w and h:
                gx, gy = cx + left, y_top + top
                for row in range(h):
                    src = row * w
                    for col in range(w):
                        a = data[src + col]
                        if a:
                            self._set(gx + col, gy + row, color, a)
            cx += adv
        return cx

    def text_lines(self, x, y_top, face, lines, leading, color=INK):
        y = y_top
        for line in lines:
            self.draw_text(x, y, face, line, color)
            y += leading
        return y

    def globe(self, cx, cy, r, color=INK):
        """A small line-drawn globe: circle, meridians, parallels."""
        def plot(px, py):
            for dx in (0, 1):
                for dy in (0, 1):
                    self._set(px + dx, py + dy, color)
        steps = 720
        for i in range(steps):
            t = 2.0 * math.pi * i / steps
            plot(int(cx + r * math.cos(t)), int(cy + r * math.sin(t)))
            plot(int(cx + (r * 0.45) * math.cos(t)),
                 int(cy + r * math.sin(t)))
            a = math.cos(0.6)
            plot(int(cx + r * math.cos(t) * a), int(cy + r * math.sin(t)))
            for fy, fr in ((-0.55, 0.83), (0.0, 1.0), (0.55, 0.83)):
                plot(int(cx + r * fr * math.cos(t)),
                     int(cy + r * fy + r * 0.22 * math.sin(t)))


# ---------------------------------------------------------------- layout
def render(page):
    at = page.atlas
    # --- masthead
    name_w = at.text_width(F_MASTHEAD, MASTHEAD)
    page.draw_text((W - name_w) // 2, 22, F_MASTHEAD, MASTHEAD)
    page.draw_text(MARGIN, 84, F_DATE, DATELINE_LEFT)
    right_w = at.text_width(F_DATE, DATELINE_RIGHT)
    page.draw_text(W - MARGIN - right_w, 84, F_DATE, DATELINE_RIGHT)
    page.hline(MARGIN, 102, CONTENT_W, INK, 2)
    page.hline(MARGIN, 106, CONTENT_W, INK, 1)

    # --- lead story + globe
    page.draw_text(MARGIN, 116, F_SECTION, LEAD_KICKER, RED)
    head_lines = at.wrap(F_LEAD_HEAD, LEAD_HEAD, 740, max_lines=2)
    y = page.text_lines(MARGIN, 136, F_LEAD_HEAD, head_lines, 35)
    deck_lines = at.wrap(F_LEAD_DECK, LEAD_DECK, 740, max_lines=3)
    y = page.text_lines(MARGIN, y + 8, F_LEAD_DECK, deck_lines, 17)
    page.globe(872, 178, 54)
    cap = "THE WORLD \u2014 23 NOV 2026"
    cap_w = at.text_width(F_FOOTER, cap)
    page.draw_text(872 - cap_w // 2, 238, F_FOOTER, cap)
    page.hline(MARGIN, 252, CONTENT_W, INK, 2)

    # --- four columns of stories.
    # Measure every story block first, then split the sequence into
    # four columns of near-equal total height so no column is left
    # half empty. The split target rises until every column fits.
    for gx in (MARGIN + COL_W + COL_GAP // 2 - 1,
               MARGIN + 2 * COL_W + 3 * COL_GAP // 2 - 1,
               MARGIN + 3 * COL_W + 5 * COL_GAP // 2 - 1):
        page.vline(gx, BODY_TOP, BODY_BOTTOM - BODY_TOP, FAINT)
    blocks = []
    current_section = None
    for section, headline, summary in STORIES:
        head = at.wrap(F_HEAD, headline, COL_W, max_lines=2)
        summ = at.wrap(F_SUMMARY, summary, COL_W, max_lines=2)
        header_h = 24 if section != current_section else 0
        current_section = section
        block_h = header_h + 16 * len(head) + 13 * len(summ) + 10
        blocks.append((section, header_h, head, summ, block_h))
    body_h = BODY_BOTTOM - BODY_TOP
    total_h = sum(b[4] for b in blocks)
    n = len(blocks)
    # Balanced partition: dynamic programming over the block sequence.
    # best[i][k] = smallest possible tallest column when the first i
    # blocks are split into k columns; split[i][k] remembers the cut.
    INF = 10 ** 9
    best = [[INF] * (NCOLS + 1) for _ in range(n + 1)]
    split = [[0] * (NCOLS + 1) for _ in range(n + 1)]
    best[0][0] = 0
    for i in range(1, n + 1):
        for k in range(1, NCOLS + 1):
            running = 0
            for j in range(i - 1, -1, -1):
                running += blocks[j][4]
                if running > body_h:
                    break
                cand = max(best[j][k - 1], running)
                if cand < best[i][k]:
                    best[i][k] = cand
                    split[i][k] = j
    if best[n][NCOLS] > body_h:
        raise SystemExit("OVERFLOW: stories do not fit in 4 columns")
    cuts = []
    i, k = n, NCOLS
    while k > 0:
        j = split[i][k]
        cuts.append(j)
        i, k = j, k - 1
    cuts.reverse()
    # cuts[0] is 0; column c holds blocks[cuts[c]:cuts[c+1]].
    bounds = cuts + [n]
    heights = [sum(b[4] for b in blocks[bounds[c]:bounds[c + 1]])
               for c in range(NCOLS)]
    target = max(heights)
    col = 0
    y = BODY_TOP
    counts = [0, 0, 0, 0]
    for idx, (section, header_h, head, summ, block_h) in enumerate(blocks):
        while idx >= bounds[col + 1]:
            col += 1
            y = BODY_TOP
        x = MARGIN + col * (COL_W + COL_GAP)
        if header_h:
            page.draw_text(x, y, F_SECTION, section, RED)
            page.hline(x, y + 16, COL_W, INK, 1)
            y += header_h
        y = page.text_lines(x, y, F_HEAD, head, 16)
        y = page.text_lines(x, y, F_SUMMARY, summ, 13)
        y += 10
        counts[col] += 1
        if y > BODY_BOTTOM:
            raise SystemExit("OVERFLOW: column %d runs past the body" % col)

    # --- day in numbers
    page.rect(MARGIN, 984, CONTENT_W, 1, INK)
    page.rect(MARGIN, 1004, CONTENT_W, 1, INK)
    num_w = at.text_width(F_SECTION, NUMBERS)
    page.draw_text((W - num_w) // 2, 988, F_SECTION, NUMBERS)
    # --- footer
    page.draw_text(MARGIN, 1010, F_FOOTER, FOOTER_LEFT)
    foot_w = at.text_width(F_FOOTER, FOOTER_RIGHT)
    page.draw_text(W - MARGIN - foot_w, 1010, F_FOOTER, FOOTER_RIGHT)
    return counts


# ---------------------------------------------------------------- png
def _chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", binascii.crc32(tag + data) & 0xFFFFFFFF)
    return out


def encode_png(page):
    raw = bytearray()
    for row in range(H):
        raw.append(0)
        raw += page.buf[row * W * 3:(row + 1) * W * 3]
    png = bytearray(b"\x89PNG\r\n\x1a\n")
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    return bytes(png)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    atlas = Atlas(os.path.join(here, "atlas.bin"))
    page = Page(atlas)
    counts = render(page)
    png = encode_png(page)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not outdir:
        outdir = "/output" if os.path.isdir("/output") else "out"
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(png)
    digest = hashlib.sha256(png).hexdigest()
    print("wrote %s (%d bytes, sha256 %s)" % (path, len(png), digest))
    print("stories=%d columns=%s" % (len(STORIES) + 1, counts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
