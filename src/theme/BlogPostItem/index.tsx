import React, { type ReactNode } from 'react';
import BlogPostItem from '@theme-original/BlogPostItem';
import type BlogPostItemType from '@theme/BlogPostItem';
import type { WrapperProps } from '@docusaurus/types';

// 1) Import your DiscourseComments
import DiscourseComments from '@site/src/components/DiscourseComments';

type Props = WrapperProps<typeof BlogPostItemType>;

export default function BlogPostItemWrapper(props: Props): ReactNode {
  return (
    <>
      {/* 2) Render the original blog content */}
      <BlogPostItem {...props} />

      {/* 3) Then render Discourse comments */}
      <DiscourseComments />
    </>
  );
}
