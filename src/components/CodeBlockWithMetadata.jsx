import React from "react";
import CodeBlock from "@theme/CodeBlock";

let uniqueID = (function () {
  let id = 0;
  return function () { return id++; };
})();

export default function CodeBlockWithMetadata({ children, meta, language }) {
  const sourceCode = children.trim();

  let metadata = {};
  try {
    metadata = JSON.parse(meta);
    if (!metadata.compilers) {
      throw new Error("Metadata JSON must include a 'compilers' field.");
    }
  } catch (err) {
    console.error("Invalid metadata JSON in code block:", err);
    return (
      <div style={{ marginBottom: "1em" }}>
        <CodeBlock language={language}>{sourceCode}</CodeBlock>
      </div>
    );
  }

  const lang = (language == "cpp" ? "c++" : language);

  const transformedLibs = (metadata.libs || []).map((lib) => {
    const [id, version] = lib.split("@");
    return { id, version };
  });

  const transformedCompilers = (metadata.compilers || []).map((compiler) => {
    const firstSpace = compiler.indexOf(" ");
    const id = firstSpace === -1 ? compiler : compiler.slice(0, firstSpace);
    const options = firstSpace === -1 ? "" : compiler.slice(firstSpace + 1);
    const libs = transformedLibs;
    const filters = metadata.filters || {};
    return { id, options, libs, filters };
  });

  const executor = {
    compilerVisible: true,
    compilerOutputVisible: true,
    compiler: transformedCompilers[0] || {},
  };

  const session = {
    id: uniqueID(),
    language: lang,
    source: sourceCode,
    compilers: transformedCompilers,
    executors: [],
  };

  const clientState = { sessions: [session] };

  const clientStateB64 = btoa(JSON.stringify(clientState)).replace(/\//g, "%2F");

  return (
    <div style={{ marginBottom: "1em" }}>
      <a
        href={`https://godbolt.org/clientstate/${clientStateB64}`}
        target="_blank"
        rel="noopener noreferrer"
        style={{ display: "inline-block", marginBottom: "0.5em", color: "#0b5ed7" }}
      >
        Try it on Compiler Explorer 🚀
      </a>
      <CodeBlock language={language}>{sourceCode}</CodeBlock>
    </div>
  );
}
