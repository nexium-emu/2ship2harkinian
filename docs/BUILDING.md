# Building 2 Ship 2 Harkinian

## Windows

Requires:
  * At least 8GB of RAM (machines with 4GB have seen compiler failures)
  * Visual Studio 2022 or 2026 Community Edition with the C++ feature set
  * One of the Windows SDKs that comes with Visual Studio, for example the current Windows 10 version 10.0.19041.0
  * The matching MSVC build tools: v143 for Visual Studio 2022 or v145 for Visual Studio 2026
  * Python 3 (can be installed manually or as part of Visual Studio)
  * Git (can be installed manually or as part of Visual Studio)
  * CMake 3.26 or newer (can be installed via chocolatey or manually); Visual Studio 2026 requires CMake 4.2 or newer

During installation, check the "Desktop development with C++" feature set:

![image](https://user-images.githubusercontent.com/30329717/183511274-d11aceea-7900-46ec-acb6-3f2cc110021a.png)
Doing so should also check one of the Windows SDKs by default. Then, in the installation details in the right-hand column, make sure you also check the matching v143 or v145 toolset. This is often done by default.

It is recommended that you install Python and Git standalone, the install process in VS Installer has given some issues in the past.

If MSYS2 or devkitPro is installed, put native Git for Windows and Windows Python before their MSYS equivalents on `PATH`. To select Windows Python explicitly, append `-DPython3_EXECUTABLE="C:/path/to/python.exe"` to the configure command, using your installed Python path.

1. Clone the 2 Ship 2 Harkinian repository

_Note: Be sure to either clone with the ``--recursive`` flag or do ``git submodule update --init`` after cloning to pull in the libultraship submodule!_

2. After setup and initial build, use the built-in O2R extraction to make your mm.o2r file from a supported ROM. Building the executable and generating 2ship.o2r do not require a ROM.

_Note: Instructions assume using powershell_
```powershell
# Navigate to the 2ship2harkinian repo within powershell. ie: cd "C:\yourpath\2ship2harkinian"
cd 2ship2harkinian

# Configure with Visual Studio 2022
& 'C:\Program Files\CMake\bin\cmake.exe' -S . -B "build/x64" -G "Visual Studio 17 2022" -T v143 -A x64 -DCMAKE_BUILD_TYPE=Release -DCMAKE_POLICY_VERSION_MINIMUM=3.5

# Or configure with Visual Studio 2026 (choose one configure command)
& 'C:\Program Files\CMake\bin\cmake.exe' -S . -B "build/x64" -G "Visual Studio 18 2026" -T v145 -A x64 -DCMAKE_BUILD_TYPE=Release -DCMAKE_POLICY_VERSION_MINIMUM=3.5

# Generate 2ship.o2r
& 'C:\Program Files\CMake\bin\cmake.exe' --build .\build\x64 --config Release --target Generate2ShipOtr

# Compile project
& 'C:\Program Files\CMake\bin\cmake.exe' --build .\build\x64 --config Release

# The executable is .\x64\Release\2ship.exe, relative to the repository root

# Assemble the executable, 2ship.o2r and supporting assets in one folder
& 'C:\Program Files\CMake\bin\cmake.exe' --install .\build\x64 --config Release --component 2s2h --prefix .\build\windows-release

# Run .\build\windows-release\2ship.exe to use the assembled folder
```

`CMAKE_POLICY_VERSION_MINIMUM=3.5` allows CMake 4 to configure older bundled dependencies. Use a separate build directory when switching Visual Studio generators. See the [CMake Visual Studio 2026 generator documentation](https://cmake.org/cmake/help/latest/generator/Visual%20Studio%2018%202026.html) for generator and toolset details.

### Anchor multiplayer

This fork includes [Anchor Beta from garrettjoecox's Anchor branch](https://github.com/garrettjoecox/2ship2harkinian/commit/3820c56b44e8b94e99deb3a3648a8e2286d26348), together with its Sail networking prerequisites. Keep `SKIP_NETWORKING=OFF` (the default) when configuring; Anchor requires SDL2_net 2.2.0 or newer, installed automatically by vcpkg on Windows.

Open the in-game menu with **F1**, then select **Network > Anchor**. Enter your name, room ID, and team ID before enabling the connection. The default server is `anchor.hm64.org:43383`. The Anchor panel includes co-op setup instructions; all players should use compatible Anchor builds. Networking stays disabled until enabled in the GUI, and a saved enabled setting reconnects on later launches.

### Startup introduction

On launch, a short purple-and-gold animation pairs the original 2Ship emblem with **Continued By Mythrax**. It runs once per launch before the normal game boot sequence and finishes automatically after 4.2 seconds. Press **Enter**, **Space**, a controller's **A**, **B**, or **Start** button, or click to skip it.

### Developing 2S2H
With the cmake build system you have two options for working on the project:

#### Visual Studio
To develop using Visual Studio you only need to use cmake to generate the solution file:
```powershell
# Generates 2s2h.sln at `build/x64` for Visual Studio 2022
& 'C:\Program Files\CMake\bin\cmake.exe' -S . -B "build/x64" -G "Visual Studio 17 2022" -T v143 -A x64 -DCMAKE_BUILD_TYPE=Release -DCMAKE_POLICY_VERSION_MINIMUM=3.5
```

For Visual Studio 2026, use `-G "Visual Studio 18 2026" -T v145` instead. Select the `Release` configuration in Visual Studio to match the commands above.

#### Visual Studio Code or another editor
To develop using Visual Studio Code or another editor you only need to open the repository in it.
To build you'll need to follow the instructions from the building section.

_Note: If you're using Visual Studio Code, the [cpack plugin](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cmake-tools) makes it very easy to just press run and debug._

_Experimental: You can also use another build system entirely rather than MSVC like [Ninja](https://ninja-build.org/) for possibly better performance._


### Generating the distributable
After compiling the project you can generate the distributable by running:
```powershell
# Go to build folder
cd "build/x64"
# Generate
& 'C:\Program Files\CMake\bin\cpack.exe' -G ZIP -C Release
```

The ZIP is written to `_packages` in the repository root.

### Additional CMake Targets
#### Clean
```powershell
# If you need to clean the project you can run
& 'C:\Program Files\CMake\bin\cmake.exe' --build .\build\x64 --config Release --target clean
```

#### Regenerate Asset Headers
```powershell
# If you need to regenerate the asset headers to check them into source
& 'C:\Program Files\CMake\bin\cmake.exe' --build .\build\x64 --config Release --target ExtractAssetHeaders
```

## Linux
### Install dependencies
#### Debian/Ubuntu
```sh
# using gcc
apt-get install gcc g++ git cmake ninja-build lsb-release libsdl2-dev libpng-dev libsdl2-net-dev libzip-dev zipcmp zipmerge ziptool nlohmann-json3-dev libtinyxml2-dev libspdlog-dev libopengl-dev libopus-dev libopusfile-dev libogg-dev libvorbis-dev

# or using clang
apt-get install clang git cmake ninja-build lsb-release libsdl2-dev libpng-dev libsdl2-net-dev libzip-dev zipcmp zipmerge ziptool nlohmann-json3-dev libtinyxml2-dev libspdlog-dev libopengl-dev libopus-dev libopusfile-dev libogg-dev libvorbis-dev
```
#### Arch
```sh
# using gcc
pacman -S gcc git cmake ninja lsb-release sdl2 libpng libzip nlohmann-json tinyxml2 spdlog sdl2_net libogg libvorbis opus opusfile

# or using clang
pacman -S clang git cmake ninja lsb-release sdl2 libpng libzip nlohmann-json tinyxml2 spdlog sdl2_net libogg libvorbis opus opusfile
```
#### Fedora
```sh
# using gcc
dnf install gcc gcc-c++ git cmake ninja-build lsb_release SDL2-devel libpng-devel libzip-devel libzip-tools nlohmann-json-devel tinyxml2-devel spdlog-devel libogg-devel libvorbis-devel opus-devel opusfile-devel

# or using clang
dnf install clang git cmake ninja-build lsb_release SDL2-devel libpng-devel libzip-devel libzip-tools nlohmann-json-devel tinyxml2-devel spdlog-devel libogg-devel libvorbis-devel opus-devel opusfile-devel
```
#### openSUSE
```sh
# using gcc
zypper in gcc gcc-c++ git cmake ninja SDL2-devel libpng16-devel libzip-devel libzip-tools nlohmann_json-devel tinyxml2-devel spdlog-devel libogg-devel libvorbis-devel opus-devel opusfile-devel

# or using clang
zypper in clang libstdc++-devel git cmake ninja SDL2-devel libpng16-devel libzip-devel libzip-tools nlohmann_json-devel tinyxml2-devel spdlog-devel libogg-devel libvorbis-devel opus-devel opusfile-devel
```
#### Nix
You can use a `flake.nix` file to instantly setup a development environment using [Nix](https://nixos.org/). Write this `flake.nix` file in the root directory:
```nix
{
  description = "Shipwright development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Build tools
            clang
            git
            cmake
            ninja
            lsb-release
            pkg-config

            # Asset extraction
            python3
            imagemagick

            # SDL2 libraries
            SDL2
            SDL2.dev
            SDL2_net

            # Other libraries
            libpng
            libzip
            nlohmann_json
            tinyxml-2
            spdlog
            libGL
            libGL.dev
            bzip2

            # X11 libraries
            libx11

            # Audio libraries
            libogg
            libogg.dev
            libvorbis
            libvorbis.dev
            libopus
            libopus.dev
            opusfile
            opusfile.dev

            # Runtime Deps
            zenity
          ];

          shellHook = ''
            echo "Shipwright development environment loaded"
            echo "Available tools: clang, git, cmake, ninja"
          '';
        };
      });
}
```
Now type `nix develop` and you will be dropped into a shell with all dependencies, ensuring that all build commands work.

### Build

_Note: If you're using Visual Studio Code, the [CMake Tools plugin](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cmake-tools) makes it very easy to just press run and debug._

```bash
# Clone the repo and enter the directory
git clone https://github.com/2ship2harkinian/2ship2harkinian.git
cd 2ship2harkinian

# Clone the submodules
git submodule update --init

# Generate Ninja project
# Add `-DCMAKE_BUILD_TYPE:STRING=Release` if you're packaging
# Add `-DPython3_EXECUTABLE=$(which python3)` if you are using non-standard Python installations such as PyEnv
cmake -H. -Bbuild-cmake -GNinja

# Generate 2ship.o2r
cmake --build build-cmake --target Generate2ShipOtr

# Compile the project
# Add `--config Release` if you're packaging
cmake --build build-cmake

# Now you can run the executable in ./build-cmake/mm/2s2h.elf
# To develop the project open the repository in VSCode (or your preferred editor)
```

### Generate a distributable
After compiling the project you can generate a distributable by running of the following:
```bash
# Go to build folder
cd build-cmake
# Generate
cpack -G DEB
cpack -G ZIP
cpack -G External (creates appimage)
```

### Additional CMake Targets
#### Clean
```bash
# If you need to clean the project you can run
cmake --build build-cmake --target clean
```

#### Regenerate Asset Headers
```bash
# If you need to regenerate the asset headers to check them into source
cmake --build build-cmake --target ExtractAssetHeaders
```

## macOS
Requires Xcode (or xcode-tools) && `sdl2, libpng, glew, ninja, cmake, nlohmann-json, libzip` (can be installed via homebrew, macports, etc)

**Important: For maximum performance make sure you have ninja build tools installed!**

_Note: If you're using Visual Studio Code, the [cpack plugin](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cmake-tools) makes it very easy to just press run and debug._

```bash
# Clone the repo
git clone https://github.com/2ship2harkinian/2ship2harkinian.git
cd 2ship2harkinian
# Clone the submodule libultraship
git submodule update --init

# Generate Ninja project
# Add `-DCMAKE_BUILD_TYPE:STRING=Release` if you're packaging
cmake -H. -Bbuild-cmake -GNinja

# Generate 2ship.o2r
cmake --build build-cmake --target Generate2ShipOtr

# Compile the project
# Add `--config Release` if you're packaging
cmake --build build-cmake

# Now you can run the executable file:
./build-cmake/mm/2s2h-macos
# To develop the project open the repository in VSCode (or your preferred editor)
```

### Generating a distributable
After compiling the project you can generate a distributable by running of the following:
```bash
# Go to build folder
cd build-cmake
# Generate
cpack
```

### Additional CMake Targets
#### Clean
```bash
# If you need to clean the project you can run
cmake --build build-cmake --target clean
```

#### Regenerate Asset Headers
```bash
# If you need to regenerate the asset headers to check them into source
cmake --build build-cmake --target ExtractAssetHeaders
```

# Compatible Roms
See [`supportedHashes.json`](supportedHashes.json)

## Getting CI to work on your fork

The CI works via [Github Actions](https://github.com/features/actions) where we mostly make use of machines hosted by Github; except for the very first step of the CI process called "Extract assets". This steps extracts assets from the game file and generates an "assets" folder in `mm/`.

To get this step working on your fork, you'll need to add a machine to your own repository as a self-hosted runner via "Settings > Actions > Runners" in your repository settings. Make sure to add the 'asset-builder' tag to your newly added runner to assign it to run this step. To setup your runner as a service read the docs [here](https://docs.github.com/en/actions/hosting-your-own-runners/configuring-the-self-hosted-runner-application-as-a-service?platform=linux).

### Runner on Windows
You'll have to enable the ability to run unsigned scripts through PowerShell. To do this, open Powershell as administrator and run `set-executionpolicy remotesigned`. Most dependencies get installed as part of the CI process. You will also need to separately install 7z and add it to the PATH so `7z` can be run as a command. [Chocolatey](https://chocolatey.org/) or other package managers can be used to install it easily.

### Runner on UNIX systems
If you're on macOS or Linux take a look at `macports-deps.txt` or `apt-deps.txt` to see the dependencies expected to be on your machine.
