#!/usr/bin/env node
/**
 * Zero the OS/2 sTypoLineGap (and hhea lineGap) after fantasticon's build.
 *
 * svg2ttf has no option to set sTypoLineGap; it always defaults it to 9% of
 * (ascent - descent), which is meant for body-text line spacing. Icon glyphs
 * are drawn to exactly fill their box (fontHeight/descent in fantasticonrc.cjs),
 * so that extra 9% throws off any renderer that centers text using the font's
 * line-height metric instead of the glyph's actual ink (e.g. Enigma2's
 * RT_VALIGN_CENTER).
 *
 * sTypoLineGap sits at a fixed, spec-defined byte offset within the OS/2
 * table (offset 72), so this patches the raw sfnt bytes directly instead of
 * pulling in a font-editing dependency for one field.
 */
const fs = require("fs");
const path = require("path");

const fontPath = path.resolve(__dirname, "../dist/fonts/MetrixLogos.ttf");

function findTable(buf, tag) {
  const numTables = buf.readUInt16BE(4);
  for (let i = 0; i < numTables; i++) {
    const recordOffset = 12 + i * 16;
    if (buf.toString("ascii", recordOffset, recordOffset + 4) === tag) {
      return buf.readUInt32BE(recordOffset + 8);
    }
  }
  return -1;
}

function main() {
  if (!fs.existsSync(fontPath)) {
    console.error(`[fix-metrics] Error: ${fontPath} not found (run build:font first)!`);
    process.exit(1);
  }

  const buf = fs.readFileSync(fontPath);

  const os2Offset = findTable(buf, "OS/2");
  const hheaOffset = findTable(buf, "hhea");
  if (os2Offset < 0 || hheaOffset < 0) {
    console.error("[fix-metrics] Error: OS/2 or hhea table not found!");
    process.exit(1);
  }

  buf.writeInt16BE(0, os2Offset + 72); // sTypoLineGap
  buf.writeInt16BE(0, hheaOffset + 8); // lineGap

  fs.writeFileSync(fontPath, buf);
  console.log(`[fix-metrics] sTypoLineGap/lineGap zeroed in ${fontPath}`);
}

main();
