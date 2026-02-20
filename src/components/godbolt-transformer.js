const GodboltTransformer = {
  name: "Godbolt",
  shouldTransform(url) {
    return url.includes("godbolt.org");
  },
  getHTML(url) {
    const fullUrl = url.includes("godbolt.org/#")
      ? url.replace("godbolt.org/#", `godbolt.org/e?hideEditorToolbars=false#`)
      : url;

    return `
      <iframe
        src="${fullUrl}"
        style="margin:auto; width:98%; height:800px; display:block; overflow:hidden;"
        frameBorder=0
      ></iframe>
    `;
  },
};

module.exports = GodboltTransformer;
