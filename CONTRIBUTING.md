# Development

## Install dependencies

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
5. Go to the [Start local server](#start-local-server) section.

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

## Start local server

To start a local development server, run:

```shell
$ make start
```

If everything is properly installed, the command should open a browser window on http://localhost:3000/.

Most changes are reflected live without having to restart the server.

## Generate static content for GitHub Pages deployment

To generate static from the project that can be served using any static contents hosting service (like `gh-pages`).

```shell
$ make build
```
