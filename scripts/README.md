# Scripts

This directory contains scripts for the Beman Project website.

## sync-docs.py

This script is used to sync the Beman Project documentation from the `beman/` repo to this `website/` repo.

Steps:

1. Copy images from `beman/images/` to `website/images/` and `website/static/images/`.
2. Copy documentation from `beman/docs/` to `website/docs/`.
3. Insert sidebar position into the documentation files.

```shell
$ python3 scripts/sync-docs.py --help
usage: sync-docs.py [-h] beman_repo_path

positional arguments:
  beman_repo_path  path to root of beman repo to clone from

optional arguments:
  -h, --help       show this help message and exit

$ python3 scripts/sync-docs.py ../beman
Copying images from ../beman/images to /Users/dariusn/dev/dn/git/Beman/website/images
Copying images from ../beman/images to /Users/dariusn/dev/dn/git/Beman/website/static/images
Copying ../beman/docs/README.md to /Users/dariusn/dev/dn/git/Beman/website/docs/README.md
Inserting sidebar position 1 into /Users/dariusn/dev/dn/git/Beman/website/docs/README.md
Copying ../beman/docs/beman_library_maturity_model.md to /Users/dariusn/dev/dn/git/Beman/website/docs/beman_library_maturity_model.md
Inserting sidebar position 2 into /Users/dariusn/dev/dn/git/Beman/website/docs/beman_library_maturity_model.md
Copying ../beman/docs/beman_standard.md to /Users/dariusn/dev/dn/git/Beman/website/docs/beman_standard.md
Inserting sidebar position 3 into /Users/dariusn/dev/dn/git/Beman/website/docs/beman_standard.md
Copying ../beman/docs/mission.md to /Users/dariusn/dev/dn/git/Beman/website/docs/mission.md
Inserting sidebar position 4 into /Users/dariusn/dev/dn/git/Beman/website/docs/mission.md
Copying ../beman/docs/faq.md to /Users/dariusn/dev/dn/git/Beman/website/docs/faq.md
Inserting sidebar position 5 into /Users/dariusn/dev/dn/git/Beman/website/docs/faq.md
Copying ../beman/docs/governance.md to /Users/dariusn/dev/dn/git/Beman/website/docs/governance.md
Inserting sidebar position 6 into /Users/dariusn/dev/dn/git/Beman/website/docs/governance.md
Copying ../beman/docs/code_of_conduct.md to /Users/dariusn/dev/dn/git/Beman/website/docs/code_of_conduct.md
Inserting sidebar position 7 into /Users/dariusn/dev/dn/git/Beman/website/docs/code_of_conduct.md
```
