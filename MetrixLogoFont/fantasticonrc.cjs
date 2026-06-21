const codepoints = require("./codepoints.json");

module.exports = {
  inputDir: "./icons",
  outputDir: "../usr/share/enigma2/MetrixHD/fonts",
  name: "MetrixLogos",

  prefix: "mi",

  fontTypes: ["ttf"],
  assetTypes: [],

  codepoints: codepoints,

  getIconId: ({ basename }) => basename,

  normalize: true,

  fontHeight: 1000,
  descent: 0,
};
