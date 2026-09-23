# 2 Ship 2 Harkinian

**Continued by Mythrax.** This repository is a community continuation of 2 Ship 2 Harkinian (2S2H), the PC port of *The Legend of Zelda: Majora's Mask*. It preserves the work of the original developers while maintaining builds, fixing bugs, and developing the included Anchor multiplayer integration.

[Download releases](https://github.com/nexium-emu/2ship2harkinian/releases) · [Build status](https://github.com/nexium-emu/2ship2harkinian/actions) · [Report an issue](https://github.com/nexium-emu/2ship2harkinian/issues) · [Build from source](docs/BUILDING.md)

## Getting started

2Ship does not include the original game's assets. You must provide your own supported ROM dump. Compare its SHA-1 hash with [the supported ROM list](docs/supportedHashes.json).

1. Download the package for your platform from [Releases](https://github.com/nexium-emu/2ship2harkinian/releases) and extract it into its own folder.
2. Launch the application and follow the extraction prompts to create `mm.o2r` from your ROM.
3. Press **F1** to open the in-game menu and configure controls, graphics, and enhancements.

On Windows, launch `2ship.exe`. On Linux, place the supported ROM beside the AppImage, make it executable if needed, and run it. On macOS, open `2s2h.app` and select your ROM when prompted. See the instructions attached to each release for package-specific requirements.

Back up your saves and configuration before updating, especially when trying a preview build. Keep the executable and bundled `2ship.o2r` from the same package together.

## Anchor multiplayer

This continuation includes **Anchor Beta**, developed by [garrettjoecox](https://github.com/garrettjoecox/2ship2harkinian/tree/anchor), with its Sail networking prerequisites.

Open **F1 → Network → Anchor** for the connection settings and co-op instructions. All players should use the **same release package**: Anchor checks build compatibility, including the source revision. Networking is disabled by default; enabling it saves the setting for later launches. Anchor remains beta software, so report reproducible multiplayer issues with the package version and setup used by each player.

## Controls and customization

| N64 control | Default keyboard input |
| --- | --- |
| A / B / Z | X / C / Z |
| Start | Space |
| Analog stick | WASD |
| C buttons | Arrow keys |
| D-Pad | T / F / G / H |

**F1** toggles the menu, **F11** toggles fullscreen, **Tab** toggles alternate assets, and **Ctrl+R** resets the game. Controller mappings can be configured in the menu.

The available graphics backends are DirectX 11 on Windows, OpenGL, and Metal on macOS. Change the backend in the menu and restart to apply it.

Place custom `.o2r` or `.otr` asset packs in the `mods` folder. Music customization is documented in the [streamed music guide](docs/CUSTOM_STREAMED_MUSIC.md) and [sequenced music guide](docs/CUSTOM_SEQUENCED_MUSIC.md).

## Development and releases

Use [stable releases](https://github.com/nexium-emu/2ship2harkinian/releases) for regular play. Successful builds of `main` publish previews named `preview-<commit>`. Version tags publish stable releases or pre-releases, depending on the tag. Preview packages and [CI artifacts](https://github.com/nexium-emu/2ship2harkinian/actions) are for testing changes; include the tag or commit when reporting a problem.

Release packages include SHA-256 checksums and build information. See [the release guide](docs/RELEASING.md) for supported tag formats and how to verify a download.

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution workflow, [BUILDING.md](docs/BUILDING.md) for local builds, and [RELEASING.md](docs/RELEASING.md) for the release process. Please file issues for this continuation in [this repository](https://github.com/nexium-emu/2ship2harkinian/issues).

## Credits and license

2Ship exists because of the original 2 Ship 2 Harkinian developers and contributors, including Archez, ProxySaw, Eblo, and BalloonDude, the Zelda decompilation community, and the libultraship developers. Their work and authorship remain in the project history. Anchor credit belongs to **garrettjoecox**. This community continuation is maintained by **Mythrax** and is separate from the upstream project.

Project code is available under [CC0 1.0](LICENSE); bundled dependencies retain their own licenses. The original game and its assets are not included.

<a href="https://github.com/Kenix3/libultraship/">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./docs/poweredbylus.darkmode.png">
    <img alt="Powered by libultraship" src="./docs/poweredbylus.lightmode.png">
  </picture>
</a>
