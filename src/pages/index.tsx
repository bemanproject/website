import type { ReactNode } from "react";
import clsx from "clsx";
import Link from "@docusaurus/Link";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import Layout from "@theme/Layout";
import HomepageFeatures from "@site/src/components/HomepageFeatures";
import Heading from "@theme/Heading";

import styles from "./index.module.css";

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <header className={clsx(styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <div className="hero__subtitle">
          <div className={styles.taglineContainer}>
            <img
              /* TODO: check if we can use SVG images*/
              src="./img/beman_logo.png"
              alt="Left Logo"
              className={styles.leftLogo}
            />
            <span className={styles.taglineText}>{siteConfig.tagline}</span>
            <img
              /* TODO: check if we can use SVG images*/
              src="./img/beman_logo_reversed.png"
              alt="Right Logo"
              className={styles.rightLogo}
            />
          </div>
        </div>
        <div className={styles.buttons}></div>
      </div>
    </header>
  );
}

export default function Home(): ReactNode {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="The Beman Project/>"
    >
      <HomepageHeader />
      <main>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
