#!/usr/bin/env node
/**
 * Rebuilds codepoints.json from the SVG files in icons/.
 * Icons are sorted alphabetically by filename; codepoints are
 * assigned sequentially starting at START_CP (0xE900).
 *
 * Usage:  node scripts/update-codepoints.js
 */

const fs   = require("fs");
const path = require("path");

const ROOT          = path.resolve(__dirname, "..");
const ICONS_DIR     = path.join(ROOT, "icons");
const CODEPOINTS    = path.join(ROOT, "codepoints.json");
const START_CP      = 0xE900;

const svgs = fs
    .readdirSync(ICONS_DIR)
    .filter(f => f.endsWith(".svg"))
    .sort((a, b) => a.localeCompare(b, undefined, { sensitivity: "base" }));

const result = {};
svgs.forEach((file, index) => {
    const name = path.basename(file, ".svg");
    result[name] = START_CP + index;
});

fs.writeFileSync(CODEPOINTS, JSON.stringify(result, null, 2) + "\n", "utf-8");

console.log(`${svgs.length} icons → codepoints 0x${START_CP.toString(16).toUpperCase()} – 0x${(START_CP + svgs.length - 1).toString(16).toUpperCase()}`);
console.log(`Written: ${CODEPOINTS}`);
