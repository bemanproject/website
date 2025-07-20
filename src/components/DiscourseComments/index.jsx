import React, { useEffect } from 'react';
import { useLocation } from '@docusaurus/router';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';

export default function DiscourseComments() {
  const {
    siteConfig: {
      url,
      themeConfig: { discourseUrl },
    },
  } = useDocusaurusContext();
  const { pathname } = useLocation();

  // If discourseUrl is not defined, return null to skip rendering
  if (!discourseUrl) {
    console.log('DiscourseComments: No discourseUrl defined in themeConfig, skipping render');
    return null;
  }

  useEffect(() => {
    const baseUrl = url.endsWith('/') ? url.slice(-1, 1) : url; // Ensure baseUrl does not end with a slash
    const forum = discourseUrl;
    const embedUrl = baseUrl + window.location.pathname;

    console.log('Discourse comments component mounted');
    console.log('Base URL:', baseUrl);
    console.log('Current pathname:', pathname);
    console.log('Discourse URL:', forum);
    console.log('Embed URL:', embedUrl);

    // Update or set DiscourseEmbed
    window.DiscourseEmbed = {
      discourseUrl: forum,
      discourseEmbedUrl: embedUrl,
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
  }, [pathname, discourseUrl]); // Depend on pathname to re-run on route changes

  return <div id="discourse-comments" />;
}
