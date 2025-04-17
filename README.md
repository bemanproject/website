# The Beman Project Website

This is the repository hosting the code for the future Beman Website.

We aim to replace the content from [the the Beman website](https://www.bemanproject.org) by deploying the website generated from current repository.

This website is built using [Docusaurus](https://docusaurus.io/), a modern static website generator.
Documentation is written in MDX format.
Building and deploying it requires Node and NPM.

## Installation and development

### Local setup

1. In order to setup the project, you have to install `npm`, `yarn` and `node`. 

For Linux:

```bash
$ sudo apt install nodejs
$ sudo apt install npm
$ npm install yarn
```

For MacOS:

```bash
$ brew install node
$ brew install npm
$ npm install -g yarn
```

For Windows:

```bash
$ winget install OpenJS.NodeJS
$ npm install -g yarn
```

You can verify `yarn` is properly installed using

```bash
yarn --version
```

1. To install the required components for running the website, run the following command inside the cloned repository:
    ```bash
    $ make install
    ```

1. To start a local development server, run:
    ```bash
    $ make start
    ```
    If everything is properly installed, the command  should open a browser window on http://localhost:3000/.
    Most changes are reflected live without having to restart the server.

1. To generate static from the project that can be served using any static contents hosting service (like `gh-pages`).

    ```bash
    $ make build
    ```

### Dev Container

This project includes a development container configuration for VS Code. To use it:

1. Install [Visual Studio Code](https://code.visualstudio.com/) and the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).
2. Open the project in VS Code.
3. When prompted, reopen the project in the dev container.
4. The container will automatically install dependencies and set up the environment.

You can then run the following commands inside the container:

- Start the development server: `make start`
- Build the static site: `make build`

