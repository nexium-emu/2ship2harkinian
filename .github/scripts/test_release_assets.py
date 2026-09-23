import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import release_assets


class ReleaseAssetsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cmake = self.root / "CMakeLists.txt"
        self.cmake.write_text("project(2s2h VERSION 5.0.1 LANGUAGES C CXX)\n", encoding="utf-8")
        self.commit = "0123456789abcdef" * 2 + "01234567"
        self.inputs = self.root / "artifacts"
        self.inputs.mkdir()
        self.output = self.root / "dist"

    def info(self, tag="v5.0.1", channel="tag"):
        return release_assets.metadata(self.cmake, self.commit, channel, tag)

    def make_assets(self, extra_zip=None):
        with zipfile.ZipFile(self.inputs / "2ship-windows.zip", "w") as archive:
            archive.writestr("2ship.exe", b"executable")
            archive.writestr("2ship.o2r", b"port assets")
            for name, data in (extra_zip or {}).items():
                archive.writestr(name, data)
        (self.inputs / "2ship-linux-x86_64.AppImage").write_bytes(b"appimage")
        (self.inputs / "2ship-macos-universal.dmg").write_bytes(b"dmg")
        (self.inputs / "readme.txt").write_text("Readme", encoding="utf-8")

    def package(self):
        release_assets.package(self.info(), self.inputs, self.output, "https://github.com/example/repo/actions/runs/123")

    def test_tag_must_match_project(self):
        with self.assertRaisesRegex(ValueError, "differs from CMake"):
            self.info("v5.0.2")

    def test_release_and_prerelease_flags(self):
        self.assertFalse(self.info()["prerelease"])
        self.assertFalse(self.info("v5.0.1+build.3")["prerelease"])
        for tag in ("v5.0.1-beta.2", "v5.0.1-rc.1", "v5.0.1-alpha+build.3"):
            with self.subTest(tag=tag):
                self.assertTrue(self.info(tag)["prerelease"])
        for tag in ("5.0.1", "v05.0.1", "v5.0.1-rc.01", "v5.0.1-", "v5.0.1\n"):
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                self.info(tag)

    def test_preview_uses_full_commit_prefix(self):
        info = self.info(None, "preview")
        self.assertEqual(info["tag"], "preview-0123456789ab")
        self.assertEqual(info["commit"], self.commit)
        self.assertTrue(info["prerelease"])
        with self.assertRaisesRegex(ValueError, "40-character"):
            release_assets.metadata(self.cmake, "abcdef0", "preview")
        with self.assertRaisesRegex(ValueError, "do not supply"):
            self.info("v5.0.1", "preview")

    def test_missing_and_empty_assets_fail_before_output(self):
        with self.assertRaisesRegex(ValueError, "exactly one"):
            self.package()
        self.make_assets()
        (self.inputs / "2ship-macos-universal.dmg").write_bytes(b"")
        with self.assertRaisesRegex(ValueError, "empty"):
            self.package()
        self.assertFalse(self.output.exists())

    def test_duplicate_assets_are_rejected(self):
        self.make_assets()
        duplicate = self.inputs / "other"
        duplicate.mkdir()
        (duplicate / "2ship-windows.zip").write_bytes(b"duplicate")
        with self.assertRaisesRegex(ValueError, "found 2"):
            self.package()

    def test_bad_zip_and_missing_executable_are_rejected(self):
        self.make_assets()
        archive_path = self.inputs / "2ship-windows.zip"
        archive_path.write_bytes(b"not a ZIP")
        with self.assertRaisesRegex(ValueError, "Invalid Windows ZIP"):
            self.package()
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr("2ship.o2r", b"port assets")
        with self.assertRaisesRegex(ValueError, "missing: 2ship.exe"):
            self.package()

    def test_crc_corruption_is_rejected(self):
        self.make_assets()
        archive_path = self.inputs / "2ship-windows.zip"
        data = archive_path.read_bytes().replace(b"executable", b"corruption", 1)
        archive_path.write_bytes(data)
        with self.assertRaisesRegex(ValueError, "CRC check failed"):
            self.package()

    def test_game_data_and_unsafe_paths_are_rejected(self):
        forbidden = (
            "mm.o2r", "assets/MM.O2R", "game.z64", "game.V64", "game.n64",
            "../escape", "/absolute", "C:\\absolute", "nested\\..\\escape",
        )
        for name in forbidden:
            with self.subTest(name=name):
                self.make_assets({name: b"forbidden"})
                with self.assertRaises(ValueError):
                    self.package()
                self.assertFalse(self.output.exists())

    def test_packages_manifest_and_checksums(self):
        self.make_assets()
        self.package()
        manifest = json.loads((self.output / "build-info.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["commit"], self.commit)
        self.assertEqual(manifest["tag"], "v5.0.1")
        self.assertEqual(manifest["version"], "5.0.1")
        self.assertEqual(manifest["run_url"], "https://github.com/example/repo/actions/runs/123")
        expected = {f"2ship-v5.0.1-{suffix}" for suffix in release_assets.ASSETS.values()}
        self.assertEqual({entry["name"] for entry in manifest["files"]}, expected)
        for entry in manifest["files"]:
            data = (self.output / entry["name"]).read_bytes()
            self.assertEqual(entry["size"], len(data))
            self.assertEqual(entry["sha256"], hashlib.sha256(data).hexdigest())
        checksum_lines = (self.output / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(checksum_lines), 4)
        for line in checksum_lines:
            digest, name = line.split("  ", 1)
            self.assertEqual(digest, hashlib.sha256((self.output / name).read_bytes()).hexdigest())
        self.assertEqual({path.name for path in self.output.iterdir()}, expected | {"build-info.json", "SHA256SUMS"})
        with self.assertRaisesRegex(ValueError, "must be empty"):
            self.package()

    def test_cli_appends_github_outputs(self):
        outputs = self.root / "outputs"
        outputs.write_text("existing=value\n", encoding="utf-8")
        with patch.dict(os.environ, {"GITHUB_OUTPUT": str(outputs)}), contextlib.redirect_stdout(io.StringIO()) as stdout:
            result = release_assets.main([
                "metadata", "--cmake", str(self.cmake), "--commit", self.commit,
                "--channel", "tag", "--tag", "v5.0.1-rc.1",
            ])
        self.assertEqual(result, 0)
        self.assertIn("prerelease=true\n", stdout.getvalue())
        self.assertEqual(outputs.read_text(encoding="utf-8"), "existing=value\n" + stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
