// news-image-20261124 — entry runner.
//
// Runs generate.py and writes entry.png into the output directory, then
// verifies the PNG. The grader runs this file as `node /bot/main.ts`
// with the repository read-only at /bot and an empty writable /output.
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
// The grader gives us a writable /output; locally we write next to main.ts.
const outDir = process.env.OUTPUT_DIR || (existsSync("/output") ? "/output" : here);
mkdirSync(outDir, { recursive: true });
const outPath = join(outDir, "entry.png");

const run = spawnSync("python3", [join(here, "generate.py"), outPath], { stdio: "inherit" });
if (run.error) {
  console.error(`failed to start python3: ${run.error.message}`);
  process.exit(1);
}
if (run.status !== 0) {
  console.error(`generate.py exited with status ${run.status}`);
  process.exit(1);
}

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
console.log(`entry.png: ${png.length} bytes, ${width}x${height}, sha256=${sha256}`);
console.log(`OK ${outPath}`);
