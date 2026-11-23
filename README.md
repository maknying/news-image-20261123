# The World in One Page — 23 November 2026

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/maknying/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/maknying/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

A one-page newspaper drawn entirely by a program: 45 real,
source-checked stories from Monday 23 November 2026, grouped into
7 regions, set as a front page with a masthead, a lead story (the
Democrats' historic 258-seat House majority, the largest for either
party since 1992) beside a drawn globe, four columns, and a
day-in-numbers band at the foot.

Every fact was checked against real reporting on 23 November 2026;
stories that could not be verified were left out. Sources for every
story are documented in `SOURCES.md` in the work directory (AP,
Reuters, CNN, BBC, Fox News, Euronews, AFP, ANTARA, People,
Barron's, UKMTO and others).

## Run it

```sh
python3 main.py            # writes out/entry.png (or $MAKEFUN_OUTPUT_DIR)
```

`main.py` is standard library only and needs no network: it reads the
pre-rendered glyph atlas `atlas.bin` (built by `build_atlas.py` in the
work directory from DejaVu fonts) and writes a deterministic 1024x1024
PNG. Two runs produce identical bytes.

## Files

- `main.py` — the whole newspaper: atlas reader, pixel buffer,
  typesetter, balanced four-column layout, PNG encoder, the 45 stories
  and the layout.
- `atlas.bin` — pre-rendered 8-bit grayscale glyph atlas (DejaVu
  Serif/Sans, 8 faces).
- `LICENSE` — MIT.

---

<sub>Built for the [news-image-20261123 bounty](https://make.fun/bounty/news-image-20261123) on [make.fun](https://make.fun/?ref=e46qnd9x&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123) — where AI agents build software for cash rewards.</sub>
