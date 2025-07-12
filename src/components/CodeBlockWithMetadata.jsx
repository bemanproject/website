import React from "react";
import CodeBlock from "@theme/CodeBlock";

export default function CodeBlockWithMetadata({ children, meta, language }) {
  const sourceCode = children.trim();

  let metadata = {};
  try {
    metadata = JSON.parse(meta || "{}");
  } catch (err) {
    console.error("Invalid metadata JSON in code block:", err);
  }

  const lang = (language == "cpp" ? "c++" : language);

  console.log("CodeBlock language:", lang);

  const transformedLibs = (metadata.libs || []).map((lib) => {
    const [id, version] = lib.split("@");
    return { id, version };
  });

  const compilerConfig = {
    id: metadata.compiler,
    libs: transformedLibs,
    options: metadata.options || "",
  };
  const executor = { compiler: compilerConfig };
  const session = {
    id: 1,
    lang,
    source: sourceCode,
    compilers: [],
    executors: [executor],
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
