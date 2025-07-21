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

      // Remove existing Discourse iframe if present
      const existingIframe = document.querySelector('#discourse-comments iframe');
      if (existingIframe && existingIframe.parentNode) {
        existingIframe.parentNode.removeChild(existingIframe);
      }

      // Load or reload the embed script
      const existingScript = document.querySelector(`script[src="${forum}javascripts/embed.js"]`);
      if (existingScript) {
        existingScript.parentNode.removeChild(existingScript);
      }

      const script = document.createElement('script');
      script.src = forum + 'javascripts/embed.js';
      script.async = true;
      script.referrerPolicy = 'no-referrer-when-downgrade';
      script.onload = () => console.log('Discourse script loaded successfully');
      script.onerror = () => console.error('Failed to load Discourse script');
      document.body.appendChild(script);

      return () => {
        if (script.parentNode) {
          script.parentNode.removeChild(script);
        }
        // Clean up iframe on unmount
        const iframe = document.querySelector('#discourse-comments iframe');
        if (iframe && iframe.parentNode) {
          iframe.parentNode.removeChild(iframe);
        }
      };
    }
  }, [discourseUrl]);

  return <div id="discourse-comments" style={{ marginTop: '2rem' }} />;
}
