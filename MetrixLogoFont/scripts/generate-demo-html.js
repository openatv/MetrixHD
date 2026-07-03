const fs = require("fs");
const path = require("path");

const projectRoot = path.resolve(__dirname, "..");
const distDir = path.join(projectRoot, "dist");
const codepointsPath = path.join(projectRoot, "codepoints.json");
const outputPath = path.join(distDir, "demo.html");

const FONT_NAME = "MetrixLogos";
const PREFIX = "mi";

function toHexCodepoint(value) {
  return value.toString(16).toUpperCase().padStart(4, "0");
}

function escapeHtml(value) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function buildInlineCss(codepoints) {
  const iconClasses = Object.entries(codepoints)
    .map(([name, value]) => `.${PREFIX}-${name}::before { content: "\\${value.toString(16)}"; }`)
    .join("\n");

  return `
    @font-face {
      font-family: "${FONT_NAME}";
      src: url("./fonts/${FONT_NAME}.woff2") format("woff2"),
           url("./fonts/${FONT_NAME}.woff") format("woff");
      font-weight: normal;
      font-style: normal;
    }
    [class^="${PREFIX}-"],
    [class*=" ${PREFIX}-"] {
      font-family: "${FONT_NAME}";
      font-style: normal;
      font-weight: normal;
      speak: none;
      display: inline-block;
      line-height: 1;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }
    ${iconClasses}`;
}

function buildIconCards(codepoints) {
  const entries = Object.entries(codepoints)
    .map(([name, value]) => ({
      name,
      value,
      hex: toHexCodepoint(value),
      className: `${PREFIX}-${name}`
    }))
    .sort((a, b) => a.name.localeCompare(b.name));

  return entries
    .map((entry) => {
      const displayName = escapeHtml(entry.name);
      const className = escapeHtml(entry.className);
      const unicode = `\\u${entry.hex}`;

      return `
        <article class="icon-card" data-name="${displayName}" data-class="${className}" data-unicode="${unicode}">
          <div class="icon-preview">
            <i class="${className}"></i>
          </div>
          <h2>${displayName}</h2>
          <p><strong>Class:</strong> .${className}</p>
          <p><strong>Unicode:</strong> ${unicode}</p>
        </article>`;
    })
    .join("\n");
}

function buildHtml(codepoints) {
  const generatedAt = new Date().toISOString();
  const iconCount = Object.keys(codepoints).length;

  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>${FONT_NAME} demo</title>
  <style>
    ${buildInlineCss(codepoints)}

    :root {
      --bg: #0b1220;
      --panel: #111a2e;
      --text: #d8e2ff;
      --muted: #9fb0db;
      --accent: #56d7a7;
      --border: #223352;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
      background: radial-gradient(circle at 15% 15%, #12203a, var(--bg) 50%);
      color: var(--text);
      min-height: 100vh;
    }

    .wrap {
      width: min(1200px, 96vw);
      margin: 0 auto;
      padding: 24px 0 40px;
    }

    header {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 18px;
    }

    h1 {
      margin: 0;
      font-size: clamp(22px, 3.5vw, 34px);
      line-height: 1.1;
    }

    .meta {
      color: var(--muted);
      font-size: 13px;
      margin-top: 6px;
    }

    .toolbar {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }

    .toolbar input {
      background: #0b1530;
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 10px 12px;
      min-width: 240px;
      font-size: 14px;
      outline: none;
    }

    .toolbar input:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(86, 215, 167, 0.2);
    }

    .cards {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
      gap: 14px;
    }

    .icon-card {
      background: linear-gradient(160deg, #172645, var(--panel));
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 14px;
      transition: transform 120ms ease, border-color 120ms ease;
    }

    .icon-card:hover {
      transform: translateY(-2px);
      border-color: var(--accent);
    }

    .icon-preview {
      height: 72px;
      display: grid;
      place-items: center;
      margin-bottom: 10px;
      border-radius: 12px;
      background: rgba(255, 255, 255, 0.04);
      border: 1px dashed rgba(159, 176, 219, 0.4);
    }

    .icon-preview i {
      font-size: 34px;
      color: var(--accent);
    }

    .icon-card h2 {
      margin: 0 0 8px;
      font-size: 18px;
      line-height: 1.2;
    }

    .icon-card p {
      margin: 4px 0;
      color: var(--muted);
      font-size: 13px;
      word-break: break-word;
    }

    .empty {
      display: none;
      margin-top: 14px;
      color: var(--muted);
    }
  </style>
</head>
<body>
  <main class="wrap">
    <header>
      <div>
        <h1>${FONT_NAME} demo</h1>
        <div class="meta">${iconCount} icons &bull; generated ${generatedAt}</div>
      </div>
      <div class="toolbar">
        <input id="filter" type="search" placeholder="Filter by name, class, unicode..." />
      </div>
    </header>

    <section class="cards">
${buildIconCards(codepoints)}
    </section>

    <p id="empty" class="empty">No icons match this filter.</p>
  </main>

  <script>
    const input = document.getElementById("filter");
    const cards = Array.from(document.querySelectorAll(".icon-card"));
    const empty = document.getElementById("empty");

    function applyFilter() {
      const q = input.value.trim().toLowerCase();
      let visible = 0;

      cards.forEach((card) => {
        const haystack = [
          card.dataset.name,
          card.dataset.class,
          card.dataset.unicode
        ].join(" ").toLowerCase();

        const show = !q || haystack.includes(q);
        card.style.display = show ? "block" : "none";
        if (show) visible += 1;
      });

      empty.style.display = visible === 0 ? "block" : "none";
    }

    input.addEventListener("input", applyFilter);
  </script>
</body>
</html>`;
}

function main() {
  const raw = fs.readFileSync(codepointsPath, "utf8");
  const codepoints = JSON.parse(raw);

  fs.mkdirSync(distDir, { recursive: true });
  fs.writeFileSync(outputPath, buildHtml(codepoints), "utf8");

  console.log(`[demo] Generated ${outputPath}`);
}

main();
