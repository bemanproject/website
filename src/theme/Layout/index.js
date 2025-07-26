import React from 'react';
import Layout from '@theme-original/Layout';
import CodeBlockWithMetadata from '@site/src/components/CodeBlockWithMetadata';
import { MDXProvider } from '@mdx-js/react';

export default function LayoutWrapper(props) {
  return (
    <MDXProvider
      components={{
        CodeBlockWithMetadata,
      }}
    >
      <Layout {...props} />
    </MDXProvider>
  );
}
