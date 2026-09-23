# Maintaining and releasing 2Ship

Development happens on `main`. Keep changes focused, use the commit format in
[CONTRIBUTING.md](../CONTRIBUTING.md), and merge pull requests after the applicable
checks pass. Release automation uses the repository's `GITHUB_TOKEN`; no personal
access token or external release service is required.

## Build and release channels

| Trigger | Result |
| --- | --- |
| Branch push or pull request | Validate workflows and release tools; build Windows x64, Linux x86-64, and universal macOS packages |
| Successful push build on `main` | Publish a `preview-<12-character-commit>` prerelease |
| Push `vX.Y.Z` | Build all platforms and publish a stable release |
| Push `vX.Y.Z-rc.1` or another SemVer prerelease tag | Build all platforms and publish a versioned prerelease |
| Pull request | Also check formatting of changed C/C++ files and link successful build artifacts on the PR |

Only the current `main` commit is eligible for a new preview; superseded builds
are skipped. Previews are separate releases with fixed source commits. They do not replace the
latest stable release or move an existing tag. Set the repository Actions variable
`ENABLE_PREVIEW_RELEASES` to `false` to pause automatic preview publishing.

Each release includes the three native packages, `build-info.json`, and
`SHA256SUMS`. The manifest identifies the full source commit and build run. Windows
ZIP validation checks integrity, required runtime files, and accidental ROM data.
The packages include `2ship.o2r`; players supply their own supported game ROM.
Anchor players should download the same release on every participating machine.

To verify downloads, place the assets and `SHA256SUMS` together and run
`sha256sum --check SHA256SUMS` on Linux or `shasum -a 256 --check SHA256SUMS` on
macOS. On Windows, run `Get-FileHash .\<downloaded-package>.zip -Algorithm SHA256`
in PowerShell and compare the hash with that filename's line in `SHA256SUMS`.

## Publish a versioned release

1. Update `project(2s2h VERSION X.Y.Z ...)` in the root `CMakeLists.txt`. Use a new
   version for each stable release; do not reuse an upstream or published tag.
2. Merge the release changes into `main`, wait for CI to pass, and test the preview
   on the supported platforms. Check startup, extraction, saves, and Anchor with
   matching builds. CI does not run the game or verify online co-op.
3. Create an annotated tag on that reviewed commit and push it. For example,
   after setting the project version to `5.0.2`:

   ```sh
   git switch main
   git pull --ff-only origin main
   git tag -a v5.0.2 -m "Release 5.0.2"
   git push origin v5.0.2
   ```

   To test the release process first, use `v5.0.2-rc.1` with the same project
   version. The workflow rejects tags whose base version differs from CMake.
4. Follow the **releases** workflow in Actions. It publishes only after all builds
   and package checks pass and all assets upload to a draft. Stable notes are
   generated from GitHub's release history; PR labels group changes using
   [.github/release.yml](../.github/release.yml).

## Recover a failed run

Fix build failures before publishing another version. For a transient failure,
use **Re-run failed jobs** or **Re-run all jobs** on the existing release run.
Publication can resume an unpublished draft for the same source commit. It never
overwrites a published release. A tag moved during a build is rejected.

The release workflow also supports manual dispatch on an existing version tag:

```sh
gh workflow run release.yml --ref v5.0.2
```

Dispatching it on a branch is rejected. Rerun the original `generate-builds` run
to retry a preview while its commit is still the tip of `main`. If its artifacts
have expired, rerun the complete build first.
Keep version tags and published releases intact; ship a new version for fixes.

## Repository configuration

- Keep `main` as the default branch so workflow-run handlers and contributor links
  use the maintained source.
- Enable GitHub Actions and allow the actions referenced by the workflows. The
  default token can remain read-only: only release publication requests
  `contents: write`, and the PR artifact commenter requests `pull-requests: write`.
- Protect `main` with reviewed pull requests and the relevant build/format checks
  when the contributor workflow is established. Avoid bypassing failing checks
  to ship a release.
- Dependabot checks GitHub Actions weekly. Review grouped updates and merge after
  CI passes. C/C++ dependency and submodule updates still need maintainer review.

The workflows share the build definition through GitHub's
[reusable workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows).
Release permissions follow GitHub's
[token authentication guidance](https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication).
