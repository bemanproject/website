# The Beman Project Website

This is the repository hosting the code for the future Beman Website.

We aim to replace the content from the [existing Beman website](https://www.bemanproject.org) by deploying the website generated from current repository.

<!-- TODO: Remove this after the website deployment switch. -->
> Note: https://bemanproject.github.io/website/ is used a temporary domain while we boostrap the new website infrastructure.

This website is built using [Docusaurus](https://docusaurus.io/), a modern static website generator.
Documentation is written in MDX format.
Building and deploying it requires Node and NPM.

## Add a blog post

1. Clone the repository and a create new branch (which is required to get a CI preview deployment with your changes).

2. Create a directory`blog/YYYY-MM-DD-tile-of-post/` and write the blog post Markdown content in `index.md`:

Example:

```shell
$ tree blog/2000-10-30-my-blog-example/
blog/2000-10-30-my-blog-example/
├── images
│   └── beman_logo.png # images are stored in ./images/
└── index.md           # actual blog post content

2 directories, 2 files
```

3. Add your blog post content - full example in [PR #46](https://github.com/bemanproject/website/pull/46/):

```shell
$ cat blog/2000-10-30-my-blog-example/index.md
---
slug: my-blog-example-slug    # Slug example. Remove this comment if using this template.
authors: [neatudarius]        # Authors list with entrie from blog/authors.yml. Remove this comment if using this template.
tags: ["cpp26", "beman-docs"] # Blog post valid tags from blog/tags.yml. Remove this comment if using this template.
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
socials:        # Include your socials (like your Github, X, Linkedin etc)
    github: <yourGithubId>
```

Full example also in [PR #46](https://github.com/bemanproject/website/pull/46/).
</details>


4. Open a `DRAFT PR` and `wait` up to one minute for a preview deployment of your blog post.

* Draft PR example - [#46](https://github.com/bemanproject/website/pull/46).

* Click on the `Deploy Preview` URL - e.g., https://deploy-preview-46--bemanproject.netlify.app/

* Successful CI preview deployment example:

![CI preview deployment success message](./images/tutorial/add-a-blog/ci-preview-deployment-success-message.gif)

* Test your deployment.

<details>
<summary> [DEBUG] Inspect CI preview deployment error logs. </summary>

The CI preview deployment logs should be public. Please ping a codeowner otherwise.

* `DRAFT` PR example with CI preview deployment error  - [#49](https://github.com/bemanproject/website/pull/49).

* Click on the `Latest deploy log` URL - e.g., https://app.netlify.com/sites/bemanproject/deploys/6809108974fd910008633aa9.

* Logs inspect example:

![](./images/tutorial/add-a-blog/ci-preview-deployment-failure-message.gif)

* Fix the error, commit and push the changes. Wait for new deployment.

> If you need to browse through more recent CI preview deployments logs use https://app.netlify.com/sites/bemanproject/deploys/. Note: netlify provides a single a single CI preview deployment for each PR - latest commit, but stores logs for multiple ones.


</details>

<details>
<summary> [DEBUG] Inspect local deployment error logs. </summary>

* On local setup, run `make` (see [Local development](#local-development)) and check if there is any error in the console - example:

```shell
$ make
...
[INFO] Starting the development server...
...
[ERROR] Error: Processing of blog source file path=2000-10-30-my-blog-example/index.md failed.
    at doProcessBlogSourceFile (/Users/dariusn/dev/dn/git/Beman/website/node_modules/@docusaurus/plugin-content-blog/lib/blogUtils.js:268:19)
    at async Promise.all (index 0)
    ... 10 lines matching cause stack trace ...
    at async file:///Users/dariusn/dev/dn/git/Beman/website/node_modules/@docusaurus/core/bin/docusaurus.mjs:44:3 {
  [cause]: Error: Blog author with key "neatudarius" not found in the authors map file.
  Valid author keys are:
  - JeffGarland
  - dabrahams
  - DavidSankel
```

* Fix the error, re-deploy the local website.

* Commit and push the changes. Wait for a new CI preview deployment.

</details>

5. After you got `a succesful CI preview deployment`, update the PR to be ready for review and add [@leads](https://github.com/orgs/bemanproject/teams/leads) /[@core-reviewers](https://github.com/orgs/bemanproject/teams/core-reviewers).

6. Apply the review feedback. Get approval. Merge the PR.

<!-- TODO: Replace with https://www.bemanproject.org/ after the website deployment switch. -->
7. The updates are automatically deployed to the productiom website after few minutes - check https://bemanproject.github.io/website/.

## Local development

### Install dependencies

In order to setup the project, you have to install `npm`, `yarn` and `node`.

```shell
$ make install
```

You can verify `yarn` is properly installed using

```shell
yarn --version
```

If this fails, please check manual instructions:

<details>
<summary> Dev Container instructions </summary>

This project includes a development container configuration for VS Code. To use it:

1. Install [Visual Studio Code](https://code.visualstudio.com/) and the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).
2. Open the project in VS Code.
3. When prompted, reopen the project in the dev container.
4. The container will automatically install dependencies and set up the environment.
5. Go to the [Start local server](#start-local-sever) section.

</details>

<details>
<summary> Linux instructions</summary>

```shell
$ sudo apt install nodejs
$ sudo apt install npm
$ npm install yarn
```

</details>

<details>
<summary> MacOS instructions</summary>

```shell
$ brew install node
$ brew install npm
$ npm install -g yarn
```

</details>

<details>
<summary> Windows instructions</summary>

```shell
$ winget install OpenJS.NodeJS
$ npm install -g yarn
```

</details>

### Start local sever

To start a local development server, run:

```shell
$ make start
```

If everything is properly installed, the command  should open a browser window on http://localhost:3000/.

Most changes are reflected live without having to restart the server.


### Generate static content for GitHub Pages deployment

To generate static from the project that can be served using any static contents hosting service (like `gh-pages`).

```shell
$ make build
```
