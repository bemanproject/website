// plugins/remark-codeblock-meta.js

// Try importing visit using both methods
let visit;
try {
  // ES Modules style import
  ({ visit } = require("unist-util-visit"));
} catch (err) {
  // Fallback if not available like that
  visit = require("unist-util-visit").default || require("unist-util-visit");
}

module.exports = function remarkCodeblockMeta() {
  return (tree) => {
    visit(tree, "code", (node) => {
      const meta = node.meta?.trim();
      if (meta && meta.startsWith("{") && meta.endsWith("}")) {
        // Attach metadata and change node to use our custom component
        node.data = {
          hName: "CodeBlockWithMetadata",
          hProperties: {
            meta,
            language: node.lang,
            children: node.value,
          },
        };
      }
    });
  };
};
