import React from "react";
import { useLocation } from "@docusaurus/router";
import BlogPostItem from "@theme-original/BlogPostItem";
import DiscourseComments from "@site/src/components/DiscourseComments";

export default function BlogPostItemWrapper(props) {
  const { pathname } = useLocation();
  // Safely access frontMatter from props.children.type
  const frontMatter = props.children?.type?.frontMatter || {};

  // Only render comments for individual blog posts (not list or archive pages)
  const isBlogListPage =
    pathname === "/blog" ||
    pathname.startsWith("/blog/archive") ||
    pathname.startsWith("/blog/tags");
  const commentsEnabled =
    frontMatter.comments === true || frontMatter.comments === "true";
  const shouldShowComments =
    commentsEnabled && !isBlogListPage && frontMatter.slug;

  return (
    <>
      <BlogPostItem {...props} />
      {shouldShowComments && (
        <DiscourseComments key={frontMatter.slug || "discourse"} />
      )}
    </>
  );
}