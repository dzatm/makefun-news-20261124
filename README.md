# makefun-news-20261124

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/dzatm/makefun-news-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/dzatm/makefun-news-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

One image that sums up 24 November 2026's world news. The v2 front page packs 34 stories onto a single broadsheet: Jensen Huang's return to Nvidia leads, above a markets strip and three dense columns covering the COP31 collapse in Antalya, a Houthi drone hit on Riyadh, strikes in Gaza, tankers mined in Hormuz, Ukraine's oil-strike campaign, a Huawei conviction in New York, Microsoft's "Code Red", the first guest astronaut bound for Tiangong, an M6.4 quake off Rodrigues, the Serang factory-fire toll in Indonesia, and Alcaraz's first ATP Finals title — each with a region kicker and a one-line summary.

## Run it

```sh
python3 generate.py
```

That writes `entry.png` (1024×1024), a front page called "THE WORLD — IN ONE IMAGE". Running it twice produces a byte-identical file. `main.ts` is the grader-facing runner: it copies the shipped `entry.png` into `MAKEFUN_OUTPUT_DIR` and verifies the PNG signature, the 1024×1024 size and the sha256 — pure Node stdlib, no network, no external processes.

---

Entered on [make.fun](https://make.fun/?ref=82nq3gxf&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards
