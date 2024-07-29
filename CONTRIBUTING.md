# Contributing

You can use your favorite Python version manager (asdf, pyenv, ...) as long
as it follows `.python-version`.

Install [pre-commit](https://pre-commit.com/) if it is not already installed.

Install pre-commit hooks in your git working copy:

    pre-commit install --hook-type pre-commit --hook-type commit-msg

Use [Conventional Commits](https://www.conventionalcommits.org/).

Create documentation as part of you pull request:

    pdm docs
