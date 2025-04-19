import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx(styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <div className="hero__subtitle">
          <div className={styles.taglineContainer}>
            <img
              src="./img/logo.png"
              alt="Left Image"
              style={{ width: '400px', height: '400px' }}
            />
            <span>{siteConfig.tagline}</span>
            <img
              src="./img/logo.png"
              alt="Right Image"
              style={{ width: '400px', height: '400px' }}
            />
          </div>
        </div>
        <div className={styles.buttons}></div>
      </div>
    </header>
  );
}


export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="Beman website/>"
    >
      <HomepageHeader />
      <main>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
