import React, { useEffect } from 'react';
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
      const forum = discourseUrl.endsWith('/') ? discourseUrl : `${discourseUrl}/`;
      const path = window.location.pathname;

      // Use production URL only if not localhost
      const isLocal = window.location.hostname === 'localhost';
      const base = isLocal
        ? 'https://bemanproject.org'
        : `${window.location.origin}`;

      win.DiscourseEmbed = {
        discourseUrl: forum,
        discourseEmbedUrl: `${base}${path}`,
      };

      const script = document.createElement('script');
      script.src = `${forum}javascripts/embed.js`;
      script.async = true;
      document.body.appendChild(script);
    }
  }, [discourseUrl]);

  return <div id="discourse-comments" style={{ marginTop: '2rem' }} />;
}
