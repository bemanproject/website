# Beman Website

This is the repository hosting Beman documentation.

It is deployed [on the Beman website](https://www.bemanproject.org) by using Github Pages.

This website is built using [Docusaurus](https://docusaurus.io/), a modern static website generator.
Documentation is written in MDX format.
Building and deploying it requires Node and NPM.

<details>
<summary>Installation and local development</summary>

1. In order to setup the project, you have to install `npm`, `yarn` and `node`. 

For Linux:

```bash
$ sudo apt install nodejs;
$ sudo apt install npm;
$ npm install yarn;
```

For MacOS:

```bash
$ brew install node; 
$ brew install npm;
$ npm install -g yarn;
```

You can verify `yarn` is properly installed using

```bash
yarn --version
```

1. To install the required components for running the website, run the following command inside the cloned repository:
    ```bash
    $ yarn
    ```

1. To start a local development server, run:
    ```bash
    $ yarn start
    ```
    If everything is properly installed, the command  should open a browser window on http://localhost:3000/.
    Most changes are reflected live without having to restart the server.

1. To generate static from the project that can be served using any static contents hosting service (like `gh-pages`).

    ```bash
    $ yarn build
    ```

</details>
