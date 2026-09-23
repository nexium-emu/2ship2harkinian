#!/usr/bin/env python3
"""Validate release metadata and prepare the three native release packages."""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
import zipfile


ASSETS = {
    "2ship-windows.zip": "windows-x64.zip",
    "2ship-linux-x86_64.AppImage": "linux-x86_64.AppImage",
    "2ship-macos-universal.dmg": "macos-universal.dmg",
}
NUMBER = r"(?:0|[1-9][0-9]*)"
VERSION = rf"{NUMBER}\.{NUMBER}\.{NUMBER}"
TAG = re.compile(
    rf"v(?P<version>{VERSION})"
    r"(?:-(?P<prerelease>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
)


def metadata(cmake, commit, channel, tag=None):
    if not re.fullmatch(r"[0-9a-fA-F]{40}", commit):
        raise ValueError("Commit must be a full 40-character Git SHA")
    source = Path(cmake).read_text(encoding="utf-8")
    source = re.sub(r"#[^\n]*", "", source)
    project = re.search(
        rf"\bproject\s*\(\s*2s2h\s+VERSION\s+({VERSION})(?=\s|\))",
        source,
        re.IGNORECASE,
    )
    if not project:
        raise ValueError("Cannot find project(2s2h VERSION X.Y.Z) in CMake")
    version = project.group(1)
    commit = commit.lower()
    if channel == "tag":
        match = TAG.fullmatch(tag or "")
        if not match:
            raise ValueError("Release tag must be vX.Y.Z or a valid SemVer prerelease")
        if match.group("version") != version:
            raise ValueError(f"Tag version {match.group('version')} differs from CMake version {version}")
        prerelease = match.group("prerelease")
        if prerelease and any(
            part.isdigit() and len(part) > 1 and part[0] == "0"
            for part in prerelease.split(".")
        ):
            raise ValueError("Numeric SemVer prerelease identifiers cannot have leading zeros")
        prerelease = bool(prerelease)
    elif channel == "preview":
        if tag is not None:
            raise ValueError("Preview tags are generated from the commit; do not supply --tag")
        tag = f"preview-{commit[:12]}"
        prerelease = True
    else:
        raise ValueError(f"Unknown release channel: {channel}")
    return {"tag": tag, "version": version, "prerelease": prerelease, "commit": commit, "channel": channel}


def validate_windows_zip(path):
    try:
        with zipfile.ZipFile(path) as archive:
            files = set()
            for entry in archive.infolist():
                name = entry.orig_filename.replace("\\", "/")
                parts = PurePosixPath(name).parts
                if "\0" in name or name.startswith("/") or re.match(r"^[A-Za-z]:", name) or ".." in parts:
                    raise ValueError(f"Unsafe Windows ZIP path: {name!r}")
                if stat.S_ISLNK(entry.external_attr >> 16):
                    raise ValueError(f"Symlinks are not allowed in the Windows ZIP: {name}")
                if entry.is_dir():
                    continue
                basename = PurePosixPath(name).name.lower()
                if basename == "mm.o2r" or PurePosixPath(basename).suffix in {".z64", ".v64", ".n64"}:
                    raise ValueError(f"Game data must not be distributed: {name}")
                files.add(basename)
            missing = {"2ship.exe", "2ship.o2r"} - files
            if missing:
                raise ValueError(f"Windows ZIP is missing: {', '.join(sorted(missing))}")
            corrupt = archive.testzip()
            if corrupt:
                raise ValueError(f"Windows ZIP CRC check failed: {corrupt}")
    except (zipfile.BadZipFile, RuntimeError) as error:
        raise ValueError(f"Invalid Windows ZIP: {error}") from error


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def package(info, input_dir, output_dir, run_url):
    input_dir, output_dir = Path(input_dir), Path(output_dir)
    if not input_dir.is_dir():
        raise ValueError(f"Artifact directory does not exist: {input_dir}")
    inputs = {}
    for name in ASSETS:
        matches = [path for path in input_dir.rglob(name) if path.name == name and path.is_file()]
        if len(matches) != 1:
            raise ValueError(f"Expected exactly one {name}; found {len(matches)}")
        if matches[0].stat().st_size == 0:
            raise ValueError(f"Artifact is empty: {name}")
        inputs[name] = matches[0]
    validate_windows_zip(inputs["2ship-windows.zip"])
    if output_dir.exists() and (not output_dir.is_dir() or any(output_dir.iterdir())):
        raise ValueError(f"Output directory must be empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    files = []
    for name, suffix in ASSETS.items():
        destination = output_dir / f"2ship-{info['tag']}-{suffix}"
        shutil.copyfile(inputs[name], destination)
        if destination.suffix == ".AppImage":
            destination.chmod(0o755)
        files.append({"name": destination.name, "size": destination.stat().st_size, "sha256": sha256(destination)})
    manifest = output_dir / "build-info.json"
    manifest.write_text(
        json.dumps({**info, "run_url": run_url, "files": files}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    checksums = [f"{entry['sha256']}  {entry['name']}" for entry in files]
    checksums.append(f"{sha256(manifest)}  {manifest.name}")
    (output_dir / "SHA256SUMS").write_text("\n".join(checksums) + "\n", encoding="utf-8")


def emit_outputs(info):
    outputs = "\n".join(
        f"{key}={str(value).lower() if isinstance(value, bool) else value}"
        for key, value in info.items()
    ) + "\n"
    print(outputs, end="")
    if os.environ.get("GITHUB_OUTPUT"):
        with Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as stream:
            stream.write(outputs)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("metadata", "package"):
        command = commands.add_parser(name)
        command.add_argument("--cmake", required=True, type=Path)
        command.add_argument("--commit", required=True)
        command.add_argument("--channel", required=True, choices=("tag", "preview"))
        command.add_argument("--tag")
        if name == "package":
            command.add_argument("--input-dir", required=True, type=Path)
            command.add_argument("--output-dir", required=True, type=Path)
            command.add_argument("--run-url", required=True)
    args = parser.parse_args(argv)
    try:
        info = metadata(args.cmake, args.commit, args.channel, args.tag)
        if args.command == "package":
            package(info, args.input_dir, args.output_dir, args.run_url)
        emit_outputs(info)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
