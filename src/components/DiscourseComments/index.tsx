import React, { useEffect } from 'react';
import type { Props } from '@docusaurus/types';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';

type DiscourseEmbedWindow = Window & {
  DiscourseEmbed?: {
    discourseUrl: string;
    discourseEmbedUrl: string;
    discourseTopicTitle?: string;
  };
};

export default function DiscourseComments(): JSX.Element {
  const {
    siteConfig: {
      themeConfig: { discourseUrl },
    },
  } = useDocusaurusContext<{ discourseUrl: string }>();

  useEffect(() => {
    const win = window as DiscourseEmbedWindow;
    if (!win.DiscourseEmbed) {
      // normalize URL to end with a single slash
      const forum = discourseUrl.replace(/\/+$/, '') + '/';
      win.DiscourseEmbed = {
        discourseUrl: forum,
        discourseEmbedUrl: window.location.href,
      };
      const script = document.createElement('script');
      script.src = forum + 'javascripts/embed.js';
      script.async = true;
      document.body.appendChild(script);
    }
  }, [discourseUrl]);

  return <div id="discourse-comments" style={{ marginTop: '2rem' }} />;
}
