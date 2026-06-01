# The Beman Project Website

This is the repository hosting the code for the future Beman Website: https://bemanproject.org/.

This website is built using [MkDocs](https://www.mkdocs.org/), a static website generator.
Documentation is written in Markdown.
Building and deploying it requires Python, Node.js/npm, and the dependencies listed
in `requirements.txt` and `package-lock.json`.

## Add a blog post

1. Repository setup: `create a local clone` or `open in Codespaces`.

2. Create a directory having an `index.md` file using this pattern: `blog/YYYY-MM-DD-tile-of-post/index.md`:

Example:

```shell
$ tree blog/2000-10-30-my-blog-example/
blog/2000-10-30-my-blog-example/
├── images
│   └── beman_logo.png # images are stored in ./images/
└── index.md           # actual blog post content

2 directories, 2 files
```

3. Add your full Markdown blog post content inside the `index.md` file.

Example

```shell
$ cat blog/2000-10-30-my-blog-example/index.md
---
slug: my-blog-example-slug    # Slug example. Remove this comment if using this template.
authors: [neatudarius]        # Authors list with entrie from blog/authors.yml. Remove this comment if using this template.
tags: ["cpp26", "beman-docs"] # Blog post valid tags from blog/tags.yml. Remove this comment if using this template.
comments: true                # If comments should be enabled for this blog post. Default: true.
---

# My Blog Example

This is my blog example.

Here I can write Markdown content.
[...]
```

<details>
<summary> Add the author if not already present in blog/authors.yml  </summary>

If this is your first time writing a blog post, you have to add yourself as an author in the `blog/authors.yml` file. Add a new entry using the following format:

```shell
<AuthorTag>:    # Your author tag, this is what you will use in the header section for a log.
name:           # Your Real Name.
title:          # Your title, how do you want to be recognized by other people.
url:            # Your Github profile page
image_url:      # A url for your profile image (for Github profile image: go to your profile, click on your image and open it in a new tab, copy the link).
page: true      # If an author page should be generated for you.
socials:        # [optional] Include your socials (like your Github, X, Linkedin etc)
    github: <yourId>      # [optional] Add GitHub page.
    linkedin: <yourId>    # [optional] Add LinkedIn page.
    x: <yourId>           # [optional] Add X page.
```

</details>

> Note: The Discourse comments plugin only works for production website (a.k.a. https://bemanproject.org/). You cannot test it locally or on preview deployments. Check [Integrate Discourse comment feature for blog posts](https://github.com/bemanproject/website/issues/25) for more details.

4. Open a `DRAFT PR` and `wait` up to one minute for a preview deployment of your blog post.

- Draft PR example: [Add blog post: My Blog Example #54](https://github.com/bemanproject/website/pull/54/).

- Click on the `Deploy Preview` URL (format `https://deploy-preview-${PR NUMBER}--bemanproject.netlify.app/`).

- Successful CI preview deployment example:

![CI preview deployment success message](./images/tutorial/add-a-blog/ci-preview-deployment-success-message.gif)

- Test your deployment.

<details>
<summary> [DEBUG] Inspect CI preview deployment error logs. </summary>

The CI preview deployment logs should be public. Please ping a codeowner otherwise.

- `DRAFT` PR example with CI preview deployment error - [#49](https://github.com/bemanproject/website/pull/49).

- Click on the `Latest deploy log` URL - e.g., https://app.netlify.com/sites/bemanproject/deploys/6809108974fd910008633aa9.

- Logs inspect example:

![CI preview deployment failure message](./images/tutorial/add-a-blog/ci-preview-deployment-failure-message.gif)

- Fix the error, commit and push the changes. Wait for new deployment.

> If you need to browse through more recent CI preview deployments logs use https://app.netlify.com/sites/bemanproject/deploys/. Note: netlify provides a single a single CI preview deployment for each PR - latest commit, but stores logs for multiple ones.

</details>

<details>
<summary> [DEBUG] Inspect local deployment error logs. </summary>

- On local setup, run `make` (see [CONTRIBUTING.md](CONTRIBUTING.md#development)) and check if there is any error in the console.

- Fix the error, re-deploy the local website.

- Commit and push the changes. Wait for a new CI preview deployment.

</details>

5. After you got `a succesful CI preview deployment`, update the PR to be ready for review and add [@leads](https://github.com/orgs/bemanproject/teams/leads) /[@core-reviewers](https://github.com/orgs/bemanproject/teams/core-reviewers).

6. Apply the review feedback. Get approval. Merge the PR.

<!-- TODO: Replace with https://www.bemanproject.org/ after the website deployment switch. -->

7. The updates are automatically deployed to the production website after a few minutes - check https://bemanproject.github.io/website/.

## Development

Local setup, dependencies, and running the site: see **[CONTRIBUTING.md](CONTRIBUTING.md#development)**.

`make` and `make start` are equivalent: both install dependencies, build the
composed MkDocs + Antora site into a staging directory, and serve that static
output locally. MkDocs owns the homepage, library index, talks, and blog.
Antora owns `/docs`, including converted library READMEs, extra Markdown pages,
and MrDocs API reference pages.

### Antora documentation

The staged website includes Antora-generated documentation under `/docs`.
Pandoc converts configured Markdown pages to AsciiDoc. MrDocs emits API
reference AsciiDoc, and Antora Collector imports those pages into each library
component.

The library list and extra Markdown pages come from
`beman_libraries_to_import.yaml`. Keep library repos adjacent to this website
repo, e.g. `../optional`, `../execution`, `../task`. Top-level library
`README.md` files are included automatically on each library overview page.

Required tools:

- Node.js/npm dependencies from `package-lock.json`
- `pandoc` on `PATH`
- `mrdocs` on `PATH`

With the `beman` micromamba environment active:

```shell
$ make start
$ make build
```

To add a library, edit `beman_libraries_to_import.yaml`, put the repo next to
`website`, then run `make start`.

The first Antora build downloads the default UI bundle; later builds reuse the
local Antora cache under `$TMPDIR/beman-website-work/antora-cache`.

## Automated `gh-pages` publishing

GitHub Actions publishes this site to the `gh-pages` branch on:

- pushes to `main`
- a 6-hour schedule (`0 */6 * * *`)
- manual dispatch

```shell
$ PAGES_DEPLOY=true python3 scripts/run-staged-website.py build \
    --repos-root /tmp/beman-external --clone-missing --update-repos
```

For builds published from a fork or any GitHub Pages project site, set the site
URL and base URL to match the repository path. Example:

```shell
$ BEMAN_SITE_URL="https://<your_username>.github.io" \
  BEMAN_BASE_URL="/beman-website/" \
  BEMAN_GITHUB_ORG="<your_username>" \
  BEMAN_GITHUB_REPO="beman-website" \
  python3 scripts/run-staged-website.py build --repos-root ..
```
