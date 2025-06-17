import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Mission',
    description: (
      <> The Beman Project’s mission is to support the efficient design and adoption of the highest quality C++ Standard libraries through implementation experience, user feedback, and technical expertise.
      Founded at C++Now in 2024 the project strives to aggregate libraries proposed for ISO standardization making a simple usage experience for the C++ Community to try out new libraries. For library authors we assist by helping to make best modern development practices easy. Including CI, coverage, and packaging.
      This project is a completely volunteer effort. Please connect with us on our discourse if you’d like to help.
      </>
    ),
  },
  {
    title: 'For Library Users',
    description: (
      <>
        The Beman Project strives to be a distributor of a single-download library collection for C++ libraries proposed for standardization. Our goals are to provide stable distributions that match with the latest versions of C++ proposals.
        (check <a href="/libraries"> The Beman Libraries page</a>).
        Please note that it’s early days for the project so we’re still building our tooling and other details – please join the discussion at <a href ="https://discourse.bemanproject.org/"> our discourse </a>.
      </>
    ),
  },
  {
    title: 'For Library Authors',
    description: (
      <>
        Submission into the Beman Project is easy – start a discussion <a href ="https://discourse.bemanproject.org/">on our discourse </a> and the welcome team will help get you started. A general precondition is an intent to submit a library for standardization. If you don’t have repository yet, or you want to upgrade to our standard we can help. Once your library is ready and has a paper, we’ll include it in <a href = "https://github.com/bemanproject"> the Beman super project </a>.
        Please note that it’s early days for the project so we’re still building our tooling and other details.
      </>
    ),
  },
];

function Feature({title, description}: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
