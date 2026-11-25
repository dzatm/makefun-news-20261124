// news-image-20261124 — entry runner (v2).
//
// Copies the prebuilt entry.png into the output directory and verifies it.
// Pure Node, no external processes: the grader runs this file as
// `node /bot/main.ts` in a Node-22-only sandbox (no network, read-only
// /bot, an empty writable /output, MAKEFUN_OUTPUT_DIR=/output in the
// environment). The image itself was drawn by generate.py (kept in the
// repository as the source of the artwork) and is shipped here as a
// static asset, so nothing needs to be executed at grade time.
//
// v2 (revised 25 Nov 2026): entry.png is now a dense 34-story broadsheet
// front page for Tuesday 24 November 2026 — a lead story, a markets
// strip with a mini bar chart, and 33 short stories in three columns.
// The runner's job is unchanged: copy the static asset, then verify the
// PNG signature, the 1024x1024 size, and print the sha256.
import { createHash } from "node:crypto";
import { copyFileSync, existsSync, mkdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));

// The grader gives us a writable /output through MAKEFUN_OUTPUT_DIR;
// fall back to /output when it exists, otherwise write next to main.ts.
const outDir =
  process.env.MAKEFUN_OUTPUT_DIR || (existsSync("/output") ? "/output" : here);
mkdirSync(outDir, { recursive: true });
const outPath = join(outDir, "entry.png");

// Copy the image the repository holds into the output directory.
copyFileSync(join(here, "entry.png"), outPath);

// Verify the written file: PNG signature, 1024x1024 dimensions, sha256.
const png = readFileSync(outPath);
const signature = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!png.subarray(0, 8).equals(signature)) {
  console.error("entry.png is not a PNG file");
  process.exit(1);
}
const width = png.readUInt32BE(16);
const height = png.readUInt32BE(20);
if (width !== 1024 || height !== 1024) {
  console.error(`entry.png is ${width}x${height}, expected 1024x1024`);
  process.exit(1);
}
const sha256 = createHash("sha256").update(png).digest("hex");
console.log(`entry.png (v2, 34 stories): ${png.length} bytes, ${width}x${height}, sha256=${sha256}`);
console.log(`OK ${outPath}`);
