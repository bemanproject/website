import { themes as prismThemes } from 'prism-react-renderer';
import type { Config } from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';
import { execSync } from 'child_process';

const remarkEmbedder = require('@remark-embedder/core');
const YouTubeTransformer = require('./src/components/youtube-transformer.js');
const GodboltTransformer = require('./src/components/godbolt-transformer.js');

// Note: This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

let branchName = process.env.NETLIFY ? process.env.HEAD : 'main';
// Get the current branch name using git command
try {
  const output = execSync('git branch --show-current', {
    encoding: 'utf-8',
  }).trim();
  if (output) {
    branchName = output;
  }
  console.log(`Current branch: ${branchName}`);
} catch (err) {
  console.error(`Error determining branch name: ${err}`);
}


const config: Config = {
  title: 'The Beman Project',
  tagline:
    'Tomorrow\'s C++ Standard Libraries Today',
  favicon: './img/beman_logo.png',

  // Set the production url of your site here
  url: 'https://bemanproject.org/',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',

  // GitHub pages deployment config.
  organizationName: 'bemanproject', // Usually your GitHub org/user name.
  projectName: 'website', // Usually your repo name.

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  staticDirectories: ['static', 'images'],

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          remarkPlugins: [
            [remarkEmbedder, { transformers: [YouTubeTransformer, GodboltTransformer] }],
          ],
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          remarkPlugins: [
            [remarkEmbedder, { transformers: [YouTubeTransformer, GodboltTransformer] }],
          ],
          // Blogging config
          onInlineTags: 'warn',
          onInlineAuthors: 'warn',
          onUntruncatedBlogPosts: 'throw', // Enforce truncation of blog posts for previews of blog posts.
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    //TODO: Replace with your project's social card
    image: './img/beman_logo.png',
    navbar: {
      title: 'The Beman Project',
      logo: {
        alt: 'The Beman Project Logo',
        src: './img/beman_logo.png',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docsSidebar',
          position: 'left',
          label: 'Docs',
        },
        { to: '/libraries', label: 'Libraries', position: 'left' },
        { to: '/blog', label: 'Blog', position: 'left' },
        {
          'aria-label': 'Discourse Forum',
          'className': 'navbar--discourse-link',
          'href': 'https://discourse.bemanproject.org/',
          'position': 'right',
        },
        {
          'aria-label': 'GitHub Repository',
          'className': 'navbar--github-link',
          'href': 'https://github.com/bemanproject',
          'position': 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      copyright: `Copyright © ${new Date().getFullYear()} The Beman Project. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
    discourseUrl: 'https://discourse.bemanproject.org/', // Temporary change, re-deploy.
  } satisfies Preset.ThemeConfig,
};

export default config;
