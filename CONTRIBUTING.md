# Contributing to 2 Ship 2 Harkinian

This repository maintains the community continuation of 2Ship by Mythrax. Contributions that improve reliability, build support, documentation, and gameplay are welcome.

## Issues

Search [existing issues](https://github.com/nexium-emu/2ship2harkinian/issues) before opening a report. Use the matching bug, crash, or accuracy template and include:

- The release tag or commit, operating system, graphics backend, and ROM revision.
- Steps to reproduce, expected behavior, and what happened instead.
- Relevant logs from `logs/`, plus screenshots or a short recording when useful.
- Enabled mods and enhancements; for Anchor, include each player's build and connection setup.

Do not attach ROMs or extracted game assets. For a proposed feature, explain the problem and intended behavior before starting a large change.

## Pull requests

1. Fork the repository and create a focused branch from `main`.
2. Follow [the build instructions](docs/BUILDING.md), including submodule setup.
3. Keep each change focused and follow the surrounding code style. Apply the repository's `.clang-format` to changed C and C++ code without reformatting unrelated files.
4. Build and test the affected behavior. For changes shared across platforms, check Windows and any other affected platforms you can access; identify anything untested in the pull request. Add regression tests when practical for the change.
5. Open a pull request against `main` describing the problem, resulting behavior, and validation performed. Let CI finish and address failures before merging.

Preserve existing authorship and license notices. When importing upstream work, identify its source and author in the pull request; keep **garrettjoecox** credited for Anchor. Avoid mixing generated build outputs, local configuration, or saves into source changes.

## Commit style

Use focused commits with a Conventional Commit title of **50 characters or fewer**, including the prefix. Commit messages are **title only**: no body, generated attribution, or co-author trailers. Put review context and test results in the pull request instead. Credit imported Anchor work to its developer in the title when appropriate.

```text
feat: add Anchor by garrettjoecox
fix: restore controller mappings on startup
ci: publish tagged release packages
docs: clarify Windows build requirements
chore: update dependency pins
```

Use `feat` for new behavior, `fix` for a bug, `ci` for automation, `docs` for documentation, and `chore` for maintenance. Choose a short description that explains the actual change.

## Releases

Release preparation and publishing are described in [RELEASING.md](docs/RELEASING.md). Keep release changes reviewable, use the CI-produced packages, and record user-visible changes in the release notes.
