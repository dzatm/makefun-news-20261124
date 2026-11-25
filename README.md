# makefun-news-20261124

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/dzatm/makefun-news-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/dzatm/makefun-news-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

One image that sums up 24 November 2026's world news. The v3 front page packs 38 dated stories across 10 regions and 20 fields onto a single page: the Dow closing above 50,000 leads, above 12 more illustrated feature cards (Huawei's 10-of-12 conviction, Russian attacks killing 9 in Ukraine, Sanofi's $41B Insmed deal, Ariane 6 lifting 36 satellites, Microsoft's "Code Red", a Houthi drone hit on Riyadh, strikes in Gaza, the Serang factory-fire toll, a Hanoi gas blast, an Indian school-bus crash, an M6.4 quake off Rodrigues, and 13 dead in a Ras Al Khaimah bus crash) plus 25 one-line briefs — with a UTC timeline, a day-in-numbers strip, a world pin map, per-story sources and confidence labels, and a date-check strip listing the wrong-day stories left out.

## Run it

```sh
python3 generate.py
```

That writes `entry.png` (1024×1024), a front page called "THE WORLD — IN ONE IMAGE". Running it twice produces a byte-identical file. `main.ts` is the grader-facing runner: it copies the shipped `entry.png` into `MAKEFUN_OUTPUT_DIR` and verifies the PNG signature, the 1024×1024 size and the sha256 — pure Node stdlib, no network, no external processes.

---

Entered on [make.fun](https://make.fun/?ref=82nq3gxf&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards
