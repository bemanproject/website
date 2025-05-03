// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

const Godbolt = ({ url, readOnly=false }) => {
  const readOnlyParam = readOnly ? "readOnly=true&" : "";
  const fullUrl = url.includes("godbolt.org/#")
    ? url.replace(
        "godbolt.org/#",
        `godbolt.org/e?${readOnlyParam}hideEditorToolbars=false#`,
      )
    : url; // Keep short links unchanged

  return (
    <iframe
      frameBorder="0"
      style={{
        margin: "auto",
        display: "block",
        overflow: "hidden",
        height: "800px",
        width: "90%",
      }}
      src={fullUrl}
    ></iframe>
  );
};

export default Godbolt;
