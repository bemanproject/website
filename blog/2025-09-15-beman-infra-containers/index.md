---
slug: beman-infra-containers
authors: ["ptsou"]
tags: ["beman", "beman-infra"]
comments: true
---

# Reliable CI within a shared container infrastructure

A challenge that comes up when creating a library or any other tool is setting up a reliable and consistent [continuous integration](https://en.wikipedia.org/wiki/Continuous_integration) (CI) pipeline for running tests, checks and other tasks. For the Beman Project, it is especially important to have a consistent and reliable CI pipeline that can be used across the full gamut of library projects.

<!-- truncate -->

This is where [bemanproject/infra-containers](https://github.com/bemanproject/infra-containers) comes in. In this post, we'll briefly examine:

- What is `bemanproject/infra-containers`?
- How does it work?
- How is it used?

# What is it?

In short, `bemanproject/infra-containers` is a set of [Docker](https://www.docker.com/) container images that can be reused in CI pipelines across the Beman library projects. These containers are automatically built and published to the GitHub package registry under the [bemanproject organization](https://github.com/orgs/bemanproject/packages). Why do this? There are several advantages:

- These images provide a standard set of tools that are "baked-in" images. There is no further configuration needed in GitHub Actions to get the necessary tooling installed and set up for a particular job.
- This setup gives complete control of specific tools are installed in a particular image.
- The images don't need to be rebuilt for each CI run. They are built once (when changes are made) and then published to a central repository.

The `infra-containers` repository also builds `devcontainer` images which are used as online development environments for the Beman library projects. In addition to the most recent stable versions of GCC and Clang, there are images for the most recent trunk builds of both compilers, as well as one for the [P2996 fork](https://github.com/bloomberg/clang-p2996) of Clang.

# How does it work?

When a change is made to the `Dockerfile` definitions in the [infra-containers](https://github.com/bemanproject/infra-containers) repository, a series of GitHub Actions are started that build and publish the containers to the package registry, both for production and staging use. These actions additionally run weekly or they can be invoked manually if needed.

If you're not familiar with Docker or containers in general, this may seem like magic. To simplify things, you can think of these images as "virtual" operating systems that have been pre-configured with specific versions of certain tools. More specifically, the CI images are built on top of [Gentoo Linux](https://www.gentoo.org/) for [fast turnaround, binary caching, and building compiler forks](https://www.gentoo.org/) while the devcontainer images are built on top of Ubuntu so that Microsoft's devcontainer images can be used as a base.

# How is it used?

The simplest way to understand how the infra-containers are used is to look at an example. We will use bemanproject/task for this purpose as it runs tests with a large and diverse set of configurations. If we look at its CI GitHub actions workflow, we can see a JSON object used to configure CI. Excerpted below is the Clang portion:

```json
{
  "clang": [
    { "versions": ["20"],
      "tests": [
        {"cxxversions": ["c++26"],
          "tests": [
            { "stdlibs": ["libstdc++", "libc++"],
              "tests": [
                "Debug.Default", "Release.Default", "Release.MaxSan",
                "Debug.Werror", "Debug.Dynamic"
              ]
            }
          ]
        },
        { "cxxversions": ["c++23", "c++20"],
          "tests": [
            {"stdlibs": ["libstdc++", "libc++"], "tests": ["Release.Default"]}
          ]
        }
      ]
    },
    { "versions": ["19", "18"],
      "tests": [
        { "cxxversions": ["c++26", "c++23", "c++20"],
          "tests": [
            {"stdlibs": ["libstdc++", "libc++"], "tests": ["Release.Default"]}
          ]
        }
      ]
    },
    { "versions": ["17"],
      "tests": [
        { "cxxversions": ["c++26", "c++23", "c++20"],
          "tests": [{"stdlibs": ["libc++"], "tests": ["Release.Default"]}]
        }
      ]
    }
  ]
}
```

The structure of this configuration allows maintainers to easily produce CI matrices that test large combinations of compilers, standard libraries, and build configurations. The snippet above generates 29 individual CI jobs, each of which takes around 2 minutes to run individually. The compiler name and version specified here is used to determine which CI image to pull.

Hopefully this brief overview of `bemanproject/infra-containers` has given you a better understanding of why it's beneficial, how it works and how it's used. If you previously were not familiar with Docker, the GitHub package registry, or even the concept of containers, I hope this has inspired you to dig deeper into the topic to improve your own CI infrastructure at your company or for your personal projects.

If you're interested in contributing to the Beman Project, please check out the [Beman Project](https://github.com/bemanproject) on GitHub or [join us on Discourse](https://discourse.bemanproject.org/latest) to get involved! Please also checkout the [official website](https://bemanproject.org) for more information on the Beman Project.
