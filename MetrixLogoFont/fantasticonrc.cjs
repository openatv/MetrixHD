const codepoints = require("./codepoints.json");

module.exports = {
  inputDir: "./icons",
  outputDir: "./dist/fonts",
  name: "MetrixLogos",

  prefix: "mi",

  fontTypes: ["woff2", "woff", "ttf"],
  assetTypes: [],

  codepoints: codepoints,

  getIconId: ({ basename }) => basename,

  normalize: true,

  fontHeight: 1000,
  descent: 0,
};
